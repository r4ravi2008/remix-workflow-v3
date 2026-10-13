import { Effect, Schema } from 'effect'

import type { D1Database } from '@cloudflare/workers-types'

import { canonicalJson } from '../canonical'
import { outputs, validateArtistProfile } from '../domain'
import {
  ApiError,
  ArtistRequest,
  AssetRow,
  CompleteRequest,
  EnrollmentRequest,
  ExchangeRequest,
  HoldRequest,
  InviteRequest,
  OutputUpload,
  ProgressRequest,
  ReleaseBrief,
  ResumeRequest,
  Submission,
  maxOutputBytes,
  partBytes,
  requireCondition,
  sha256Pattern,
  validateBrief,
  validateMeasurement,
} from './contracts'
import { Store, StudioStore } from './store'

declare const FixedLengthStream: new (length: number) => {
  readable: ReadableStream<Uint8Array>
  writable: WritableStream<Uint8Array>
}

export interface MediaBucket {
  put(
    key: string,
    body: ReadableStream<Uint8Array>,
    options: {
      sha256: string
      httpMetadata: { contentType: string }
      customMetadata: Record<string, string>
    },
  ): Promise<unknown>
  head(key: string): Promise<{ size: number; etag?: string } | null>
  get(
    key: string,
    options: {
      range?: { offset: number; length?: number }
      onlyIf?: { etagMatches: string }
    },
  ): Promise<{
    body: ReadableStream<Uint8Array>
    size: number
    httpEtag: string
    range?: { offset?: number; length?: number }
  } | null>
  createMultipartUpload(
    key: string,
    options: {
      httpMetadata: { contentType: string }
      customMetadata: Record<string, string>
    },
  ): Promise<{ uploadId: string }>
  resumeMultipartUpload(
    key: string,
    uploadId: string,
  ): {
    uploadPart(number: number, body: ArrayBuffer): Promise<{ etag: string }>
    complete(
      parts: Array<{ partNumber: number; etag: string }>,
    ): Promise<unknown>
  }
}
export interface ProductionEnv {
  STUDIO_DB: D1Database
  MEDIA: MediaBucket
  STUDIO_OPERATOR_TOKEN: string
  EDITOR?: { fetch: (request: Request) => Promise<Response> }
}
const digest = async (value: string | ArrayBuffer) =>
  Array.from(
    new Uint8Array(
      await crypto.subtle.digest(
        'SHA-256',
        typeof value === 'string' ? new TextEncoder().encode(value) : value,
      ),
    ),
    byte => byte.toString(16).padStart(2, '0'),
  ).join('')
const token = () =>
  `${crypto.randomUUID()}${crypto.randomUUID()}`.replaceAll('-', '')
const now = () => Math.floor(Date.now() / 1000)
const json = (value: unknown, status = 200, headers: HeadersInit = {}) =>
  Response.json(value, {
    status,
    headers: {
      'Cache-Control': 'no-store',
      'X-Content-Type-Options': 'nosniff',
      ...headers,
    },
  })
const bearer = (request: Request) =>
  request.headers.get('Authorization')?.replace(/^Bearer /, '') ?? ''
const cookie = (request: Request) =>
  request.headers
    .get('Cookie')
    ?.split(';')
    .map(value => value.trim())
    .find(value => value.startsWith('studio_session='))
    ?.slice(15) ?? ''
const secureCookie = (value: string, lifetime: number) =>
  `studio_session=${value}; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=${lifetime}`
