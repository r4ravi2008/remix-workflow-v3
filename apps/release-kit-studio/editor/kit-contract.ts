import { Schema } from 'effect'

const Hash = Schema.String.check(Schema.isPattern(/^[a-f0-9]{64}$/))
const Id = Schema.String.check(Schema.isPattern(/^[a-zA-Z0-9_-]{1,80}$/))
export const kitNames = [
  'film.mp4',
  'short-1.mp4',
  'short-2.mp4',
  'short-3.mp4',
  'thumbnail.jpg',
  'artwork.jpg',
  'project.json',
  'manifest.json',
] as const
export const KitDescriptor = Schema.Struct({
  jobId: Id,
  releaseId: Id,
  projectId: Id,
  revision: Schema.Int,
  bytes: Schema.Int.check(
    Schema.isBetween({ minimum: 1, maximum: 12885000000 }),
  ),
  manifestSha256: Hash,
  entries: Schema.Array(
    Schema.Struct({
      name: Schema.Literals(kitNames),
      bytes: Schema.Int.check(
        Schema.isBetween({ minimum: 1, maximum: 2147483648 }),
      ),
      sha256: Hash,
    }),
  ).check(Schema.isMinLength(8), Schema.isMaxLength(8)),
  downloadPath: Schema.String,
})
export type KitDescriptor = typeof KitDescriptor.Type
