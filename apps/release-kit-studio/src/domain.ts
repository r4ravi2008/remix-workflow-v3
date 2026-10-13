import { Schema } from 'effect'

export const OutputId = Schema.Literals([
  'film',
  'short-1',
  'short-2',
  'short-3',
  'thumbnail',
  'artwork',
])
export type OutputId = typeof OutputId.Type

export const ArtistProfile = Schema.Struct({
  name: Schema.String,
  identity: Schema.String,
  palette: Schema.Literals(['River dusk', 'Golden hour', 'Midnight city']),
  intensity: Schema.Literals(['Restrained', 'Balanced', 'Expressive']),
})
export type ArtistProfile = typeof ArtistProfile.Type
export const ReleaseBrief = Schema.Struct({
  title: Schema.String,
  lyrics: Schema.String,
  language: Schema.String,
  audioName: Schema.String,
  audioSha256: Schema.String,
  audioDuration: Schema.Number,
  audioBytes: Schema.Number,
  profile: ArtistProfile,
})
export type ReleaseBrief = typeof ReleaseBrief.Type
export const SavedArtist = Schema.Struct({
  profile: ArtistProfile,
  revision: Schema.Number,
  updatedAt: Schema.Number,
})
export type SavedArtist = typeof SavedArtist.Type
export const validateArtistProfile = (
  profile: ArtistProfile,
): ReadonlyArray<string> => [
  ...(profile.name.trim() && profile.name.length <= 200
    ? []
    : ['Add an artist name of up to 200 characters.']),
  ...(profile.identity.trim() && profile.identity.length <= 5000
    ? []
    : ['Describe your visual identity in up to 5,000 characters.']),
]

export const ReleaseDraft = Schema.Struct({
  schemaVersion: Schema.Literal(1),
  id: Schema.String,
  title: Schema.String,
  lyrics: Schema.String,
  language: Schema.String,
  audioName: Schema.String,
  audioSha256: Schema.String,
  audioDuration: Schema.Number,
  audioBytes: Schema.Number,
  profile: ArtistProfile,
  createdAt: Schema.String,
  revisionNotes: Schema.Array(Schema.String),
  status: Schema.Literal('draft'),
})
export type ReleaseDraft = typeof ReleaseDraft.Type

export const outputs: ReadonlyArray<{
  id: OutputId
  name: string
  format: string
  description: string
  ratio: string
}> = [
  {
    id: 'film',
    name: 'Music video',
    format: '16:9 · 1080p',
    description: 'The full song, directed as one film.',
    ratio: 'wide',
  },
  {
    id: 'short-1',
    name: 'Opening hook',
    format: '9:16 · up to 30s',
    description: 'A first impression with its own framing.',
    ratio: 'portrait',
  },
  {
    id: 'short-2',
    name: 'Chorus moment',
    format: '9:16 · up to 30s',
    description: 'The musical peak, composed for mobile.',
    ratio: 'portrait',
  },
  {
    id: 'short-3',
    name: 'Story moment',
    format: '9:16 · up to 30s',
    description: 'A different reason to hear the song.',
    ratio: 'portrait',
  },
  {
    id: 'thumbnail',
    name: 'Thumbnail',
    format: '16:9 · JPG',
    description: 'A recognizable cover for the film.',
    ratio: 'wide',
  },
  {
    id: 'artwork',
    name: 'Cover artwork',
    format: '1:1 · JPG',
    description: 'The same visual world, in a square.',
    ratio: 'square',
  },
]

export const defaultProfile: ArtistProfile = {
  name: 'My artist',
  identity:
    'A cinematic world with recurring places, expressive native-script lyrics, and music-responsive environments.',
  palette: 'River dusk',
  intensity: 'Balanced',
}

export const formatDuration = (seconds: number): string => {
  const minutes = Math.floor(seconds / 60)
  const remainder = Math.floor(seconds % 60)
    .toString()
    .padStart(2, '0')
  return `${minutes}:${remainder}`
}

export const validateRelease = (input: {
  title: string
  lyrics: string
  audioName: string
  audioDuration: number
}): ReadonlyArray<string> => [
  ...(input.title.trim() ? [] : ['Add a song title.']),
  ...(input.lyrics.trim()
    ? []
    : ['Add the exact lyrics in their original script.']),
  ...(input.audioName ? [] : ['Choose an audio file.']),
  ...(Number.isFinite(input.audioDuration) && input.audioDuration > 0
    ? []
    : ['Choose a playable audio file.']),
]
