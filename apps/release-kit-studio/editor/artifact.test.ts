import { Schema } from 'effect'
import { describe, expect, it } from 'vitest'

import { FrameDiagnostics, NativeArtifact } from './artifact'
import { tools } from './catalog'

const diagnostics = {
  schemaVersion: 1,
  method: 'all-frame-reduced-rgb-luma/v1',
  width: 32,
  height: 18,
  timebaseFps: 24,
  sampledFrames: 48,
  completeFrameCoverage: true,
  motionExpected: true,
  thresholds: {
    blackMeanLuma: 3,
    blackPeakLuma: 6,
    flatLumaSpread: 2,
    staticMeanAbsoluteDelta: 0.2,
    staticMinimumFrames: 12,
    abruptMeanAbsoluteDelta: 60,
  },
  counts: {
    nearBlackFrames: 0,
    flatFrames: 0,
    nearStaticFrames: 48,
    nearBlackRanges: 0,
    flatRanges: 0,
    nearStaticRanges: 1,
    abruptChanges: 0,
    unplannedFindingRanges: 1,
  },
  omittedFindings: {
    nearBlackRanges: 0,
    flatRanges: 0,
    nearStaticRanges: 0,
    abruptChanges: 0,
  },
  nearBlackRanges: [],
  flatRanges: [],
  nearStaticRanges: [
    {
      startFrame: 0,
      endFrame: 48,
      expected: false,
      context: 'no-declared-exemption',
      maximumMeanAbsoluteDelta: 0,
    },
  ],
  abruptChanges: [],
  joinMeasurements: [],
  reviewSuggested: true,
  semanticReviewed: false,
}

describe('artifact measurement discovery', () => {
  it('preserves measured findings without converting them into motion or creative review', () => {
    const output = Schema.decodeUnknownSync(NativeArtifact)({
      id: 'film',
      sha256: 'a'.repeat(64),
      bytes: 4000,
      width: 1920,
      height: 1080,
      frames: 48,
      duration: 2,
      fps: 24,
      codec: 'h264',
      pixelFormat: 'yuv420p',
      audio: {},
      completeDecode: true,
      motionReviewed: false,
      heard: false,
      creativelyAccepted: false,
      frameDiagnostics: diagnostics,
    })
    expect(output.frameDiagnostics?.nearStaticRanges[0]?.endFrame).toBe(48)
    expect(output.motionReviewed).toBe(false)
    expect(() =>
      Schema.decodeUnknownSync(FrameDiagnostics)({
        ...diagnostics,
        semanticReviewed: true,
      }),
    ).toThrow()
    expect(() =>
      Schema.decodeUnknownSync(FrameDiagnostics)({
        ...diagnostics,
        completeFrameCoverage: false,
      }),
    ).toThrow()
  })

  it('exposes the diagnostic output schema to agents', () => {
    const tool = tools().find(row => row.name === 'artifact.verify')
    expect(tool).toHaveProperty('output')
    expect(JSON.stringify(tool)).toContain('frameDiagnostics')
    expect(JSON.stringify(tool)).toContain('semanticReviewed')
  })
})
