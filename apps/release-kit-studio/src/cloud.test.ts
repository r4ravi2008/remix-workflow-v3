import { Effect, Option, Schema } from 'effect'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { CloudStatus, archiveUrl, canDownloadKit } from './cloud'
import { outputs } from './domain'
import { QueueRelease, SaveCloudArtist, initialModel } from './main'

afterEach(() => vi.unstubAllGlobals())

describe('cloud command failures', () => {
  it('enables a kit download only for six distinct verified outputs from the ready editor release', () => {
    const status = Schema.decodeUnknownSync(CloudStatus)({
      id: 'release-one',
      state: 'review',
      archiveAvailable: true,
      brief: {
        title: 'Test',
        lyrics: 'ప్రతి నిమిషం',
        language: 'Telugu',
        audioName: 'song.wav',
        audioSha256: 'a'.repeat(64),
        audioBytes: 100,
        audioDuration: 2,
        profile: initialModel.profile,
      },
      job: {
        id: 'job-one',
        state: 'review',
        phase: 'verified',
        progress: 1,
        attempt: 1,
        error: null,
      },
      assets: outputs.map(output => ({
        id: output.id,
        outputId: output.id,
        bytes: 10,
        sha256: 'b'.repeat(64),
        contentType: 'video/mp4',
        state: 'ready',
        verified: true,
        measurement: {},
      })),
    })
    expect(canDownloadKit(status)).toBe(true)
    expect(archiveUrl({ id: status.id })).toBe(
      '/api/releases/release-one/archive',
    )
    expect(canDownloadKit({ ...status, archiveAvailable: false })).toBe(false)
    expect(canDownloadKit({ ...status, state: 'running' })).toBe(false)
    expect(
      canDownloadKit({ ...status, assets: status.assets.slice(0, 5) }),
    ).toBe(false)
    expect(
      canDownloadKit({
        ...status,
        assets: [...status.assets.slice(0, 5), status.assets[0]!],
      }),
    ).toBe(false)
    expect(
      canDownloadKit({
        ...status,
        assets: status.assets.map(asset => ({ ...asset, verified: false })),
      }),
    ).toBe(false)
  })
  it('preserves a server revision conflict through the Effect error wrapper', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () =>
        Response.json(
          { error: 'Another tab changed this identity.' },
          { status: 409 },
        ),
      ),
    )
    const result = await Effect.runPromise(
      SaveCloudArtist({
        profile: initialModel.profile,
        expectedRevision: 2,
        tenantId: 'studio-one',
        authAttempt: 3,
        attempt: 4,
        edit: 5,
      }).effect,
    )
    expect(result).toMatchObject({
      _tag: 'FailedSaveCloudArtist',
      conflict: true,
      reason: 'Another tab changed this identity.',
      tenantId: 'studio-one',
      authAttempt: 3,
      attempt: 4,
    })
  })
  it('uploads the selected original file without fetching its preview URL', async () => {
    const file = new File(['canonical audio'], 'song.wav', {
      type: 'audio/wav',
    })
    const fetch = vi
      .fn()
      .mockResolvedValueOnce(
        Response.json({ id: 'retry-release', state: 'uploading' }),
      )
      .mockResolvedValueOnce(Response.json({ verified: true }))
      .mockResolvedValueOnce(Response.json({ job: { id: 'job-one' } }))
    vi.stubGlobal('fetch', fetch)
    const result = await Effect.runPromise(
      QueueRelease({
        model: {
          ...initialModel,
          maybeAudio: Option.some({
            file,
            name: 'song.wav',
            url: 'blob:gone',
            bytes: file.size,
            duration: 239.68,
            sha256: 'a'.repeat(64),
          }),
        },
        attempt: 2,
      }).effect,
    )
    expect(result).toMatchObject({
      _tag: 'QueuedProduction',
      attempt: 2,
      id: 'retry-release',
    })
    expect(fetch).toHaveBeenCalledTimes(3)
    expect(fetch.mock.calls[1]?.[0]).toBe('/api/releases/retry-release/audio')
    expect(fetch.mock.calls[1]?.[1].body).toBe(file)
  })
})