const decodeBody = async <S extends Schema.ConstraintDecoder<unknown>>(
  request: Request,
  schema: S,
): Promise<S['Type']> => {
  requireCondition(
    Number(request.headers.get('Content-Length') ?? 0) <= 65536,
    413,
    'The request is too large.',
  )
  requireCondition(request.body, 400, 'The request body is missing.')
  const reader = request.body.getReader()
  const decoder = new TextDecoder()
  const boundedText = async (
    chunks: Array<string>,
    bytes: number,
  ): Promise<string> => {
    const chunk = await reader.read()
    if (chunk.done) return chunks.join('') + decoder.decode()
    if (bytes + chunk.value.byteLength > 65536) {
      await reader.cancel()
      throw new ApiError(413, 'The request is too large.')
    }
    return boundedText(
      [...chunks, decoder.decode(chunk.value, { stream: true })],
      bytes + chunk.value.byteLength,
    )
  }
  const text = await boundedText([], 0)
  try {
    return Schema.decodeUnknownSync(schema)(JSON.parse(text))
  } catch {
    throw new ApiError(400, 'The request has missing or invalid fields.')
  }
}
const publicAsset = (asset: AssetRow) => ({
  id: asset.id,
  outputId: asset.output_id,
  bytes: asset.bytes,
  sha256: asset.sha256,
  contentType: asset.content_type,
  state: asset.state,
  verified: asset.verified === 1,
  measurement: asset.measurement_json
    ? JSON.parse(asset.measurement_json)
    : null,
})
export const makeStore = (database: D1Database) =>
  new Store({
    first: (sql, values) =>
      database
        .prepare(sql)
        .bind(...values)
        .first(),
    all: async (sql, values) =>
      (
        await database
          .prepare(sql)
          .bind(...values)
          .all()
      ).results,
    run: async (sql, values) => {
      await database
        .prepare(sql)
        .bind(...values)
        .run()
    },
    batch: async statements => {
      await database.batch(
        statements.map(statement =>
          database.prepare(statement.sql).bind(...statement.values),
        ),
      )
    },
  })

