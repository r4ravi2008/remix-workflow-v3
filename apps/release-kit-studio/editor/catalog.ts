import { Schema } from 'effect'

import { FrameDiagnostics, NativeArtifact } from './artifact'
import { jsonSchema } from './json-schema'
import { Preview, PreviewBundle } from './preview'
import { Asset, Edit, Project } from './project'

const Id = Schema.String.check(Schema.isPattern(/^[a-zA-Z0-9_-]{1,80}$/))
const Revision = Schema.Int.check(
  Schema.isBetween({ minimum: 0, maximum: 1000000 }),
)
export const Commit = Schema.Struct({
  projectId: Id,
  expectedRevision: Revision,
  intentId: Id,
  project: Project,
})
export const Inspect = Schema.Struct({
  projectId: Id,
  revision: Schema.NullOr(Revision),
})
export const Apply = Schema.Struct({
  projectId: Id,
  expectedRevision: Revision,
  intentId: Id,
  edits: Schema.Array(Edit).check(
    Schema.isMinLength(1),
    Schema.isMaxLength(500),
  ),
})
export const Render = Schema.Struct({
  projectId: Id,
  revision: Revision,
  intentId: Id,
  mode: Schema.Literals(['diagnostic', 'kit']),
  outputId: Schema.NullOr(Schema.String),
})
export const Job = Schema.Struct({ jobId: Id })
export const Media = Schema.Struct({ assetId: Id })
export const Verify = Schema.Struct({ jobId: Id, outputId: Schema.String })
export const Review = Schema.Struct({
  jobId: Id,
  outputId: Schema.String,
  sha256: Schema.String,
  kind: Schema.Literals([
    'frame-inspected',
    'motion-reviewed',
    'heard',
    'creatively-accepted',
  ]),
  startFrame: Schema.Int,
  endFrame: Schema.Int,
  method: Schema.String,
  notes: Schema.String,
})
export { default as features } from './feature-ledger.json'

export const tools = () => [
  {
    name: 'media.register',
    featureId: 'F02',
    input: jsonSchema(Asset),
  },
  {
    name: 'media.inspect',
    featureId: 'F02',
    input: jsonSchema(Media),
  },
  {
    name: 'project.commit',
    featureId: 'F01',
    input: jsonSchema(Commit),
  },
  {
    name: 'project.inspect',
    featureId: 'F01',
    input: jsonSchema(Inspect),
  },
  {
    name: 'project.history',
    featureId: 'F01',
    input: jsonSchema(Inspect),
  },
  {
    name: 'project.edit',
    featureId: 'F03',
    input: jsonSchema(Apply),
  },
  {
    name: 'project.validate',
    featureId: 'F11',
    input: jsonSchema(Project),
  },
  {
    name: 'render.start',
    featureId: 'F09',
    input: jsonSchema(Render),
  },
  {
    name: 'render.status',
    featureId: 'F09',
    input: jsonSchema(Job),
  },
  {
    name: 'render.cancel',
    featureId: 'F09',
    input: jsonSchema(Job),
  },
  {
    name: 'render.reconcile',
    featureId: 'F09',
    input: jsonSchema(Job),
  },
  {
    name: 'kit.locate',
    featureId: 'F11',
    input: jsonSchema(Job),
  },
  {
    name: 'artifact.locate',
    featureId: 'F10',
    input: jsonSchema(Verify),
  },
  {
    name: 'artifact.verify',
    featureId: 'F10',
    input: jsonSchema(Verify),
    output: jsonSchema(
      Schema.Struct({
        ...NativeArtifact.fields,
        frameDiagnostics: FrameDiagnostics,
      }),
    ),
  },
  {
    name: 'artifact.review',
    featureId: 'F10',
    input: jsonSchema(Review),
  },
  {
    name: 'artifact.preview',
    featureId: 'F10',
    input: jsonSchema(Preview),
    output: jsonSchema(
      Schema.Struct({ bundle: PreviewBundle, reused: Schema.Boolean }),
    ),
  },
]
