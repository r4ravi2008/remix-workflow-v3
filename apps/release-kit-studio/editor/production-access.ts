import { Effect, Schema } from 'effect'

import { canonicalJson } from '../src/canonical'
import { OutputId, outputs } from '../src/domain'
import { makeStore } from '../src/server/api'
import {
  ApiError,
  AssetRow,
  ReleaseBrief,
  validateMeasurement,
} from '../src/server/contracts'
import type { Store } from '../src/server/store'
import {
  type EditorEnv,
  type EditorRuntime,
  editorBody,
  editorStore,
  makeEditorApi,
} from './api'
import type { ProductionScope } from './production-contract'
import { decodeProject, validateProject } from './project'
import { EditorError, type EditorStore, digest } from './store'

const Promote = Schema.Struct({ editorJobId: Schema.String })
const Receipt = Schema.Struct({
  measured: Schema.Literal(true),
  storedByteReadback: Schema.Literal(true),
  receiptStored: Schema.Literal(true),
  receiptSha256: Schema.String,
  projectSha256: Schema.String,
  outputs: Schema.Array(
    Schema.Struct({
      id: OutputId,
      sha256: Schema.String,
      bytes: Schema.Number,
      width: Schema.Number,
      height: Schema.Number,
      duration: Schema.Number,
      completeDecode: Schema.Literal(true),
    }),
  ),
})
const promote = async (
  request: Request,
  env: EditorRuntime,
  scope: ProductionScope,
  studio: Store,
  editor: EditorStore,
) => {
  const input = await editorBody(request, Promote)
  const render = await editor.job(scope.tenantId, input.editorJobId)
  if (
    render.release_id !== scope.releaseId ||
    render.state !== 'ready' ||
    !render.receipt_json
  )
    throw new EditorError(
      409,
      'render_not_ready',
      'A verified kit render for this assigned release is required.',
    )
  const snapshot = await editor.inspect(
    scope.tenantId,
    render.project_id,
    render.revision,
  )
  const project = decodeProject(snapshot.project)
  const receipt = Schema.decodeUnknownSync(Receipt)(
    JSON.parse(render.receipt_json),
  )
  const receiptObject = await env.MEDIA.get(
    `editor/${scope.tenantId}/jobs/${render.id}/receipt.json`,
    {},
  )
  if (
    !receiptObject ||
    receiptObject.size > 4 * 1024 * 1024 ||
    (await digest(await new Response(receiptObject.body).text())) !==
      receipt.receiptSha256
  )
    throw new EditorError(
      409,
      'receipt_integrity',
      'The private immutable render receipt failed readback.',
    )
  if (
    validateProject(project, 'kit').length ||
    receipt.outputs.length !== 6 ||
    new Set(receipt.outputs.map(output => output.id)).size !== 6 ||
    receipt.projectSha256 !== (await digest(canonicalJson(project)))
  )
    throw new EditorError(
      409,
      'kit_binding',
      'The render receipt must match an immutable six-output kit revision.',
    )
  const release = await studio.release(scope.tenantId, scope.releaseId)
  if (!release)
    throw new EditorError(404, 'release_not_found', 'Release not found.')
  const brief = Schema.decodeUnknownSync(ReleaseBrief)(
    JSON.parse(release.brief_json),
  )
  if (
    project.briefSha256 !== (await digest(canonicalJson(brief))) ||
    project.audioSha256 !== brief.audioSha256
  )
    throw new EditorError(
      409,
      'source_binding',
      'The kit differs from the assigned frozen source.',
    )
  const measured = []
  for (const output of outputs) {
    const artifact = receipt.outputs.find(item => item.id === output.id)
    const composition = project.compositions.find(item => item.id === output.id)
    if (!artifact || !composition)
      throw new EditorError(
        409,
        'output_missing',
        'All six outputs are required.',
      )
    const measurement = {
      width: artifact.width,
      height: artifact.height,
      duration: artifact.duration,
      decoded: true,
      sha256: artifact.sha256,
      storageSha256: artifact.sha256,
      composition: composition.rationale,
    }
    validateMeasurement(output.id, measurement, brief.audioDuration)
    const key = `editor/${scope.tenantId}/jobs/${render.id}/${output.id}`
    if ((await env.MEDIA.head(key))?.size !== artifact.bytes)
      throw new EditorError(
        409,
        'stored_output_missing',
        'A verified private output is missing or changed.',
      )
    const id = await digest(`${scope.jobId}/${render.id}/${output.id}`)
    const asset = Schema.decodeUnknownSync(AssetRow)({
      id,
      release_id: scope.releaseId,
      job_id: scope.jobId,
      attempt: scope.attempt,
      kind: 'output',
      output_id: output.id,
      object_key: key,
      bytes: artifact.bytes,
      sha256: artifact.sha256,
      content_type: ['thumbnail', 'artwork'].includes(output.id)
        ? 'image/jpeg'
        : 'video/mp4',
      state: 'uploaded',
      upload_id: null,
      verified: 0,
      measurement_json: null,
      created_at: Math.floor(Date.now() / 1000),
    })
    const existing = await studio.asset(id)
    if (!existing) {
      try {
        await studio.insertAsset(asset)
      } catch {
        if (!(await studio.asset(id)))
          throw new EditorError(
            409,
            'promotion_uncertain',
            'Reconcile the saved output promotion.',
          )
      }
    }
    if (existing && existing.attempt !== scope.attempt)
      await editor.db.run(
        "UPDATE assets SET attempt=? WHERE id=? AND job_id=? AND release_id=? AND state IN ('uploading','uploaded') AND EXISTS(SELECT 1 FROM jobs WHERE id=? AND state='running' AND attempt=? AND lease_hash=? AND lease_until>?)",
        [
          scope.attempt,
          id,
          scope.jobId,
          scope.releaseId,
          scope.jobId,
          scope.attempt,
          scope.leaseHash,
          Math.floor(Date.now() / 1000),
        ],
      )
    const stored = await studio.asset(id)
    if (
      !stored ||
      stored.object_key !== key ||
      stored.sha256 !== artifact.sha256 ||
      stored.bytes !== artifact.bytes ||
      stored.job_id !== scope.jobId ||
      stored.release_id !== scope.releaseId
    )
      throw new EditorError(
        409,
        'promotion_conflict',
        'The saved promotion refers to different immutable bytes.',
      )
    if (stored.state === 'uploading')
      await editor.db.run(
        "UPDATE assets SET state='uploaded',verified=0 WHERE id=? AND state='uploading' AND attempt=? AND EXISTS(SELECT 1 FROM jobs WHERE id=? AND state='running' AND attempt=? AND lease_hash=? AND lease_until>?)",
        [
          id,
          scope.attempt,
          scope.jobId,
          scope.attempt,
          scope.leaseHash,
          Math.floor(Date.now() / 1000),
        ],
      )
    const finalAsset = await studio.asset(id)
    if (!finalAsset)
      throw new EditorError(
        409,
        'promotion_uncertain',
        'The saved output promotion is missing.',
      )
    measured.push({ asset: finalAsset, measurement })
  }
  const time = Math.floor(Date.now() / 1000)
  const worker = await studio.device(
    await digest(
      request.headers.get('Authorization')?.replace(/^Bearer /, '') ?? '',
    ),
    time,
  )
  if (!worker)
    throw new EditorError(
      401,
      'worker_required',
      'Worker authentication is required.',
    )
  const job = await studio.lease(scope.jobId, worker.id, scope.leaseHash, time)
  if (job.attempt !== scope.attempt)
    throw new EditorError(409, 'lease_changed', 'The assigned attempt changed.')
  await studio.complete(
    job,
    scope.leaseHash,
    measured,
    {
      finishing: 'cloudflare-editor',
      editorJobId: render.id,
      projectId: render.project_id,
      revision: render.revision,
      receiptSha256: receipt.receiptSha256,
      receipt,
      motionReviewed: false,
      heard: false,
      creativelyAccepted: false,
    },
    time,
  )
  return Response.json({
    state: 'review',
    outputCount: 6,
    humanAccepted: false,
    editorJobId: render.id,
  })
}
export const makeProductionEditorApi =
  (env: EditorRuntime, studio: Store, editor: EditorStore) =>
  (request: Request) =>
    Effect.runPromise(
      Effect.tryPromise({
        try: async () => {
          const url = new URL(request.url)
          const route = /^\/v1\/production\/jobs\/([a-zA-Z0-9-]+)\/(.+)$/.exec(
            url.pathname,
          )
          if (!route?.[1] || !route[2])
            throw new EditorError(
              404,
              'route_not_found',
              'Production editor route not found.',
            )
          const time = Math.floor(Date.now() / 1000)
          const worker = await studio.device(
            await digest(
              request.headers.get('Authorization')?.replace(/^Bearer /, '') ??
                '',
            ),
            time,
          )
          if (!worker)
            throw new EditorError(
              401,
              'worker_required',
              'Worker authentication is required.',
            )
          const leaseHash = await digest(
            request.headers.get('X-Job-Lease') ?? '',
          )
          const job = await studio.lease(route[1], worker.id, leaseHash, time)
          const release = await studio.releaseById(job.release_id)
          if (!release)
            throw new EditorError(
              404,
              'release_not_found',
              'Assigned release not found.',
            )
          const scope = {
            tenantId: release.tenant_id,
            releaseId: release.id,
            jobId: job.id,
            attempt: job.attempt,
            leaseHash,
          }
          if (route[2] === 'promote' && request.method === 'POST')
            return promote(request, env, scope, studio, editor)
          if (
            !/^(tools\/[^/]+|media\/[a-zA-Z0-9_-]{1,80}|jobs\/[^/]+\/outputs\/[^/]+)$/.test(
              route[2],
            )
          )
            throw new EditorError(
              404,
              'route_not_found',
              'This production editor operation is not supported.',
            )
          url.pathname = `/v1/${route[2]}`
          return makeEditorApi(env, editor)(new Request(url, request), scope)
        },
        catch: error => error,
      }).pipe(
        Effect.catch(error =>
          Effect.succeed(
            Response.json(
              {
                error:
                  error instanceof Error
                    ? error.message
                    : 'Production editor request failed.',
              },
              {
                status:
                  error instanceof EditorError || error instanceof ApiError
                    ? error.status
                    : 400,
              },
            ),
          ),
        ),
      ),
    )
export const productionEditorApi = (request: Request, env: EditorEnv) =>
  makeProductionEditorApi(
    env,
    makeStore(env.STUDIO_DB),
    editorStore(env),
  )(request)
