import { Schema } from 'effect'
import { createHash } from 'node:crypto'
import { readFile } from 'node:fs/promises'

import { productionAssetPrefix } from '../editor/production-contract'
import { decodeProject, validateProject } from '../editor/project'
import { canonicalJson } from '../src/canonical'
import { OutputId } from '../src/domain'
import type { WorkerConfig } from './config'
import { type OwnedJob, workerHeaders } from './connection'
import {
  materializeEditorRecipe,
  readEditorJson,
  readEditorRecipe,
} from './editor-recipe'
import { editorRequest } from './editor-request'
import { type EditorProductionPlan, briefFingerprint } from './plan'
import { fileReceipt } from './transfer'

const Status = Schema.Struct({
  jobId: Schema.String,
  state: Schema.String,
  progress: Schema.Unknown,
  receipt: Schema.NullOr(
    Schema.Struct({
      measured: Schema.Literal(true),
      storedByteReadback: Schema.Literal(true),
      receiptStored: Schema.Literal(true),
      outputs: Schema.Array(
        Schema.Struct({
          id: OutputId,
          sha256: Schema.String,
          bytes: Schema.Number,
        }),
      ),
    }),
  ),
})
export const finishCloudEditor = async (
  config: WorkerConfig,
  job: OwnedJob & {
    releaseId: string
    brief: Parameters<typeof briefFingerprint>[0]
  },
  plan: EditorProductionPlan,
  source: string,
  scenes: ReadonlyMap<string, string>,
  signal: AbortSignal,
  report: (phase: string, progress: number, receipt: unknown) => Promise<void>,
) => {
  const recipe = await readEditorRecipe(plan, job)
  const resolved = recipe
    ? await materializeEditorRecipe(recipe, job, source, scenes, signal)
    : plan.schemaVersion === 2
      ? {
          project: decodeProject(await readEditorJson(plan.editor.projectPath)),
          bindings: plan.editor.assets,
        }
      : (() => {
          throw new Error('The generated-media recipe is missing.')
        })()
  const { project, bindings } = resolved
  if (
    project.releaseId !== job.releaseId ||
    project.audioSha256 !== job.brief.audioSha256 ||
    project.briefSha256 !== briefFingerprint(job.brief) ||
    project.lyrics !== job.brief.lyrics ||
    project.language !== job.brief.language
  )
    throw new Error(
      'The editor project differs from the assigned frozen release.',
    )
  const findings = validateProject(project, 'kit')
  if (findings.length)
    throw new Error(JSON.stringify({ code: 'invalid_kit', findings }))
  if (
    bindings.length !== project.assets.length ||
    new Set(bindings.map(asset => asset.assetId)).size !== project.assets.length
  )
    throw new Error(
      'Each immutable project asset needs exactly one input binding.',
    )
  const root = `/api/worker/jobs/${job.id}/editor`
  const call = (path: string, value: unknown) =>
    editorRequest(config, job, root, path, value, signal)
  for (const asset of project.assets) {
    if (!asset.id.startsWith(productionAssetPrefix(job.releaseId)))
      throw new Error(
        'Production asset IDs must use the assigned release namespace.',
      )
    const binding = bindings.find(input => input.assetId === asset.id)
    if (!binding) throw new Error('Project asset input is missing.')
    const path =
      binding.kind === 'canonical-audio'
        ? source
        : binding.kind === 'shot'
          ? scenes.get(binding.shotId)
          : binding.path
    if (!path) throw new Error('The generated scene binding is missing.')
    if (
      binding.kind === 'canonical-audio' &&
      (asset.kind !== 'audio' || asset.sha256 !== job.brief.audioSha256)
    )
      throw new Error(
        'The canonical audio binding differs from the exact master.',
      )
    const measured = await fileReceipt(path, signal)
    if (
      asset.bytes > 100 * 1024 * 1024 ||
      measured.sha256 !== asset.sha256 ||
      measured.bytes !== asset.bytes
    )
      throw new Error(
        'Editor media differs from the immutable project asset; reconcile before upload.',
      )
    await call('tools/media.register', asset)
    const existing = Schema.decodeUnknownSync(
      Schema.Struct({ uploaded: Schema.Boolean }),
    )(await call('tools/media.inspect', { assetId: asset.id }))
    if (!existing.uploaded) {
      const content = await readFile(path)
      if (
        content.byteLength !== asset.bytes ||
        createHash('sha256').update(content).digest('hex') !== asset.sha256
      )
        throw new Error('Editor media changed while preparing upload.')
      const response = await fetch(
        new URL(`${root}/media/${asset.id}`, config.baseUrl),
        {
          method: 'PUT',
          headers: {
            ...workerHeaders(config, job),
            'Content-Type': 'application/octet-stream',
            'Content-Length': String(asset.bytes),
          },
          body: new Blob([new Uint8Array(content)]),
          redirect: 'error',
          signal: AbortSignal.any([signal, AbortSignal.timeout(120000)]),
        },
      )
      if (!response.ok)
        throw new Error(
          `Cloudflare editor media upload failed (${response.status}).`,
        )
      await response.body?.cancel()
    }
    const stored = Schema.decodeUnknownSync(
      Schema.Struct({
        uploaded: Schema.Literal(true),
        metadata: Schema.Struct({
          bytes: Schema.Number,
          sha256: Schema.String,
        }),
      }),
    )(await call('tools/media.inspect', { assetId: asset.id }))
    if (
      stored.metadata.bytes !== asset.bytes ||
      stored.metadata.sha256 !== asset.sha256
    )
      throw new Error('Private editor media readback differs from its source.')
  }
  const fingerprint = createHash('sha256')
    .update(
      canonicalJson({
        projectId: plan.editor.projectId,
        expectedRevision: plan.editor.expectedRevision,
        project,
      }),
    )
    .digest('hex')
  const revision = Schema.decodeUnknownSync(
    Schema.Struct({ revision: Schema.Number }),
  )(
    await call('tools/project.commit', {
      projectId: plan.editor.projectId,
      expectedRevision: plan.editor.expectedRevision,
      intentId: `commit-${fingerprint}`,
      project,
    }),
  )
  const renderFingerprint = createHash('sha256')
    .update(
      canonicalJson({
        projectId: plan.editor.projectId,
        revision: revision.revision,
        mode: 'kit',
        outputId: null,
      }),
    )
    .digest('hex')
  let status = Schema.decodeUnknownSync(Status)(
    await call('tools/render.start', {
      projectId: plan.editor.projectId,
      revision: revision.revision,
      intentId: `kit-${renderFingerprint}`,
      mode: 'kit',
      outputId: null,
    }),
  )
  while (['queued', 'staging', 'running', 'verifying'].includes(status.state)) {
    await report(
      status.state === 'queued'
        ? 'Your release kit is queued'
        : 'Creating your release kit',
      0.75,
      {
        editorJobId: status.jobId,
        state: status.state,
        progress: status.progress,
      },
    )
    await new Promise<void>((resolve, reject) => {
      const onAbort = () => {
        clearTimeout(timer)
        reject(signal.reason)
      }
      const timer = setTimeout(() => {
        signal.removeEventListener('abort', onAbort)
        resolve()
      }, 3000)
      signal.addEventListener('abort', onAbort, { once: true })
      if (signal.aborted) onAbort()
    })
    status = Schema.decodeUnknownSync(Status)(
      await call('tools/render.status', { jobId: status.jobId }),
    )
  }
  if (
    status.state !== 'ready' ||
    !status.receipt ||
    status.receipt.outputs.length !== 6 ||
    new Set(status.receipt.outputs.map(output => output.id)).size !== 6
  )
    throw new Error(
      `Cloudflare render ${status.jobId} is ${status.state} and needs reconciliation; no renderer replay was submitted.`,
    )
  for (const output of status.receipt.outputs) {
    await report('Checking your release kit', 0.9, {
      editorJobId: status.jobId,
      outputId: output.id,
    })
    const verified = Schema.decodeUnknownSync(
      Schema.Struct({
        sha256: Schema.String,
        bytes: Schema.Number,
        completeDecode: Schema.Literal(true),
      }),
    )(
      await call('tools/artifact.verify', {
        jobId: status.jobId,
        outputId: output.id,
      }),
    )
    if (verified.sha256 !== output.sha256 || verified.bytes !== output.bytes)
      throw new Error(
        'Independent verification differs from the immutable rendered bytes.',
      )
  }
  const promoted = Schema.decodeUnknownSync(
    Schema.Struct({
      state: Schema.Literal('review'),
      outputCount: Schema.Literal(6),
      humanAccepted: Schema.Literal(false),
      editorJobId: Schema.String,
    }),
  )(await call('promote', { editorJobId: status.jobId }))
  return {
    ...promoted,
    jobId: job.id,
    releaseId: job.releaseId,
    finishing: 'cloudflare-editor',
  }
}
