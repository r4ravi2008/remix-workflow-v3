import { Schema } from 'effect'
import {
  mkdir,
  mkdtemp,
  readFile,
  rename,
  rm,
  writeFile,
} from 'node:fs/promises'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'

import { OutputId, ReleaseBrief, outputs } from '../src/domain'
import type { WorkerConfig } from './config'
import { command } from './gpu'
import { briefFingerprint } from './plan'
import { fileReceipt } from './transfer'

const AudioAnalysis = Schema.Struct({
  schemaVersion: Schema.Literal(2),
  sourceSha256: Schema.String,
  sourceBytes: Schema.Number,
  durationSeconds: Schema.Number,
  fps: Schema.Literal(24),
  frameCount: Schema.Number,
  rms: Schema.Array(Schema.Number),
  environmentGain: Schema.Array(Schema.Number),
  fullSongHeard: Schema.Literal(false),
})
export const DirectionPacket = Schema.Struct({
  schemaVersion: Schema.Literal(2),
  status: Schema.Literal('prepared-for-review'),
  jobId: Schema.String,
  releaseId: Schema.String,
  briefSha256: Schema.String,
  brief: ReleaseBrief,
  source: Schema.Struct({
    path: Schema.String,
    sha256: Schema.String,
    bytes: Schema.Number,
  }),
  analysis: Schema.Struct({
    sha256: Schema.String,
    bytes: Schema.Number,
    frameCount: Schema.Number,
  }),
  lyricLines: Schema.Array(Schema.String),
  requirements: Schema.Array(
    Schema.Struct({
      id: Schema.String,
      interpretation: Schema.String,
      verification: Schema.String,
    }),
  ),
  deliverables: Schema.Array(
    Schema.Struct({
      id: OutputId,
      format: Schema.String,
      description: Schema.String,
    }),
  ),
  review: Schema.Struct({
    fullSongHeard: Schema.Literal(false),
    lyricTimingVerified: Schema.Literal(false),
    chronologicalStoryboardReviewed: Schema.Literal(false),
    pilotWatched: Schema.Literal(false),
    pilotHeard: Schema.Literal(false),
    approvedForBulk: Schema.Literal(false),
  }),
  execution: Schema.Struct({
    gpu: Schema.Literal('tailscale-herdr'),
    finishing: Schema.Literal('cloudflare-editor'),
  }),
})

