import { Schema } from 'effect'

import { canonicalJson } from '../src/canonical'
import { OutputId } from '../src/domain'
import type { MediaBucket } from '../src/server/api'
import { EditorError, type JobRow, digest } from './store'

const Hash = Schema.String.check(Schema.isPattern(/^[a-f0-9]{64}$/))
const Frame = Schema.Int.check(Schema.isBetween({ minimum: 0, maximum: 21600 }))
const PositiveFrame = Schema.Int.check(
  Schema.isBetween({ minimum: 1, maximum: 240 }),
)
const Bytes = Schema.Int.check(
  Schema.isBetween({ minimum: 1, maximum: 33554432 }),
)
export const Preview = Schema.Struct({
  jobId: Schema.String.check(Schema.isPattern(/^[a-zA-Z0-9_-]{1,80}$/)),
  outputId: OutputId,
  startFrame: Frame,
  frames: PositiveFrame,
  sampleFrames: Schema.Array(Frame).check(Schema.isMaxLength(8)),
})
export type Preview = typeof Preview.Type
export const PreviewSource = Schema.Struct({
  id: OutputId,
  sha256: Hash,
  bytes: Schema.Int.check(
    Schema.isBetween({ minimum: 1, maximum: 2147483648 }),
  ),
  width: Schema.Int,
  height: Schema.Int,
  frames: Schema.Int,
})
export type PreviewSource = typeof PreviewSource.Type
export const PreviewFile = Schema.Struct({
  name: Schema.String.check(
    Schema.isPattern(/^(?:preview\.(?:mp4|jpg)|frame-[0-9]{6}\.jpg)$/),
  ),
  sha256: Hash,
  bytes: Bytes,
  width: Schema.Int,
  height: Schema.Int,
  frames: PositiveFrame,
  fps: Schema.Int,
  duration: Schema.Finite,
  sourceFrame: Schema.NullOr(Frame),
  completeDecode: Schema.Literal(true),
  audioComparison: Schema.NullOr(
    Schema.Struct({
      channelCosine: Schema.Array(Schema.Finite),
      threshold: Schema.Literal(0.99),
      passed: Schema.Literal(true),
      sampleRate: Schema.Literal(4000),
      sourceStartSeconds: Schema.Finite,
      sourceDurationSeconds: Schema.Finite,
    }),
  ),
})
export const PreviewBundle = Schema.Struct({
  schemaVersion: Schema.Literal(1),
  method: Schema.Literal('native-review-preview/v2'),
  bundleId: Hash,
  jobId: Preview.fields.jobId,
  outputId: OutputId,
  source: PreviewSource,
  startFrame: Frame,
  frames: PositiveFrame,
  sampleFrames: Schema.Array(Frame).check(Schema.isMaxLength(8)),
  files: Schema.Array(PreviewFile).check(
    Schema.isMinLength(2),
    Schema.isMaxLength(9),
  ),
  measured: Schema.Literal(true),
  semanticReviewed: Schema.Literal(false),
  motionReviewed: Schema.Literal(false),
  heard: Schema.Literal(false),
  creativelyAccepted: Schema.Literal(false),
})
export type PreviewBundle = typeof PreviewBundle.Type
export const previewSamples = (input: Preview, source: PreviewSource) => {
  const end = input.startFrame + input.frames
  const still = ['thumbnail', 'artwork'].includes(source.id)
  if (
    source.id !== input.outputId ||
    input.startFrame < 0 ||
    end > source.frames ||
    (still && (input.startFrame !== 0 || input.frames !== 1))
  )
    throw new EditorError(
      422,
      'preview_range',
      'Preview must select an exact range of the completed output.',
    )
  const samples = input.sampleFrames.length
    ? [...input.sampleFrames]
    : [
        ...new Set([
          input.startFrame,
          input.startFrame + Math.floor((input.frames - 1) / 2),
          end - 1,
        ]),
      ]
  if (
    new Set(samples).size !== samples.length ||
    samples.some(frame => frame < input.startFrame || frame >= end)
  )
    throw new EditorError(
      422,
      'preview_samples',
      'Samples must be unique source frames within the preview range.',
    )
  return samples.sort((left, right) => left - right)
}
export const previewIdentity = async (input: Preview, source: PreviewSource) =>
  digest(
    canonicalJson({
      method: 'native-review-preview/v2',
      ...input,
      sampleFrames: previewSamples(input, source),
      source,
    }),
  )
