import { Schema, pipe } from 'effect'
import * as Route from 'foldkit/route'

import { OutputId, ReleaseBrief, outputs } from './domain'

const Routes = Route.defineRouteUnion({
  Asset: { id: Schema.String },
  Archive: { id: Schema.String },
})
export const assetUrl = pipe(
  Route.literal('api'),
  Route.slash(Route.literal('assets')),
  Route.slash(Route.string('id')),
  Route.mapTo(Routes.Asset),
)
export const archiveUrl = pipe(
  Route.literal('api'),
  Route.slash(Route.literal('releases')),
  Route.slash(Route.string('id')),
  Route.slash(Route.literal('archive')),
  Route.mapTo(Routes.Archive),
)

export const Tenant = Schema.Struct({ id: Schema.String, name: Schema.String })
export const CloudSummary = Schema.Struct({
  id: Schema.String,
  title: Schema.String,
  state: Schema.String,
  createdAt: Schema.Number,
})
export const CloudAsset = Schema.Struct({
  id: Schema.String,
  outputId: OutputId,
  bytes: Schema.Number,
  sha256: Schema.String,
  contentType: Schema.String,
  state: Schema.String,
  verified: Schema.Boolean,
  measurement: Schema.Unknown,
})
export const CloudStatus = Schema.Struct({
  id: Schema.String,
  state: Schema.String,
  brief: ReleaseBrief,
  job: Schema.NullOr(
    Schema.Struct({
      id: Schema.String,
      state: Schema.String,
      phase: Schema.String,
      progress: Schema.Number,
      attempt: Schema.Number,
      error: Schema.NullOr(Schema.String),
    }),
  ),
  assets: Schema.Array(CloudAsset),
  archiveAvailable: Schema.optionalKey(Schema.Boolean),
})
export const canDownloadKit = (status: typeof CloudStatus.Type) =>
  status.archiveAvailable === true &&
  status.state === 'review' &&
  status.job?.state === 'review' &&
  status.assets.length === 6 &&
  outputs.every(
    output =>
      status.assets.filter(
        asset =>
          asset.outputId === output.id &&
          asset.verified &&
          asset.state === 'ready',
      ).length === 1,
  )
export class CloudRequestError extends Error {
  constructor(
    readonly status: number,
    message: string,
  ) {
    super(message)
  }
}
export const cloudRequest = async <S extends Schema.ConstraintDecoder<unknown>>(
  path: string,
  schema: S,
  init?: RequestInit,
): Promise<S['Type']> => {
  const response = await fetch(path, { ...init, credentials: 'same-origin' })
  const body: unknown = await response.json()
  if (!response.ok) {
    const parsed = Schema.decodeUnknownSync(
      Schema.Struct({ error: Schema.String }),
    )(body)
    throw new CloudRequestError(response.status, parsed.error)
  }
  return Schema.decodeUnknownSync(schema)(body)
}
export const jsonPost = (value: unknown): RequestInit => ({
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(value),
})
