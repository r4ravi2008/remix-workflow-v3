import { Schema } from 'effect'
import { readFile } from 'node:fs/promises'

import { ReleaseBrief } from '../src/domain'
import { WorkerConfig } from './config'
import { finishCloudEditor } from './editor'
import { EditorProductionPlan } from './plan'

const Canary = Schema.Struct({
  config: WorkerConfig,
  job: Schema.Struct({
    id: Schema.String,
    releaseId: Schema.String,
    attempt: Schema.Number,
    lease: Schema.String,
    brief: ReleaseBrief,
  }),
  plan: EditorProductionPlan,
  source: Schema.String,
  collectedShots: Schema.Array(
    Schema.Struct({ id: Schema.String, path: Schema.String }),
  ),
})
const path = process.argv[2]
if (!path) throw new Error('A private local canary input is required.')
const input = Schema.decodeUnknownSync(Canary, { onExcessProperty: 'error' })(
  JSON.parse(await readFile(path, 'utf8')),
)
if (
  !['localhost', '127.0.0.1'].includes(
    new URL(input.config.baseUrl).hostname,
  ) ||
  input.job.brief.title !== 'Production adapter synthetic canary'
)
  throw new Error(
    'This check runs only a synthetic canary against local Workerd.',
  )
if (
  new Set(input.collectedShots.map(shot => shot.id)).size !==
    input.collectedShots.length ||
  input.plan.shots.length !== input.collectedShots.length ||
  input.plan.shots.some(
    shot => !input.collectedShots.some(collected => collected.id === shot.id),
  )
)
  throw new Error('The synthetic collected-shot bindings must match the plan.')
const result = await finishCloudEditor(
  input.config,
  input.job,
  input.plan,
  input.source,
  new Map(input.collectedShots.map(shot => [shot.id, shot.path])),
  AbortSignal.timeout(600000),
  async () => {},
)
process.stdout.write(JSON.stringify(result) + '\n')
