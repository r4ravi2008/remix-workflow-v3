import { Context, Effect, Ref, Schema } from 'effect'
import { mkdir, readFile, writeFile } from 'node:fs/promises'
import { join } from 'node:path'

import { OutputId } from '../src/domain'
import { ReleaseBrief } from '../src/server/contracts'
import type { WorkerConfig } from './config'
import { workerHeaders, workerRequest } from './connection'
import { stageDirection } from './direction'
import { finishCloudEditor } from './editor'
import { readEditorRecipe } from './editor-recipe'
import { GPU, WorkstationConfig, tailscaleGPU } from './gpu'
import { withLease } from './lease'
import { ProductionPlan, assertPlanBinding, briefFingerprint } from './plan'
import { downloadVerified, fileReceipt } from './transfer'

const ClaimedJob = Schema.Struct({
  id: Schema.String,
  releaseId: Schema.String,
  attempt: Schema.Number,
  lease: Schema.String,
  expiresAt: Schema.Number,
  brief: ReleaseBrief,
  audioAssetId: Schema.String,
  contract: Schema.Literal('release-kit-v1'),
})
type ClaimedJob = typeof ClaimedJob.Type
export class Dispatch extends Context.Service<
  Dispatch,
  {
    claim: Effect.Effect<ClaimedJob | null, Error>
    heartbeat: (
      job: ClaimedJob,
      phase: string,
      progress: number,
      receipt: unknown,
    ) => Effect.Effect<void, Error>
    downloadSource: (
      job: ClaimedJob,
      destination: string,
    ) => Effect.Effect<void, Error>
  }
>()('release-kit/Dispatch') {}
const effect = <A>(operation: (signal: AbortSignal) => Promise<A>) =>
  Effect.tryPromise({
    try: operation,
    catch: error =>
      new Error(
        error instanceof Error ? error.message : 'Worker operation failed',
      ),
  })
