import { Effect, Schema } from 'effect'

import type { D1Database } from '@cloudflare/workers-types'

import { canonicalJson } from '../src/canonical'
import { ReleaseBrief } from '../src/domain'
import type { MediaBucket } from '../src/server/api'
import { prepareKit } from './archive'
import {
  Apply,
  Commit,
  Inspect,
  Job,
  Media,
  Render,
  Review,
  Verify,
  features,
  tools,
} from './catalog'
import { jsonSchema } from './json-schema'
import { Preview, previewPrefix, readPreview } from './preview'
import {
  type ProductionScope,
  productionAssetPrefix,
} from './production-contract'
import { Asset, applyEdits, decodeProject, validateProject } from './project'
import { EditorError, EditorStore, digest } from './store'
import { type ArchiveHashFactory, streamZip } from './zip'

export interface EditorEnv {
  STUDIO_DB: D1Database
  MEDIA: MediaBucket
  STUDIO_OPERATOR_TOKEN: string
  runtimeInfo?: { hosting: string; rendering: string }
  fixedLengthStream?: (length: number) => {
    readable: ReadableStream<Uint8Array>
    writable: WritableStream<Uint8Array>
  }
  archiveHashFactory?: ArchiveHashFactory
  RENDERER?: {
    getByName: (name: string) => {
      fetch: (request: Request) => Promise<Response>
    }
  }
}
export type EditorRuntime = Omit<EditorEnv, 'STUDIO_DB'>
declare const FixedLengthStream: new (length: number) => {
  readable: ReadableStream<Uint8Array>
  writable: WritableStream<Uint8Array>
}
export const fixedStream = (env: EditorRuntime, length: number) =>
  env.fixedLengthStream?.(length) ?? new FixedLengthStream(length)
export const editorStore = (env: Pick<EditorEnv, 'STUDIO_DB'>) =>
  new EditorStore({
    first: async (query, values) =>
      env.STUDIO_DB.prepare(query)
        .bind(...values)
        .first(),
    all: async (query, values) =>
      (
        await env.STUDIO_DB.prepare(query)
          .bind(...values)
          .all()
      ).results,
    run: async (query, values) => {
      await env.STUDIO_DB.prepare(query)
        .bind(...values)
        .run()
    },
    batch: async statements => {
      await env.STUDIO_DB.batch(
        statements.map(statement =>
          env.STUDIO_DB.prepare(statement.sql).bind(...statement.values),
        ),
      )
    },
  })
const response = (value: unknown, status = 200) =>
  Response.json(value, {
    status,
    headers: {
      'Cache-Control': 'no-store',
      'X-Content-Type-Options': 'nosniff',
    },
  })
