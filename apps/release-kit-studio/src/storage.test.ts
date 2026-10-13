import { Effect, Option, Schema } from 'effect'
import { modifyFields } from 'foldkit/struct'
import { beforeEach, describe, expect, it } from 'vitest'

import {
  LoadStudio,
  PersistedStudio,
  STORAGE_KEY,
  SaveDraft,
  initialModel,
} from './main'

describe('device persistence', () => {
  beforeEach(() => localStorage.clear())

  it('saves verified audio metadata and Unicode lyrics without storing audio bytes or blob URLs', async () => {
    const input = modifyFields(initialModel, {
      lyrics: () => 'ప్రతి క్షణం',
      maybeAudio: () =>
        Option.some({
          file: new File(['audio'], 'song.wav'),
          name: 'song.wav',
          sha256: 'a'.repeat(64),
          bytes: 1234,
          duration: 239.68,
          url: 'blob:local-only',
        }),
    })
    const result = await Effect.runPromise(SaveDraft({ model: input }).effect)
    expect(result._tag).toBe('CompletedSaveDraft')
    const stored = localStorage.getItem(STORAGE_KEY) ?? ''
    const decoded = Schema.decodeUnknownSync(PersistedStudio)(
      JSON.parse(stored),
    )
    expect(decoded.drafts[0]?.lyrics).toBe('ప్రతి క్షణం')
    expect(decoded.drafts[0]?.audioSha256).toBe('a'.repeat(64))
    expect(stored).not.toContain('blob:local-only')
    const loaded = await Effect.runPromise(LoadStudio().effect)
    expect(loaded._tag).toBe('CompletedLoadStudio')
  })

  it('preserves corrupted stored data and reports a recoverable failure', async () => {
    localStorage.setItem(STORAGE_KEY, '{broken')
    const result = await Effect.runPromise(LoadStudio().effect)
    expect(result._tag).toBe('FailedLoadStudio')
    expect(localStorage.getItem(STORAGE_KEY)).toBe('{broken')
  })
})