export const runWorker = async (
  config: WorkerConfig,
  signal: AbortSignal = new AbortController().signal,
) => {
  const workstation = Schema.decodeUnknownSync(WorkstationConfig)(
    JSON.parse(await readFile(config.workstationConfig, 'utf8')),
  )
  await mkdir(config.localState, { recursive: true, mode: 0o700 })
  const headers = (job?: ClaimedJob) => workerHeaders(config, job)
  const request = async (
    path: string,
    body: unknown,
    job?: ClaimedJob,
    signal: AbortSignal = new AbortController().signal,
  ) => {
    return workerRequest(config, 'POST', path, body, job, signal)
  }
  const owned: { job: ClaimedJob | null } = { job: null }
  const dispatch: typeof Dispatch.Service = {
    claim: effect(async signal => {
      const job = Schema.decodeUnknownSync(
        Schema.Struct({ job: Schema.NullOr(ClaimedJob) }),
      )(await request('/api/worker/claim', {}, undefined, signal)).job
      owned.job = job
      return job
    }),
    heartbeat: (job, phase, progress, receipt) =>
      effect(async signal => {
        await request(
          `/api/worker/jobs/${job.id}/heartbeat`,
          { phase, progress, receipt },
          job,
          signal,
        )
      }),
    downloadSource: (job, destination) =>
      effect(async signal => {
        const cached = await fileReceipt(destination, signal).catch(error => {
          if (error.code === 'ENOENT') return null
          throw error
        })
        if (cached) {
          if (
            cached.bytes !== job.brief.audioBytes ||
            cached.sha256 !== job.brief.audioSha256
          )
            throw new Error(
              'The cached source differs from the canonical song; preserve and reconcile it.',
            )
          return
        }
        const response = await fetch(
          new URL(`/api/worker/assets/${job.audioAssetId}`, config.baseUrl),
          { headers: headers(job), signal },
        )
        if (!response.ok)
          throw new Error(
            'The canonical source could not be downloaded under the job lease.',
          )
        await downloadVerified(
          response,
          destination,
          {
            bytes: job.brief.audioBytes,
            sha256: job.brief.audioSha256,
          },
          signal,
        )
      }),
  }
  const produce = Effect.gen(function* () {
    const cloud = yield* Dispatch
    const gpu = yield* GPU
    const job = yield* cloud.claim
    if (!job) return { state: 'idle' }
    const initialProgress: {
      phase: string
      progress: number
      receipt: unknown
    } = {
      phase: 'Verifying the canonical song',
      progress: 0.01,
      receipt: { contract: job.contract },
    }
    const progress = yield* Ref.make(initialProgress)
    const report = (phase: string, value: number, receipt: unknown) =>
      Ref.set(progress, { phase, progress: value, receipt }).pipe(
        Effect.flatMap(() => cloud.heartbeat(job, phase, value, receipt)),
      )
    const work = Effect.gen(function* () {
      const directory = join(config.localState, job.id)
      yield* effect(() => mkdir(directory, { recursive: true, mode: 0o700 }))
      yield* effect(() =>
        writeFile(
          join(directory, `claim-${job.attempt}.json`),
          JSON.stringify(job, null, 2),
          { mode: 0o600, flag: 'wx' },
        ),
      )
      yield* report('Verifying the canonical song', 0.01, {
        contract: job.contract,
      })
      const source = join(directory, 'canonical-audio')
      yield* cloud.downloadSource(job, source)
      const sourceReceipt = {
        jobId: job.id,
        releaseId: job.releaseId,
        sourceSha256: job.brief.audioSha256,
        briefSha256: briefFingerprint(job.brief),
        attempt: job.attempt,
        bytes: job.brief.audioBytes,
        gpuProvider: 'tailscale-herdr',
        finishing: 'cloudflare-editor',
        scope: 'source and dispatch verified; full kit pending',
      }
      yield* effect(() =>
        writeFile(
          join(directory, 'source-receipt.json'),
          JSON.stringify(sourceReceipt, null, 2),
        ),
      )
      const planPath = join(config.planRegistry, `${job.releaseId}.json`)
      const planText = yield* effect(() =>
        readFile(planPath, 'utf8').catch(error => {
          if (error.code === 'ENOENT') return null
          throw error
        }),
      )
      if (!planText) {
        yield* report(
          'Preparing the song analysis and director handoff',
          0.03,
          sourceReceipt,
        )
        const direction = yield* effect(signal =>
          stageDirection(config, job, signal),
        )
        const prepared = {
          state: direction.state,
          briefSha256: direction.briefSha256,
          analysisSha256: direction.analysisSha256,
          frameCount: direction.frameCount,
        }
        yield* report(
          'Song analysis prepared; waiting for musical direction and pilot review',
          0.03,
          { ...sourceReceipt, direction: prepared },
        )
        return {
          state: 'waiting-for-direction',
          ...sourceReceipt,
          direction: prepared,
        }
      }
      const plan = Schema.decodeUnknownSync(ProductionPlan, {
        onExcessProperty: 'error',
      })(JSON.parse(planText))
      assertPlanBinding(plan, job)
      if (plan.schemaVersion === 1)
        throw new Error(
          'Migrate this legacy Resolve plan to a Cloudflare editor project or generated-media recipe before production.',
        )
      if (!plan.approvedForBulk || !plan.reviewEvidence) {
        yield* report(
          'Waiting for the motion pilot review',
          0.03,
          sourceReceipt,
        )
        return { state: 'waiting-for-review', ...sourceReceipt }
      }
      yield* effect(() => readEditorRecipe(plan, job))
      if (plan.shots.length) {
        const probe = yield* gpu.probe
        yield* report('Connected to the GPU workstation', 0.04, { gpu: probe })
      }
      const results = yield* Effect.forEach(
        plan.shots,
        (shot, index) =>
          Effect.gen(function* () {
            yield* report(
              `Generating scene ${index + 1} of ${plan.shots.length}`,
              0.05 + (index / Math.max(plan.shots.length, 1)) * 0.6,
              { attempt: shot.id },
            )
            const current = yield* gpu.ensure(shot)
            const State = Schema.Struct({ state: Schema.String })
            const wait: Effect.Effect<void, Error> = Effect.suspend(() =>
              gpu.status(shot).pipe(
                Effect.flatMap(status => {
                  const value = Schema.decodeUnknownSync(State)(status)
                  if (value.state === 'generated-unreviewed') return Effect.void
                  if (
                    ['failed', 'unknown-do-not-resubmit'].includes(value.state)
                  )
                    return Effect.fail(
                      new Error(
                        `Scene ${shot.id} needs reconciliation; no new inference was submitted.`,
                      ),
                    )
                  return Effect.sleep('20 seconds').pipe(
                    Effect.flatMap(() =>
                      report(
                        `Generating scene ${index + 1} of ${plan.shots.length}`,
                        0.05 + (index / Math.max(plan.shots.length, 1)) * 0.6,
                        { attempt: shot.id, status },
                      ),
                    ),
                    Effect.flatMap(() => wait),
                  )
                }),
              ),
            )
            yield* wait
            const original = yield* gpu.collect(
              shot,
              join(directory, `${shot.id}.mp4`),
            )
            return {
              id: shot.id,
              path: join(directory, `${shot.id}.mp4`),
              current,
              original,
            }
          }),
        { concurrency: 1 },
      )
      yield* report('Preparing the Cloudflare editor project', 0.7, {
        scenes: results.length,
      })
      return yield* effect(signal =>
        finishCloudEditor(
          config,
          job,
          plan,
          source,
          new Map(results.map(scene => [scene.id, scene.path])),
          signal,
          (phase, value, receipt) =>
            Effect.runPromise(report(phase, value, receipt), { signal }),
        ),
      )
    })
    const outcome = yield* withLease(
      work,
      Ref.get(progress).pipe(
        Effect.flatMap(value =>
          cloud.heartbeat(job, value.phase, value.progress, value.receipt),
        ),
      ),
    )
    if (outcome.state === 'review') return outcome
    yield* effect(signal =>
      request(
        `/api/worker/jobs/${job.id}/hold`,
        { reason: outcome.state, receipt: outcome },
        job,
        signal,
      ),
    )
    return outcome
  }).pipe(
    Effect.provideService(Dispatch, dispatch),
    Effect.provideService(GPU, tailscaleGPU(workstation)),
  )
  const receipt = await Effect.runPromise(produce, { signal }).catch(
    async error => {
      if (!owned.job) throw error
      const job = owned.job
      const attention = {
        state: 'needs-reconciliation',
        jobId: job.id,
        releaseId: job.releaseId,
        attempt: job.attempt,
        reason:
          'The production attempt was interrupted; preserve and reconcile its provider and renderer receipts.',
      }
      const recorded = await request(
        `/api/worker/jobs/${job.id}/hold`,
        {
          reason: 'needs-reconciliation',
          receipt: attention,
        },
        job,
      )
        .then(() => true)
        .catch(() => false)
      if (recorded) return attention
      const status = await workerRequest(
        config,
        'GET',
        `/api/worker/jobs/${job.id}`,
      )
        .then(value =>
          Schema.decodeUnknownSync(
            Schema.Struct({
              state: Schema.String,
              attempt: Schema.Number,
              assets: Schema.Array(
                Schema.Struct({ outputId: OutputId, verified: Schema.Boolean }),
              ),
            }),
          )(value),
        )
        .catch(() => null)
      if (
        status?.state === 'review' &&
        status.assets.length === 6 &&
        new Set(status.assets.map(asset => asset.outputId)).size === 6 &&
        status.assets.every(asset => asset.verified)
      )
        return {
          state: 'review',
          jobId: job.id,
          releaseId: job.releaseId,
          outputCount: 6,
          humanAccepted: false,
          completionReconciled: true,
        }
      if (
        status?.attempt === job.attempt &&
        [
          'waiting-for-direction',
          'waiting-for-review',
          'needs-reconciliation',
        ].includes(status.state)
      )
        return { ...attention, state: status.state }
      await writeFile(
        join(config.localState, 'worker-attention.json'),
        JSON.stringify(attention, null, 2),
        { mode: 0o600 },
      )
      throw new Error(
        'Job ownership could not be reconciled; dispatch is held by worker-attention.json.',
      )
    },
  )
  await writeFile(
    join(config.localState, 'last-run.json'),
    JSON.stringify(receipt, null, 2),
    { mode: 0o600 },
  )
  return receipt
}