const handle = async (request: Request, env: ProductionEnv, store: Store) => {
  const url = new URL(request.url)
  const path = url.pathname
  const time = now()
  const operator = async () => {
    requireCondition(
      env.STUDIO_OPERATOR_TOKEN.length >= 32 &&
        (await digest(bearer(request))) ===
          (await digest(env.STUDIO_OPERATOR_TOKEN)),
      401,
      'Operator authentication is required.',
    )
  }
  const device = async () => {
    const value = await store.device(await digest(bearer(request)), time)
    requireCondition(value, 401, 'Worker authentication is required.')
    return value
  }
  const tenant = async () => {
    const value = await store.session(await digest(cookie(request)), time)
    requireCondition(value, 401, 'Sign in with your studio invitation.')
    return value
  }
  if (
    !['GET', 'HEAD'].includes(request.method) &&
    !path.startsWith('/api/worker/') &&
    !path.startsWith('/api/operator/')
  ) {
    requireCondition(
      request.headers.get('Origin') === url.origin,
      403,
      'This action must originate from your studio.',
    )
  }
  if (path === '/api/health' && request.method === 'GET') {
    return json({
      service: 'release-kit-studio',
      stage: 'invite-beta',
      version: '0.2.0',
      productionConnected: false,
      cloudProduction: false,
      tenantAuthentication: true,
      cloudUploads: true,
      jobDispatch: true,
      finishing: 'cloudflare-editor',
      gpuTransport: 'worker-provider',
    })
  }
  if (path === '/api/operator/invites' && request.method === 'POST') {
    await operator()
    const body = await decodeBody(request, InviteRequest)
    requireCondition(
      body.tenantName.trim().length > 0 && body.tenantName.length <= 100,
      400,
      'Provide a studio name.',
    )
    const raw = token()
    const tenantId = crypto.randomUUID()
    await store.issueInvite(
      tenantId,
      body.tenantName.trim(),
      await digest(raw),
      time,
    )
    return json({ tenantId, token: raw, expiresIn: 86400 }, 201)
  }
  const returnInvite = path.match(
    /^\/api\/operator\/tenants\/([a-zA-Z0-9-]+)\/invites$/,
  )
  if (returnInvite && request.method === 'POST') {
    await operator()
    const tenantId = returnInvite[1] ?? ''
    const raw = token()
    await store.issueReturnInvite(tenantId, await digest(raw), time)
    return json({ tenantId, token: raw, expiresIn: 86400 }, 201)
  }
  if (path === '/api/operator/devices' && request.method === 'POST') {
    await operator()
    const body = await decodeBody(request, EnrollmentRequest)
    requireCondition(
      body.name.trim().length > 0 && body.name.length <= 100,
      400,
      'Provide a worker name.',
    )
    const raw = token()
    const id = crypto.randomUUID()
    await store.enroll(id, await digest(raw), body.name.trim())
    return json({ id, token: raw }, 201)
  }
  const revokeDevice = path.match(
    /^\/api\/operator\/devices\/([a-zA-Z0-9-]+)\/revoke$/,
  )
  if (revokeDevice && request.method === 'POST') {
    await operator()
    const worker = await store.revokeDevice(revokeDevice[1] ?? '')
    return json({ id: worker.id, revoked: true })
  }
  if (path === '/api/auth/exchange' && request.method === 'POST') {
    const body = await decodeBody(request, ExchangeRequest)
    requireCondition(
      /^[a-f0-9]{64}$/.test(body.token),
      401,
      'Invalid studio invitation.',
    )
    const raw = token()
    const account = await store.exchangeInvite(
      await digest(body.token),
      await digest(raw),
      time,
    )
    return json({ tenant: account }, 200, {
      'Set-Cookie': secureCookie(raw, 7 * 86400),
    })
  }
  if (path === '/api/auth/session' && request.method === 'GET')
    return json({ tenant: await tenant() })
  if (path === '/api/artist-profile') {
    const account = await tenant()
    if (request.method === 'GET')
      return json({ artist: await store.artist(account.id) })
    if (request.method === 'PUT') {
      const body = await decodeBody(request, ArtistRequest)
      const errors = validateArtistProfile(body.profile)
      requireCondition(
        errors.length === 0,
        400,
        errors[0] ?? 'Invalid artist identity.',
      )
      requireCondition(
        Number.isInteger(body.expectedRevision) &&
          body.expectedRevision >= 0 &&
          body.expectedRevision < 1000000000,
        400,
        'Invalid artist identity revision.',
      )
      return json({
        artist: await store.saveArtist(
          account.id,
          body.profile,
          body.expectedRevision,
          time,
        ),
      })
    }
  }
  if (path === '/api/auth/logout' && request.method === 'POST') {
    await store.logout(await digest(cookie(request)))
    return json({ signedOut: true }, 200, { 'Set-Cookie': secureCookie('', 0) })
  }
  if (path === '/api/releases' && request.method === 'GET')
    return json({
      releases: (await store.list((await tenant()).id)).map(release => ({
        id: release.id,
        title: Schema.decodeUnknownSync(ReleaseBrief)(
          JSON.parse(release.brief_json),
        ).title,
        state: release.state,
        createdAt: release.created_at,
      })),
    })
  if (path === '/api/releases' && request.method === 'POST') {
    const account = await tenant()
    const body = await decodeBody(request, Submission)
    requireCondition(
      /^[a-zA-Z0-9-]{16,100}$/.test(body.requestKey),
      400,
      'Invalid submission key.',
    )
    validateBrief(body.brief)
    const release = await store.createRelease(
      account.id,
      crypto.randomUUID(),
      body.requestKey,
      body.brief,
      time,
    )
    return json({ id: release.id, state: release.state }, 201)
  }
  const releaseRoute = path.match(
    /^\/api\/releases\/([a-zA-Z0-9-]+)(?:\/(audio|start|archive))?$/,
  )
  if (releaseRoute) {
    const account = await tenant()
    const id = releaseRoute[1] ?? ''
    const release = await store.release(account.id, id)
    requireCondition(release, 404, 'Release not found.')
    if (
      releaseRoute[2] === 'archive' &&
      ['GET', 'HEAD'].includes(request.method)
    ) {
      requireCondition(
        env.EDITOR,
        503,
        'The Cloudflare editor is not connected.',
      )
      const job = await store.jobForRelease(id)
      requireCondition(
        release.state === 'review' &&
          job?.state === 'review' &&
          job.receipt_json,
        409,
        'The verified release kit is not ready.',
      )
      const assets = (await store.assets(id)).filter(
        asset =>
          asset.kind === 'output' &&
          asset.state === 'ready' &&
          asset.verified === 1 &&
          asset.job_id === job.id &&
          asset.attempt === job.attempt,
      )
      requireCondition(
        assets.length === 6 &&
          outputs.every(
            output =>
              assets.filter(asset => asset.output_id === output.id).length ===
              1,
          ),
        409,
        'All six verified outputs are required.',
      )
      const receipt = Schema.decodeUnknownSync(
        Schema.Struct({
          finishing: Schema.Literal('cloudflare-editor'),
          editorJobId: Schema.String.check(
            Schema.isPattern(/^[a-zA-Z0-9_-]{1,80}$/),
          ),
        }),
      )(JSON.parse(job.receipt_json))
      const target = new URL(request.url)
      target.pathname = `/v1/jobs/${receipt.editorJobId}/archive`
      target.search = ''
      target.searchParams.set('releaseId', id)
      const headers = new Headers(request.headers)
      headers.delete('Authorization')
      return env.EDITOR.fetch(
        new Request(target, { method: request.method, headers }),
      )
    }
    if (!releaseRoute[2] && request.method === 'GET') {
      const job = await store.jobForRelease(id)
      const assets = (await store.assets(id)).filter(
        asset => asset.kind === 'output' && asset.state === 'ready',
      )
      const editorReceipt = job?.receipt_json
        ? Schema.decodeUnknownSync(
            Schema.Struct({ finishing: Schema.optionalKey(Schema.String) }),
          )(JSON.parse(job.receipt_json))
        : null
      return json({
        id,
        state: release.state,
        brief: Schema.decodeUnknownSync(ReleaseBrief)(
          JSON.parse(release.brief_json),
        ),
        job: job
          ? {
              id: job.id,
              state: job.state,
              phase: job.phase,
              progress: job.progress,
              attempt: job.attempt,
              error: job.error,
            }
          : null,
        assets: assets.map(publicAsset),
        archiveAvailable:
          !!env.EDITOR &&
          release.state === 'review' &&
          job?.state === 'review' &&
          editorReceipt?.finishing === 'cloudflare-editor' &&
          assets.length === 6 &&
          outputs.every(
            output =>
              assets.filter(
                asset =>
                  asset.output_id === output.id &&
                  asset.verified === 1 &&
                  asset.job_id === job.id &&
                  asset.attempt === job.attempt,
              ).length === 1,
          ),
      })
    }
    if (releaseRoute[2] === 'audio' && request.method === 'PUT') {
      requireCondition(
        release.state === 'uploading',
        409,
        'This release has already started.',
      )
      const brief = Schema.decodeUnknownSync(ReleaseBrief)(
        JSON.parse(release.brief_json),
      )
      const suppliedBytes = Number(
        request.headers.get('X-Upload-Bytes') ??
          request.headers.get('Content-Length'),
      )
      requireCondition(
        suppliedBytes === brief.audioBytes &&
          request.headers.get('X-Content-Sha256') === brief.audioSha256,
        400,
        'Audio size or SHA-256 differs from the brief.',
      )
      const existing = await store.audio(id)
      const audio =
        existing ??
        Schema.decodeUnknownSync(AssetRow)({
          id: crypto.randomUUID(),
          release_id: id,
          job_id: null,
          attempt: null,
          kind: 'audio',
          output_id: null,
          object_key: `${account.id}/${id}/source/audio`,
          bytes: brief.audioBytes,
          sha256: brief.audioSha256,
          content_type: 'application/octet-stream',
          state: 'uploading',
          upload_id: null,
          verified: 0,
          measurement_json: null,
          created_at: time,
        })
      if (!existing) await store.insertAsset(audio)
      requireCondition(request.body, 400, 'The audio body is missing.')
      const fixed = new FixedLengthStream(audio.bytes)
      await Promise.all([
        env.MEDIA.put(audio.object_key, fixed.readable, {
          sha256: audio.sha256,
          httpMetadata: { contentType: audio.content_type },
          customMetadata: { sha256: audio.sha256 },
        }),
        request.body.pipeTo(fixed.writable),
      ])
      const head = await env.MEDIA.head(audio.object_key)
      requireCondition(
        head?.size === audio.bytes,
        409,
        'The stored audio has an unexpected size.',
      )
      await store.markUploaded(audio.id, true)
      return json({ assetId: audio.id, verified: true })
    }
    if (releaseRoute[2] === 'start' && request.method === 'POST') {
      const job = await store.startRelease(id, crypto.randomUUID(), time)
      return json({ job: job ? { id: job.id, state: job.state } : null }, 202)
    }
  }
  if (path === '/api/worker/claim' && request.method === 'POST') {
    const worker = await device()
    const raw = token()
    const job = await store.claim(worker.id, await digest(raw), time)
    if (!job) return json({ job: null })
    const release = await store.releaseById(job.release_id)
    const audio = await store.audio(job.release_id)
    requireCondition(
      release && audio?.verified === 1,
      409,
      'The queued source is incomplete.',
    )
    return json({
      job: {
        id: job.id,
        releaseId: job.release_id,
        attempt: job.attempt,
        lease: raw,
        expiresAt: job.lease_until,
        brief: JSON.parse(release.brief_json),
        audioAssetId: audio.id,
        contract: 'release-kit-v1',
      },
    })
  }
  if (path === '/api/worker/holds' && request.method === 'GET') {
    const worker = await device()
    return json({
      jobs: await Promise.all(
        (await store.holds(worker.id)).map(async job => {
          const release = await store.releaseById(job.release_id)
          requireCondition(release, 404, 'Release not found.')
          return {
            id: job.id,
            releaseId: job.release_id,
            state: job.state,
            attempt: job.attempt,
            brief: JSON.parse(release.brief_json),
          }
        }),
      ),
    })
  }
  const workerJobStatus = path.match(/^\/api\/worker\/jobs\/([a-zA-Z0-9-]+)$/)
  if (workerJobStatus && request.method === 'GET') {
    const worker = await device()
    const job = await store.ownedJob(workerJobStatus[1] ?? '', worker.id)
    requireCondition(job, 404, 'Job not found for this worker.')
    return json({
      id: job.id,
      releaseId: job.release_id,
      state: job.state,
      attempt: job.attempt,
      assets: (await store.assets(job.release_id))
        .filter(asset => asset.kind === 'output' && asset.state === 'ready')
        .map(publicAsset),
    })
  }
  const jobRoute = path.match(
    /^\/api\/worker\/jobs\/([a-zA-Z0-9-]+)\/(heartbeat|uploads|complete|fail|hold|resume)$/,
  )
  if (jobRoute) {
    const worker = await device()
    if (jobRoute[2] === 'resume' && request.method === 'POST') {
      const body = await decodeBody(request, ResumeRequest)
      const job = await store.resumable(jobRoute[1] ?? '', worker.id)
      const release = await store.releaseById(job.release_id)
      requireCondition(release, 404, 'Release not found.')
      const brief = Schema.decodeUnknownSync(ReleaseBrief)(
        JSON.parse(release.brief_json),
      )
      requireCondition(
        body.briefSha256 === (await digest(canonicalJson(brief))) &&
          body.audioSha256 === brief.audioSha256 &&
          body.reviewEvidence.trim().length > 0 &&
          body.reviewEvidence.length <= 2000,
        409,
        'Register a reviewed plan matching this release and its full artist brief.',
      )
      await store.resume(job, worker.id, body, time)
      return json({ state: 'queued' })
    }
    const leaseHash = await digest(request.headers.get('X-Job-Lease') ?? '')
    const job = await store.lease(jobRoute[1] ?? '', worker.id, leaseHash, time)
    if (jobRoute[2] === 'hold' && request.method === 'POST') {
      const body = await decodeBody(request, HoldRequest)
      await store.hold(job, leaseHash, body.reason, body.receipt, time)
      return json({ state: body.reason })
    }
    if (jobRoute[2] === 'heartbeat' && request.method === 'POST') {
      const body = await decodeBody(request, ProgressRequest)
      requireCondition(
        body.phase.length > 0 &&
          body.phase.length <= 200 &&
          Number.isFinite(body.progress) &&
          body.progress >= 0 &&
          body.progress <= 1,
        400,
        'Invalid progress update.',
      )
      const current = await store.heartbeat(
        job,
        leaseHash,
        body.phase,
        body.progress,
        body.receipt,
        time,
      )
      return json({ expiresAt: current.lease_until })
    }
    if (jobRoute[2] === 'uploads' && request.method === 'POST') {
      const body = await decodeBody(request, OutputUpload)
      requireCondition(
        Number.isInteger(body.bytes) &&
          body.bytes > 0 &&
          body.bytes <= maxOutputBytes &&
          sha256Pattern.test(body.sha256),
        400,
        'Invalid output size or SHA-256.',
      )
      const contentType =
        body.outputId === 'artwork' || body.outputId === 'thumbnail'
          ? 'image/jpeg'
          : 'video/mp4'
      requireCondition(
        body.contentType === contentType,
        400,
        'Invalid output media type.',
      )
      const id = crypto.randomUUID()
      const key = `production/${job.release_id}/${job.attempt}/${id}`
      const multipart = await env.MEDIA.createMultipartUpload(key, {
        httpMetadata: { contentType },
        customMetadata: { sha256: body.sha256 },
      })
      const asset = Schema.decodeUnknownSync(AssetRow)({
        id,
        release_id: job.release_id,
        job_id: job.id,
        attempt: job.attempt,
        kind: 'output',
        output_id: body.outputId,
        object_key: key,
        bytes: body.bytes,
        sha256: body.sha256,
        content_type: contentType,
        state: 'uploading',
        upload_id: multipart.uploadId,
        verified: 0,
        measurement_json: null,
        created_at: time,
      })
      await store.insertAsset(asset)
      return json({ assetId: id, partBytes }, 201)
    }
    if (jobRoute[2] === 'complete' && request.method === 'POST') {
      const body = await decodeBody(request, CompleteRequest)
      const release = await store.releaseById(job.release_id)
      requireCondition(release, 404, 'Release not found.')
      const brief = Schema.decodeUnknownSync(ReleaseBrief)(
        JSON.parse(release.brief_json),
      )
      const measured = await Promise.all(
        body.outputs.map(async output => {
          const asset = await store.asset(output.assetId)
          requireCondition(asset?.output_id, 409, 'An output is missing.')
          validateMeasurement(
            asset.output_id,
            output.measurement,
            brief.audioDuration,
          )
          return { asset, measurement: output.measurement }
        }),
      )
      await store.complete(job, leaseHash, measured, body.receipt, time)
      return json({ state: 'review', humanAccepted: false })
    }
    if (jobRoute[2] === 'fail' && request.method === 'POST') {
      const body = await decodeBody(
        request,
        Schema.Struct({ reason: Schema.String }),
      )
      requireCondition(
        body.reason.length > 0 && body.reason.length <= 2000,
        400,
        'Invalid failure description.',
      )
      await store.fail(job, leaseHash, body.reason, time)
      return json({ state: 'failed' })
    }
  }
  const assetRoute = path.match(
    /^\/api\/(assets|worker\/assets)\/([a-zA-Z0-9-]+)(?:\/(parts\/([0-9]+)|complete))?$/,
  )
  if (assetRoute) {
    const asset = await store.asset(assetRoute[2] ?? '')
    requireCondition(asset, 404, 'Asset not found.')
    if (assetRoute[1] === 'worker/assets') {
      const worker = await device()
      const jobId = request.headers.get('X-Job-Id') ?? ''
      const job = await store.lease(
        jobId,
        worker.id,
        await digest(request.headers.get('X-Job-Lease') ?? ''),
        time,
      )
      requireCondition(
        asset.release_id === job.release_id &&
          (asset.kind === 'audio' ||
            (asset.job_id === job.id && asset.attempt === job.attempt)),
        404,
        'Asset not found.',
      )
    } else {
      const account = await tenant()
      requireCondition(
        await store.release(account.id, asset.release_id),
        404,
        'Asset not found.',
      )
      requireCondition(
        asset.state === 'ready',
        409,
        'This asset is not ready for review.',
      )
    }
    if (!assetRoute[3] && request.method === 'GET') {
      requireCondition(
        asset.state === 'ready' || asset.state === 'uploaded',
        409,
        'This asset is still uploading.',
      )
      const range = request.headers.get('Range')
      const rangeMatch = range?.match(/^bytes=([0-9]+)-([0-9]*)$/)
      requireCondition(
        !range || rangeMatch,
        416,
        'Only a single byte range is supported.',
      )
      const offset = Number(rangeMatch?.[1] ?? 0)
      const end = rangeMatch?.[2] ? Number(rangeMatch[2]) : asset.bytes - 1
      requireCondition(
        offset >= 0 &&
          offset < asset.bytes &&
          end >= offset &&
          end < asset.bytes,
        416,
        'Invalid byte range.',
      )
      const object = await env.MEDIA.get(
        asset.object_key,
        rangeMatch ? { range: { offset, length: end - offset + 1 } } : {},
      )
      requireCondition(
        object && 'body' in object,
        404,
        'The stored asset is missing.',
      )
      const headers = new Headers({
        'Content-Type': asset.content_type,
        'Cache-Control': 'private, no-store',
        'X-Content-Type-Options': 'nosniff',
        ETag: object.httpEtag,
        'Accept-Ranges': 'bytes',
        'Content-Length': String(object.size),
        'X-Content-Sha256': asset.sha256,
      })
      if (rangeMatch) {
        headers.set('Content-Range', `bytes ${offset}-${end}/${object.size}`)
        headers.set('Content-Length', String(end - offset + 1))
      }
      return new Response(object.body, {
        status: headers.has('Content-Range') ? 206 : 200,
        headers,
      })
    }
    requireCondition(
      assetRoute[1] === 'worker/assets' &&
        asset.kind === 'output' &&
        asset.state === 'uploading' &&
        asset.upload_id,
      409,
      'This upload is closed.',
    )
    const multipart = env.MEDIA.resumeMultipartUpload(
      asset.object_key,
      asset.upload_id,
    )
    if (assetRoute[4] && request.method === 'PUT') {
      const number = Number(assetRoute[4])
      requireCondition(
        Number.isInteger(number) &&
          number >= 1 &&
          number <= Math.ceil(asset.bytes / partBytes),
        400,
        'Invalid part number.',
      )
      const expectedBytes = Math.min(
        partBytes,
        asset.bytes - (number - 1) * partBytes,
      )
      requireCondition(
        Number(
          request.headers.get('X-Upload-Bytes') ??
            request.headers.get('Content-Length'),
        ) === expectedBytes,
        400,
        'Invalid part size.',
      )
      const buffer = await request.arrayBuffer()
      requireCondition(
        buffer.byteLength === expectedBytes,
        400,
        'The part body is incomplete.',
      )
      const hash = await digest(buffer)
      requireCondition(
        request.headers.get('X-Content-Sha256') === hash,
        409,
        'The uploaded part failed its hash check.',
      )
      const result = await multipart.uploadPart(number, buffer)
      await store.part(asset.id, number, result.etag, expectedBytes, hash)
      return json({ partNumber: number, etag: result.etag })
    }
    if (assetRoute[3] === 'complete' && request.method === 'POST') {
      const parts = await store.parts(asset.id)
      requireCondition(
        parts.length === Math.ceil(asset.bytes / partBytes) &&
          parts.every((part, index) => part.part_number === index + 1) &&
          parts.reduce((total, part) => total + part.bytes, 0) === asset.bytes,
        409,
        'Upload every part before completing.',
      )
      await multipart.complete(
        parts.map(part => ({ partNumber: part.part_number, etag: part.etag })),
      )
      requireCondition(
        (await env.MEDIA.head(asset.object_key))?.size === asset.bytes,
        409,
        'The completed asset has the wrong size.',
      )
      await store.markUploaded(asset.id, false)
      return json({
        assetId: asset.id,
        state: 'uploaded',
        requiresWorkerReadback: true,
      })
    }
  }
  throw new ApiError(404, 'API route not found.')
}
export const productionApi = (
  request: Request,
  env: ProductionEnv,
): Promise<Response> =>
  Effect.runPromise(
    Effect.gen(function* () {
      const store = yield* StudioStore
      return yield* Effect.tryPromise({
        try: () => handle(request, env, store),
        catch: error => error,
      })
    }).pipe(
      Effect.provideService(StudioStore, makeStore(env.STUDIO_DB)),
      Effect.catch(error =>
        Effect.sync(() => {
          if (!(error instanceof ApiError))
            console.error(
              'Studio API failure',
              error instanceof Error
                ? error.message.slice(0, 500)
                : 'Unknown error',
            )
          return json(
            {
              error:
                error instanceof ApiError
                  ? error.message
                  : 'The studio could not complete this action.',
            },
            error instanceof ApiError ? error.status : 500,
          )
        }),
      ),
    ),
  )
