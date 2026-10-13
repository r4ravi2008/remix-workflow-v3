import { Cause, Clock, Crypto, Effect, Option, Schema } from 'effect'
import { Command, Runtime, type Update } from 'foldkit'
import { defineMessageUnion } from 'foldkit/message'
import { modifyFields } from 'foldkit/struct'

import { BrowserCrypto } from '@effect/platform-browser'

import { decodedAudioDuration } from './audio'
import {
  CloudRequestError,
  CloudStatus,
  CloudSummary,
  Tenant,
  cloudRequest,
  jsonPost,
} from './cloud'
import {
  ArtistProfile,
  OutputId,
  ReleaseDraft,
  SavedArtist,
  defaultProfile,
  validateArtistProfile,
  validateRelease,
} from './domain'

const AudioAsset = Schema.Struct({
  file: Schema.File,
  name: Schema.String,
  url: Schema.String,
  sha256: Schema.String,
  duration: Schema.Number,
  bytes: Schema.Number,
})
export const PersistedStudio = Schema.Struct({
  schemaVersion: Schema.Literal(1),
  profile: ArtistProfile,
  drafts: Schema.Array(ReleaseDraft),
})
export const STORAGE_KEY = 'release-kit-studio:v1'

export const Model = Schema.Struct({
  title: Schema.String,
  lyrics: Schema.String,
  language: Schema.String,
  profile: ArtistProfile,
  drafts: Schema.Array(ReleaseDraft),
  maybeDraftId: Schema.Option(Schema.String),
  maybeAudio: Schema.Option(AudioAsset),
  maybeBriefUrl: Schema.Option(Schema.String),
  libraryState: Schema.Literals(['closed', 'open']),
  audioAttempt: Schema.Number,
  audioState: Schema.Literals(['idle', 'reading']),
  saveState: Schema.Literals(['idle', 'saving']),
  pane: Schema.Literals(['release', 'artist', 'about']),
  selectedOutput: OutputId,
  revisionNote: Schema.String,
  revisionNotes: Schema.Array(Schema.String),
  errors: Schema.Array(Schema.String),
  notice: Schema.String,
  invitation: Schema.String,
  maybeTenant: Schema.Option(Tenant),
  cloudAvailable: Schema.Boolean,
  cloudState: Schema.Literals(['idle', 'connecting', 'uploading']),
  cloudReleases: Schema.Array(CloudSummary),
  maybeCloudId: Schema.Option(Schema.String),
  maybeCloudStatus: Schema.Option(CloudStatus),
  cloudAttempt: Schema.Number,
  authAttempt: Schema.Number,
  artistState: Schema.Literals([
    'idle',
    'loading',
    'saving',
    'load-error',
    'conflict',
  ]),
  maybeArtistRevision: Schema.Option(Schema.Number),
  artistAttempt: Schema.Number,
  profileEdit: Schema.Number,
})
export type Model = typeof Model.Type

export const Message = defineMessageUnion({
  UpdatedTitle: { value: Schema.String },
  UpdatedLyrics: { value: Schema.String },
  UpdatedLanguage: { value: Schema.String },
  UpdatedArtistName: { value: Schema.String },
  UpdatedIdentity: { value: Schema.String },
  UpdatedPalette: { value: ArtistProfile.fields.palette },
  UpdatedIntensity: { value: ArtistProfile.fields.intensity },
  SelectedAudio: { files: Schema.Array(Schema.File) },
  CompletedReadAudio: { asset: AudioAsset, attempt: Schema.Number },
  FailedReadAudio: { reason: Schema.String, attempt: Schema.Number },
  CompletedReleaseAudio: {},
  CompletedPrepareBrief: { id: Schema.String, url: Schema.String },
  FailedPrepareBrief: {},
  SelectedOutput: { id: OutputId },
  SelectedPane: { pane: Model.fields.pane },
  ClickedNewRelease: {},
  SelectedDraft: { id: Schema.String },
  SubmittedDraft: {},
  CompletedSaveDraft: {
    draft: ReleaseDraft,
    drafts: Schema.Array(ReleaseDraft),
  },
  FailedSaveDraft: { reason: Schema.String },
  ClickedSaveProfile: {},
  CompletedSaveProfile: { attempt: Schema.Number, edit: Schema.Number },
  FailedSaveProfile: { reason: Schema.String, attempt: Schema.Number },
  ClickedReloadProfile: {},
  LoadedArtist: {
    artist: Schema.Option(SavedArtist),
    tenantId: Schema.String,
    authAttempt: Schema.Number,
    attempt: Schema.Number,
    edit: Schema.Number,
  },
  FailedLoadArtist: {
    reason: Schema.String,
    tenantId: Schema.String,
    authAttempt: Schema.Number,
    attempt: Schema.Number,
  },
  SavedCloudArtist: {
    artist: SavedArtist,
    tenantId: Schema.String,
    authAttempt: Schema.Number,
    attempt: Schema.Number,
    edit: Schema.Number,
  },
  FailedSaveCloudArtist: {
    reason: Schema.String,
    conflict: Schema.Boolean,
    tenantId: Schema.String,
    authAttempt: Schema.Number,
    attempt: Schema.Number,
  },
  CompletedLoadStudio: { studio: PersistedStudio },
  FailedLoadStudio: { reason: Schema.String },
  UpdatedRevisionNote: { value: Schema.String },
  SubmittedRevisionNote: {},
  UpdatedInvitation: { value: Schema.String },
  SubmittedInvitation: {},
  LoadedConnection: {
    available: Schema.Boolean,
    tenant: Schema.Option(Tenant),
    attempt: Schema.Number,
  },
  FailedConnection: { reason: Schema.String, attempt: Schema.Number },
  LoadedCloudLibrary: {
    releases: Schema.Array(CloudSummary),
    tenantId: Schema.String,
  },
  FailedCloudLibrary: { reason: Schema.String, tenantId: Schema.String },
  RequestedProduction: {},
  QueuedProduction: { id: Schema.String, attempt: Schema.Number },
  FailedProduction: { reason: Schema.String, attempt: Schema.Number },
  SelectedCloudRelease: { id: Schema.String },
  RequestedCloudStatus: { id: Schema.String },
  LoadedCloudStatus: { status: CloudStatus },
  FailedCloudStatus: { id: Schema.String, reason: Schema.String },
  RequestedSignOut: {},
  CompletedSignOut: { attempt: Schema.Number },
})
export type Message = typeof Message.Type

