import { Schema } from 'effect'
import { readFile, stat } from 'node:fs/promises'

import { productionAssetPrefix } from '../editor/production-contract'
import {
  Asset,
  Composition,
  Id,
  type Project,
  validateProject,
} from '../editor/project'
import { type ReleaseBrief, outputs } from '../src/domain'
import { command } from './gpu'
import { AssetInput, type EditorProductionPlan, briefFingerprint } from './plan'
import { fileReceipt } from './transfer'

const Hash = Schema.String.check(Schema.isPattern(/^[a-f0-9]{64}$/))
export const EditorRecipe = Schema.Struct({
  schemaVersion: Schema.Literal(1),
  releaseId: Id,
  briefSha256: Hash,
  audioSha256: Hash,
  language: Schema.Literals(['Telugu', 'Hindi', 'Tamil']),
  lyrics: Schema.String.check(Schema.isMinLength(1), Schema.isMaxLength(30000)),
  fps: Schema.Literal(24),
  inputs: Schema.Array(
    Schema.Struct({
      mediaKind: Schema.Literals(['audio', 'video', 'image', 'mask']),
      source: AssetInput,
    }),
  ).check(Schema.isMinLength(1), Schema.isMaxLength(600)),
  compositions: Schema.Array(Composition).check(
    Schema.isMinLength(1),
    Schema.isMaxLength(6),
  ),
})
export type EditorRecipe = typeof EditorRecipe.Type
const Probe = Schema.Struct({
  streams: Schema.Array(
    Schema.Struct({
      codec_type: Schema.String,
      codec_name: Schema.optional(Schema.String),
      width: Schema.optional(Schema.Number),
      height: Schema.optional(Schema.Number),
      duration: Schema.optional(Schema.String),
      nb_frames: Schema.optional(Schema.String),
    }),
  ),
  format: Schema.Struct({ duration: Schema.optional(Schema.String) }),
})
interface RecipeJob {
  releaseId: string
  brief: ReleaseBrief
}
export const readEditorJson = async (path: string): Promise<unknown> => {
  if ((await stat(path)).size > 4 * 1024 * 1024)
    throw new Error('Editor JSON input exceeds 4 MiB.')
  const text = await readFile(path, 'utf8')
  if (Buffer.byteLength(text) > 4 * 1024 * 1024)
    throw new Error('Editor JSON input changed beyond its size limit.')
  return JSON.parse(text)
}
export const assertRecipeBinding = (
  recipe: EditorRecipe,
  job: RecipeJob,
  shotIds: ReadonlyArray<string>,
) => {
  if (
    recipe.releaseId !== job.releaseId ||
    recipe.audioSha256 !== job.brief.audioSha256 ||
    recipe.briefSha256 !== briefFingerprint(job.brief) ||
    recipe.lyrics !== job.brief.lyrics ||
    recipe.language !== job.brief.language
  )
    throw new Error(
      'The generated-media recipe differs from the assigned frozen release.',
    )
  const ids = recipe.inputs.map(input => input.source.assetId)
  const audio = recipe.inputs.filter(
    input => input.source.kind === 'canonical-audio',
  )
  if (
    new Set(ids).size !== ids.length ||
    ids.some(id => !id.startsWith(productionAssetPrefix(job.releaseId)))
  )
    throw new Error(
      'Recipe inputs require unique IDs in the assigned release namespace.',
    )
  if (
    audio.length !== 1 ||
    audio[0]?.mediaKind !== 'audio' ||
    recipe.inputs.some(
      input =>
        input.mediaKind === 'audio' && input.source.kind !== 'canonical-audio',
    )
  )
    throw new Error('The recipe requires exactly one canonical audio input.')
  const boundShots = recipe.inputs.flatMap(input =>
    input.source.kind === 'shot' ? [input.source.shotId] : [],
  )
  if (
    new Set(shotIds).size !== shotIds.length ||
    boundShots.some(id => !shotIds.includes(id)) ||
    shotIds.some(id => !boundShots.includes(id))
  )
    throw new Error(
      'Every planned GPU shot must have a recipe binding; unknown shots are rejected.',
    )
  if (
    recipe.compositions.length !== 6 ||
    new Set(recipe.compositions.map(item => item.id)).size !== 6
  )
    throw new Error('The recipe requires six separate output compositions.')
  for (const composition of recipe.compositions) {
    const still = ['thumbnail', 'artwork'].includes(composition.id)
    const portrait = composition.id.startsWith('short-')
    if (
      !outputs.some(output => output.id === composition.id) ||
      !composition.rationale.trim() ||
      composition.width !== (portrait ? 1080 : 1920) ||
      composition.height !==
        (portrait || composition.id === 'artwork' ? 1920 : 1080) ||
      (still && (composition.frames !== 1 || composition.audio !== null)) ||
      (!still &&
        (composition.audio?.assetId !== audio[0]?.source.assetId ||
          composition.audio.startSeconds + composition.frames / 24 >
            job.brief.audioDuration + 1 / 24)) ||
      (composition.id === 'film' &&
        (composition.audio?.startSeconds !== 0 ||
          composition.frames !==
            Math.ceil(job.brief.audioDuration * 24 - 0.000001))) ||
      (portrait && composition.frames > 720)
    )
      throw new Error(
        'The recipe output differs from the full-song six-format contract.',
      )
    const references = [
      ...(composition.audio ? [composition.audio.assetId] : []),
      ...composition.clips.flatMap(clip => [
        clip.assetId,
        ...(clip.reactive ? [clip.reactive.maskAssetId] : []),
      ]),
    ]
    if (references.some(id => !ids.includes(id)))
      throw new Error('A composition refers to an unbound recipe input.')
    const clips = [...composition.clips].sort((a, b) => a.at - b.at)
    const finalClip = clips.at(-1)
    if (
      !clips.length ||
      clips[0]?.at !== 0 ||
      !finalClip ||
      finalClip.at + finalClip.frames !== composition.frames ||
      clips.some((clip, index) => {
        const previous = clips[index - 1]
        return previous && previous.at + previous.frames !== clip.at
      })
    )
      throw new Error(
        'The recipe must cover every output without gaps or implicit loops.',
      )
  }
}
export const readEditorRecipe = async (
  plan: EditorProductionPlan,
  job: RecipeJob,
) => {
  if (plan.schemaVersion !== 3) return null
  const recipe = Schema.decodeUnknownSync(EditorRecipe, {
    onExcessProperty: 'error',
  })(await readEditorJson(plan.editor.recipePath))
  assertRecipeBinding(
    recipe,
    job,
    plan.shots.map(shot => shot.id),
  )
  return recipe
}
export const materializeEditorRecipe = async (
  recipe: EditorRecipe,
  job: RecipeJob,
  canonicalSource: string,
  shots: ReadonlyMap<string, string>,
  signal: AbortSignal,
) => {
  assertRecipeBinding(recipe, job, [...shots.keys()])
  const assets: Array<typeof Asset.Type> = []
  for (const input of recipe.inputs) {
    signal.throwIfAborted()
    const path =
      input.source.kind === 'canonical-audio'
        ? canonicalSource
        : input.source.kind === 'shot'
          ? shots.get(input.source.shotId)
          : input.source.path
    if (!path) throw new Error('The collected GPU original is missing.')
    const measured = await fileReceipt(path, signal)
    if (measured.bytes > 100 * 1024 * 1024)
      throw new Error('Recipe media exceeds the 100 MiB editor upload limit.')
    const probe = Schema.decodeUnknownSync(Probe)(
      JSON.parse(
        await command(
          'ffprobe',
          [
            '-v',
            'error',
            '-show_entries',
            'format=duration:stream=codec_type,codec_name,width,height,duration,nb_frames',
            '-of',
            'json',
            path,
          ],
          120000,
          signal,
        ),
      ),
    )
    const stream = probe.streams.find(
      stream =>
        stream.codec_type === (input.mediaKind === 'audio' ? 'audio' : 'video'),
    )
    if (!stream)
      throw new Error(
        'The collected media does not contain its declared stream kind.',
      )
    const still = input.mediaKind === 'image' || input.mediaKind === 'mask'
    if (
      still &&
      (!['png', 'mjpeg', 'webp', 'bmp'].includes(stream.codec_name ?? '') ||
        Number(stream.nb_frames ?? 1) > 1 ||
        Number(probe.format.duration ?? stream.duration ?? 0) > 0)
    )
      throw new Error('Images and masks must be single-frame stills.')
    const duration = still
      ? 0
      : Number(probe.format.duration ?? stream.duration)
    if (!Number.isFinite(duration) || duration < 0 || (!still && duration <= 0))
      throw new Error('The collected media has no valid measured duration.')
    if (
      input.source.kind === 'canonical-audio' &&
      (measured.sha256 !== job.brief.audioSha256 ||
        measured.bytes !== job.brief.audioBytes ||
        Math.abs(duration - job.brief.audioDuration) > 1 / 24 + 0.005)
    )
      throw new Error(
        'Measured canonical audio differs from the frozen master.',
      )
    const after = await fileReceipt(path, signal)
    if (after.sha256 !== measured.sha256 || after.bytes !== measured.bytes)
      throw new Error(
        'Collected media changed during its probe; reconcile before committing.',
      )
    assets.push(
      Schema.decodeUnknownSync(Asset)({
        id: input.source.assetId,
        kind: input.mediaKind,
        ...measured,
        width: input.mediaKind === 'audio' ? 0 : (stream.width ?? 0),
        height: input.mediaKind === 'audio' ? 0 : (stream.height ?? 0),
        duration,
      }),
    )
  }
  const project: Project = {
    schemaVersion: 1,
    releaseId: recipe.releaseId,
    briefSha256: recipe.briefSha256,
    audioSha256: recipe.audioSha256,
    language: recipe.language,
    lyrics: recipe.lyrics,
    fps: recipe.fps,
    assets,
    compositions: recipe.compositions,
  }
  const findings = validateProject(project, 'kit')
  if (findings.length)
    throw new Error(
      JSON.stringify({ code: 'invalid_materialized_kit', findings }),
    )
  return { project, bindings: recipe.inputs.map(input => input.source) }
}
