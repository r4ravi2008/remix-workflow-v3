import { Option, Schema } from 'effect'
import type { Document, HtmlBuilder } from 'foldkit/html'

import { archiveUrl, assetUrl, canDownloadKit } from './cloud'
import { ArtistProfile, formatDuration, outputs } from './domain'
import { Message, type Model } from './main'

const image = '/media/river-dusk.webp'
const releaseTitle = (model: Model) =>
  Option.match(model.maybeCloudStatus, {
    onSome: status => status.brief.title,
    onNone: () =>
      Option.match(model.maybeCloudId, {
        onNone: () => model.title || 'New release',
        onSome: id =>
          model.cloudReleases.find(release => release.id === id)?.title ??
          'Release',
      }),
  })
const releaseStateLabel = (state: string) => {
  const labels: Record<string, string> = {
    uploading: 'Uploading song',
    queued: 'Waiting to start',
    running: 'In production',
    'waiting-for-direction': 'Preparing direction',
    'waiting-for-review': 'Reviewing the pilot',
    'needs-reconciliation': 'Needs attention',
    review: 'Ready for review',
    failed: 'Needs attention',
  }
  return labels[state] ?? 'In production'
}
const icon = (name: string, h: HtmlBuilder<Message>, className = 'ui-icon') =>
  h.img([h.Src(`/icons/${name}.svg`), h.Alt(''), h.Class(className)])
const button = (
  label: string,
  message: Message,
  className: string,
  h: HtmlBuilder<Message>,
) =>
  h.button([h.Class(className), h.Type('button'), h.OnClick(message)], [label])

