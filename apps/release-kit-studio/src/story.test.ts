import { Option } from 'effect'
import { Command, given, message, model, story } from 'foldkit/story'
import { describe, expect, it } from 'vitest'

import {
  LoadCloudStatus,
  Message,
  PollCloudStatus,
  PrepareBrief,
  ReleaseAudio,
  initialModel,
  update,
} from './main'

describe('release drafts', () => {
  it('does not submit a release before the studio artist identity has loaded', () => {
    story(
      update,
      given({
        ...initialModel,
        cloudAvailable: true,
        maybeTenant: Option.some({ id: 'studio-one', name: 'Studio one' }),
        artistState: 'loading',
        lyrics: 'తెలుగు',
        maybeAudio: Option.some({
          file: new File(['audio'], 'song.wav'),
          name: 'song.wav',
          url: 'blob:source',
          sha256: 'a'.repeat(64),
          duration: 239.68,
          bytes: 5,
        }),
      }),
      message(Message.RequestedProduction()),
      model(next => {
        expect(next.cloudState).toBe('idle')
        expect(next.errors).toEqual([
          'Load your studio artist identity before starting production.',
        ])
      }),
    )
  })
  it('updates the library state from the selected release status without changing another release', () => {
    const selected = {
      id: 'web-release',
      title: 'Song',
      state: 'queued',
      createdAt: 1,
    }
    const other = {
      id: 'other-release',
      title: 'Another song',
      state: 'review',
      createdAt: 2,
    }
    const brief = {
      title: selected.title,
      lyrics: 'తెలుగు',
      language: 'Telugu',
      audioName: 'song.wav',
      audioSha256: 'a'.repeat(64),
      audioDuration: 239.68,
      audioBytes: 100,
      profile: initialModel.profile,
    }
    story(
      update,
      given({
        ...initialModel,
        maybeCloudId: Option.some(selected.id),
        cloudReleases: [selected, other],
      }),
      message(
        Message.LoadedCloudStatus({
          status: {
            id: selected.id,
            state: 'waiting-for-direction',
            brief,
            job: null,
            assets: [],
          },
        }),
      ),
      model(next => {
        expect(next.cloudReleases[0]?.state).toBe('waiting-for-direction')
        expect(next.cloudReleases[1]).toEqual(other)
      }),
      Command.resolveAll(
        [PollCloudStatus, Message.RequestedCloudStatus({ id: selected.id })],
        [
          LoadCloudStatus,
          Message.LoadedCloudStatus({
            status: {
              id: selected.id,
              state: 'review',
              brief,
              job: null,
              assets: [],
            },
          }),
        ],
      ),
    )
  })
  it('keeps an artist edit made during loading and ignores later device defaults', () => {
    story(
      update,
      given({
        ...initialModel,
        maybeTenant: Option.some({ id: 'studio-one', name: 'Studio one' }),
        artistState: 'loading',
      }),
      message(Message.UpdatedArtistName({ value: 'My current edit' })),
      message(
        Message.LoadedArtist({
          tenantId: 'studio-one',
          authAttempt: 0,
          attempt: 0,
          edit: 0,
          artist: Option.some({
            profile: { ...initialModel.profile, name: 'Saved name' },
            revision: 2,
            updatedAt: 1,
          }),
        }),
      ),
      message(
        Message.CompletedLoadStudio({
          studio: {
            schemaVersion: 1,
            profile: initialModel.profile,
            drafts: [],
          },
        }),
      ),
      model(next => {
        expect(next.profile.name).toBe('My current edit')
        expect(next.maybeArtistRevision).toEqual(Option.some(2))
        expect(next.artistState).toBe('idle')
      }),
    )
  })
  it('ignores artist responses after logout and from another studio', () => {
    const previous = {
      tenantId: 'studio-one',
      authAttempt: 0,
      attempt: 0,
      edit: 0,
      artist: {
        profile: { ...initialModel.profile, name: 'Private old identity' },
        revision: 2,
        updatedAt: 1,
      },
    }
    story(
      update,
      given({
        ...initialModel,
        maybeTenant: Option.some({ id: 'studio-one', name: 'Studio one' }),
      }),
      message(Message.CompletedSignOut({ attempt: 0 })),
      message(
        Message.LoadedArtist({
          ...previous,
          artist: Option.some(previous.artist),
        }),
      ),
      message(Message.SavedCloudArtist(previous)),
      model(next => {
        expect(next.profile).toEqual(initialModel.profile)
        expect(Option.isNone(next.maybeArtistRevision)).toBe(true)
        expect(next.notice).toContain('signed out')
      }),
    )
    story(
      update,
      given({
        ...initialModel,
        maybeTenant: Option.some({ id: 'studio-two', name: 'Studio two' }),
      }),
      message(Message.SavedCloudArtist(previous)),
      model(next => expect(next.profile).toEqual(initialModel.profile)),
    )
  })
  it('keeps edits made during a save and carries forward its committed revision', () => {
    story(
      update,
      given({
        ...initialModel,
        maybeTenant: Option.some({ id: 'studio-one', name: 'Studio one' }),
        artistState: 'saving',
        maybeArtistRevision: Option.some(2),
      }),
      message(Message.UpdatedIdentity({ value: 'A newer direction' })),
      message(
        Message.SavedCloudArtist({
          tenantId: 'studio-one',
          authAttempt: 0,
          attempt: 0,
          edit: 0,
          artist: { profile: initialModel.profile, revision: 3, updatedAt: 2 },
        }),
      ),
      model(next => {
        expect(next.profile.identity).toBe('A newer direction')
        expect(next.maybeArtistRevision).toEqual(Option.some(3))
        expect(next.notice).toContain('latest edits still need saving')
      }),
    )
  })
  it('preserves unsaved identity on a conflict and prevents a blind overwrite', () => {
    story(
      update,
      given({
        ...initialModel,
        maybeTenant: Option.some({ id: 'studio-one', name: 'Studio one' }),
        artistState: 'saving',
        maybeArtistRevision: Option.some(2),
        profile: { ...initialModel.profile, name: 'Unsaved direction' },
      }),
      message(
        Message.FailedSaveCloudArtist({
          tenantId: 'studio-one',
          authAttempt: 0,
          attempt: 0,
          reason: 'Another tab changed this identity.',
          conflict: true,
        }),
      ),
      message(Message.ClickedSaveProfile()),
      model(next => {
        expect(next.profile.name).toBe('Unsaved direction')
        expect(next.artistState).toBe('conflict')
        expect(Option.isNone(next.maybeArtistRevision)).toBe(true)
      }),
    )
  })
  it('restores device identity when the unsigned session check finishes first', () => {
    const deviceProfile = { ...initialModel.profile, name: 'Device artist' }
    story(
      update,
      given(initialModel),
      message(
        Message.LoadedConnection({
          available: true,
          tenant: Option.none(),
          attempt: 0,
        }),
      ),
      message(
        Message.CompletedLoadStudio({
          studio: { schemaVersion: 1, profile: deviceProfile, drafts: [] },
        }),
      ),
      model(next => expect(next.profile).toEqual(deviceProfile)),
    )
  })
  it('does not restore private cloud release names after sign-out', () => {
    story(
      update,
      given({
        ...initialModel,
        maybeTenant: Option.some({ id: 'tenant-one', name: 'Studio one' }),
      }),
      message(Message.CompletedSignOut({ attempt: 0 })),
      message(
        Message.LoadedCloudLibrary({
          tenantId: 'tenant-one',
          releases: [
            {
              id: 'private-film',
              title: 'Private release',
              state: 'review',
              createdAt: 1,
            },
          ],
        }),
      ),
      model(next => {
        expect(Option.isNone(next.maybeTenant)).toBe(true)
        expect(next.cloudReleases).toEqual([])
      }),
    )
  })
  it('does not attach an earlier upload response to a new release', () => {
    story(
      update,
      given(initialModel),
      message(Message.ClickedNewRelease()),
      message(Message.QueuedProduction({ id: 'earlier-release', attempt: 0 })),
      model(next => expect(Option.isNone(next.maybeCloudId)).toBe(true)),
    )
  })
  it('ignores a session response that predates the current sign-in', () => {
    story(
      update,
      given({
        ...initialModel,
        authAttempt: 2,
        maybeTenant: Option.some({ id: 'new-studio', name: 'New studio' }),
      }),
      message(
        Message.LoadedConnection({
          attempt: 0,
          available: false,
          tenant: Option.none(),
        }),
      ),
      model(next =>
        expect(Option.map(next.maybeTenant, tenant => tenant.id)).toEqual(
          Option.some('new-studio'),
        ),
      ),
    )
  })
  it('blocks saving an incomplete release', () => {
    story(
      update,
      given(initialModel),
      message(Message.SubmittedDraft()),
      model(next => {
        expect(next.errors).toContain('Choose an audio file.')
        expect(next.errors).toContain(
          'Add the exact lyrics in their original script.',
        )
        expect(next.saveState).toBe('idle')
      }),
    )
  })

  it('discards a stale audio result after the user starts a different release', () => {
    story(
      update,
      given(initialModel),
      message(Message.ClickedNewRelease()),
      message(
        Message.CompletedReadAudio({
          attempt: 0,
          asset: {
            file: new File(['audio'], 'old.wav'),
            name: 'old.wav',
            url: 'blob:old',
            bytes: 400,
            sha256: 'old',
            duration: 4,
          },
        }),
      ),
      Command.resolveAll([ReleaseAudio, Message.CompletedReleaseAudio()]),
      model(next => {
        expect(Option.isNone(next.maybeAudio)).toBe(true)
        expect(next.title).toBe('')
      }),
    )
  })

  it('a saved draft requires the user to reselect its audio after reopening', () => {
    const draft = {
      schemaVersion: 1,
      id: 'release-1',
      title: 'Song',
      lyrics: 'తెలుగు',
      language: 'Telugu',
      audioName: 'song.wav',
      audioSha256: 'hash',
      audioDuration: 239.68,
      audioBytes: 1000,
      profile: initialModel.profile,
      createdAt: '2026-10-03T00:00:00.000Z',
      revisionNotes: ['Keep the character still.'],
      status: 'draft',
    }
    story(
      update,
      given(initialModel),
      message(
        Message.CompletedSaveDraft({
          draft: { ...draft, schemaVersion: 1, status: 'draft' },
          drafts: [{ ...draft, schemaVersion: 1, status: 'draft' }],
        }),
      ),
      Command.resolveAll([
        PrepareBrief,
        Message.CompletedPrepareBrief({ id: 'release-1', url: 'blob:brief-1' }),
      ]),
      message(Message.SelectedDraft({ id: 'release-1' })),
      Command.resolveAll(
        [ReleaseAudio, Message.CompletedReleaseAudio()],
        [
          PrepareBrief,
          Message.CompletedPrepareBrief({
            id: 'release-1',
            url: 'blob:brief-2',
          }),
        ],
      ),
      model(next => {
        expect(next.lyrics).toBe('తెలుగు')
        expect(next.revisionNotes).toEqual(['Keep the character still.'])
        expect(Option.isNone(next.maybeAudio)).toBe(true)
        expect(next.notice).toContain('Reselect song.wav')
      }),
      message(Message.SubmittedDraft()),
      model(next => expect(next.errors).toContain('Choose an audio file.')),
    )
  })
})
