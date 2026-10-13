import { Schema } from 'effect'

import { ArtistProfile, OutputId, ReleaseBrief } from '../domain'

export { ReleaseBrief } from '../domain'
export const Submission = Schema.Struct({
  requestKey: Schema.String,
  brief: ReleaseBrief,
})
export const InviteRequest = Schema.Struct({ tenantName: Schema.String })
export const ExchangeRequest = Schema.Struct({ token: Schema.String })
export const EnrollmentRequest = Schema.Struct({ name: Schema.String })
export const ArtistRequest = Schema.Struct({
  profile: ArtistProfile,
  expectedRevision: Schema.Number,
})
export const ArtistRow = Schema.Struct({
  profile_json: Schema.String,
  revision: Schema.Number,
  updated_at: Schema.Number,
})
export const ProgressRequest = Schema.Struct({
  phase: Schema.String,
  progress: Schema.Number,
  receipt: Schema.Unknown,
})
export const HoldReason = Schema.Literals([
  'waiting-for-direction',
  'waiting-for-review',
  'needs-reconciliation',
])
export type HoldReason = typeof HoldReason.Type
export const HoldRequest = Schema.Struct({
  reason: HoldReason,
  receipt: Schema.Unknown,
})
export const ResumeRequest = Schema.Struct({
  briefSha256: Schema.String,
  audioSha256: Schema.String,
  reviewEvidence: Schema.String,
})
export const OutputUpload = Schema.Struct({
  outputId: OutputId,
  bytes: Schema.Number,
  sha256: Schema.String,
  contentType: Schema.String,
})
export const Measurement = Schema.Struct({
  width: Schema.Number,
  height: Schema.Number,
  duration: Schema.Number,
  decoded: Schema.Boolean,
  sha256: Schema.String,
  storageSha256: Schema.String,
  composition: Schema.String,
})
export type Measurement = typeof Measurement.Type
export const CompleteRequest = Schema.Struct({
  outputs: Schema.Array(
    Schema.Struct({ assetId: Schema.String, measurement: Measurement }),
  ),
  receipt: Schema.Unknown,
})
export const ReleaseRow = Schema.Struct({
  id: Schema.String,
  tenant_id: Schema.String,
  request_key: Schema.String,
  brief_json: Schema.String,
  state: Schema.String,
  created_at: Schema.Number,
})
export type ReleaseRow = typeof ReleaseRow.Type
export const JobRow = Schema.Struct({
  id: Schema.String,
  release_id: Schema.String,
  state: Schema.String,
  device_id: Schema.NullOr(Schema.String),
  lease_hash: Schema.NullOr(Schema.String),
  lease_until: Schema.NullOr(Schema.Number),
  attempt: Schema.Number,
  phase: Schema.String,
  progress: Schema.Number,
  receipt_json: Schema.NullOr(Schema.String),
  error: Schema.NullOr(Schema.String),
  created_at: Schema.Number,
  updated_at: Schema.Number,
})
export type JobRow = typeof JobRow.Type
export const AssetRow = Schema.Struct({
  id: Schema.String,
  release_id: Schema.String,
  job_id: Schema.NullOr(Schema.String),
  attempt: Schema.NullOr(Schema.Number),
  kind: Schema.String,
  output_id: Schema.NullOr(OutputId),
  object_key: Schema.String,
  bytes: Schema.Number,
  sha256: Schema.String,
  content_type: Schema.String,
  state: Schema.String,
  upload_id: Schema.NullOr(Schema.String),
  verified: Schema.Number,
  measurement_json: Schema.NullOr(Schema.String),
  created_at: Schema.Number,
})
export type AssetRow = typeof AssetRow.Type
export const PartRow = Schema.Struct({
  part_number: Schema.Number,
  etag: Schema.String,
  bytes: Schema.Number,
  sha256: Schema.String,
})
export const TenantRow = Schema.Struct({
  id: Schema.String,
  name: Schema.String,
})
export const DeviceRow = Schema.Struct({
  id: Schema.String,
  name: Schema.String,
})
export const sha256Pattern = /^[a-f0-9]{64}$/
export const partBytes = 8 * 1024 * 1024
export const maxAudioBytes = 100 * 1024 * 1024
export const maxOutputBytes = 2 * 1024 * 1024 * 1024

export class ApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
  ) {
    super(message)
  }
}
export const requireCondition: (
  condition: unknown,
  status: number,
  message: string,
) => asserts condition = (condition, status, message) => {
  if (!condition) throw new ApiError(status, message)
}
export const validateBrief = (brief: ReleaseBrief) => {
  requireCondition(
    brief.title.trim().length > 0 && brief.title.length <= 200,
    400,
    'Add a song title of up to 200 characters.',
  )
  requireCondition(
    brief.lyrics.trim().length > 0 && brief.lyrics.length <= 30000,
    400,
    'Add the exact song lyrics.',
  )
  const scripts: Record<string, RegExp> = {
    Telugu: /[\u0c00-\u0c7f]/u,
    Hindi: /[\u0900-\u097f]/u,
    Tamil: /[\u0b80-\u0bff]/u,
  }
  const script = scripts[brief.language]
  requireCondition(
    script && script.test(brief.lyrics),
    400,
    'Use Telugu, Hindi or Tamil lyrics in their native script.',
  )
  requireCondition(
    sha256Pattern.test(brief.audioSha256),
    400,
    'Invalid audio SHA-256.',
  )
  requireCondition(
    Number.isInteger(brief.audioBytes) &&
      brief.audioBytes > 0 &&
      brief.audioBytes <= maxAudioBytes,
    400,
    'Audio must be between 1 byte and 100 MB.',
  )
  requireCondition(
    Number.isFinite(brief.audioDuration) &&
      brief.audioDuration > 0 &&
      brief.audioDuration <= 900,
    400,
    'Songs must be between 0 and 15 minutes.',
  )
  requireCondition(
    brief.audioName.length <= 250 &&
      brief.profile.identity.length <= 5000 &&
      brief.profile.name.length <= 200,
    400,
    'The artist brief is too long.',
  )
}
export const validateMeasurement = (
  id: OutputId,
  m: Measurement,
  duration: number,
) => {
  requireCondition(
    m.decoded &&
      sha256Pattern.test(m.sha256) &&
      m.composition.length > 0 &&
      m.composition.length <= 2000,
    409,
    'Each output needs a decode, hash and composition receipt.',
  )
  requireCondition(
    m.storageSha256 === m.sha256,
    409,
    'Read back the stored output and verify its full hash.',
  )
  if (id === 'film')
    requireCondition(
      m.width === 1920 &&
        m.height === 1080 &&
        Math.abs(m.duration - duration) <= 1 / 24 + 0.005,
      409,
      'The film must cover the full song in 1080p.',
    )
  else if (id.startsWith('short-'))
    requireCondition(
      m.width === 1080 &&
        m.height === 1920 &&
        m.duration > 0 &&
        m.duration <= 30.05,
      409,
      'Promos must be composed vertically and last up to 30 seconds.',
    )
  else if (id === 'thumbnail')
    requireCondition(
      m.width === 1920 && m.height === 1080 && m.duration === 0,
      409,
      'The thumbnail must be 1920 × 1080.',
    )
  else
    requireCondition(
      m.width === 1920 && m.height === 1920 && m.duration === 0,
      409,
      'Artwork must be 1920 × 1920.',
    )
}