export const editorBody = async <S extends Schema.ConstraintDecoder<unknown>>(
  request: Request,
  schema: S,
): Promise<S['Type']> => {
  if (!request.body)
    throw new EditorError(400, 'missing_body', 'A JSON request is required.')
  const reader = request.body.getReader()
  const decoder = new TextDecoder()
  const chunks: Array<string> = []
  const counter = { bytes: 0 }
  for (;;) {
    const part = await reader.read()
    if (part.done) break
    counter.bytes += part.value.byteLength
    if (counter.bytes > 4 * 1024 * 1024) {
      await reader.cancel()
      throw new EditorError(413, 'body_too_large', 'JSON input exceeds 4 MiB.')
    }
    chunks.push(decoder.decode(part.value, { stream: true }))
  }
  try {
    return Schema.decodeUnknownSync(schema, { onExcessProperty: 'error' })(
      JSON.parse(chunks.join('') + decoder.decode()),
    )
  } catch {
    throw new EditorError(
      400,
      'invalid_schema',
      'Input does not match the tool schema. Query /v1/tools for schemas.',
    )
  }
}
const viewJob = (job: {
  id: string
  project_id: string
  revision: number
  state: string
  progress_json: string
  receipt_json: string | null
  error: string | null
}) => ({
  jobId: job.id,
  projectId: job.project_id,
  revision: job.revision,
  state: job.state,
  progress: JSON.parse(job.progress_json),
  receipt: job.receipt_json ? JSON.parse(job.receipt_json) : null,
  error: job.error,
  motionReviewed: false,
  heard: false,
  creativelyAccepted: false,
})
const handle = async (
  request: Request,
  env: EditorRuntime,
  store: EditorStore,
  scope?: ProductionScope,
) => {
  const url = new URL(request.url)
  const path = url.pathname
  const bearer =
    request.headers.get('Authorization')?.replace(/^Bearer /, '') ?? ''
  const cookie =
    request.headers
      .get('Cookie')
      ?.split(';')
      .map(value => value.trim())
      .find(value => value.startsWith('studio_session='))
      ?.slice(15) ?? ''
  const time = Math.floor(Date.now() / 1000)
  if (path === '/v1/health' && request.method === 'GET')
    return response({
      service: 'release-kit-editor',
      version: '0.1.0',
      hosting: env.runtimeInfo?.hosting ?? 'cloudflare-worker',
      rendering: env.runtimeInfo?.rendering ?? 'cloudflare-container',
      rendererConfigured: !!env.RENDERER,
      cloudRenderVerified: false,
      fullKitCompleted: false,
    })
  if (path === '/v1/tools' && request.method === 'GET')
    return response({
      tools: tools(),
      editSchema: jsonSchema(Schema.Array((await import('./project')).Edit)),
      features,
      rendererConfigured: !!env.RENDERER,
      declaredSupportIsNotCloudVerification: true,
    })
  if (path === '/v1/progress' && request.method === 'GET')
    return response({
      features,
      cloudRenderVerified: false,
      fullKitCompleted: false,
    })
  if (
    ['/v1/operator/tokens', '/v1/operator/tokens/revoke'].includes(path) &&
    request.method === 'POST'
  ) {
    if (
      env.STUDIO_OPERATOR_TOKEN.length < 32 ||
      (await digest(bearer)) !== (await digest(env.STUDIO_OPERATOR_TOKEN))
    )
      throw new EditorError(
        401,
        'operator_required',
        'Operator authentication is required.',
      )
    if (path === '/v1/operator/tokens/revoke') {
      const input = await editorBody(
        request,
        Schema.Struct({
          targetToken: Schema.String.check(Schema.isPattern(/^[a-f0-9]{64}$/)),
        }),
      )
      await store.db.run('UPDATE editor_tokens SET enabled=0 WHERE hash=?', [
        await digest(input.targetToken),
      ])
      return response({ revoked: true })
    }
    const input = await editorBody(
      request,
      Schema.Struct({ tenantId: Schema.String }),
    )
    if (
      !(await store.db.first('SELECT id FROM tenants WHERE id=?', [
        input.tenantId,
      ]))
    )
      throw new EditorError(404, 'tenant_not_found', 'Tenant not found.')
    const token = `${crypto.randomUUID()}${crypto.randomUUID()}`.replaceAll(
      '-',
      '',
    )
    const expiresAt = time + 7 * 86400
    await store.db.run(
      'INSERT INTO editor_tokens(hash,tenant_id,expires_at) VALUES(?,?,?)',
      [await digest(token), input.tenantId, expiresAt],
    )
    return response({ token, expiresAt }, 201)
  }
  const principal = scope
    ? { tenant_id: scope.tenantId }
    : await store.principal(await digest(bearer || cookie), time, !bearer)
  if (!principal || !(bearer || cookie))
    throw new EditorError(
      401,
      'authentication_required',
      'A studio session or tenant-scoped editor token is required.',
    )
  const tenant = principal.tenant_id
  const assertRelease = (releaseId: string) => {
    if (scope && scope.releaseId !== releaseId)
      throw new EditorError(
        404,
        'assigned_release_required',
        'This operation is outside the assigned release.',
      )
  }
  const assertAsset = (assetId: string) => {
    if (scope && !assetId.startsWith(productionAssetPrefix(scope.releaseId)))
      throw new EditorError(
        404,
        'assigned_asset_required',
        'Production media must use the assigned release namespace.',
      )
  }
  const scopedJob = async (id: string) => {
    const job = await store.job(tenant, id)
    assertRelease(job.release_id)
    return job
  }
  const scopedProject = async (id: string, revision: number | null) => {
    const snapshot = await store.inspect(tenant, id, revision)
    assertRelease(snapshot.project.releaseId)
    return snapshot
  }
  const registerAsset = async () => {
    const asset = await editorBody(request, Asset)
    assertAsset(asset.id)
    return store.registerAsset(tenant, asset)
  }
  if (
    !bearer &&
    !['GET', 'HEAD'].includes(request.method) &&
    request.headers.get('Origin') !== url.origin
  )
    throw new EditorError(
      403,
      'origin_required',
      'Session mutations must originate from the studio.',
    )
  if (path === '/v1/media' && request.method === 'POST')
    return response(await registerAsset(), 201)
  const upload = /^\/v1\/media\/([a-zA-Z0-9_-]{1,80})$/.exec(path)
  if (upload?.[1] && request.method === 'PUT') {
    assertAsset(upload[1])
    const asset = await store.asset(tenant, upload[1])
    if (!asset || asset.uploaded)
      throw new EditorError(
        409,
        'asset_upload_state',
        'Register a new immutable asset before uploading.',
      )
    const metadata = Schema.decodeUnknownSync(Asset)(asset.metadata)
    if (
      !request.body ||
      metadata.bytes > 100 * 1024 * 1024 ||
      Number(request.headers.get('Content-Length') ?? metadata.bytes) !==
        metadata.bytes
    )
      throw new EditorError(
        413,
        'media_size',
        'Upload the exact registered byte count, at most 100 MiB.',
      )
    const fixed = fixedStream(env, metadata.bytes)
    await Promise.all([
      env.MEDIA.put(asset.object_key, fixed.readable, {
        sha256: metadata.sha256,
        httpMetadata: {
          contentType:
            request.headers.get('Content-Type') ?? 'application/octet-stream',
        },
        customMetadata: { tenant, assetId: metadata.id },
      }),
      request.body.pipeTo(fixed.writable),
    ])
    if ((await env.MEDIA.head(asset.object_key))?.size !== metadata.bytes)
      throw new EditorError(
        422,
        'media_integrity',
        'Stored media size does not match the asset.',
      )
    await store.db.run(
      'UPDATE editor_assets SET uploaded=1 WHERE tenant_id=? AND id=?',
      [tenant, metadata.id],
    )
    return response({
      id: metadata.id,
      uploaded: true,
      sha256: metadata.sha256,
      bytes: metadata.bytes,
      mediaProbeVerified: false,
    })
  }
  const archive = /^\/v1\/jobs\/([a-zA-Z0-9_-]{1,80})\/archive$/.exec(path)
  if (archive?.[1] && ['GET', 'HEAD'].includes(request.method)) {
    const job = await scopedJob(archive[1])
    if (
      url.searchParams.has('releaseId') &&
      url.searchParams.get('releaseId') !== job.release_id
    )
      throw new EditorError(
        404,
        'assigned_release_required',
        'Archive is outside the assigned release.',
      )
    if (request.headers.has('Range'))
      throw new EditorError(
        416,
        'archive_range_unsupported',
        'Download the complete verified archive.',
      )
    const kit = await prepareKit(store, env.MEDIA, tenant, job)
    const deliver = () => {
      const fixed = fixedStream(env, kit.descriptor.bytes)
      void streamZip(kit.entries, env.archiveHashFactory)
        .pipeTo(fixed.writable)
        .catch(() => {})
      return fixed.readable
    }
    return new Response(request.method === 'HEAD' ? null : deliver(), {
      headers: {
        'Content-Type': 'application/zip',
        'Content-Disposition': `attachment; filename="release-kit-${job.release_id}.zip"`,
        'Content-Length': String(kit.descriptor.bytes),
        'X-Kit-Manifest-Sha256': kit.descriptor.manifestSha256,
        'Cache-Control': 'private, no-store',
        'X-Content-Type-Options': 'nosniff',
      },
    })
  }
  const download =
    /^\/v1\/jobs\/([a-zA-Z0-9_-]+)\/outputs\/(film|short-1|short-2|short-3|thumbnail|artwork)$/.exec(
      path,
    )
  if (download?.[1] && download[2] && request.method === 'GET') {
    const job = await scopedJob(download[1])
    if (job.state !== 'ready')
      throw new EditorError(
        409,
        'output_not_ready',
        'Verified output is not ready.',
      )
    const object = await env.MEDIA.get(
      `editor/${tenant}/jobs/${job.id}/${download[2]}`,
      {},
    )
    if (!object)
      throw new EditorError(404, 'artifact_not_found', 'Artifact not found.')
    return new Response(object.body, {
      headers: {
        'Content-Type': ['thumbnail', 'artwork'].includes(download[2])
          ? 'image/jpeg'
          : 'video/mp4',
        'Content-Length': String(object.size),
        'Cache-Control': 'private, no-store',
      },
    })
  }
  const previewFile =
    /^\/v1\/jobs\/([a-zA-Z0-9_-]{1,80})\/previews\/([a-f0-9]{64})\/(preview\.(?:mp4|jpg)|frame-[0-9]{6}\.jpg)$/.exec(
      path,
    )
  if (
    previewFile?.[1] &&
    previewFile[2] &&
    previewFile[3] &&
    ['GET', 'HEAD'].includes(request.method)
  ) {
    const job = await scopedJob(previewFile[1])
    const bundle = await readPreview(env.MEDIA, tenant, job, previewFile[2])
    const file = bundle?.files.find(item => item.name === previewFile[3])
    if (!bundle || !file)
      throw new EditorError(
        404,
        'preview_not_found',
        'Verified review preview is missing.',
      )
    const range = request.headers.get('Range')
    const match = range?.match(/^bytes=([0-9]+)-([0-9]*)$/)
    const offset = Number(match?.[1] ?? 0)
    const end = match?.[2] ? Number(match[2]) : file.bytes - 1
    if (
      (range && !match) ||
      !Number.isSafeInteger(offset) ||
      !Number.isSafeInteger(end) ||
      offset < 0 ||
      offset >= file.bytes ||
      end < offset ||
      end >= file.bytes
    )
      throw new EditorError(
        416,
        'preview_range',
        'Request one bounded byte range of the review file.',
      )
    const key = previewPrefix(tenant, job.id, bundle.bundleId) + file.name
    const head = await env.MEDIA.head(key)
    if (head?.size !== file.bytes)
      throw new EditorError(
        422,
        'preview_integrity',
        'Stored review file is missing or changed.',
      )
    const object =
      request.method === 'HEAD'
        ? null
        : await env.MEDIA.get(key, {
            ...(head.etag ? { onlyIf: { etagMatches: head.etag } } : {}),
            ...(match ? { range: { offset, length: end - offset + 1 } } : {}),
          })
    if (request.method === 'GET' && (!object || object.size !== file.bytes))
      throw new EditorError(
        422,
        'preview_integrity',
        'Review file changed during download.',
      )
    return new Response(object?.body ?? null, {
      status: match ? 206 : 200,
      headers: {
        'Content-Type': file.name.endsWith('.mp4') ? 'video/mp4' : 'image/jpeg',
        'Content-Length': String(match ? end - offset + 1 : file.bytes),
        ...(match
          ? { 'Content-Range': `bytes ${offset}-${end}/${file.bytes}` }
          : {}),
        'Accept-Ranges': 'bytes',
        'Cache-Control': 'private, no-store',
        'X-Content-Type-Options': 'nosniff',
        'X-Content-Sha256': file.sha256,
        'X-Source-Sha256': bundle.source.sha256,
      },
    })
  }
  if (request.method !== 'POST')
    throw new EditorError(404, 'route_not_found', 'Editor route not found.')
  const tool = path.replace('/v1/tools/', '')
  if (tool === 'media.register') return response(await registerAsset(), 201)
  if (tool === 'media.inspect') {
    const input = await editorBody(request, Media)
    assertAsset(input.assetId)
    const asset = await store.asset(tenant, input.assetId)
    if (!asset)
      throw new EditorError(404, 'asset_not_found', 'Asset not found.')
    return response({
      assetId: input.assetId,
      metadata: asset.metadata,
      uploaded: !!asset.uploaded,
      mediaProbeVerified: false,
    })
  }
  const assertSource = async (project: ReturnType<typeof decodeProject>) => {
    assertRelease(project.releaseId)
    for (const asset of project.assets) assertAsset(asset.id)
    const row = await store.db.first(
      'SELECT brief_json FROM releases WHERE tenant_id=? AND id=?',
      [tenant, project.releaseId],
    )
    const release = Schema.decodeUnknownSync(
      Schema.NullOr(Schema.Struct({ brief_json: Schema.String })),
    )(row)
    if (!release)
      throw new EditorError(404, 'release_not_found', 'Release not found.')
    const brief = Schema.decodeUnknownSync(ReleaseBrief)(
      JSON.parse(release.brief_json),
    )
    if (
      project.briefSha256 !== (await digest(canonicalJson(brief))) ||
      project.audioSha256 !== brief.audioSha256 ||
      project.lyrics !== brief.lyrics ||
      project.language !== brief.language
    )
      throw new EditorError(
        409,
        'source_binding',
        'Project must bind this release and its exact frozen brief, audio and lyrics.',
      )
    const findings = validateProject(project)
    if (findings.length)
      throw new EditorError(422, 'invalid_project', JSON.stringify(findings))
  }
  if (tool === 'project.commit') {
    const input = await editorBody(request, Commit)
    await assertSource(input.project)
    if (scope) {
      const existing = await store.db.first(
        'SELECT release_id FROM editor_projects WHERE tenant_id=? AND id=?',
        [tenant, input.projectId],
      )
      if (existing)
        assertRelease(
          Schema.decodeUnknownSync(
            Schema.Struct({ release_id: Schema.String }),
          )(existing).release_id,
        )
    }
    return response(
      await store.commit(
        tenant,
        input.projectId,
        input.expectedRevision,
        input.intentId,
        input.project,
      ),
    )
  }
  if (tool === 'project.inspect' || tool === 'project.history') {
    const input = await editorBody(request, Inspect)
    const snapshot = await scopedProject(input.projectId, input.revision)
    return response(
      tool === 'project.inspect'
        ? snapshot
        : await store.history(tenant, input.projectId),
    )
  }
  if (tool === 'project.edit') {
    const input = await editorBody(request, Apply)
    const snapshot = await scopedProject(
      input.projectId,
      input.expectedRevision,
    )
    const project = applyEdits(snapshot.project, input.edits)
    await assertSource(project)
    return response(
      await store.commit(
        tenant,
        input.projectId,
        input.expectedRevision,
        input.intentId,
        project,
      ),
    )
  }
  if (tool === 'project.validate') {
    const project = await editorBody(
      request,
      (await import('./project')).Project,
    )
    await assertSource(project)
    const findings = validateProject(project, 'kit')
    return response({
      valid: findings.length === 0,
      findings,
      measured: false,
      heard: false,
      motionReviewed: false,
    })
  }
  if (tool === 'render.start') {
    if (!env.RENDERER)
      throw new EditorError(
        503,
        'renderer_unavailable',
        'The editor renderer is not configured.',
      )
    const input = await editorBody(request, Render)
    const snapshot = await scopedProject(input.projectId, input.revision)
    await assertSource(snapshot.project)
    const project =
      input.mode === 'diagnostic'
        ? {
            ...snapshot.project,
            compositions: snapshot.project.compositions.filter(
              item => item.id === input.outputId,
            ),
          }
        : snapshot.project
    if (!project.compositions.length)
      throw new EditorError(
        422,
        'output_missing',
        'Select an existing composition for the diagnostic.',
      )
    const findings = validateProject(
      project,
      input.mode === 'kit' ? 'kit' : 'render',
    )
    if (findings.length)
      throw new EditorError(422, 'invalid_render', JSON.stringify(findings))
    for (const asset of project.assets) {
      const stored = await store.asset(tenant, asset.id)
      if (!stored?.uploaded)
        throw new EditorError(
          422,
          'asset_not_uploaded',
          `Asset ${asset.id} is not uploaded for this tenant.`,
        )
      const identity = Schema.decodeUnknownSync(
        Schema.Struct({ sha256: Schema.String, bytes: Schema.Number }),
      )(stored.metadata)
      if (identity.sha256 !== asset.sha256 || identity.bytes !== asset.bytes)
        throw new EditorError(
          409,
          'asset_binding',
          'Project asset differs from the immutable uploaded media.',
        )
    }
    const job = await store.start(
      tenant,
      input.projectId,
      input.revision,
      input.intentId,
      input,
    )
    const attached = await env.RENDERER.getByName(
      `${tenant}/${job.release_id}`,
    ).fetch(
      new Request('https://renderer/start', {
        method: 'POST',
        body: JSON.stringify({ jobId: job.id, tenant }),
      }),
    )
    if (!attached.ok)
      return response(
        {
          ...viewJob(await store.job(tenant, job.id)),
          attachment: 'needs-reconciliation',
        },
        202,
      )
    return response(viewJob(await store.job(tenant, job.id)), 202)
  }
  if (
    tool === 'render.status' ||
    tool === 'render.cancel' ||
    tool === 'render.reconcile'
  ) {
    const input = await editorBody(request, Job)
    const job = await scopedJob(input.jobId)
    if (tool !== 'render.status') {
      if (!env.RENDERER)
        throw new EditorError(
          503,
          'renderer_unavailable',
          'Renderer is not configured.',
        )
      const result = await env.RENDERER.getByName(
        `${tenant}/${job.release_id}`,
      ).fetch(
        new Request(
          `https://renderer/${tool === 'render.cancel' ? 'cancel' : 'reconcile'}`,
          { method: 'POST', body: JSON.stringify({ jobId: job.id, tenant }) },
        ),
      )
      if (!result.ok)
        throw new EditorError(
          409,
          'reconciliation_required',
          'Renderer could not establish the job outcome.',
        )
    }
    return response(viewJob(await store.job(tenant, job.id)))
  }
  if (tool === 'kit.locate') {
    const input = await editorBody(request, Job)
    const kit = await prepareKit(
      store,
      env.MEDIA,
      tenant,
      await scopedJob(input.jobId),
    )
    return response(kit.descriptor)
  }
  if (tool === 'artifact.locate') {
    const input = await editorBody(request, Verify)
    const job = await scopedJob(input.jobId)
    if (job.state !== 'ready' || !job.receipt_json)
      throw new EditorError(
        409,
        'output_not_ready',
        'A completed render is required.',
      )
    const receipt = Schema.decodeUnknownSync(
      Schema.Struct({
        outputs: Schema.Array(
          Schema.Struct({
            id: Schema.String,
            sha256: Schema.String,
            bytes: Schema.Number,
          }),
        ),
      }),
    )(JSON.parse(job.receipt_json))
    const artifact = receipt.outputs.find(
      output => output.id === input.outputId,
    )
    if (!artifact)
      throw new EditorError(404, 'artifact_not_found', 'Artifact not found.')
    return response({
      downloadPath: `/v1/jobs/${job.id}/outputs/${artifact.id}`,
      artifact,
    })
  }
  if (tool === 'artifact.preview') {
    const input = await editorBody(request, Preview)
    const job = await scopedJob(input.jobId)
    if (!env.RENDERER || job.state !== 'ready')
      throw new EditorError(
        409,
        'output_not_ready',
        'Review previews require a completed immutable output.',
      )
    return env.RENDERER.getByName(`${tenant}/${job.release_id}`).fetch(
      new Request('https://renderer/preview', {
        method: 'POST',
        body: JSON.stringify({ jobId: job.id, tenant, preview: input }),
      }),
    )
  }
  if (tool === 'artifact.verify') {
    const input = await editorBody(request, Verify)
    const job = await scopedJob(input.jobId)
    if (!env.RENDERER || job.state !== 'ready')
      throw new EditorError(
        409,
        'output_not_ready',
        'A completed render is required for independent verification.',
      )
    return env.RENDERER.getByName(`${tenant}/${job.release_id}`).fetch(
      new Request('https://renderer/verify', {
        method: 'POST',
        body: JSON.stringify({
          jobId: job.id,
          tenant,
          outputId: input.outputId,
        }),
      }),
    )
  }
  if (tool === 'artifact.review') {
    const input = await editorBody(request, Review)
    if (input.kind === 'creatively-accepted' && bearer)
      throw new EditorError(
        403,
        'human_acceptance_required',
        'Agent tokens cannot record creative acceptance. Use the authenticated studio review flow.',
      )
    const job = await scopedJob(input.jobId)
    if (job.state !== 'ready')
      throw new EditorError(
        409,
        'output_not_ready',
        'Review requires completed immutable output bytes.',
      )
    const receipt = Schema.decodeUnknownSync(
      Schema.Struct({
        outputs: Schema.Array(
          Schema.Struct({
            id: Schema.String,
            sha256: Schema.String,
            frames: Schema.Number,
          }),
        ),
      }),
    )(JSON.parse(job.receipt_json ?? '{}'))
    const artifact = receipt.outputs.find(
      output => output.id === input.outputId && output.sha256 === input.sha256,
    )
    if (
      !artifact ||
      input.startFrame < 0 ||
      input.startFrame >= input.endFrame ||
      input.endFrame > artifact.frames ||
      !input.method.trim() ||
      !input.notes.trim()
    )
      throw new EditorError(
        422,
        'review_binding',
        'Review must identify exact artifact bytes, an actual range, method and notes.',
      )
    const id = crypto.randomUUID()
    await store.db.run(
      'INSERT INTO editor_reviews(id,tenant_id,job_id,output_id,sha256,kind,detail_json,created_at) VALUES(?,?,?,?,?,?,?,?)',
      [
        id,
        tenant,
        job.id,
        input.outputId,
        input.sha256,
        input.kind,
        canonicalJson(input),
        time,
      ],
    )
    return response({
      id,
      recorded: true,
      assertedBy: 'authenticated-tenant',
      automatedAcceptance: false,
    })
  }
  throw new EditorError(
    404,
    'unsupported_tool',
    'Unknown or unimplemented tool. Query /v1/tools.',
  )
}
export const makeEditorApi =
  (env: EditorRuntime, store: EditorStore) =>
  (request: Request, scope?: ProductionScope) =>
    Effect.runPromise(
      Effect.tryPromise({
        try: () => handle(request, env, store, scope),
        catch: error => error,
      }).pipe(
        Effect.catch(error =>
          Effect.succeed(
            response(
              {
                ok: false,
                code:
                  error instanceof EditorError ? error.code : 'editor_error',
                error:
                  error instanceof EditorError
                    ? error.message
                    : 'Editor operation failed; preserve the intent and reconcile before retrying.',
              },
              error instanceof EditorError ? error.status : 500,
            ),
          ),
        ),
      ),
    )
export const editorApi = (
  request: Request,
  env: EditorEnv,
  scope?: ProductionScope,
) => makeEditorApi(env, editorStore(env))(request, scope)
