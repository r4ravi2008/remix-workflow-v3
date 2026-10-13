import { Effect, Schema } from 'effect'
import { createHash } from 'node:crypto'
import { mkdir, readFile, writeFile } from 'node:fs/promises'
import { join } from 'node:path'

import { canonicalJson } from '../src/canonical'
import type { WorkerConfig } from './config'
import type { DirectionJob } from './direction'
import { GPU, GPUError, type WorkstationConfig, tailscaleGPU } from './gpu'
import {
  type ObservationIntent,
  validateObservationReceipt,
} from './observation'
import { briefFingerprint } from './plan'
import { fileReceipt } from './transfer'

export const observationWindows = (duration: number) => {
  if (!Number.isFinite(duration) || duration <= 0 || duration > 900)
    throw new Error(
      'Observation coverage requires a finite song up to 900 seconds.',
    )
  const rows: Array<{ startSeconds: number; endSeconds: number }> = []
  for (let start = 0; start < duration; start += 26) {
    const end = Math.min(start + 28, duration)
    rows.push({ startSeconds: start, endSeconds: end })
    if (end === duration) break
  }
  return rows
}
const WindowResult = Schema.Struct({
  observationContractPassed: Schema.Boolean,
  observations: Schema.Array(Schema.Struct({ usable: Schema.Boolean })),
})
const Stored = Schema.Struct({
  schemaVersion: Schema.Literal(1),
  jobId: Schema.String,
  releaseId: Schema.String,
  briefSha256: Schema.String,
  sourceSha256: Schema.String,
  sourceBytes: Schema.Number,
  sourceDuration: Schema.Number,
  windowCount: Schema.Number,
  invalidObservationCount: Schema.Number,
  modelAudioCoverageComplete: Schema.Literal(true),
  automaticDirectionQualified: Schema.Literal(false),
  fullSongHeard: Schema.Literal(false),
  pilotApproved: Schema.Literal(false),
  humanAccepted: Schema.Literal(false),
  windows: Schema.Array(
    Schema.Struct({
      id: Schema.String,
      sha256: Schema.String,
      bytes: Schema.Number,
    }),
  ),
})
const operation = <A>(run: (signal: AbortSignal) => Promise<A>) =>
  Effect.tryPromise({
    try: run,
    catch: error =>
      new GPUError(
        error instanceof Error
          ? error.message
          : 'Observation preparation failed.',
      ),
  })

