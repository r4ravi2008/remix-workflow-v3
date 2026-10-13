import { Schema } from 'effect'

import {
  type Preview,
  PreviewBundle,
  PreviewSource,
  previewIdentity,
  previewSamples,
} from './preview'
import { digest } from './store'

export const previewFixture = async (
  source: PreviewSource,
  jobId: string,
  overrides: Partial<Preview> = {},
) => {
  source = Schema.decodeUnknownSync(PreviewSource)(source)
  const input: Preview = {
    jobId,
    outputId: source.id,
    startFrame: 6,
    frames: 36,
    sampleFrames: [],
    ...overrides,
  }
  const samples = previewSamples(input, source)
  const still = ['thumbnail', 'artwork'].includes(source.id)
  const names = [
    `preview.${still ? 'jpg' : 'mp4'}`,
    ...samples.map(frame => `frame-${String(frame).padStart(6, '0')}.jpg`),
  ]
  const content = new Map(names.map(name => [name, `synthetic-${name}`]))
  const ratio = Math.min(1, 960 / Math.max(source.width, source.height))
  const files = await Promise.all(
    names.map(async (name, index) => ({
      name,
      sha256: await digest(content.get(name)!),
      bytes: content.get(name)!.length,
      width: index ? source.width : Math.floor((source.width * ratio) / 2) * 2,
      height: index
        ? source.height
        : Math.floor((source.height * ratio) / 2) * 2,
      frames: index || still ? 1 : input.frames,
      fps: index || still ? 0 : 24,
      duration: index || still ? 0 : input.frames / 24,
      sourceFrame: index ? samples[index - 1] : still ? input.startFrame : null,
      completeDecode: true,
      audioComparison:
        index || still
          ? null
          : {
              channelCosine: [1, 1],
              threshold: 0.99,
              passed: true,
              sampleRate: 4000,
              sourceStartSeconds: input.startFrame / 24,
              sourceDurationSeconds: input.frames / 24,
            },
    })),
  )
  const bundle = Schema.decodeUnknownSync(PreviewBundle)({
    schemaVersion: 1,
    method: 'native-review-preview/v2',
    ...input,
    sampleFrames: samples,
    bundleId: await previewIdentity(input, source),
    source,
    files,
    measured: true,
    semanticReviewed: false,
    motionReviewed: false,
    heard: false,
    creativelyAccepted: false,
  })
  return { input, bundle, content }
}
