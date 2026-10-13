import { Schema } from 'effect'
import { createHash } from 'node:crypto'

import { Id } from '../editor/project'
import { canonicalJson } from '../src/canonical'
import type { ReleaseBrief } from '../src/server/contracts'

const GPUAttempt = Schema.Struct({
  id: Schema.String,
  ledger: Schema.String,
  workflow: Schema.String,
  inputs: Schema.String,
  bindings: Schema.String,
  inputRoot: Schema.String,
  outputRoot: Schema.String,
  archive: Schema.String,
  outputNode: Schema.String,
})
const LegacyProductionPlan = Schema.Struct({
  schemaVersion: Schema.Literal(1),
  releaseId: Schema.String,
  briefSha256: Schema.String,
  audioSha256: Schema.String,
  approvedForBulk: Schema.Boolean,
  reviewEvidence: Schema.String,
  shots: Schema.Array(GPUAttempt),
  resolvePlan: Schema.String,
})
export const AssetInput = Schema.Union([
  Schema.Struct({ assetId: Id, kind: Schema.Literal('canonical-audio') }),
  Schema.Struct({
    assetId: Id,
    kind: Schema.Literal('shot'),
    shotId: Schema.String,
  }),
  Schema.Struct({
    assetId: Id,
    kind: Schema.Literal('file'),
    path: Schema.String,
  }),
])
export type AssetInput = typeof AssetInput.Type
export const CloudProductionPlan = Schema.Struct({
  schemaVersion: Schema.Literal(2),
  releaseId: Schema.String,
  briefSha256: Schema.String,
  audioSha256: Schema.String,
  approvedForBulk: Schema.Boolean,
  reviewEvidence: Schema.String,
  shots: Schema.Array(GPUAttempt),
  editor: Schema.Struct({
    projectId: Id,
    expectedRevision: Schema.Int.check(
      Schema.isBetween({ minimum: 0, maximum: 1000000 }),
    ),
    projectPath: Schema.String,
    assets: Schema.Array(AssetInput),
  }),
})
export const GeneratedProductionPlan = Schema.Struct({
  schemaVersion: Schema.Literal(3),
  releaseId: Schema.String,
  briefSha256: Schema.String,
  audioSha256: Schema.String,
  approvedForBulk: Schema.Boolean,
  reviewEvidence: Schema.String,
  shots: Schema.Array(GPUAttempt),
  editor: Schema.Struct({
    projectId: Id,
    expectedRevision: Schema.Int.check(
      Schema.isBetween({ minimum: 0, maximum: 1000000 }),
    ),
    recipePath: Schema.String,
  }),
})
export const EditorProductionPlan = Schema.Union([
  CloudProductionPlan,
  GeneratedProductionPlan,
])
export type EditorProductionPlan = typeof EditorProductionPlan.Type
export const ProductionPlan = Schema.Union([
  LegacyProductionPlan,
  CloudProductionPlan,
  GeneratedProductionPlan,
])

export const briefFingerprint = (brief: ReleaseBrief) =>
  createHash('sha256').update(canonicalJson(brief)).digest('hex')

export const assertPlanBinding = (
  plan: typeof ProductionPlan.Type,
  job: { releaseId: string; brief: ReleaseBrief },
) => {
  if (
    plan.releaseId !== job.releaseId ||
    plan.briefSha256 !== briefFingerprint(job.brief) ||
    plan.audioSha256 !== job.brief.audioSha256
  )
    throw new Error(
      'The production plan does not belong to this release and its frozen artist brief.',
    )
}