export const initialModel: Model = {
  title: 'Pal Pal Nimisham',
  lyrics: '',
  language: 'Telugu',
  profile: defaultProfile,
  drafts: [],
  maybeDraftId: Option.none(),
  maybeAudio: Option.none(),
  maybeBriefUrl: Option.none(),
  libraryState: 'closed',
  audioAttempt: 0,
  audioState: 'idle',
  saveState: 'idle',
  pane: 'release',
  selectedOutput: 'film',
  revisionNote: '',
  revisionNotes: [],
  errors: [],
  notice: '',
  invitation: '',
  maybeTenant: Option.none(),
  cloudAvailable: false,
  cloudState: 'idle',
  cloudReleases: [],
  maybeCloudId: Option.none(),
  maybeCloudStatus: Option.none(),
  cloudAttempt: 0,
  authAttempt: 0,
  artistState: 'idle',
  maybeArtistRevision: Option.none(),
  artistAttempt: 0,
  profileEdit: 0,
}

const commandCause = (error: unknown): unknown =>
  Cause.isUnknownError(error) ? error.cause : error
const errorText = (error: unknown): string => {
  const cause = commandCause(error)
  return cause instanceof Error
    ? cause.message
    : 'This action could not be completed.'
}

export const ReadAudio = Command.define('ReadAudio', {
  args: { file: Schema.File, attempt: Schema.Number },
  messages: [Message.CompletedReadAudio, Message.FailedReadAudio],
  execute: ({ file, attempt }) =>
    Effect.gen(function* () {
      if (file.size === 0 || file.size > 100 * 1024 * 1024) {
        return yield* Effect.fail(
          new Error('Choose an audio file between 1 byte and 100 MB.'),
        )
      }
      if (
        !file.type.startsWith('audio/') &&
        !/\.(wav|mp3|m4a|aac|ogg|flac)$/i.test(file.name)
      ) {
        return yield* Effect.fail(
          new Error('Choose an audio file: WAV, MP3, M4A, AAC, OGG, or FLAC.'),
        )
      }
      const buffer = yield* Effect.tryPromise(() => file.arrayBuffer())
      const cryptoService = yield* Crypto.Crypto
      const hash = yield* cryptoService.digest(
        'SHA-256',
        new Uint8Array(buffer),
      )
      const sha256 = Array.from(hash, byte =>
        byte.toString(16).padStart(2, '0'),
      ).join('')
      const url = yield* Effect.sync(() => URL.createObjectURL(file))
      const duration = yield* Effect.tryPromise({
        try: signal => decodedAudioDuration(buffer, signal),
        catch: error => new Error(errorText(error)),
      }).pipe(
        Effect.timeout('20 seconds'),
        Effect.onError(() => Effect.sync(() => URL.revokeObjectURL(url))),
      )
      return Message.CompletedReadAudio({
        attempt,
        asset: {
          file,
          name: file.name,
          url,
          sha256,
          duration,
          bytes: file.size,
        },
      })
    }).pipe(
      Effect.provide(BrowserCrypto.layer),
      Effect.catch(error =>
        Effect.succeed(
          Message.FailedReadAudio({ attempt, reason: errorText(error) }),
        ),
      ),
    ),
})

export const ReleaseAudio = Command.define('ReleaseAudio', {
  args: { url: Schema.String },
  messages: [Message.CompletedReleaseAudio],
  execute: ({ url }) =>
    Effect.sync(() => URL.revokeObjectURL(url)).pipe(
      Effect.as(Message.CompletedReleaseAudio()),
      Effect.catch(() => Effect.succeed(Message.CompletedReleaseAudio())),
    ),
})

export const LoadStudio = Command.define('LoadStudio', {
  messages: [Message.CompletedLoadStudio, Message.FailedLoadStudio],
  execute: Effect.try((): typeof PersistedStudio.Type => {
    const saved = localStorage.getItem(STORAGE_KEY)
    return saved
      ? Schema.decodeUnknownSync(PersistedStudio)(JSON.parse(saved))
      : { schemaVersion: 1, profile: defaultProfile, drafts: [] }
  }).pipe(
    Effect.map(studio => Message.CompletedLoadStudio({ studio })),
    Effect.catch(() =>
      Effect.succeed(
        Message.FailedLoadStudio({
          reason:
            'Saved drafts could not be read. You can start a new draft; the stored data has been left untouched.',
        }),
      ),
    ),
  ),
})

