import { Schema } from 'effect'

const Range = {
  startFrame: Schema.Number,
  endFrame: Schema.Number,
  expected: Schema.Boolean,
  context: Schema.Literals([
    'declared-image-hold',
    'planned-fade',
    'no-declared-exemption',
  ]),
}
const Change = Schema.Struct({
  atFrame: Schema.Number,
  meanAbsoluteDelta: Schema.Number,
  maximumPixelDelta: Schema.Number,
  plannedCut: Schema.Boolean,
})
export const FrameDiagnostics = Schema.Struct({
  schemaVersion: Schema.Literal(1),
  method: Schema.Literal('all-frame-reduced-rgb-luma/v1'),
  width: Schema.Literal(32),
  height: Schema.Literal(18),
  timebaseFps: Schema.Literal(24),
  sampledFrames: Schema.Number,
  completeFrameCoverage: Schema.Literal(true),
  motionExpected: Schema.Boolean,
  thresholds: Schema.Struct({
    blackMeanLuma: Schema.Number,
    blackPeakLuma: Schema.Number,
    flatLumaSpread: Schema.Number,
    staticMeanAbsoluteDelta: Schema.Number,
    staticMinimumFrames: Schema.Number,
    abruptMeanAbsoluteDelta: Schema.Number,
  }),
  counts: Schema.Struct({
    nearBlackFrames: Schema.Number,
    flatFrames: Schema.Number,
    nearStaticFrames: Schema.Number,
    nearBlackRanges: Schema.Number,
    flatRanges: Schema.Number,
    nearStaticRanges: Schema.Number,
    abruptChanges: Schema.Number,
    unplannedFindingRanges: Schema.Number,
  }),
  omittedFindings: Schema.Struct({
    nearBlackRanges: Schema.Number,
    flatRanges: Schema.Number,
    nearStaticRanges: Schema.Number,
    abruptChanges: Schema.Number,
  }),
  nearBlackRanges: Schema.Array(
    Schema.Struct({
      ...Range,
      maximumMeanLuma: Schema.Number,
      maximumPeakLuma: Schema.Number,
    }),
  ),
  flatRanges: Schema.Array(
    Schema.Struct({ ...Range, maximumLumaSpread: Schema.Number }),
  ),
  nearStaticRanges: Schema.Array(
    Schema.Struct({ ...Range, maximumMeanAbsoluteDelta: Schema.Number }),
  ),
  abruptChanges: Schema.Array(Change),
  joinMeasurements: Schema.Array(Change),
  reviewSuggested: Schema.Boolean,
  semanticReviewed: Schema.Literal(false),
})
export const NativeArtifact = Schema.Struct({
  id: Schema.String,
  sha256: Schema.String,
  bytes: Schema.Number,
  width: Schema.Number,
  height: Schema.Number,
  frames: Schema.Number,
  duration: Schema.Number,
  fps: Schema.Number,
  codec: Schema.String,
  pixelFormat: Schema.String,
  audio: Schema.Unknown,
  frameDiagnostics: Schema.optional(FrameDiagnostics),
  completeDecode: Schema.Literal(true),
  motionReviewed: Schema.Literal(false),
  heard: Schema.Literal(false),
  creativelyAccepted: Schema.Literal(false),
})