export const previewPrefix = (
  tenant: string,
  jobId: string,
  bundleId: string,
) => `editor/${tenant}/jobs/${jobId}/previews/${bundleId}/`
export const previewSource = (job: JobRow, outputId: string) => {
  if (job.state !== 'ready' || !job.receipt_json)
    throw new EditorError(
      409,
      'output_not_ready',
      'Review previews require a verified completed output.',
    )
  const receipt = Schema.decodeUnknownSync(
    Schema.Struct({ outputs: Schema.Array(PreviewSource) }),
  )(JSON.parse(job.receipt_json))
  const source = receipt.outputs.find(output => output.id === outputId)
  if (!source)
    throw new EditorError(
      404,
      'artifact_not_found',
      'The completed artifact is missing.',
    )
  return source
}
export const validatePreview = async (
  input: Preview,
  source: PreviewSource,
  bundle: PreviewBundle,
) => {
  const samples = previewSamples(input, source)
  const still = ['thumbnail', 'artwork'].includes(source.id)
  const ratio = Math.min(1, 960 / Math.max(source.width, source.height))
  const width = Math.floor((source.width * ratio) / 2) * 2
  const height = Math.floor((source.height * ratio) / 2) * 2
  const expectedNames = [
    `preview.${still ? 'jpg' : 'mp4'}`,
    ...samples.map(frame => `frame-${String(frame).padStart(6, '0')}.jpg`),
  ]
  if (
    bundle.bundleId !== (await previewIdentity(input, source)) ||
    bundle.jobId !== input.jobId ||
    bundle.outputId !== input.outputId ||
    canonicalJson(bundle.source) !== canonicalJson(source) ||
    bundle.startFrame !== input.startFrame ||
    bundle.frames !== input.frames ||
    canonicalJson(bundle.sampleFrames) !== canonicalJson(samples) ||
    bundle.files.length !== expectedNames.length ||
    new Set(bundle.files.map(file => file.name)).size !==
      expectedNames.length ||
    bundle.files.some(file => !expectedNames.includes(file.name)) ||
    bundle.files.reduce((total, file) => total + file.bytes, 0) > 33554432
  )
    throw new EditorError(
      422,
      'preview_binding',
      'The review bundle differs from its immutable source and exact range.',
    )
  for (const file of bundle.files) {
    const proxy = file.name.startsWith('preview.')
    const video = proxy && !still
    const frame = proxy
      ? still
        ? input.startFrame
        : null
      : Number(file.name.slice(6, 12))
    if (
      file.width !== (proxy ? width : source.width) ||
      file.height !== (proxy ? height : source.height) ||
      file.frames !== (video ? input.frames : 1) ||
      file.fps !== (video ? 24 : 0) ||
      Math.abs(file.duration - (video ? input.frames / 24 : 0)) > 0.000001 ||
      file.sourceFrame !== frame ||
      (video ? !file.audioComparison : file.audioComparison !== null) ||
      (file.audioComparison &&
        (file.audioComparison.channelCosine.length !== 2 ||
          Math.min(...file.audioComparison.channelCosine) < 0.99 ||
          Math.abs(
            file.audioComparison.sourceStartSeconds - input.startFrame / 24,
          ) > 0.000001))
    )
      throw new EditorError(
        422,
        'preview_measurement',
        'Measured preview media differs from its bounded recipe.',
      )
  }
}
export const readPreview = async (
  media: MediaBucket,
  tenant: string,
  job: JobRow,
  bundleId: string,
) => {
  const object = await media.get(
    previewPrefix(tenant, job.id, bundleId) + 'receipt.json',
    {},
  )
  if (!object) return null
  if (object.size < 1 || object.size > 65536)
    throw new EditorError(
      422,
      'preview_integrity',
      'Preview receipt is missing or oversized.',
    )
  const text = await new Response(object.body).text()
  if (new TextEncoder().encode(text).length !== object.size)
    throw new EditorError(
      422,
      'preview_integrity',
      'Preview receipt is incomplete.',
    )
  const bundle = Schema.decodeUnknownSync(PreviewBundle)(JSON.parse(text))
  const input = {
    jobId: job.id,
    outputId: bundle.outputId,
    startFrame: bundle.startFrame,
    frames: bundle.frames,
    sampleFrames: bundle.sampleFrames,
  }
  if (bundle.bundleId !== bundleId)
    throw new EditorError(
      422,
      'preview_integrity',
      'Preview receipt belongs to another bundle.',
    )
  await validatePreview(input, previewSource(job, bundle.outputId), bundle)
  return bundle
}