export const SaveDraft = Command.define('SaveDraft', {
  args: { model: Model },
  messages: [Message.CompletedSaveDraft, Message.FailedSaveDraft],
  execute: ({ model }) =>
    Effect.gen(function* () {
      const cryptoService = yield* Crypto.Crypto
      const uuid = yield* cryptoService.randomUUIDv4
      const now = yield* Clock.currentTimeMillis
      const audio = yield* Option.match(model.maybeAudio, {
        onNone: () =>
          Effect.fail(
            new Error('Reselect the audio file to save this release.'),
          ),
        onSome: Effect.succeed,
      })
      const id = Option.getOrElse(model.maybeDraftId, () => uuid)
      const existing = model.drafts.find(draft => draft.id === id)
      const draft: ReleaseDraft = {
        schemaVersion: 1,
        id,
        title: model.title.trim(),
        lyrics: model.lyrics.trim(),
        language: model.language,
        audioName: audio.name,
        audioSha256: audio.sha256,
        audioDuration: audio.duration,
        audioBytes: audio.bytes,
        profile: model.profile,
        createdAt: existing?.createdAt ?? new Date(now).toISOString(),
        revisionNotes: model.revisionNotes,
        status: 'draft',
      }
      const drafts = [draft, ...model.drafts.filter(item => item.id !== id)]
      yield* Effect.try(() =>
        localStorage.setItem(
          STORAGE_KEY,
          JSON.stringify({ schemaVersion: 1, profile: model.profile, drafts }),
        ),
      )
      return Message.CompletedSaveDraft({ draft, drafts })
    }).pipe(
      Effect.provide(BrowserCrypto.layer),
      Effect.catch(() =>
        Effect.succeed(
          Message.FailedSaveDraft({
            reason:
              'The draft could not be saved on this device. Check browser storage permissions and try again.',
          }),
        ),
      ),
    ),
})

export const SaveProfile = Command.define('SaveProfile', {
  args: {
    profile: ArtistProfile,
    drafts: Schema.Array(ReleaseDraft),
    attempt: Schema.Number,
    edit: Schema.Number,
  },
  messages: [Message.CompletedSaveProfile, Message.FailedSaveProfile],
  execute: ({ profile, drafts, attempt, edit }) =>
    Effect.try(() =>
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({ schemaVersion: 1, profile, drafts }),
      ),
    ).pipe(
      Effect.as(Message.CompletedSaveProfile({ attempt, edit })),
      Effect.catch(() =>
        Effect.succeed(
          Message.FailedSaveProfile({
            reason: 'The artist profile could not be saved on this device.',
            attempt,
          }),
        ),
      ),
    ),
})

export const LoadArtist = Command.define('LoadArtist', {
  args: {
    tenantId: Schema.String,
    authAttempt: Schema.Number,
    attempt: Schema.Number,
    edit: Schema.Number,
  },
  messages: [Message.LoadedArtist, Message.FailedLoadArtist],
  execute: ({ tenantId, authAttempt, attempt, edit }) =>
    Effect.tryPromise(async signal => {
      const result = await cloudRequest(
        '/api/artist-profile',
        Schema.Struct({ artist: Schema.NullOr(SavedArtist) }),
        { signal },
      )
      return Message.LoadedArtist({
        artist: Option.fromNullOr(result.artist),
        tenantId,
        authAttempt,
        attempt,
        edit,
      })
    }).pipe(
      Effect.timeout('20 seconds'),
      Effect.catch(error =>
        Effect.succeed(
          Message.FailedLoadArtist({
            reason: errorText(error),
            tenantId,
            authAttempt,
            attempt,
          }),
        ),
      ),
    ),
})

export const SaveCloudArtist = Command.define('SaveCloudArtist', {
  args: {
    profile: ArtistProfile,
    expectedRevision: Schema.Number,
    tenantId: Schema.String,
    authAttempt: Schema.Number,
    attempt: Schema.Number,
    edit: Schema.Number,
  },
  messages: [Message.SavedCloudArtist, Message.FailedSaveCloudArtist],
  execute: ({
    profile,
    expectedRevision,
    tenantId,
    authAttempt,
    attempt,
    edit,
  }) =>
    Effect.tryPromise(async signal => {
      const result = await cloudRequest(
        '/api/artist-profile',
        Schema.Struct({ artist: SavedArtist }),
        {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ profile, expectedRevision }),
          signal,
        },
      )
      return Message.SavedCloudArtist({
        artist: result.artist,
        tenantId,
        authAttempt,
        attempt,
        edit,
      })
    }).pipe(
      Effect.timeout('20 seconds'),
      Effect.catch(error => {
        const cause = commandCause(error)
        return Effect.succeed(
          Message.FailedSaveCloudArtist({
            reason: errorText(error),
            conflict:
              cause instanceof CloudRequestError && cause.status === 409,
            tenantId,
            authAttempt,
            attempt,
          }),
        )
      }),
    ),
})

const ownsArtistResponse = (
  model: Model,
  tenantId: string,
  authAttempt: number,
  attempt: number,
) =>
  authAttempt === model.authAttempt &&
  attempt === model.artistAttempt &&
  Option.exists(model.maybeTenant, tenant => tenant.id === tenantId)

