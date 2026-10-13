import { Schema } from 'effect'

import { canonicalJson } from '../src/canonical'
import { OutputId, ReleaseBrief, outputs } from '../src/domain'
import type { MediaBucket } from '../src/server/api'
import { validateMeasurement } from '../src/server/contracts'
import { FrameDiagnostics } from './artifact'
import { Review } from './catalog'
import { KitDescriptor } from './kit-contract'
import { validateProject } from './project'
import { EditorError, type EditorStore, type JobRow, digest } from './store'
import { type ArchiveEntry, zipBytes } from './zip'

const Hash = Schema.String.check(Schema.isPattern(/^[a-f0-9]{64}$/))
const ReceiptContent = Schema.Struct({
  projectSha256: Hash,
  outputs: Schema.Array(
    Schema.Struct({
      id: OutputId,
      sha256: Hash,
      bytes: Schema.Int.check(
        Schema.isBetween({ minimum: 1, maximum: 2147483648 }),
      ),
      width: Schema.Int,
      height: Schema.Int,
      duration: Schema.Finite,
      completeDecode: Schema.Literal(true),
      frameDiagnostics: Schema.optional(FrameDiagnostics),
    }),
  ),
})
const Receipt = Schema.Struct({
  ...ReceiptContent.fields,
  measured: Schema.Literal(true),
  storedByteReadback: Schema.Literal(true),
  receiptStored: Schema.Literal(true),
  receiptSha256: Hash,
})
const failure = (code: string, detail: string): never => {
  throw new EditorError(409, code, detail)
}
const memoryEntry = async (
  name: string,
  content: string,
): Promise<ArchiveEntry> => {
  const data = new TextEncoder().encode(content)
  return {
    name,
    bytes: data.byteLength,
    sha256: await digest(content),
    open: async () => new Blob([data]).stream(),
  }
}
export const prepareKit = async (
  store: EditorStore,
  media: MediaBucket,
  tenant: string,
  job: JobRow,
) => {
  if (job.tenant_id !== tenant || job.state !== 'ready' || !job.receipt_json)
    failure('kit_not_ready', 'A verified six-output render is required.')
  const receipt = Schema.decodeUnknownSync(Receipt)(
    JSON.parse(job.receipt_json!),
  )
  const snapshot = await store.inspect(tenant, job.project_id, job.revision)
  const project = snapshot.project
  const projectContent = canonicalJson(project)
  if (
    project.releaseId !== job.release_id ||
    validateProject(project, 'kit').length ||
    receipt.outputs.length !== 6 ||
    new Set(receipt.outputs.map(item => item.id)).size !== 6 ||
    receipt.projectSha256 !== (await digest(projectContent))
  )
    failure(
      'kit_binding',
      'The render must match an immutable six-output project revision.',
    )
  const row = Schema.decodeUnknownSync(
    Schema.NullOr(Schema.Struct({ brief_json: Schema.String })),
  )(
    await store.db.first(
      'SELECT brief_json FROM releases WHERE tenant_id=? AND id=?',
      [tenant, job.release_id],
    ),
  )
  if (!row) failure('source_binding', 'The assigned release is missing.')
  const brief = Schema.decodeUnknownSync(ReleaseBrief)(
    JSON.parse(row!.brief_json),
  )
  if (
    project.briefSha256 !== (await digest(canonicalJson(brief))) ||
    project.audioSha256 !== brief.audioSha256 ||
    project.lyrics !== brief.lyrics ||
    project.language !== brief.language
  )
    failure(
      'source_binding',
      'The project differs from its frozen source, lyrics or language.',
    )
  const receiptObject = await media.get(
    `editor/${tenant}/jobs/${job.id}/receipt.json`,
    {},
  )
  if (
    !receiptObject ||
    receiptObject.size < 1 ||
    receiptObject.size > 4 * 1024 * 1024
  )
    failure(
      'receipt_integrity',
      'The private render receipt is missing or oversized.',
    )
  const receiptText = await new Response(receiptObject!.body).text()
  if (
    new TextEncoder().encode(receiptText).byteLength !== receiptObject!.size ||
    (await digest(receiptText)) !== receipt.receiptSha256
  )
    failure(
      'receipt_integrity',
      'The private render receipt failed hash readback.',
    )
  const stored = Schema.decodeUnknownSync(ReceiptContent)(
    JSON.parse(receiptText),
  )
  if (
    canonicalJson(stored) !==
    canonicalJson({
      projectSha256: receipt.projectSha256,
      outputs: receipt.outputs,
    })
  )
    failure(
      'receipt_binding',
      'The job metadata differs from the immutable stored receipt.',
    )
  const entries: Array<ArchiveEntry> = []
  const files = []
  for (const output of outputs) {
    const artifact = receipt.outputs.find(item => item.id === output.id)!
    const composition = project.compositions.find(
      item => item.id === output.id,
    )!
    validateMeasurement(
      output.id,
      {
        width: artifact.width,
        height: artifact.height,
        duration: artifact.duration,
        sha256: artifact.sha256,
        storageSha256: artifact.sha256,
        decoded: true,
        composition: composition.rationale,
      },
      brief.audioDuration,
    )
    if (
      artifact.width !== composition.width ||
      artifact.height !== composition.height ||
      (artifact.frameDiagnostics &&
        artifact.frameDiagnostics.sampledFrames !== composition.frames) ||
      (composition.audio &&
        Math.abs(artifact.duration - composition.frames / project.fps) >
          1 / project.fps + 0.005)
    )
      failure(
        'measurement_binding',
        'Output measurements differ from the encoded composition.',
      )
    const key = `editor/${tenant}/jobs/${job.id}/${output.id}`
    const head = await media.head(key)
    if (head?.size !== artifact.bytes)
      failure(
        'stored_output_missing',
        'A verified private output is missing or changed.',
      )
    const name = `${output.id}.${composition.audio ? 'mp4' : 'jpg'}`
    entries.push({
      name,
      bytes: artifact.bytes,
      sha256: artifact.sha256,
      open: async () => {
        const object = await media.get(
          key,
          head?.etag ? { onlyIf: { etagMatches: head.etag } } : {},
        )
        if (!object || !object.body || object.size !== artifact.bytes)
          failure(
            'stored_output_changed',
            'The output changed during archive delivery.',
          )
        return object!.body
      },
    })
    files.push({ ...artifact, name })
  }
  const projectEntry = await memoryEntry('project.json', projectContent + '\n')
  entries.push(projectEntry)
  const rows = await store.db.all(
    'SELECT output_id,sha256,kind,detail_json,created_at FROM editor_reviews WHERE tenant_id=? AND job_id=? ORDER BY created_at,id LIMIT 101',
    [tenant, job.id],
  )
  const reviews = rows.slice(0, 100).flatMap(raw => {
    const record = Schema.decodeUnknownSync(
      Schema.Struct({
        output_id: OutputId,
        sha256: Hash,
        kind: Schema.String,
        detail_json: Schema.String,
        created_at: Schema.Int,
      }),
    )(raw)
    if (
      !receipt.outputs.some(
        item => item.id === record.output_id && item.sha256 === record.sha256,
      )
    )
      return []
    const detail = Schema.decodeUnknownSync(Review)(
      JSON.parse(record.detail_json),
    )
    if (
      detail.jobId !== job.id ||
      detail.outputId !== record.output_id ||
      detail.sha256 !== record.sha256 ||
      detail.kind !== record.kind ||
      detail.method.length > 2000 ||
      detail.notes.length > 10000
    )
      failure(
        'review_binding',
        'Review evidence differs from its immutable output.',
      )
    return [{ ...detail, createdAt: record.created_at }]
  })
  const manifest = {
    schemaVersion: 1,
    format: 'release-kit',
    jobId: job.id,
    releaseId: job.release_id,
    projectId: job.project_id,
    revision: job.revision,
    briefSha256: project.briefSha256,
    audioSha256: project.audioSha256,
    renderReceiptSha256: receipt.receiptSha256,
    files,
    project: {
      name: projectEntry.name,
      bytes: projectEntry.bytes,
      sha256: projectEntry.sha256,
    },
    reviewRecords: reviews,
    reviewRecordsComplete: rows.length <= 100,
    verification: { measured: true, storedByteReadback: true },
    motionReviewed: false,
    heard: false,
    creativelyAccepted: false,
  }
  const manifestEntry = await memoryEntry(
    'manifest.json',
    canonicalJson(manifest) + '\n',
  )
  entries.push(manifestEntry)
  const descriptor = Schema.decodeUnknownSync(KitDescriptor)({
    jobId: job.id,
    releaseId: job.release_id,
    projectId: job.project_id,
    revision: job.revision,
    bytes: zipBytes(entries),
    manifestSha256: manifestEntry.sha256,
    entries: entries.map(({ name, bytes, sha256 }) => ({
      name,
      bytes,
      sha256,
    })),
    downloadPath: `/v1/jobs/${job.id}/archive`,
  })
  return { entries, descriptor }
}
