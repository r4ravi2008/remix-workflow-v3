import { afterEach, describe, expect, it, vi } from 'vitest'

import { decodedAudioDuration } from './audio'

afterEach(() => vi.unstubAllGlobals())

describe('decoded upload duration', () => {
  it('measures decoded frames without using padded container metadata', async () => {
    vi.stubGlobal(
      'OfflineAudioContext',
      class {
        decodeAudioData() {
          return Promise.resolve({
            length: 3834880,
            sampleRate: 16000,
            duration: 239.726,
          })
        }
      },
    )
    expect(
      await decodedAudioDuration(
        new ArrayBuffer(1),
        new AbortController().signal,
      ),
    ).toBe(239.68)
  })

  it('does not accept a late result after an upload is interrupted', async () => {
    let complete: (value: {
      length: number
      sampleRate: number
    }) => void = () => {}
    vi.stubGlobal(
      'OfflineAudioContext',
      class {
        decodeAudioData() {
          return new Promise(resolve => {
            complete = resolve
          })
        }
      },
    )
    const controller = new AbortController()
    const duration = decodedAudioDuration(new ArrayBuffer(1), controller.signal)
    await Promise.resolve()
    const result = expect(duration).rejects.toThrow('interrupted')
    controller.abort()
    complete({ length: 16000, sampleRate: 16000 })
    await result
  })

  it('rejects unreadable and overlong audio without a metadata fallback', async () => {
    vi.stubGlobal(
      'OfflineAudioContext',
      class {
        decodeAudioData() {
          return Promise.reject(new Error('bad media'))
        }
      },
    )
    await expect(
      decodedAudioDuration(new ArrayBuffer(1), new AbortController().signal),
    ).rejects.toThrow('could not be decoded')
    vi.stubGlobal(
      'OfflineAudioContext',
      class {
        decodeAudioData() {
          return Promise.resolve({ length: 14416000, sampleRate: 16000 })
        }
      },
    )
    await expect(
      decodedAudioDuration(new ArrayBuffer(1), new AbortController().signal),
    ).rejects.toThrow('15 minutes')
  })
})
