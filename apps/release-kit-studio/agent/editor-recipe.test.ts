// @vitest-environment node
import { mkdtemp, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { afterEach, describe, expect, it } from 'vitest'

import { productionAssetPrefix } from '../editor/production-contract'
import { validateProject } from '../editor/project'
import { projectFixture } from '../editor/testing'
import { defaultProfile, outputs } from '../src/domain'
import { runEditorCli } from './editor-cli'
import {
  type EditorRecipe,
  assertRecipeBinding,
  materializeEditorRecipe,
} from './editor-recipe'
import { command } from './gpu'
import { briefFingerprint } from './plan'
import { fileReceipt } from './transfer'

const roots: Array<string> = []
afterEach(async () => {
  await Promise.all(
    roots.splice(0).map(root => rm(root, { recursive: true, force: true })),
  )
})
const fixture = async (sceneSeconds = 2) => {
  const root = await mkdtemp(join(tmpdir(), 'editor-recipe-'))
  roots.push(root)
  const audio = join(root, 'master.wav')
  const scene = join(root, 'new-original.mp4')
  await command('ffmpeg', [
    '-v',
    'error',
    '-f',
    'lavfi',
    '-i',
    'sine=frequency=440:sample_rate=48000',
    '-t',
    '2',
    '-ac',
    '2',
    audio,
  ])
  await command('ffmpeg', [
    '-v',
    'error',
    '-f',
    'lavfi',
    '-i',
    'testsrc2=size=320x180:rate=24',
    '-t',
    String(sceneSeconds),
    '-c:v',
    'libx264',
    '-pix_fmt',
    'yuv420p',
    scene,
  ])
  const measured = await fileReceipt(audio)
  const brief = {
    title: 'Recipe test',
    lyrics: 'ప్రతి నిమిషం',
    language: 'Telugu',
    audioName: 'song.wav',
    audioSha256: measured.sha256,
    audioBytes: measured.bytes,
    audioDuration: 2,
    profile: defaultProfile,
  }
  const job = { releaseId: 'release-one', brief }
  const prefix = productionAssetPrefix(job.releaseId)
  const clip = projectFixture().compositions[0]?.clips[0]
  if (!clip) throw new Error('Missing fixture clip')
  const recipe: EditorRecipe = {
    schemaVersion: 1,
    releaseId: job.releaseId,
    briefSha256: briefFingerprint(brief),
    audioSha256: measured.sha256,
    language: 'Telugu',
    lyrics: brief.lyrics,
    fps: 24,
    inputs: [
      {
        mediaKind: 'audio',
        source: { kind: 'canonical-audio', assetId: prefix + 'master' },
      },
      {
        mediaKind: 'video',
        source: { kind: 'shot', assetId: prefix + 'scene', shotId: 'new-shot' },
      },
    ],
    compositions: outputs.map(output => {
      const still = ['thumbnail', 'artwork'].includes(output.id)
      return {
        id: output.id,
        width: output.id.startsWith('short-') ? 1080 : 1920,
        height:
          output.id.startsWith('short-') || output.id === 'artwork'
            ? 1920
            : 1080,
        frames: still ? 1 : 48,
        rationale: `${output.id} independent composition`,
        audio: still ? null : { assetId: prefix + 'master', startSeconds: 0 },
        clips: [{ ...clip, assetId: prefix + 'scene', frames: still ? 1 : 48 }],
        captions: [],
      }
    }),
  }
  return {
    root,
    audio,
    scene,
    job,
    recipe,
    shots: new Map([['new-shot', scene]]),
    signal: new AbortController().signal,
  }
}
describe('generated-footage editor recipes', () => {
  it('measures a newly collected shot and creates a full immutable project without a predicted footage hash', async () => {
    const test = await fixture()
    const result = await materializeEditorRecipe(
      test.recipe,
      test.job,
      test.audio,
      test.shots,
      test.signal,
    )
    const original = await fileReceipt(test.scene)
    expect(
      result.project.assets.find(asset => asset.kind === 'video'),
    ).toMatchObject({ ...original, width: 320, height: 180, duration: 2 })
    expect(validateProject(result.project, 'kit')).toEqual([])
    expect(test.recipe.inputs[1]).not.toHaveProperty('sha256')
    expect(result.project.audioSha256).toBe(test.job.brief.audioSha256)
  })
  it('rejects foreign source binding, missing or unused GPU attempts and incomplete recipes before inference', async () => {
    const test = await fixture()
    expect(() =>
      assertRecipeBinding(
        { ...test.recipe, releaseId: 'other-release' },
        test.job,
        ['new-shot'],
      ),
    ).toThrow('frozen release')
    expect(() => assertRecipeBinding(test.recipe, test.job, [])).toThrow(
      'planned GPU shot',
    )
    expect(() =>
      assertRecipeBinding(test.recipe, test.job, ['new-shot', 'unused-shot']),
    ).toThrow('planned GPU shot')
    expect(() =>
      assertRecipeBinding(
        { ...test.recipe, compositions: test.recipe.compositions.slice(0, 5) },
        test.job,
        ['new-shot'],
      ),
    ).toThrow('six separate')
    expect(() =>
      assertRecipeBinding(
        {
          ...test.recipe,
          compositions: test.recipe.compositions.map(item =>
            item.id === 'film' ? { ...item, frames: 24 } : item,
          ),
        },
        test.job,
        ['new-shot'],
      ),
    ).toThrow('full-song')
  })
  it('rejects insufficient generated coverage instead of looping the short original', async () => {
    const test = await fixture(1)
    await expect(
      materializeEditorRecipe(
        test.recipe,
        test.job,
        test.audio,
        test.shots,
        test.signal,
      ),
    ).rejects.toThrow('source_trim')
  })
  it('preserves the exact canonical audio and rejects a changed master', async () => {
    const test = await fixture()
    await writeFile(test.audio, 'changed master')
    await expect(
      materializeEditorRecipe(
        test.recipe,
        test.job,
        test.audio,
        test.shots,
        test.signal,
      ),
    ).rejects.toThrow()
  })
  it('exposes recipe and generated-plan schemas and refuses to overwrite a materialized project', async () => {
    const test = await fixture()
    expect(
      await runEditorCli(['schema', 'generated-production-plan'], {}),
    ).toMatchObject({ properties: { schemaVersion: { enum: [3] } } })
    expect(await runEditorCli(['schema', 'recipe'], {})).toMatchObject({
      additionalProperties: false,
    })
    const recipePath = join(test.root, 'recipe.json'),
      inputPath = join(test.root, 'inputs.json'),
      outputPath = join(test.root, 'project.json')
    await writeFile(recipePath, JSON.stringify(test.recipe))
    await writeFile(
      inputPath,
      JSON.stringify({
        ...test.job,
        canonicalSource: test.audio,
        shots: [{ id: 'new-shot', path: test.scene }],
      }),
    )
    const args = ['materialize', recipePath, inputPath, outputPath]
    expect(await runEditorCli(args, {})).toMatchObject({
      projectFile: outputPath,
      fullKitCompleted: false,
      creativelyAccepted: false,
    })
    await expect(runEditorCli(args, {})).rejects.toThrow('EEXIST')
  })
})