const releaseAudioCommands = (model: Model) =>
  Option.match(model.maybeAudio, {
    onNone: () => [],
    onSome: audio => [ReleaseAudio({ url: audio.url })],
  })

export const PrepareBrief = Command.define('PrepareBrief', {
  args: { draft: ReleaseDraft },
  messages: [Message.CompletedPrepareBrief, Message.FailedPrepareBrief],
  execute: ({ draft }) =>
    Effect.try(() =>
      URL.createObjectURL(
        new Blob([JSON.stringify(draft, null, 2)], {
          type: 'application/json',
        }),
      ),
    ).pipe(
      Effect.map(url => Message.CompletedPrepareBrief({ id: draft.id, url })),
      Effect.catch(() => Effect.succeed(Message.FailedPrepareBrief())),
    ),
})

const releaseBriefCommands = (model: Model) =>
  Option.match(model.maybeBriefUrl, {
    onNone: () => [],
    onSome: url => [ReleaseAudio({ url })],
  })

export const LoadConnection = Command.define('LoadConnection', {
  args: { attempt: Schema.Number },
  messages: [Message.LoadedConnection, Message.FailedConnection],
  execute: ({ attempt }) =>
    Effect.tryPromise(async () => {
      const health = await cloudRequest(
        '/api/health',
        Schema.Struct({ tenantAuthentication: Schema.Boolean }),
      )
      if (!health.tenantAuthentication)
        return Message.LoadedConnection({
          available: false,
          tenant: Option.none(),
          attempt,
        })
      const response = await fetch('/api/auth/session', {
        credentials: 'same-origin',
      })
      if (response.status === 401)
        return Message.LoadedConnection({
          available: true,
          tenant: Option.none(),
          attempt,
        })
      if (!response.ok)
        throw new Error('The studio connection could not be checked.')
      const body = Schema.decodeUnknownSync(Schema.Struct({ tenant: Tenant }))(
        await response.json(),
      )
      return Message.LoadedConnection({
        available: true,
        tenant: Option.some(body.tenant),
        attempt,
      })
    }).pipe(
      Effect.catch(error =>
        Effect.succeed(
          Message.FailedConnection({ reason: errorText(error), attempt }),
        ),
      ),
    ),
})
export const ExchangeInvitation = Command.define('ExchangeInvitation', {
  args: { invitation: Schema.String, attempt: Schema.Number },
  messages: [Message.LoadedConnection, Message.FailedConnection],
  execute: ({ invitation, attempt }) =>
    Effect.tryPromise(async () => {
      const result = await cloudRequest(
        '/api/auth/exchange',
        Schema.Struct({ tenant: Tenant }),
        jsonPost({ token: invitation.trim() }),
      )
      return Message.LoadedConnection({
        available: true,
        tenant: Option.some(result.tenant),
        attempt,
      })
    }).pipe(
      Effect.catch(error =>
        Effect.succeed(
          Message.FailedConnection({ reason: errorText(error), attempt }),
        ),
      ),
    ),
})
export const LoadCloudLibrary = Command.define('LoadCloudLibrary', {
  args: { tenantId: Schema.String },
  messages: [Message.LoadedCloudLibrary, Message.FailedCloudLibrary],
  execute: ({ tenantId }) =>
    Effect.tryPromise(async () => {
      const result = await cloudRequest(
        '/api/releases',
        Schema.Struct({ releases: Schema.Array(CloudSummary) }),
      )
      return Message.LoadedCloudLibrary({ releases: result.releases, tenantId })
    }).pipe(
      Effect.catch(error =>
        Effect.succeed(
          Message.FailedCloudLibrary({ reason: errorText(error), tenantId }),
        ),
      ),
    ),
})
export const QueueRelease = Command.define('QueueRelease', {
  args: { model: Model, attempt: Schema.Number },
  messages: [Message.QueuedProduction, Message.FailedProduction],
  execute: ({ model, attempt }) =>
    Effect.gen(function* () {
      const audio = yield* Option.match(model.maybeAudio, {
        onNone: () => Effect.fail(new Error('Choose the audio file first.')),
        onSome: Effect.succeed,
      })
      const cryptoService = yield* Crypto.Crypto
      const brief = {
        title: model.title.trim(),
        lyrics: model.lyrics.trim(),
        language: model.language,
        audioName: audio.name,
        audioSha256: audio.sha256,
        audioBytes: audio.bytes,
        audioDuration: audio.duration,
        profile: model.profile,
      }
      const fingerprint = yield* cryptoService.digest(
        'SHA-256',
        new TextEncoder().encode(JSON.stringify(brief)),
      )
      const journal = `release-kit:submission:${Array.from(fingerprint, byte => byte.toString(16).padStart(2, '0')).join('')}`
      const uuid = yield* cryptoService.randomUUIDv4
      const requestKey = yield* Effect.try(() => {
        const existing = sessionStorage.getItem(journal)
        if (existing) return existing
        sessionStorage.setItem(journal, uuid)
        return uuid
      })
      const result = yield* Effect.tryPromise(async () => {
        const release = await cloudRequest(
          '/api/releases',
          Schema.Struct({ id: Schema.String, state: Schema.String }),
          jsonPost({ requestKey, brief }),
        )
        if (release.state === 'uploading') {
          await cloudRequest(
            `/api/releases/${release.id}/audio`,
            Schema.Struct({ verified: Schema.Boolean }),
            {
              method: 'PUT',
              headers: {
                'Content-Type': 'application/octet-stream',
                'X-Content-Sha256': audio.sha256,
                'X-Upload-Bytes': String(audio.bytes),
              },
              body: audio.file,
            },
          )
          await cloudRequest(
            `/api/releases/${release.id}/start`,
            Schema.Struct({ job: Schema.Unknown }),
            jsonPost({}),
          )
        }
        return release.id
      })
      return Message.QueuedProduction({ id: result, attempt })
    }).pipe(
      Effect.provide(BrowserCrypto.layer),
      Effect.catch(error =>
        Effect.succeed(
          Message.FailedProduction({ reason: errorText(error), attempt }),
        ),
      ),
    ),
})
export const LoadCloudStatus = Command.define('LoadCloudStatus', {
  args: { id: Schema.String },
  messages: [Message.LoadedCloudStatus, Message.FailedCloudStatus],
  execute: ({ id }) =>
    Effect.tryPromise(async () =>
      Message.LoadedCloudStatus({
        status: await cloudRequest(`/api/releases/${id}`, CloudStatus),
      }),
    ).pipe(
      Effect.catch(error =>
        Effect.succeed(
          Message.FailedCloudStatus({ id, reason: errorText(error) }),
        ),
      ),
    ),
})
export const PollCloudStatus = Command.define('PollCloudStatus', {
  args: { id: Schema.String },
  messages: [Message.RequestedCloudStatus],
  execute: ({ id }) =>
    Effect.sleep('20 seconds').pipe(
      Effect.as(Message.RequestedCloudStatus({ id })),
    ),
})
export const SignOut = Command.define('SignOut', {
  args: { attempt: Schema.Number },
  messages: [Message.CompletedSignOut, Message.FailedConnection],
  execute: ({ attempt }) =>
    Effect.tryPromise(async () => {
      await cloudRequest(
        '/api/auth/logout',
        Schema.Struct({ signedOut: Schema.Boolean }),
        jsonPost({}),
      )
      return Message.CompletedSignOut({ attempt })
    }).pipe(
      Effect.catch(error =>
        Effect.succeed(
          Message.FailedConnection({ reason: errorText(error), attempt }),
        ),
      ),
    ),
})