export interface DirectionJob {
  id: string
  releaseId: string
  brief: typeof ReleaseBrief.Type
}
export const stageDirection = async (
  config: WorkerConfig,
  job: DirectionJob,
  signal: AbortSignal,
) => {
  if (!/^[a-zA-Z0-9-]+$/.test(job.id))
    throw new Error('Invalid direction job identifier.')
  const root = join(config.localState, job.id)
  const source = join(root, 'canonical-audio')
  const receipt = await fileReceipt(source, signal)
  if (
    receipt.sha256 !== job.brief.audioSha256 ||
    receipt.bytes !== job.brief.audioBytes
  )
    throw new Error(
      'Direction source differs from the immutable release brief.',
    )
  const fingerprint = briefFingerprint(job.brief)
  const directory = join(root, `direction-v2-${fingerprint}`)
  const packetPath = join(directory, 'direction-input.json')
  const readPrepared = async () => {
    const packet = Schema.decodeUnknownSync(DirectionPacket)(
      JSON.parse(await readFile(packetPath, 'utf8')),
    )
    const analysis = await fileReceipt(
      join(directory, 'audio-analysis.json'),
      signal,
    )
    if (
      packet.jobId !== job.id ||
      packet.releaseId !== job.releaseId ||
      packet.briefSha256 !== fingerprint ||
      briefFingerprint(packet.brief) !== fingerprint ||
      packet.source.path !== source ||
      packet.source.sha256 !== receipt.sha256 ||
      packet.source.bytes !== receipt.bytes ||
      packet.analysis.sha256 !== analysis.sha256 ||
      packet.analysis.bytes !== analysis.bytes
    )
      throw new Error(
        'Prepared direction does not match this release and its verified analysis.',
      )
    return {
      packetPath,
      briefSha256: fingerprint,
      analysisSha256: analysis.sha256,
      frameCount: packet.analysis.frameCount,
      state: 'direction-prepared',
    }
  }
  const existing = await readFile(packetPath, 'utf8').catch(error => {
    if (error.code === 'ENOENT') return null
    throw error
  })
  if (existing) return readPrepared()
  await mkdir(root, { recursive: true, mode: 0o700 })
  const temporary = await mkdtemp(join(root, '.direction-incoming-'))
  try {
    const analysisPath = join(temporary, 'audio-analysis.json')
    await command(
      'python3',
      [
        fileURLToPath(new URL('./analyze_audio.py', import.meta.url)),
        source,
        analysisPath,
      ],
      300000,
      signal,
    )
    const analysis = Schema.decodeUnknownSync(AudioAnalysis)(
      JSON.parse(await readFile(analysisPath, 'utf8')),
    )
    if (
      analysis.sourceSha256 !== receipt.sha256 ||
      analysis.sourceBytes !== receipt.bytes ||
      Math.abs(analysis.durationSeconds - job.brief.audioDuration) > 0.15 ||
      analysis.frameCount !== analysis.rms.length ||
      analysis.frameCount !== analysis.environmentGain.length ||
      Math.abs(analysis.frameCount / 24 - analysis.durationSeconds) > 0.15 ||
      !analysis.rms.every(value => Number.isFinite(value) && value >= 0) ||
      !analysis.environmentGain.every(
        value => Number.isFinite(value) && value >= 0.22 && value <= 0.8,
      )
    )
      throw new Error(
        'Audio analysis is incomplete or differs from the canonical song.',
      )
    const measured = await fileReceipt(analysisPath, signal)
    const packet = Schema.decodeUnknownSync(DirectionPacket)({
      schemaVersion: 2,
      status: 'prepared-for-review',
      jobId: job.id,
      releaseId: job.releaseId,
      briefSha256: fingerprint,
      brief: job.brief,
      source: { path: source, ...receipt },
      analysis: { ...measured, frameCount: analysis.frameCount },
      lyricLines: job.brief.lyrics.split(/\r?\n/u),
      requirements: [
        {
          id: 'cinematic',
          interpretation: job.brief.profile.identity,
          verification:
            'Develop a chronological story and prove its hardest complete passage in the Cloudflare editor. Musical interpretation awaits a full listen.',
        },
        {
          id: 'lyrics',
          interpretation: `Use the supplied ${job.brief.language} lyrics exactly in their native script.`,
          verification:
            'Align against the sung words; prove glyph shaping, phrasing, dwell and subject clearance in motion.',
        },
        {
          id: 'music-response',
          interpretation: `${job.brief.profile.intensity} response in the ${job.brief.profile.palette} world; protect people, lyrics and story props.`,
          verification:
            'Measured envelope is available. Confirm musical accents by listening and inspect animated environment masks in the pilot.',
        },
        {
          id: 'release-kit',
          interpretation:
            'One complete film, three separately composed vertical promos, a landscape thumbnail and square artwork.',
          verification:
            'Cloudflare-native exports, decode and dimensions checks, private stored-file hashes, and full watch/listen review.',
        },
      ],
      deliverables: outputs.map(output => ({
        id: output.id,
        format: output.format,
        description: output.description,
      })),
      review: {
        fullSongHeard: false,
        lyricTimingVerified: false,
        chronologicalStoryboardReviewed: false,
        pilotWatched: false,
        pilotHeard: false,
        approvedForBulk: false,
      },
      execution: { gpu: 'tailscale-herdr', finishing: 'cloudflare-editor' },
    })
    await writeFile(
      join(temporary, 'direction-input.json'),
      `${JSON.stringify(packet, null, 2)}\n`,
      { mode: 0o600 },
    )
    signal.throwIfAborted()
    await rename(temporary, directory).catch(error => {
      if (!['EEXIST', 'ENOTEMPTY'].includes(error.code)) throw error
    })
    return await readPrepared()
  } finally {
    await rm(temporary, { recursive: true, force: true })
  }
}