export const stageObservations = async (
  config: WorkerConfig,
  workstation: WorkstationConfig,
  job: DirectionJob,
  attempt: string,
  signal: AbortSignal,
  provider: typeof GPU.Service = tailscaleGPU(workstation),
) => {
  if (
    !/^[a-zA-Z0-9-]{1,64}$/u.test(attempt) ||
    !/^[a-zA-Z0-9-]+$/u.test(job.id)
  )
    throw new Error('Invalid observation attempt or assigned job identifier.')
  const fingerprint = briefFingerprint(job.brief)
  const selectedBackend = config.audioObservations?.backend
  const backendSelection = selectedBackend
    ? { audioBackend: selectedBackend }
    : {}
  const source = join(config.localState, job.id, 'canonical-audio')
  const measured = await fileReceipt(source, signal)
  if (
    measured.sha256 !== job.brief.audioSha256 ||
    measured.bytes !== job.brief.audioBytes
  )
    throw new Error(
      'Observation preparation source differs from the frozen brief.',
    )
  const directory = join(
    config.localState,
    job.id,
    `perception-v1-${fingerprint}-${attempt}`,
  )
  await mkdir(directory, { recursive: true, mode: 0o700 })
  const target = join(directory, 'perception-receipt.json')
  const planned = observationWindows(job.brief.audioDuration).map(window => {
    const identity = {
      purpose: 'audio-observation-v1',
      attempt,
      jobId: job.id,
      releaseId: job.releaseId,
      fingerprint,
      ...backendSelection,
      ...window,
    }
    const intent: ObservationIntent = {
      schemaVersion: 1,
      id: createHash('sha256').update(canonicalJson(identity)).digest('hex'),
      kind: 'audio-window',
      ...backendSelection,
      jobId: job.id,
      releaseId: job.releaseId,
      briefSha256: fingerprint,
      sourceSha256: job.brief.audioSha256,
      sourceBytes: job.brief.audioBytes,
      sourceDuration: job.brief.audioDuration,
      language: Schema.decodeUnknownSync(
        Schema.Literals(['Telugu', 'Hindi', 'Tamil', 'English']),
      )(job.brief.language),
      lyrics: job.brief.lyrics,
      ...window,
    }
    return { intent, path: join(directory, `${intent.id}.json`) }
  })
  const readWindow = async (item: (typeof planned)[number]) => {
    const raw = JSON.parse(await readFile(item.path, 'utf8'))
    validateObservationReceipt(item.intent, raw)
    return {
      intent: item.intent,
      result: Schema.decodeUnknownSync(WindowResult)(raw),
      measured: await fileReceipt(item.path, signal),
    }
  }
  const existing = await readFile(target, 'utf8').catch(error => {
    if (error.code === 'ENOENT') return null
    throw error
  })
  if (existing) {
    const stored = Schema.decodeUnknownSync(Stored)(JSON.parse(existing))
    if (
      stored.jobId !== job.id ||
      stored.releaseId !== job.releaseId ||
      stored.briefSha256 !== fingerprint ||
      stored.sourceSha256 !== measured.sha256 ||
      stored.sourceBytes !== measured.bytes ||
      stored.sourceDuration !== job.brief.audioDuration ||
      stored.windowCount !== planned.length ||
      stored.windows.length !== planned.length
    )
      throw new Error(
        'Preserved perception summary belongs to a different release.',
      )
    const windows = await Promise.all(planned.map(readWindow))
    for (const [index, row] of windows.entries()) {
      const record = stored.windows[index]
      if (
        !record ||
        record.id !== row.intent.id ||
        record.sha256 !== row.measured.sha256 ||
        record.bytes !== row.measured.bytes
      )
        throw new Error(
          'Preserved observation summary differs from its exact window bytes.',
        )
    }
    if (
      stored.invalidObservationCount !==
      windows.reduce(
        (count, row) =>
          count +
          row.result.observations.filter(observation => !observation.usable)
            .length,
        0,
      )
    )
      throw new Error(
        'Preserved observation quality count differs from its evidence.',
      )
    return {
      state: 'audio-observations-prepared',
      receiptPath: target,
      ...stored,
    }
  }
  const prepared = await Effect.runPromise(
    Effect.gen(function* () {
      const gpu = yield* GPU
      const rows = []
      for (const item of planned) {
        const present = yield* operation(() =>
          readFile(item.path, 'utf8').catch(error => {
            if (error.code === 'ENOENT') return null
            throw error
          }),
        )
        if (!present)
          yield* gpu.observe({
            intent: item.intent,
            localSource: source,
            localReceipt: item.path,
          })
        rows.push(yield* operation(() => readWindow(item)))
      }
      return rows
    }).pipe(Effect.provideService(GPU, provider)),
    { signal },
  )
  const after = await fileReceipt(source, signal)
  if (after.sha256 !== measured.sha256 || after.bytes !== measured.bytes)
    throw new Error(
      'The canonical source changed during observation preparation.',
    )
  const summary = Schema.decodeUnknownSync(Stored)({
    schemaVersion: 1,
    jobId: job.id,
    releaseId: job.releaseId,
    briefSha256: fingerprint,
    sourceSha256: measured.sha256,
    sourceBytes: measured.bytes,
    sourceDuration: job.brief.audioDuration,
    windowCount: prepared.length,
    invalidObservationCount: prepared.reduce(
      (count, row) =>
        count +
        row.result.observations.filter(observation => !observation.usable)
          .length,
      0,
    ),
    modelAudioCoverageComplete: true,
    automaticDirectionQualified: false,
    fullSongHeard: false,
    pilotApproved: false,
    humanAccepted: false,
    windows: prepared.map(row => ({ id: row.intent.id, ...row.measured })),
  })
  signal.throwIfAborted()
  await writeFile(target, `${JSON.stringify(summary, null, 2)}\n`, {
    mode: 0o600,
    flag: 'wx',
  })
  return {
    state: 'audio-observations-prepared',
    receiptPath: target,
    ...summary,
  }
}