export const update = (model: Model, message: Message) =>
  Message.match<Update.Return<Model, Message>>(message, {
    UpdatedTitle: ({ value }) => ({
      model: modifyFields(model, { title: () => value }),
    }),
    UpdatedLyrics: ({ value }) => ({
      model: modifyFields(model, { lyrics: () => value }),
    }),
    UpdatedLanguage: ({ value }) => ({
      model: modifyFields(model, { language: () => value }),
    }),
    UpdatedArtistName: ({ value }) => ({
      model: modifyFields(model, {
        profile: profile => modifyFields(profile, { name: () => value }),
        profileEdit: edit => edit + 1,
      }),
    }),
    UpdatedIdentity: ({ value }) => ({
      model: modifyFields(model, {
        profile: profile => modifyFields(profile, { identity: () => value }),
        profileEdit: edit => edit + 1,
      }),
    }),
    UpdatedPalette: ({ value }) => ({
      model: modifyFields(model, {
        profile: profile => modifyFields(profile, { palette: () => value }),
        profileEdit: edit => edit + 1,
      }),
    }),
    UpdatedIntensity: ({ value }) => ({
      model: modifyFields(model, {
        profile: profile => modifyFields(profile, { intensity: () => value }),
        profileEdit: edit => edit + 1,
      }),
    }),
    SelectedAudio: ({ files }) => {
      const file = files[0]
      if (!file) {
        return { model }
      }
      const attempt = model.audioAttempt + 1
      return {
        model: modifyFields(model, {
          audioAttempt: () => attempt,
          audioState: () => 'reading',
          errors: () => [],
          notice: () => '',
        }),
        commands: [ReadAudio({ file, attempt })],
      }
    },
    CompletedReadAudio: ({ asset, attempt }) => {
      if (attempt !== model.audioAttempt) {
        return { model, commands: [ReleaseAudio({ url: asset.url })] }
      }
      return {
        model: modifyFields(model, {
          maybeAudio: () => Option.some(asset),
          audioState: () => 'idle',
          errors: () => [],
          notice: () => 'Audio is ready to preview. It stays on this device.',
        }),
        commands: releaseAudioCommands(model),
      }
    },
    FailedReadAudio: ({ reason, attempt }) =>
      attempt === model.audioAttempt
        ? {
            model: modifyFields(model, {
              audioState: () => 'idle',
              errors: () => [reason],
            }),
          }
        : { model },
    CompletedReleaseAudio: () => ({ model }),
    CompletedPrepareBrief: ({ id, url }) =>
      Option.contains(model.maybeDraftId, id)
        ? {
            model: modifyFields(model, {
              maybeBriefUrl: () => Option.some(url),
            }),
            commands: releaseBriefCommands(model),
          }
        : { model, commands: [ReleaseAudio({ url })] },
    FailedPrepareBrief: () => ({
      model: modifyFields(model, {
        errors: () => [
          'The brief export could not be prepared. Your saved draft is still available.',
        ],
      }),
    }),
    SelectedOutput: ({ id }) => ({
      model: modifyFields(model, { selectedOutput: () => id }),
    }),
    SelectedPane: ({ pane }) => ({
      model: modifyFields(model, {
        pane: () => pane,
        libraryState: state =>
          pane === 'release' && state === 'closed' ? 'open' : 'closed',
      }),
    }),
    ClickedNewRelease: () => ({
      model: modifyFields(initialModel, {
        title: () => '',
        profile: () => model.profile,
        drafts: () => model.drafts,
        audioAttempt: () => model.audioAttempt + 1,
        maybeTenant: () => model.maybeTenant,
        cloudAvailable: () => model.cloudAvailable,
        cloudReleases: () => model.cloudReleases,
        cloudAttempt: () => model.cloudAttempt + 1,
        authAttempt: () => model.authAttempt,
        artistState: () => model.artistState,
        artistAttempt: () => model.artistAttempt,
        maybeArtistRevision: () => model.maybeArtistRevision,
        profileEdit: () => model.profileEdit,
      }),
      commands: [
        ...releaseAudioCommands(model),
        ...releaseBriefCommands(model),
      ],
    }),
    SelectedDraft: ({ id }) => {
      const draft = model.drafts.find(item => item.id === id)
      if (!draft) {
        return { model }
      }
      return {
        model: modifyFields(model, {
          maybeDraftId: () => Option.some(id),
          maybeCloudId: () => Option.none(),
          maybeCloudStatus: () => Option.none(),
          cloudAttempt: value => value + 1,
          title: () => draft.title,
          lyrics: () => draft.lyrics,
          language: () => draft.language,
          profile: () => draft.profile,
          profileEdit: edit => edit + 1,
          maybeAudio: () => Option.none(),
          maybeBriefUrl: () => Option.none(),
          libraryState: () => 'closed',
          audioAttempt: value => value + 1,
          audioState: () => 'idle',
          revisionNotes: () => draft.revisionNotes,
          revisionNote: () => '',
          errors: () => [],
          pane: () => 'release',
          notice: () =>
            `Opened saved draft. Reselect ${draft.audioName} to preview audio and save changes.`,
        }),
        commands: [
          ...releaseAudioCommands(model),
          ...releaseBriefCommands(model),
          PrepareBrief({ draft }),
        ],
      }
    },
    SubmittedDraft: () => {
      if (Option.isSome(model.maybeCloudId)) return { model }
      if (model.audioState === 'reading' || model.saveState === 'saving') {
        return { model }
      }
      const errors = validateRelease({
        title: model.title,
        lyrics: model.lyrics,
        audioName: Option.match(model.maybeAudio, {
          onNone: () => '',
          onSome: audio => audio.name,
        }),
        audioDuration: Option.match(model.maybeAudio, {
          onNone: () => 0,
          onSome: audio => audio.duration,
        }),
      })
      if (errors.length > 0) {
        return {
          model: modifyFields(model, {
            errors: () => errors,
            notice: () => '',
          }),
        }
      }
      return {
        model: modifyFields(model, {
          saveState: () => 'saving',
          errors: () => [],
          notice: () => '',
        }),
        commands: [SaveDraft({ model })],
      }
    },
    CompletedSaveDraft: ({ draft, drafts }) => ({
      model: modifyFields(model, {
        drafts: () => drafts,
        maybeDraftId: () => Option.some(draft.id),
        saveState: () => 'idle',
        notice: () =>
          model.cloudAvailable
            ? 'Draft saved on this device. Start production to upload your song and queue the kit.'
            : 'Draft saved on this device. Export the brief to keep a copy. Production is not connected yet.',
      }),
      commands: [PrepareBrief({ draft })],
    }),
    FailedSaveDraft: ({ reason }) => ({
      model: modifyFields(model, {
        saveState: () => 'idle',
        errors: () => [reason],
      }),
    }),
    ClickedSaveProfile: () => {
      if (model.artistState !== 'idle') return { model }
      const errors = validateArtistProfile(model.profile)
      if (errors.length)
        return { model: modifyFields(model, { errors: () => errors }) }
      const attempt = model.artistAttempt + 1
      return {
        model: modifyFields(model, {
          artistAttempt: () => attempt,
          artistState: () => 'saving',
          notice: () => '',
          errors: () => [],
        }),
        commands: Option.match(model.maybeTenant, {
          onNone: () => [
            SaveProfile({
              profile: model.profile,
              drafts: model.drafts,
              attempt,
              edit: model.profileEdit,
            }),
          ],
          onSome: tenant =>
            Option.match(model.maybeArtistRevision, {
              onNone: () => [
                LoadArtist({
                  tenantId: tenant.id,
                  authAttempt: model.authAttempt,
                  attempt,
                  edit: model.profileEdit,
                }),
              ],
              onSome: expectedRevision => [
                SaveCloudArtist({
                  profile: model.profile,
                  expectedRevision,
                  tenantId: tenant.id,
                  authAttempt: model.authAttempt,
                  attempt,
                  edit: model.profileEdit,
                }),
              ],
            }),
        }),
      }
    },
    CompletedSaveProfile: ({ attempt, edit }) =>
      attempt !== model.artistAttempt
        ? { model }
        : {
            model: modifyFields(model, {
              artistState: () => 'idle',
              notice: () =>
                edit === model.profileEdit
                  ? 'Artist identity saved on this device.'
                  : 'Artist identity saved on this device. Your latest edits still need saving.',
            }),
          },
    FailedSaveProfile: ({ reason, attempt }) =>
      attempt !== model.artistAttempt
        ? { model }
        : {
            model: modifyFields(model, {
              artistState: () => 'idle',
              errors: () => [reason],
            }),
          },
    ClickedReloadProfile: () =>
      Option.match(model.maybeTenant, {
        onNone: () => ({ model }),
        onSome: tenant => ({
          model: modifyFields(model, {
            artistState: () => 'loading',
            artistAttempt: value => value + 1,
            errors: () => [],
          }),
          commands: [
            LoadArtist({
              tenantId: tenant.id,
              authAttempt: model.authAttempt,
              attempt: model.artistAttempt + 1,
              edit: model.profileEdit,
            }),
          ],
        }),
      }),
    LoadedArtist: ({ artist, tenantId, authAttempt, attempt, edit }) =>
      !ownsArtistResponse(model, tenantId, authAttempt, attempt)
        ? { model }
        : {
            model: modifyFields(model, {
              artistState: () => 'idle',
              maybeArtistRevision: () =>
                Option.some(
                  Option.match(artist, {
                    onNone: () => 0,
                    onSome: saved => saved.revision,
                  }),
                ),
              profile: profile =>
                edit === model.profileEdit
                  ? Option.match(artist, {
                      onNone: () => defaultProfile,
                      onSome: saved => saved.profile,
                    })
                  : profile,
              notice: () =>
                edit === model.profileEdit
                  ? Option.match(artist, {
                      onNone: () =>
                        'Set your artist identity and save it to this studio.',
                      onSome: () => 'Studio artist identity loaded.',
                    })
                  : 'Studio identity loaded. Your unsaved edits are still here.',
            }),
          },
    FailedLoadArtist: ({ reason, tenantId, authAttempt, attempt }) =>
      !ownsArtistResponse(model, tenantId, authAttempt, attempt)
        ? { model }
        : {
            model: modifyFields(model, {
              artistState: () => 'load-error',
              maybeArtistRevision: () => Option.none(),
              errors: () => [
                `${reason} Reload the studio identity to try again.`,
              ],
            }),
          },
    SavedCloudArtist: ({ artist, tenantId, authAttempt, attempt, edit }) =>
      !ownsArtistResponse(model, tenantId, authAttempt, attempt)
        ? { model }
        : {
            model: modifyFields(model, {
              artistState: () => 'idle',
              maybeArtistRevision: () => Option.some(artist.revision),
              notice: () =>
                edit === model.profileEdit
                  ? 'Artist identity saved to your studio. Reuse it on your next release.'
                  : 'Artist identity saved to your studio. Your latest edits still need saving.',
            }),
          },
    FailedSaveCloudArtist: ({
      reason,
      conflict,
      tenantId,
      authAttempt,
      attempt,
    }) =>
      !ownsArtistResponse(model, tenantId, authAttempt, attempt)
        ? { model }
        : {
            model: modifyFields(model, {
              artistState: () => (conflict ? 'conflict' : 'idle'),
              maybeArtistRevision: revision =>
                conflict ? Option.none() : revision,
              errors: () => [reason],
            }),
          },
    CompletedLoadStudio: ({ studio }) => ({
      model: modifyFields(model, {
        profile: profile =>
          model.profileEdit === 0 && Option.isNone(model.maybeTenant)
            ? studio.profile
            : profile,
        drafts: () => studio.drafts,
      }),
    }),
    FailedLoadStudio: ({ reason }) => ({
      model: modifyFields(model, { notice: () => reason }),
    }),
    UpdatedRevisionNote: ({ value }) => ({
      model: modifyFields(model, { revisionNote: () => value }),
    }),
    SubmittedRevisionNote: () =>
      model.revisionNote.trim()
        ? {
            model: modifyFields(model, {
              revisionNotes: notes => [...notes, model.revisionNote.trim()],
              revisionNote: () => '',
              notice: () =>
                'Note added to this brief. Save the draft to keep it on this device.',
            }),
          }
        : {
            model: modifyFields(model, {
              errors: () => ['Write a revision note first.'],
            }),
          },
    UpdatedInvitation: ({ value }) => ({
      model: modifyFields(model, { invitation: () => value }),
    }),
    SubmittedInvitation: () => ({
      model: modifyFields(model, {
        cloudState: () => 'connecting',
        errors: () => [],
        authAttempt: value => value + 1,
      }),
      commands: [
        ExchangeInvitation({
          invitation: model.invitation,
          attempt: model.authAttempt + 1,
        }),
      ],
    }),
    LoadedConnection: ({ available, tenant, attempt }) =>
      attempt !== model.authAttempt
        ? { model }
        : {
            model: modifyFields(model, {
              cloudAvailable: () => available,
              maybeTenant: () => tenant,
              invitation: () => '',
              cloudState: () => 'idle',
              artistState: () => (Option.isSome(tenant) ? 'loading' : 'idle'),
              maybeArtistRevision: () => Option.none(),
              artistAttempt: value => value + 1,
              profile: profile =>
                Option.isSome(tenant) ? defaultProfile : profile,
              profileEdit: value => (Option.isSome(tenant) ? value + 1 : value),
            }),
            commands: Option.match(tenant, {
              onNone: () => [],
              onSome: account => [
                LoadCloudLibrary({ tenantId: account.id }),
                LoadArtist({
                  tenantId: account.id,
                  authAttempt: model.authAttempt,
                  attempt: model.artistAttempt + 1,
                  edit: model.profileEdit + 1,
                }),
              ],
            }),
          },
    FailedConnection: ({ reason, attempt }) =>
      attempt !== model.authAttempt
        ? { model }
        : {
            model: modifyFields(model, {
              cloudState: () => 'idle',
              errors: () => [reason],
            }),
          },
    LoadedCloudLibrary: ({ releases, tenantId }) =>
      Option.exists(model.maybeTenant, tenant => tenant.id === tenantId)
        ? { model: modifyFields(model, { cloudReleases: () => releases }) }
        : { model },
    FailedCloudLibrary: ({ reason, tenantId }) =>
      Option.exists(model.maybeTenant, tenant => tenant.id === tenantId)
        ? { model: modifyFields(model, { notice: () => reason }) }
        : { model },
    RequestedProduction: () => {
      if (model.cloudState !== 'idle' || Option.isSome(model.maybeCloudId))
        return { model }
      const errors = [
        ...validateRelease({
          title: model.title,
          lyrics: model.lyrics,
          audioName: Option.match(model.maybeAudio, {
            onNone: () => '',
            onSome: audio => audio.name,
          }),
          audioDuration: Option.match(model.maybeAudio, {
            onNone: () => 0,
            onSome: audio => audio.duration,
          }),
        }),
        ...(!model.cloudAvailable || Option.isNone(model.maybeTenant)
          ? ['Connect your studio invitation before starting production.']
          : []),
        ...(Option.isSome(model.maybeTenant) &&
        Option.isNone(model.maybeArtistRevision)
          ? ['Load your studio artist identity before starting production.']
          : []),
      ]
      if (errors.length)
        return { model: modifyFields(model, { errors: () => errors }) }
      const attempt = model.cloudAttempt + 1
      return {
        model: modifyFields(model, {
          cloudAttempt: () => attempt,
          cloudState: () => 'uploading',
          errors: () => [],
        }),
        commands: [QueueRelease({ model, attempt })],
      }
    },
    QueuedProduction: ({ id, attempt }) =>
      attempt !== model.cloudAttempt
        ? { model }
        : {
            model: modifyFields(model, {
              cloudState: () => 'idle',
              maybeCloudId: () => Option.some(id),
              notice: () =>
                'Song uploaded and queued. Your worker will report progress here.',
            }),
            commands: [
              LoadCloudStatus({ id }),
              ...Option.match(model.maybeTenant, {
                onNone: () => [],
                onSome: tenant => [LoadCloudLibrary({ tenantId: tenant.id })],
              }),
            ],
          },
    FailedProduction: ({ reason, attempt }) =>
      attempt !== model.cloudAttempt
        ? { model }
        : {
            model: modifyFields(model, {
              cloudState: () => 'idle',
              errors: () => [reason],
            }),
          },
    SelectedCloudRelease: ({ id }) => ({
      model: modifyFields(model, {
        maybeCloudId: () => Option.some(id),
        maybeCloudStatus: () => Option.none(),
        maybeDraftId: () => Option.none(),
        maybeAudio: () => Option.none(),
        maybeBriefUrl: () => Option.none(),
        audioAttempt: value => value + 1,
        audioState: () => 'idle',
      }),
      commands: [
        LoadCloudStatus({ id }),
        ...releaseAudioCommands(model),
        ...releaseBriefCommands(model),
      ],
    }),
    RequestedCloudStatus: ({ id }) =>
      Option.contains(model.maybeCloudId, id)
        ? { model, commands: [LoadCloudStatus({ id })] }
        : { model },
    LoadedCloudStatus: ({ status }) =>
      Option.contains(model.maybeCloudId, status.id)
        ? {
            model: modifyFields(model, {
              maybeCloudStatus: () => Option.some(status),
              cloudReleases: releases =>
                releases.map(release =>
                  release.id === status.id
                    ? modifyFields(release, { state: () => status.state })
                    : release,
                ),
            }),
            commands: ['review', 'failed'].includes(status.state)
              ? []
              : [PollCloudStatus({ id: status.id })],
          }
        : { model },
    FailedCloudStatus: ({ id, reason }) =>
      Option.contains(model.maybeCloudId, id)
        ? {
            model: modifyFields(model, { notice: () => reason }),
            commands: [PollCloudStatus({ id })],
          }
        : { model },
    RequestedSignOut: () => ({
      model: modifyFields(model, {
        authAttempt: value => value + 1,
        artistAttempt: value => value + 1,
      }),
      commands: [SignOut({ attempt: model.authAttempt + 1 })],
    }),
    CompletedSignOut: ({ attempt }) =>
      attempt !== model.authAttempt
        ? { model }
        : {
            model: modifyFields(model, {
              maybeTenant: () => Option.none(),
              maybeCloudId: () => Option.none(),
              maybeCloudStatus: () => Option.none(),
              cloudReleases: () => [],
              cloudAttempt: value => value + 1,
              cloudState: () => 'idle',
              invitation: () => '',
              notice: () =>
                'Studio signed out. Device drafts remain in this browser.',
              profile: () => defaultProfile,
              profileEdit: value => value + 1,
              maybeArtistRevision: () => Option.none(),
              artistState: () => 'idle',
              artistAttempt: value => value + 1,
            }),
          },
  })

export const init: Runtime.ApplicationInit<Model, Message> = () => ({
  model: initialModel,
  commands: [LoadStudio(), LoadConnection({ attempt: 0 })],
})
