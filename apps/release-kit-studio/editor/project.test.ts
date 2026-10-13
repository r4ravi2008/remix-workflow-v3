import { describe, expect, it } from 'vitest'

import {
  type Project,
  applyEdits,
  decodeProject,
  validateProject,
} from './project'
import { projectFixture } from './testing'

describe('Cloudflare editor project', () => {
  it('accepts a bounded render and refuses it as a full six-output kit', () => {
    expect(validateProject(projectFixture(), 'render')).toEqual([])
    expect(
      validateProject(projectFixture(), 'kit').map(issue => issue.code),
    ).toContain('kit_outputs')
  })
  it('splits source ranges exactly without changing original project or sound', () => {
    const original = projectFixture()
    const edited = applyEdits(original, [
      {
        tool: 'clip.split',
        outputId: 'film',
        clipId: 'scene',
        at: 24,
        rightId: 'scene-right',
      },
    ])
    expect(
      edited.compositions[0]?.clips.map(item => [
        item.at,
        item.inFrame,
        item.frames,
      ]),
    ).toEqual([
      [0, 0, 24],
      [24, 24, 24],
    ])
    expect(original.compositions[0]?.clips).toHaveLength(1)
    expect(edited.audioSha256).toBe(original.audioSha256)
    expect(validateProject(edited, 'render')).toEqual([])
  })
  it('rejects source overrun, gaps and a diagnostic masquerading as a full film', () => {
    const extended = applyEdits(projectFixture(), [
      {
        tool: 'clip.trim',
        outputId: 'film',
        clipId: 'scene',
        inFrame: 36,
        frames: 48,
      },
    ])
    expect(
      validateProject(extended, 'render').map(issue => issue.code),
    ).toContain('source_trim')
    const short = {
      ...projectFixture(),
      compositions: projectFixture().compositions.map(item => ({
        ...item,
        frames: 24,
      })),
    }
    expect(validateProject(short, 'render').map(issue => issue.code)).toContain(
      'full_film',
    )
  })
  it('rejects changed or romanized lyrics, font fallback, raw graph and unsafe caption controls', () => {
    expect(
      validateProject({
        ...projectFixture(),
        lyrics: `${projectFixture().lyrics} romanized words`,
      }).map(issue => issue.code),
    ).toContain('native_script')
    const changed = applyEdits(projectFixture(), [
      {
        tool: 'caption.put',
        outputId: 'film',
        caption: {
          id: 'cue',
          kind: 'lyric',
          start: 0,
          end: 48,
          text: 'prathi nimisham',
          font: 'Noto Sans',
          size: 64,
          marginBottom: 100,
        },
      },
    ])
    expect(
      validateProject(changed, 'render').map(issue => issue.code),
    ).toContain('exact_lyric')
    expect(() =>
      decodeProject({
        ...projectFixture(),
        filterGraph: 'movie=https://example.com',
      }),
    ).toThrow()
    expect(() =>
      decodeProject({
        ...projectFixture(),
        compositions: projectFixture().compositions.map(item => ({
          ...item,
          captions: item.captions.map(cue => ({
            ...cue,
            text: '{\\pos(0,0)}',
          })),
        })),
      }),
    ).toThrow()
  })
  it('rejects a render whose registered sources exceed the scratch input budget', () => {
    const project = projectFixture()
    expect(
      validateProject(
        {
          ...project,
          assets: project.assets.map(asset => ({
            ...asset,
            bytes: 2147483648,
          })),
        },
        'render',
      ).map(issue => issue.code),
    ).toContain('source_budget')
  })
  it('rounds full-film coverage upward so fractional source frames cannot trim the audio tail', () => {
    const fixture = projectFixture()
    const project = {
      ...fixture,
      assets: fixture.assets.map(asset =>
        asset.kind === 'audio' ? { ...asset, duration: 1.99 } : asset,
      ),
    }
    expect(validateProject(project, 'render')).toEqual([])
    const shortened = {
      ...project,
      compositions: project.compositions.map(comp => ({
        ...comp,
        frames: 47,
        clips: comp.clips.map(clip => ({ ...clip, frames: 47 })),
        captions: [],
      })),
    }
    expect(
      validateProject(shortened, 'render').map(finding => finding.code),
    ).toContain('full_film')
  })
  it('requires a bound source-sized environment mask and strictly ordered envelope', () => {
    const edited = applyEdits(projectFixture(), [
      {
        tool: 'effect.environment.put',
        outputId: 'film',
        clipId: 'scene',
        reactive: {
          maskAssetId: 'not-uploaded',
          audioSha256: 'd'.repeat(64),
          points: [
            { frame: 24, value: 0.5 },
            { frame: 12, value: 1 },
          ],
        },
      },
    ])
    expect(validateProject(edited, 'render').map(issue => issue.code)).toEqual(
      expect.arrayContaining([
        'environment_mask',
        'envelope_source',
        'envelope_order',
      ]),
    )
  })
  it('validates all six independent output formats', () => {
    const original = projectFixture()
    const template = original.compositions[0]
    if (!template) throw new Error('Fixture missing')
    const ids: ReadonlyArray<
      'short-1' | 'short-2' | 'short-3' | 'thumbnail' | 'artwork'
    > = ['short-1', 'short-2', 'short-3', 'thumbnail', 'artwork']
    const kit: Project = {
      ...original,
      compositions: [
        template,
        ...ids.map((id, index) => ({
          ...template,
          id,
          width: id.startsWith('short') ? 1080 : 1920,
          height: id === 'thumbnail' ? 1080 : 1920,
          frames: id === 'thumbnail' || id === 'artwork' ? 1 : 48,
          rationale: `Independent composition ${index}`,
          audio: id === 'thumbnail' || id === 'artwork' ? null : template.audio,
          clips: template.clips.map(item => ({
            ...item,
            frames: id === 'thumbnail' || id === 'artwork' ? 1 : 48,
          })),
          captions: [],
        })),
      ],
    }
    expect(validateProject(kit, 'kit')).toEqual([])
  })
})