const rail = (model: Model, h: HtmlBuilder<Message>) =>
  h.aside(
    [h.Class(`rail ${model.libraryState === 'open' ? 'library-open' : ''}`)],
    [
      h.a(
        [h.Class('brand'), h.Href('#main'), h.AriaLabel('Release Kit studio')],
        [
          h.img([h.Src('/mark.svg'), h.Alt(''), h.Class('brand-mark')]),
          h.span([], ['Release Kit']),
        ],
      ),
      h.p([h.Class('rail-label')], ['YOUR STUDIO']),
      h.nav(
        [h.AriaLabel('Studio')],
        [
          h.button(
            [
              h.Class(`nav-item ${model.pane === 'release' ? 'active' : ''}`),
              h.Type('button'),
              h.AriaPressed(String(model.pane === 'release')),
              h.OnClick(Message.SelectedPane({ pane: 'release' })),
            ],
            [icon('releases', h, 'ui-icon nav-symbol'), 'Releases'],
          ),
          h.button(
            [
              h.Class(`nav-item ${model.pane === 'artist' ? 'active' : ''}`),
              h.Type('button'),
              h.AriaPressed(String(model.pane === 'artist')),
              h.OnClick(Message.SelectedPane({ pane: 'artist' })),
            ],
            [icon('artist', h, 'ui-icon nav-symbol'), 'Artist identity'],
          ),
          h.button(
            [
              h.Class(`nav-item ${model.pane === 'about' ? 'active' : ''}`),
              h.Type('button'),
              h.AriaPressed(String(model.pane === 'about')),
              h.OnClick(Message.SelectedPane({ pane: 'about' })),
            ],
            [icon('help', h, 'ui-icon nav-symbol'), 'How it works'],
          ),
        ],
      ),
      h.div(
        [h.Class('release-library'), h.Id('release-library')],
        [
          h.div(
            [h.Class('rail-heading')],
            [
              h.p([h.Class('rail-label')], ['SAVED RELEASES']),
              h.button(
                [
                  h.Class('new-release'),
                  h.Type('button'),
                  h.AriaLabel('New release'),
                  h.OnClick(Message.ClickedNewRelease()),
                ],
                [icon('plus', h)],
              ),
            ],
          ),
          model.drafts.length
            ? h.ul(
                [h.Class('draft-list')],
                model.drafts.map(draft =>
                  h.keyed('li')(
                    draft.id,
                    [],
                    [
                      h.button(
                        [
                          h.Class(
                            `draft-item ${Option.contains(model.maybeDraftId, draft.id) ? 'selected' : ''}`,
                          ),
                          h.Type('button'),
                          h.OnClick(Message.SelectedDraft({ id: draft.id })),
                        ],
                        [
                          h.span([h.Class('draft-title')], [draft.title]),
                          h.span(
                            [h.Class('draft-status')],
                            [`Draft · ${formatDuration(draft.audioDuration)}`],
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              )
            : model.cloudReleases.length
              ? h.empty
              : h.p(
                  [h.Class('library-empty')],
                  ['Your saved releases will live here. Start with a song.'],
                ),
          model.cloudReleases.length
            ? h.ul(
                [h.Class('draft-list')],
                model.cloudReleases.map(release =>
                  h.keyed('li')(
                    release.id,
                    [],
                    [
                      h.button(
                        [
                          h.Class(
                            `draft-item ${Option.contains(model.maybeCloudId, release.id) ? 'selected' : ''}`,
                          ),
                          h.Type('button'),
                          h.Id(`cloud-release-${release.id}`),
                          h.OnClick(
                            Message.SelectedCloudRelease({ id: release.id }),
                          ),
                        ],
                        [
                          h.span([h.Class('draft-title')], [release.title]),
                          h.span(
                            [h.Class('draft-status')],
                            [releaseStateLabel(release.state)],
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              )
            : h.empty,
        ],
      ),
      h.div(
        [h.Class('rail-bottom')],
        [
          h.div(
            [h.Class('avatar'), h.AriaHidden(true)],
            [model.profile.name.slice(0, 1).toUpperCase() || 'A'],
          ),
          h.div(
            [],
            [
              h.p(
                [h.Class('artist-name')],
                [model.profile.name || 'My artist'],
              ),
              h.p(
                [h.Class('muted tiny')],
                [
                  Option.match(model.maybeTenant, {
                    onNone: () => 'Device drafts',
                    onSome: tenant => tenant.name,
                  }),
                ],
              ),
            ],
          ),
        ],
      ),
    ],
  )

const manifest = (model: Model, h: HtmlBuilder<Message>) =>
  h.aside(
    [h.Class('manifest'), h.AriaLabel('Release kit formats')],
    [
      h.div(
        [h.Class('section-heading')],
        [h.h2([], ['Your release kit']), h.span([h.Class('count')], ['06'])],
      ),
      h.p(
        [h.Class('muted manifest-intro')],
        ['One visual world. Every place your song goes.'],
      ),
      h.ul(
        [h.Class('output-list')],
        outputs.map(output =>
          h.keyed('li')(
            output.id,
            [],
            [
              h.button(
                [
                  h.Class(
                    `output-item ${model.selectedOutput === output.id ? 'selected' : ''}`,
                  ),
                  h.Type('button'),
                  h.AriaPressed(String(model.selectedOutput === output.id)),
                  h.OnClick(Message.SelectedOutput({ id: output.id })),
                ],
                [
                  h.span([
                    h.Class(`format-icon ${output.ratio}`),
                    h.AriaHidden(true),
                  ]),
                  h.span(
                    [h.Class('output-copy')],
                    [
                      h.span([h.Class('output-name')], [output.name]),
                      h.span([h.Class('output-format')], [output.format]),
                    ],
                  ),
                  icon('arrow', h, 'ui-icon output-arrow'),
                ],
              ),
            ],
          ),
        ),
      ),
      h.div(
        [h.Class('production-state')],
        [
          h.span([h.Class('status-dot')]),
          h.p(
            [],
            [
              Option.match(model.maybeCloudStatus, {
                onNone: () =>
                  model.cloudAvailable
                    ? 'Studio production queue'
                    : 'Production not connected',
                onSome: status => status.job?.phase ?? 'Preparing upload',
              }),
            ],
          ),
          h.p(
            [h.Class('muted tiny')],
            [
              Option.match(model.maybeCloudStatus, {
                onNone: () =>
                  model.cloudAvailable
                    ? 'Upload your song to queue a complete release kit.'
                    : 'Save the brief now. Rendering will become available after the production worker is connected.',
                onSome: status =>
                  status.state === 'review'
                    ? 'Six outputs measured. Watch and listen before accepting the release.'
                    : status.state === 'waiting-for-direction'
                      ? 'Waiting for a completed production direction.'
                      : status.state === 'waiting-for-review'
                        ? 'Pilot review is pending before full-song production.'
                        : (status.job?.error ??
                          `${Math.round((status.job?.progress ?? 0) * 100)}% · Workstation progress`),
              }),
            ],
          ),
        ],
      ),
    ],
  )

const screening = (model: Model, h: HtmlBuilder<Message>) => {
  const output =
    outputs.find(item => item.id === model.selectedOutput) ?? outputs[0]!
  const asset = Option.flatMap(model.maybeCloudStatus, status =>
    Option.fromUndefinedOr(
      status.assets.find(item => item.outputId === model.selectedOutput),
    ),
  )
  return h.section(
    [h.Class('screening'), h.AriaLabel('Visual direction preview')],
    [
      h.div(
        [h.Class('screening-caption')],
        [
          h.span([], ['VISUAL DIRECTION']),
          h.span(
            [h.Class('preview-label')],
            [
              Option.isSome(asset)
                ? 'Release output · awaiting review'
                : 'Illustrative preview',
            ],
          ),
        ],
      ),
      h.div(
        [h.Class(`viewer aperture-${output.ratio}`)],
        [
          Option.match(asset, {
            onSome: item =>
              item.contentType === 'video/mp4'
                ? h.video([
                    h.Class('film-image'),
                    h.Src(assetUrl({ id: item.id })),
                    h.Controls(true),
                    h.Preload('metadata'),
                    h.AriaLabel(`${output.name} release output`),
                  ])
                : h.img([
                    h.Class('film-image'),
                    h.Src(assetUrl({ id: item.id })),
                    h.Alt(`${output.name} release output`),
                  ]),
            onNone: () =>
              h.div(
                [h.Class(`film-frame ${output.ratio}`)],
                [
                  h.img([
                    h.Class('film-image'),
                    h.Src(image),
                    h.Alt(
                      'Illustrative film still: a person on a bridge above a river at dusk. This is sample artwork, not a rendered music video.',
                    ),
                  ]),
                  h.div(
                    [h.Class('film-title')],
                    [h.h2([], [releaseTitle(model)])],
                  ),
                  h.span([h.Class('frame-format')], [output.format]),
                ],
              ),
          }),
        ],
      ),
      h.div(
        [h.Class('viewer-footer'), h.AriaLive('polite')],
        [
          h.div(
            [],
            [
              h.strong([], [output.name]),
              h.span([h.Class('muted')], [output.description]),
            ],
          ),
          Option.match(asset, {
            onNone: () =>
              h.span([h.Class('muted tiny')], ['No film rendered yet']),
            onSome: item =>
              h.a(
                [
                  h.Class('button secondary'),
                  h.Href(assetUrl({ id: item.id })),
                  h.Download(
                    `${releaseTitle(model)}-${item.outputId}.${item.contentType === 'video/mp4' ? 'mp4' : 'jpg'}`,
                  ),
                ],
                ['Download output'],
              ),
          }),
          ...Option.match(model.maybeCloudStatus, {
            onNone: () => [],
            onSome: status =>
              canDownloadKit(status)
                ? [
                    h.a(
                      [
                        h.Class('button primary'),
                        h.Href(archiveUrl({ id: status.id })),
                        h.Download(`release-kit-${status.id}.zip`),
                      ],
                      ['Download release kit'],
                    ),
                  ]
                : [],
          }),
        ],
      ),
      h.div(
        [h.Class('creative-layers')],
        [
          h.div(
            [],
            [
              h.span([h.Class('layer-index')], ['01']),
              h.h3([], ['Cinematic direction']),
              h.p([], ['A story and a visual world that hold together.']),
            ],
          ),
          h.div(
            [],
            [
              h.span([h.Class('layer-index')], ['02']),
              h.h3([], ['Lyric expression']),
              h.p([], ['Your words become part of the composition.']),
            ],
          ),
          h.div(
            [],
            [
              h.span([h.Class('layer-index')], ['03']),
              h.h3([], ['Music-responsive motion']),
              h.p([], ['Rhythm moves the environment around them.']),
            ],
          ),
        ],
      ),
    ],
  )
}

const feedback = (model: Model, h: HtmlBuilder<Message>) =>
  h.div(
    [h.Class('feedback'), h.AriaLive('polite')],
    [
      model.errors.length
        ? h.ul(
            [h.Class('errors'), h.Role('alert')],
            model.errors.map(error => h.li([], [error])),
          )
        : h.empty,
      model.notice
        ? h.p([h.Class('notice'), h.Role('status')], [model.notice])
        : h.empty,
    ],
  )

const songForm = (model: Model, h: HtmlBuilder<Message>) =>
  h.section(
    [h.Class('song-form')],
    [
      h.div(
        [h.Class('section-heading')],
        [
          h.h2([], ['Start with your song']),
          h.span(
            [h.Class('muted tiny')],
            ['Audio uploads when you start production'],
          ),
        ],
      ),
      h.div(
        [h.Class('song-input-grid')],
        [
          h.div(
            [h.Class('upload-block')],
            [
              h.label(
                [h.For('audio-upload'), h.Class('upload-label')],
                [
                  h.span(
                    [h.Class('upload-symbol'), h.AriaHidden(true)],
                    [icon('upload', h)],
                  ),
                  h.strong(
                    [],
                    [
                      model.audioState === 'reading'
                        ? 'Inspecting your audio…'
                        : 'Choose your audio',
                    ],
                  ),
                  h.span([], ['WAV, MP3, M4A · up to 100 MB']),
                ],
              ),
              h.input([
                h.Id('audio-upload'),
                h.Type('file'),
                h.Accept('audio/*,.wav,.mp3,.m4a,.aac,.ogg,.flac'),
                h.OnFileChange(files => Message.SelectedAudio({ files })),
                h.AriaLabel('Choose your audio file'),
              ]),
              Option.match(model.maybeAudio, {
                onNone: () =>
                  h.p(
                    [h.Class('muted tiny upload-hint')],
                    ['A finished mix is all you need to begin.'],
                  ),
                onSome: audio =>
                  h.div(
                    [h.Class('audio-details')],
                    [
                      h.p([h.Class('audio-filename')], [audio.name]),
                      h.p(
                        [h.Class('muted tiny')],
                        [
                          `${formatDuration(audio.duration)} · ${(audio.bytes / 1024 / 1024).toFixed(1)} MB · SHA-256 verified locally`,
                        ],
                      ),
                      h.audio([
                        h.Src(audio.url),
                        h.Controls(true),
                        h.Preload('metadata'),
                        h.AriaLabel('Preview your uploaded song'),
                      ]),
                    ],
                  ),
              }),
            ],
          ),
          h.div(
            [h.Class('song-fields')],
            [
              h.label([h.For('song-title')], ['Song title']),
              h.input([
                h.Id('song-title'),
                h.Type('text'),
                h.Value(model.title),
                h.Placeholder('Name your release'),
                h.Maxlength(120),
                h.OnInput(value => Message.UpdatedTitle({ value })),
              ]),
              h.label([h.For('song-language')], ['Lyric language']),
              h.select(
                [
                  h.Id('song-language'),
                  h.Value(model.language),
                  h.OnChange(value => Message.UpdatedLanguage({ value })),
                ],
                ['Telugu', 'Hindi', 'Tamil'].map(language =>
                  h.option([h.Value(language)], [language]),
                ),
              ),
              h.p(
                [h.Class('muted tiny')],
                ['Keep the exact lyrics in their original script.'],
              ),
            ],
          ),
        ],
      ),
      h.label([h.For('song-lyrics')], ['Lyrics']),
      h.textarea([
        h.Id('song-lyrics'),
        h.Rows(5),
        h.Value(model.lyrics),
        h.Placeholder('Paste the exact lyrics here…'),
        h.OnInput(value => Message.UpdatedLyrics({ value })),
      ]),
      h.p(
        [h.Class('muted tiny')],
        [
          'Lyrics, cinematic direction, and music response are included together in every film.',
        ],
      ),
    ],
  )

const submittedSong = (model: Model, h: HtmlBuilder<Message>) =>
  Option.match(model.maybeCloudStatus, {
    onNone: () =>
      h.p(
        [h.Class('muted section-intro'), h.AriaLive('polite')],
        ['Loading the submitted song…'],
      ),
    onSome: status =>
      h.section(
        [h.Class('song-form')],
        [
          h.h2([], ['Submitted song']),
          h.p(
            [h.Class('muted section-intro')],
            [
              'This song and direction were saved when you submitted the release.',
            ],
          ),
          h.p([h.Class('audio-filename')], [status.brief.audioName]),
          h.p(
            [h.Class('muted')],
            [
              `${formatDuration(status.brief.audioDuration)} · ${status.brief.language} · ${(status.brief.audioBytes / 1024 / 1024).toFixed(1)} MB`,
            ],
          ),
          h.h3([], ['Artist direction']),
          h.p(
            [],
            [
              `${status.brief.profile.name} · ${status.brief.profile.palette} · ${status.brief.profile.intensity}`,
            ],
          ),
          h.p([], [status.brief.profile.identity]),
          h.details(
            [],
            [
              h.summary([], ['Submitted lyrics']),
              h.pre([h.Class('submitted-lyrics')], [status.brief.lyrics]),
            ],
          ),
        ],
      ),
  })

const artistForm = (model: Model, h: HtmlBuilder<Message>) =>
  h.section(
    [h.Class('artist-form')],
    [
      h.div(
        [h.Class('section-heading')],
        [
          h.h2([], ['A world that feels like you']),
          h.span([h.Class('muted tiny')], ['Reusable artist identity']),
        ],
      ),
      h.p(
        [h.Class('muted section-intro')],
        ['Carry the same visual language from one release to the next.'],
      ),
      h.div(
        [h.Class('artist-fields')],
        [
          h.div(
            [],
            [
              h.label([h.For('artist-name')], ['Artist name']),
              h.input([
                h.Id('artist-name'),
                h.Value(model.profile.name),
                h.Maxlength(80),
                h.OnInput(value => Message.UpdatedArtistName({ value })),
              ]),
            ],
          ),
          h.div(
            [],
            [
              h.label([h.For('artist-palette')], ['Visual palette']),
              h.select(
                [
                  h.Id('artist-palette'),
                  h.Value(model.profile.palette),
                  h.OnChange(value =>
                    Message.UpdatedPalette({
                      value: Schema.decodeUnknownSync(
                        ArtistProfile.fields.palette,
                      )(value),
                    }),
                  ),
                ],
                ['River dusk', 'Golden hour', 'Midnight city'].map(value =>
                  h.option([h.Value(value)], [value]),
                ),
              ),
            ],
          ),
          h.div(
            [],
            [
              h.label([h.For('artist-intensity')], ['Music response']),
              h.select(
                [
                  h.Id('artist-intensity'),
                  h.Value(model.profile.intensity),
                  h.OnChange(value =>
                    Message.UpdatedIntensity({
                      value: Schema.decodeUnknownSync(
                        ArtistProfile.fields.intensity,
                      )(value),
                    }),
                  ),
                ],
                ['Restrained', 'Balanced', 'Expressive'].map(value =>
                  h.option([h.Value(value)], [value]),
                ),
              ),
            ],
          ),
        ],
      ),
      h.label([h.For('artist-identity')], ['Describe your visual identity']),
      h.textarea([
        h.Id('artist-identity'),
        h.Rows(3),
        h.Value(model.profile.identity),
        h.Placeholder(
          'Recurring characters, places, textures, and the feeling you want to be known for…',
        ),
        h.Maxlength(5000),
        h.OnInput(value => Message.UpdatedIdentity({ value })),
      ]),
      h.div(
        [h.Class('profile-footer')],
        [
          h.p(
            [h.Class('muted tiny')],
            [
              'Motion follows the music in the environment, while people and lyrics remain clear.',
            ],
          ),
          h.button(
            [
              h.Type('button'),
              h.Class('button secondary'),
              h.Disabled(model.artistState !== 'idle'),
              h.OnClick(Message.ClickedSaveProfile()),
            ],
            [
              model.artistState === 'saving'
                ? 'Saving identity…'
                : 'Save artist identity',
            ],
          ),
        ],
      ),
      h.p(
        [h.Class('muted tiny'), h.AriaLive('polite')],
        [
          model.artistState === 'loading'
            ? 'Loading your studio identity…'
            : Option.isSome(model.maybeTenant)
              ? 'Saved identity belongs to this studio. Queued releases keep their original direction.'
              : 'Sign in to save this identity to your studio, or save it on this device.',
        ],
      ),
      ['load-error', 'conflict'].includes(model.artistState)
        ? h.div(
            [h.Class('profile-footer')],
            [
              h.p(
                [h.Class('muted tiny')],
                [
                  'Reload replaces these fields with the saved studio identity.',
                ],
              ),
              button(
                'Reload studio identity',
                Message.ClickedReloadProfile(),
                'button secondary',
                h,
              ),
            ],
          )
        : h.empty,
    ],
  )

const revisionForm = (model: Model, h: HtmlBuilder<Message>) =>
  h.section(
    [h.Class('revision-form')],
    [
      h.h2([], ['Notes for the next pass']),
      h.p(
        [h.Class('muted section-intro')],
        [
          'Describe what should change and where in the song. Notes are part of the brief.',
        ],
      ),
      h.form(
        [h.OnSubmit(Message.SubmittedRevisionNote())],
        [
          h.label([h.For('revision-note')], ['Revision note']),
          h.textarea([
            h.Id('revision-note'),
            h.Rows(2),
            h.Value(model.revisionNote),
            h.Placeholder(
              'At the chorus, let the lights move with the beat. Keep the person still.',
            ),
            h.OnInput(value => Message.UpdatedRevisionNote({ value })),
          ]),
          h.button(
            [h.Class('button secondary'), h.Type('submit')],
            ['Add note'],
          ),
        ],
      ),
      model.revisionNotes.length
        ? h.ol(
            [h.Class('revision-list')],
            model.revisionNotes.map(note => h.li([], [note])),
          )
        : h.empty,
    ],
  )

const connection = (model: Model, h: HtmlBuilder<Message>) =>
  h.section(
    [h.Class('song-form')],
    [
      h.h2(
        [],
        [
          Option.isSome(model.maybeTenant)
            ? 'Studio connected'
            : 'Connect your studio',
        ],
      ),
      Option.match(model.maybeTenant, {
        onSome: tenant =>
          h.div(
            [],
            [
              h.p(
                [h.Class('muted')],
                [
                  `${tenant.name} · Your songs and outputs are private to this studio.`,
                ],
              ),
              h.button(
                [
                  h.Class('button secondary'),
                  h.Type('button'),
                  h.OnClick(Message.RequestedSignOut()),
                ],
                ['Sign out'],
              ),
            ],
          ),
        onNone: () =>
          model.cloudAvailable
            ? h.form(
                [h.OnSubmit(Message.SubmittedInvitation())],
                [
                  h.label([h.For('studio-invitation')], ['Studio invitation']),
                  h.input([
                    h.Id('studio-invitation'),
                    h.Type('password'),
                    h.Value(model.invitation),
                    h.Autocomplete('off'),
                    h.OnInput(value => Message.UpdatedInvitation({ value })),
                  ]),
                  h.button(
                    [
                      h.Class('button secondary'),
                      h.Type('submit'),
                      h.Disabled(model.cloudState === 'connecting'),
                    ],
                    [
                      model.cloudState === 'connecting'
                        ? 'Connecting…'
                        : 'Connect studio',
                    ],
                  ),
                ],
              )
            : h.p(
                [h.Class('muted')],
                [
                  'The hosted production API is being connected. You can keep a device draft.',
                ],
              ),
      }),
    ],
  )

const about = (h: HtmlBuilder<Message>) =>
  h.section(
    [h.Class('about-panel')],
    [
      h.h2([], ['One song. One complete release.']),
      h.p(
        [h.Class('section-intro')],
        [
          'The production service will direct a film, place original-script lyrics in its visual world, and let the music shape its environment. The same direction carries into three vertical promos and cover artwork.',
        ],
      ),
      h.ol(
        [h.Class('how-list')],
        [
          h.li(
            [],
            [
              h.strong([], ['Bring the finished song']),
              h.p(
                [],
                [
                  'Supply audio and exact lyrics. Set your artist identity once, then reuse it.',
                ],
              ),
            ],
          ),
          h.li(
            [],
            [
              h.strong([], ['Produce the release kit']),
              h.p(
                [],
                [
                  'Your song becomes a cinematic film with original-script lyrics and music-responsive environments.',
                ],
              ),
            ],
          ),
          h.li(
            [],
            [
              h.strong([], ['Review and release']),
              h.p(
                [],
                [
                  'Review the full film, hear the mix, request a revision, and download verified outputs.',
                ],
              ),
            ],
          ),
        ],
      ),
      h.div(
        [h.Class('preview-boundary')],
        [
          h.h3([], ['What works in this preview']),
          h.p(
            [],
            [
              'Inspect and preview your song, save device drafts, and set artist identity. With a studio invitation, upload your song to the private production queue and track the worker’s progress.',
            ],
          ),
          h.p(
            [],
            [
              'Completed kits appear here for playback and download after all six outputs pass technical checks. Creative acceptance follows a full watch and listen.',
            ],
          ),
        ],
      ),
    ],
  )

export const view = (model: Model, h: HtmlBuilder<Message>): Document => {
  const viewingRelease = Option.isSome(model.maybeCloudId)
  const draft = Option.match(model.maybeDraftId, {
    onNone: () => undefined,
    onSome: id => model.drafts.find(item => item.id === id),
  })
  return {
    title: `${releaseTitle(model)} — Release Kit`,
    body: h.div(
      [h.Class('studio-shell')],
      [
        h.a([h.Class('skip-link'), h.Href('#main')], ['Skip to release']),
        rail(model, h),
        h.main(
          [h.Id('main'), h.Class('main')],
          [
            h.header(
              [h.Class('workspace-header')],
              [
                h.div(
                  [],
                  [
                    h.h1([], [releaseTitle(model)]),
                    h.div(
                      [h.Class('release-meta')],
                      viewingRelease
                        ? Option.match(model.maybeCloudStatus, {
                            onNone: () => [h.span([], ['Loading release…'])],
                            onSome: status => [
                              h.span(
                                [h.Class('draft-badge')],
                                [releaseStateLabel(status.state)],
                              ),
                              h.span([], [status.brief.language]),
                              h.span(
                                [],
                                [formatDuration(status.brief.audioDuration)],
                              ),
                            ],
                          })
                        : [
                            h.span([h.Class('draft-badge')], ['Draft']),
                            h.span([], [model.language]),
                            Option.match(model.maybeAudio, {
                              onNone: () =>
                                h.span([], ['Add your audio to begin']),
                              onSome: audio =>
                                h.span([], [formatDuration(audio.duration)]),
                            }),
                          ],
                    ),
                  ],
                ),
                h.div(
                  [h.Class('header-actions')],
                  viewingRelease
                    ? [
                        button(
                          'New release',
                          Message.ClickedNewRelease(),
                          'button primary',
                          h,
                        ),
                      ]
                    : [
                        draft
                          ? Option.match(model.maybeBriefUrl, {
                              onNone: () => h.empty,
                              onSome: url =>
                                h.a(
                                  [
                                    h.Class('button secondary'),
                                    h.Download(
                                      `${draft.title.replace(/[^\p{L}\p{N}]+/gu, '-').toLowerCase()}-brief.json`,
                                    ),
                                    h.Href(url),
                                  ],
                                  ['Export saved brief'],
                                ),
                            })
                          : h.empty,
                        h.button(
                          [
                            h.Class('button primary'),
                            h.Type('button'),
                            h.Disabled(
                              model.audioState === 'reading' ||
                                model.saveState === 'saving',
                            ),
                            h.OnClick(Message.SubmittedDraft()),
                          ],
                          [
                            model.saveState === 'saving'
                              ? 'Saving…'
                              : 'Save draft',
                            icon('arrow-light', h),
                          ],
                        ),
                        model.cloudAvailable
                          ? h.button(
                              [
                                h.Class('button primary'),
                                h.Type('button'),
                                h.Disabled(
                                  model.cloudState !== 'idle' ||
                                    Option.isNone(model.maybeTenant) ||
                                    Option.isNone(model.maybeArtistRevision),
                                ),
                                h.OnClick(Message.RequestedProduction()),
                              ],
                              [
                                model.cloudState === 'uploading'
                                  ? 'Uploading song…'
                                  : 'Produce release kit',
                              ],
                            )
                          : h.empty,
                      ],
                ),
              ],
            ),
            feedback(model, h),
            h.div(
              [h.Class('review-grid')],
              [screening(model, h), manifest(model, h)],
            ),
            h.div(
              [h.Class('editing-area')],
              model.pane === 'about'
                ? [about(h)]
                : model.pane === 'artist'
                  ? [artistForm(model, h)]
                  : [
                      connection(model, h),
                      ...(viewingRelease
                        ? [submittedSong(model, h)]
                        : [
                            songForm(model, h),
                            artistForm(model, h),
                            revisionForm(model, h),
                          ]),
                    ],
            ),
            h.footer(
              [h.Class('studio-footer')],
              [
                h.p([], ['Made for artists who keep making.']),
                h.p(
                  [],
                  [
                    model.cloudAvailable
                      ? 'Private studio · Workstation production'
                      : 'Frontend preview · Production not connected',
                  ],
                ),
              ],
            ),
          ],
        ),
      ],
    ),
  }
}
