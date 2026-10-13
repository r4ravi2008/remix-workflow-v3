// @vitest-environment node
import { describe, expect, it } from 'vitest'

import { defaultProfile } from '../src/domain'
import type { ReleaseBrief } from '../src/server/contracts'
import { assertPlanBinding, briefFingerprint } from './plan'

const brief: ReleaseBrief = {
  title: 'పల్ పల్',
  lyrics: 'ప్రతి నిమిషం',
  language: 'Telugu',
  audioName: 'song.wav',
  audioSha256: 'a'.repeat(64),
  audioDuration: 239.68,
  audioBytes: 46018732,
  profile: defaultProfile,
}
const plan = {
  schemaVersion: 1,
  releaseId: 'release-one',
  briefSha256: briefFingerprint(brief),
  audioSha256: brief.audioSha256,
  approvedForBulk: false,
  reviewEvidence: '',
  shots: [],
  resolvePlan: '/private/resolve-plan.json',
} satisfies Parameters<typeof assertPlanBinding>[0]

describe('production plan ownership', () => {
  it('rejects the same song submitted by a different release or with another artist identity', () => {
    expect(() =>
      assertPlanBinding(plan, { releaseId: 'release-one', brief }),
    ).not.toThrow()
    expect(() =>
      assertPlanBinding(plan, { releaseId: 'release-two', brief }),
    ).toThrow('frozen artist brief')
    expect(() =>
      assertPlanBinding(plan, {
        releaseId: 'release-one',
        brief: {
          ...brief,
          profile: {
            ...brief.profile,
            identity: 'A different artist and character',
          },
        },
      }),
    ).toThrow('frozen artist brief')
    expect(() =>
      assertPlanBinding(plan, {
        releaseId: 'release-one',
        brief: {
          ...brief,
          lyrics: 'కొత్త పదాలు',
        },
      }),
    ).toThrow('frozen artist brief')
  })

  it('keeps the fingerprint stable across JSON field ordering', () => {
    const reordered: ReleaseBrief = {
      profile: {
        intensity: brief.profile.intensity,
        palette: brief.profile.palette,
        identity: brief.profile.identity,
        name: brief.profile.name,
      },
      audioBytes: brief.audioBytes,
      audioDuration: brief.audioDuration,
      audioSha256: brief.audioSha256,
      audioName: brief.audioName,
      language: brief.language,
      lyrics: brief.lyrics,
      title: brief.title,
    }
    expect(briefFingerprint(reordered)).toBe(briefFingerprint(brief))
  })
})
