import { Effect, Schema } from 'effect'
import { mkdir, readFile, rename, unlink, writeFile } from 'node:fs/promises'
import { join } from 'node:path'

import { OutputId } from '../src/domain'
import { ReleaseBrief } from '../src/server/contracts'
import { type WorkerConfig, loadWorkerConfig } from './config'
import { workerRequest } from './connection'
import { stageDirection } from './direction'
import { readEditorRecipe } from './editor-recipe'
import { WorkstationConfig } from './gpu'
import { stageObservations } from './perception'
import { ProductionPlan, assertPlanBinding } from './plan'
import { runWorker } from './production'

const Holds = Schema.Struct({
  jobs: Schema.Array(
    Schema.Struct({
      id: Schema.String,
      releaseId: Schema.String,
      state: Schema.String,
      attempt: Schema.Number,
      brief: ReleaseBrief,
    }),
  ),
})
const Attention = Schema.Struct({
  jobId: Schema.String,
  attempt: Schema.Number,
})
const Reconciled = Schema.Struct({
  state: Schema.String,
  attempt: Schema.Number,
  assets: Schema.Array(
    Schema.Struct({ outputId: OutputId, verified: Schema.Boolean }),
  ),
})
const readOptional = async (path: string) =>
  readFile(path, 'utf8').catch(error => {
    if (error.code === 'ENOENT') return null
    throw error
  })
const operation = <A>(run: (signal: AbortSignal) => Promise<A>) =>
  Effect.tryPromise({
    try: run,
    catch: error =>
      error instanceof Error
        ? error
        : new Error('Worker service operation failed.'),
  })

interface InspectedHold {
  id: string
  state: string
  direction?: { state: string }
  observations?: { state: string }
}

export const superviseCycle = async (
  config: WorkerConfig,
  signal: AbortSignal,
  produce: (
    config: WorkerConfig,
    signal: AbortSignal,
  ) => Promise<{ state: string }> = runWorker,
) => {
  const attentionPath = join(config.localState, 'worker-attention.json')
  const attentionText = await readOptional(attentionPath)
  if (attentionText) {
    const attention = Schema.decodeUnknownSync(Attention)(
      JSON.parse(attentionText),
    )
    const state = Schema.decodeUnknownSync(Reconciled)(
      await workerRequest(
        config,
        'GET',
        `/api/worker/jobs/${attention.jobId}`,
        undefined,
        undefined,
        signal,
      ),
    )
    if (
      state.state === 'review' &&
      state.attempt === attention.attempt &&
      state.assets.length === 6 &&
      new Set(state.assets.map(asset => asset.outputId)).size === 6 &&
      state.assets.every(asset => asset.verified)
    )
      await unlink(attentionPath)
    else
      return {
        state: 'needs-reconciliation',
        jobId: attention.jobId,
        resumed: 0,
        held: [],
      }
  }
  const holds = Schema.decodeUnknownSync(Holds)(
    await workerRequest(
      config,
      'GET',
      '/api/worker/holds',
      undefined,
      undefined,
      signal,
    ),
  )
  const inspected = await Effect.runPromise(
    Effect.forEach(
      holds.jobs,
      job =>
        operation<InspectedHold>(async () => {
          if (job.state === 'needs-reconciliation')
            return { id: job.id, state: job.state }
          const text = await readOptional(
            join(config.planRegistry, `${job.releaseId}.json`),
          )
          if (!text) {
            const direction = await stageDirection(config, job, signal).catch(
              error => ({
                state: 'direction-needs-attention',
                reason:
                  error instanceof Error
                    ? error.message.slice(0, 300)
                    : 'Direction preparation failed.',
              }),
            )
            const observations =
              config.audioObservations &&
              direction.state === 'direction-prepared'
                ? await stageObservations(
                    config,
                    Schema.decodeUnknownSync(WorkstationConfig)(
                      JSON.parse(
                        await readFile(config.workstationConfig, 'utf8'),
                      ),
                    ),
                    job,
                    config.audioObservations.attempt,
                    signal,
                  ).catch(error => ({
                    state: 'observations-needs-attention',
                    reason:
                      error instanceof Error
                        ? error.message.slice(0, 300)
                        : 'Observation preparation failed.',
                  }))
                : undefined
            return {
              id: job.id,
              state: job.state,
              direction,
              ...(observations ? { observations } : {}),
            }
          }
          const plan = (() => {
            try {
              const value = Schema.decodeUnknownSync(ProductionPlan, {
                onExcessProperty: 'error',
              })(JSON.parse(text))
              assertPlanBinding(value, job)
              return value
            } catch {
              return null
            }
          })()
          if (!plan || plan.schemaVersion === 1)
            return { id: job.id, state: 'plan-needs-correction' }
          if (!plan.approvedForBulk || !plan.reviewEvidence.trim())
            return { id: job.id, state: 'waiting-for-review' }
          const recipeReady = await readEditorRecipe(plan, job).then(
            () => true,
            () => false,
          )
          if (!recipeReady)
            return { id: job.id, state: 'plan-needs-correction' }
          await workerRequest(
            config,
            'POST',
            `/api/worker/jobs/${job.id}/resume`,
            {
              briefSha256: plan.briefSha256,
              audioSha256: plan.audioSha256,
              reviewEvidence: plan.reviewEvidence,
            },
            undefined,
            signal,
          )
          return { id: job.id, state: 'resumed' }
        }),
      { concurrency: 1 },
    ),
    { signal },
  )
  signal.throwIfAborted()
  const processed = await produce(config, signal)
  return {
    state: processed.state,
    processed,
    resumed: inspected.filter(job => job.state === 'resumed').length,
    held: inspected.filter(job => job.state !== 'resumed'),
  }
}

export const supervise = async (configPath: string, signal: AbortSignal) => {
  const observed = { signature: '' }
  const cycle = operation(async signal => {
    const config = await loadWorkerConfig(configPath)
    await mkdir(config.localState, { recursive: true, mode: 0o700 })
    const status = await superviseCycle(config, signal).catch(error => ({
      state: 'needs-attention',
      resumed: 0,
      held: [],
      reason:
        error instanceof Error
          ? error.message.slice(0, 300)
          : 'Service operation failed.',
    }))
    const record = {
      ...status,
      pid: process.pid,
      observedAt: new Date().toISOString(),
    }
    const target = join(config.localState, 'service-status.json')
    const temporary = `${target}.${crypto.randomUUID()}.tmp`
    await writeFile(temporary, JSON.stringify(record, null, 2), { mode: 0o600 })
    await rename(temporary, target)
    const signature = JSON.stringify(status)
    if (signature !== observed.signature) {
      console.log(JSON.stringify(record))
      observed.signature = signature
    }
  }).pipe(
    Effect.flatMap(() => Effect.sleep('20 seconds')),
    Effect.forever,
  )
  await Effect.runPromise(cycle, { signal })
}
