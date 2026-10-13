import { Schema } from 'effect'

import { OutputId } from '../src/domain'

export const Id = Schema.String.check(Schema.isPattern(/^[a-zA-Z0-9_-]{1,80}$/))
const Hash = Schema.String.check(Schema.isPattern(/^[a-f0-9]{64}$/))
const Frame = Schema.Int.check(Schema.isBetween({ minimum: 0, maximum: 21600 }))
const PositiveFrame = Schema.Int.check(
  Schema.isBetween({ minimum: 1, maximum: 21600 }),
)
const Seconds = Schema.Finite.check(
  Schema.isBetween({ minimum: 0, maximum: 900 }),
)
const Canvas = Schema.Int.check(
  Schema.isBetween({ minimum: 16, maximum: 1920 }),
)
export const Asset = Schema.Struct({
  id: Id,
  kind: Schema.Literals(['audio', 'video', 'image', 'mask']),
  sha256: Hash,
  bytes: Schema.Int.check(
    Schema.isBetween({ minimum: 1, maximum: 2147483648 }),
  ),
  width: Schema.Int.check(Schema.isBetween({ minimum: 0, maximum: 8192 })),
  height: Schema.Int.check(Schema.isBetween({ minimum: 0, maximum: 8192 })),
  duration: Seconds,
})
export type Asset = typeof Asset.Type
export const Transform = Schema.Struct({
  centerX: Schema.Finite.check(Schema.isBetween({ minimum: 0, maximum: 1 })),
  centerY: Schema.Finite.check(Schema.isBetween({ minimum: 0, maximum: 1 })),
  zoom: Schema.Finite.check(Schema.isBetween({ minimum: 1, maximum: 4 })),
})
export const Color = Schema.Struct({
  brightness: Schema.Finite.check(
    Schema.isBetween({ minimum: -0.2, maximum: 0.2 }),
  ),
  contrast: Schema.Finite.check(Schema.isBetween({ minimum: 0.5, maximum: 2 })),
  saturation: Schema.Finite.check(Schema.isBetween({ minimum: 0, maximum: 2 })),
})
export const Reactive = Schema.Struct({
  maskAssetId: Id,
  audioSha256: Hash,
  points: Schema.Array(
    Schema.Struct({
      frame: Frame,
      value: Schema.Finite.check(Schema.isBetween({ minimum: 0, maximum: 1 })),
    }),
  ).check(Schema.isMaxLength(21601)),
})
export const Clip = Schema.Struct({
  id: Id,
  assetId: Id,
  at: Frame,
  inFrame: Frame,
  frames: PositiveFrame,
  transform: Transform,
  color: Color,
  fadeIn: Frame,
  fadeOut: Frame,
  reactive: Schema.NullOr(Reactive),
})
export type Clip = typeof Clip.Type
export const Caption = Schema.Struct({
  id: Id,
  kind: Schema.Literals(['lyric', 'title']),
  start: Frame,
  end: PositiveFrame,
  text: Schema.String.check(
    Schema.isMinLength(1),
    Schema.isMaxLength(1000),
    Schema.isPattern(/^[^{}\\]*$/u),
  ),
  font: Schema.Literals([
    'Noto Sans Telugu',
    'Noto Sans Devanagari',
    'Noto Sans Tamil',
    'Noto Sans',
  ]),
  size: Schema.Int.check(Schema.isBetween({ minimum: 16, maximum: 160 })),
  marginBottom: Schema.Int.check(
    Schema.isBetween({ minimum: 0, maximum: 600 }),
  ),
})
export const Composition = Schema.Struct({
  id: OutputId,
  width: Canvas,
  height: Canvas,
  frames: PositiveFrame,
  rationale: Schema.String.check(Schema.isMaxLength(2000)),
  audio: Schema.NullOr(Schema.Struct({ assetId: Id, startSeconds: Seconds })),
  clips: Schema.Array(Clip).check(Schema.isMaxLength(500)),
  captions: Schema.Array(Caption).check(Schema.isMaxLength(1000)),
})
export type Composition = typeof Composition.Type
export const Project = Schema.Struct({
  schemaVersion: Schema.Literal(1),
  releaseId: Id,
  briefSha256: Hash,
  audioSha256: Hash,
  language: Schema.Literals(['Telugu', 'Hindi', 'Tamil']),
  lyrics: Schema.String.check(Schema.isMinLength(1), Schema.isMaxLength(30000)),
  fps: Schema.Literal(24),
  assets: Schema.Array(Asset).check(Schema.isMaxLength(600)),
  compositions: Schema.Array(Composition).check(Schema.isMaxLength(6)),
})
export type Project = typeof Project.Type
export const Edit = Schema.Union([
  Schema.Struct({
    tool: Schema.Literal('timeline.put'),
    composition: Composition,
  }),
  Schema.Struct({ tool: Schema.Literal('asset.put'), asset: Asset }),
  Schema.Struct({
    tool: Schema.Literal('clip.put'),
    outputId: OutputId,
    clip: Clip,
  }),
  Schema.Struct({
    tool: Schema.Literal('clip.remove'),
    outputId: OutputId,
    clipId: Id,
  }),
  Schema.Struct({
    tool: Schema.Literal('clip.trim'),
    outputId: OutputId,
    clipId: Id,
    inFrame: Frame,
    frames: PositiveFrame,
  }),
  Schema.Struct({
    tool: Schema.Literal('clip.split'),
    outputId: OutputId,
    clipId: Id,
    at: PositiveFrame,
    rightId: Id,
  }),
  Schema.Struct({
    tool: Schema.Literal('transform.set'),
    outputId: OutputId,
    clipId: Id,
    transform: Transform,
  }),
  Schema.Struct({
    tool: Schema.Literal('color.set'),
    outputId: OutputId,
    clipId: Id,
    color: Color,
  }),
  Schema.Struct({
    tool: Schema.Literal('effect.environment.put'),
    outputId: OutputId,
    clipId: Id,
    reactive: Schema.NullOr(Reactive),
  }),
  Schema.Struct({
    tool: Schema.Literal('caption.put'),
    outputId: OutputId,
    caption: Caption,
  }),
])
export type Edit = typeof Edit.Type
export interface Finding {
  code: string
  outputId: string | null
  detail: string
}
const script = {
  Telugu: /[\u0c00-\u0c7f]/u,
  Hindi: /[\u0900-\u097f]/u,
  Tamil: /[\u0b80-\u0bff]/u,
}
const fonts = {
  Telugu: 'Noto Sans Telugu',
  Hindi: 'Noto Sans Devanagari',
  Tamil: 'Noto Sans Tamil',
}
const nativeText = (language: Project['language'], text: string) => {
  const letters = [...text].filter(character => /\p{Letter}/u.test(character))
  return (
    letters.length > 0 &&
    letters.every(character => script[language].test(character))
  )
}
export const outputIds = [
  'film',
  'short-1',
  'short-2',
  'short-3',
  'thumbnail',
  'artwork',
]
export const validateProject = (
  project: Project,
  mode: 'edit' | 'render' | 'kit' = 'edit',
): Array<Finding> => {
  const issues: Array<Finding> = []
  const issue = (code: string, outputId: string | null, detail: string) =>
    issues.push({ code, outputId, detail })
  if (
    new Set(project.assets.map(asset => asset.id)).size !==
    project.assets.length
  )
    issue('duplicate_asset', null, 'Asset IDs must be unique.')
  if (
    new Set(project.compositions.map(item => item.id)).size !==
    project.compositions.length
  )
    issue('duplicate_output', null, 'Output IDs must be unique.')
  if (!nativeText(project.language, project.lyrics))
    issue(
      'native_script',
      null,
      'Canonical lyrics must use the selected native script.',
    )
  if (
    mode !== 'edit' &&
    project.assets.reduce((total, asset) => total + asset.bytes, 0) > 2147483648
  )
    issue(
      'source_budget',
      null,
      'A render accepts at most 2 GiB of registered input media.',
    )
  if (
    mode === 'kit' &&
    (project.compositions.length !== 6 ||
      outputIds.some(id => !project.compositions.some(item => item.id === id)))
  )
    issue(
      'kit_outputs',
      null,
      'A kit requires six distinct output compositions.',
    )
  project.assets.forEach(asset => {
    if (asset.kind !== 'audio' && (asset.width <= 0 || asset.height <= 0))
      issue(
        'asset_dimensions',
        null,
        `Asset ${asset.id} needs measured dimensions.`,
      )
    if (['video', 'audio'].includes(asset.kind) && asset.duration <= 0)
      issue(
        'asset_duration',
        null,
        `Asset ${asset.id} needs measured duration.`,
      )
  })
  project.compositions.forEach(item => {
    const image = ['thumbnail', 'artwork'].includes(item.id)
    const audio = project.assets.find(asset => asset.id === item.audio?.assetId)
    if (item.width % 2 || item.height % 2)
      issue('canvas', item.id, 'Canvas dimensions must be even.')
    if (image && (item.frames !== 1 || item.audio !== null))
      issue('image_timeline', item.id, 'Stills have one frame and no audio.')
    if (
      !image &&
      (!audio || audio.kind !== 'audio' || audio.sha256 !== project.audioSha256)
    )
      issue(
        'canonical_audio',
        item.id,
        'Video requires the canonical audio asset.',
      )
    if (
      audio &&
      item.audio &&
      item.audio.startSeconds + item.frames / 24 > audio.duration + 1 / 24
    )
      issue('audio_range', item.id, 'Audio interval exceeds the source.')
    if (
      item.id === 'film' &&
      audio &&
      (item.audio?.startSeconds !== 0 ||
        item.frames !== Math.ceil(audio.duration * 24 - 0.000001))
    )
      issue(
        'full_film',
        item.id,
        'Film must cover the complete canonical master.',
      )
    if (item.id.startsWith('short-') && item.frames > 720)
      issue('promo_duration', item.id, 'Promos must be at most 30 seconds.')
    if (mode === 'kit') {
      const expected =
        item.id === 'artwork'
          ? [1920, 1920]
          : item.id.startsWith('short-')
            ? [1080, 1920]
            : [1920, 1080]
      if (item.width !== expected[0] || item.height !== expected[1])
        issue(
          'preset_dimensions',
          item.id,
          'Canvas does not match release-kit-v1.',
        )
      if (!item.rationale.trim())
        issue(
          'composition_rationale',
          item.id,
          'Each output requires its own composition rationale.',
        )
    }
    if (new Set(item.clips.map(clip => clip.id)).size !== item.clips.length)
      issue('duplicate_clip', item.id, 'Clip IDs must be unique.')
    const sorted = [...item.clips].sort((a, b) => a.at - b.at)
    if (
      mode !== 'edit' &&
      (!sorted.length ||
        sorted[0]?.at !== 0 ||
        (sorted.at(-1) &&
          (sorted.at(-1)?.at ?? 0) + (sorted.at(-1)?.frames ?? 0) !==
            item.frames))
    )
      issue(
        'coverage',
        item.id,
        'Clips must cover the timeline from first through final frame.',
      )
    sorted.forEach((clip, index) => {
      const asset = project.assets.find(
        candidate => candidate.id === clip.assetId,
      )
      if (!asset || !['video', 'image'].includes(asset.kind))
        issue('clip_asset', item.id, `Missing visual source for ${clip.id}.`)
      if (
        asset?.kind === 'video' &&
        clip.inFrame + clip.frames > Math.floor(asset.duration * 24 + 0.05)
      )
        issue(
          'source_trim',
          item.id,
          `Clip ${clip.id} exceeds source coverage; implicit looping is disabled.`,
        )
      if (
        clip.at + clip.frames > item.frames ||
        clip.fadeIn + clip.fadeOut > clip.frames
      )
        issue('clip_bounds', item.id, `Invalid bounds or fades for ${clip.id}.`)
      const previous = sorted[index - 1]
      if (
        mode !== 'edit' &&
        previous &&
        previous.at + previous.frames !== clip.at
      )
        issue(
          'coverage',
          item.id,
          'The first renderer requires continuous clips without gaps or overlap.',
        )
      if (clip.reactive) {
        const mask = project.assets.find(
          candidate => candidate.id === clip.reactive?.maskAssetId,
        )
        if (
          !mask ||
          mask.kind !== 'mask' ||
          mask.width !== asset?.width ||
          mask.height !== asset?.height
        )
          issue(
            'environment_mask',
            item.id,
            'Reactivity requires a source-sized environment mask.',
          )
        if (clip.reactive.audioSha256 !== project.audioSha256)
          issue(
            'envelope_source',
            item.id,
            'Envelope belongs to a different song.',
          )
        if (
          clip.reactive.points.some(
            (point, at) =>
              at > 0 &&
              point.frame <= (clip.reactive?.points[at - 1]?.frame ?? 0),
          ) ||
          clip.reactive.points.length < 2
        )
          issue(
            'envelope_order',
            item.id,
            'Envelope points must be strictly increasing and contain at least two samples.',
          )
      }
    })
    if (
      new Set(item.captions.map(caption => caption.id)).size !==
      item.captions.length
    )
      issue('duplicate_caption', item.id, 'Caption IDs must be unique.')
    item.captions.forEach(caption => {
      if (caption.start >= caption.end || caption.end > item.frames)
        issue(
          'caption_range',
          item.id,
          `Caption ${caption.id} is out of bounds.`,
        )
      if (
        caption.kind === 'lyric' &&
        (!project.lyrics.includes(caption.text) ||
          !nativeText(project.language, caption.text) ||
          caption.font !== fonts[project.language])
      )
        issue(
          'exact_lyric',
          item.id,
          'Lyrics must match canonical native text and its shaping font.',
        )
    })
  })
  return issues
}
const put = <A extends { readonly id: string }>(
  items: ReadonlyArray<A>,
  item: A,
) => [...items.filter(candidate => candidate.id !== item.id), item]
export const applyEdits = (
  project: Project,
  edits: ReadonlyArray<Edit>,
): Project =>
  edits.reduce((current, edit) => {
    if (edit.tool === 'asset.put')
      return { ...current, assets: put(current.assets, edit.asset) }
    if (edit.tool === 'timeline.put')
      return {
        ...current,
        compositions: put(current.compositions, edit.composition),
      }
    const composition = current.compositions.find(
      item => item.id === edit.outputId,
    )
    if (!composition) throw new Error('The output composition does not exist.')
    if (edit.tool === 'caption.put')
      return {
        ...current,
        compositions: put(current.compositions, {
          ...composition,
          captions: put(composition.captions, edit.caption),
        }),
      }
    if (edit.tool === 'clip.put')
      return {
        ...current,
        compositions: put(current.compositions, {
          ...composition,
          clips: put(composition.clips, edit.clip),
        }),
      }
    const clip = composition.clips.find(
      candidate => candidate.id === edit.clipId,
    )
    if (!clip) throw new Error('The clip does not exist.')
    const clips =
      edit.tool === 'clip.remove'
        ? composition.clips.filter(candidate => candidate.id !== clip.id)
        : edit.tool === 'clip.split'
          ? (() => {
              if (
                edit.at <= clip.at ||
                edit.at >= clip.at + clip.frames ||
                composition.clips.some(
                  candidate => candidate.id === edit.rightId,
                )
              )
                throw new Error(
                  'Split must be inside the clip and use a new ID.',
                )
              const left = edit.at - clip.at
              return [
                ...composition.clips.filter(
                  candidate => candidate.id !== clip.id,
                ),
                { ...clip, frames: left, fadeOut: 0 },
                {
                  ...clip,
                  id: edit.rightId,
                  at: edit.at,
                  inFrame: clip.inFrame + left,
                  frames: clip.frames - left,
                  fadeIn: 0,
                },
              ]
            })()
          : put(
              composition.clips,
              edit.tool === 'clip.trim'
                ? { ...clip, inFrame: edit.inFrame, frames: edit.frames }
                : edit.tool === 'transform.set'
                  ? { ...clip, transform: edit.transform }
                  : edit.tool === 'color.set'
                    ? { ...clip, color: edit.color }
                    : { ...clip, reactive: edit.reactive },
            )
    return {
      ...current,
      compositions: put(current.compositions, { ...composition, clips }),
    }
  }, project)
export const decodeProject = (value: unknown) =>
  Schema.decodeUnknownSync(Project, { onExcessProperty: 'error' })(value)
