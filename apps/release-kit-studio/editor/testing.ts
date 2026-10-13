import { type Clip, type Project } from './project'

const clip: Clip = {
  id: 'scene',
  assetId: 'scene',
  at: 0,
  inFrame: 0,
  frames: 48,
  transform: { centerX: 0.5, centerY: 0.5, zoom: 1 },
  color: { brightness: 0, contrast: 1, saturation: 1 },
  fadeIn: 0,
  fadeOut: 0,
  reactive: null,
}
export const projectFixture = (): Project => ({
  schemaVersion: 1,
  releaseId: 'release-one',
  briefSha256: 'b'.repeat(64),
  audioSha256: 'a'.repeat(64),
  language: 'Telugu',
  lyrics: 'ప్రతి నిమిషం',
  fps: 24,
  assets: [
    {
      id: 'audio',
      kind: 'audio',
      sha256: 'a'.repeat(64),
      bytes: 100,
      width: 0,
      height: 0,
      duration: 2,
    },
    {
      id: 'scene',
      kind: 'video',
      sha256: 'c'.repeat(64),
      bytes: 100,
      width: 1920,
      height: 1080,
      duration: 2,
    },
  ],
  compositions: [
    {
      id: 'film',
      width: 1920,
      height: 1080,
      frames: 48,
      rationale: 'Cinematic scene',
      audio: { assetId: 'audio', startSeconds: 0 },
      clips: [clip],
      captions: [
        {
          id: 'cue',
          kind: 'lyric',
          start: 0,
          end: 48,
          text: 'ప్రతి నిమిషం',
          font: 'Noto Sans Telugu',
          size: 64,
          marginBottom: 100,
        },
      ],
    },
  ],
})
