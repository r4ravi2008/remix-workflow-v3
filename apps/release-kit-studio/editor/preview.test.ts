// @vitest-environment node
import { Schema } from 'effect'
import { describe, expect, it } from 'vitest'

import { canonicalJson } from '../src/canonical'
import { makeEditorApi } from './api'
import { kitFixture } from './kit-testing'
import {
  Preview,
  PreviewBundle,
  previewIdentity,
  previewPrefix,
  previewSamples,
  validatePreview,
} from './preview'
import { previewFixture } from './preview-testing'

const source = {
  id: 'film' as const,
  sha256: 'a'.repeat(64),
  bytes: 100,
  width: 1920,
  height: 1080,
  frames: 48,
}
describe('source-bound review previews', () => {
  it('keeps exact frame ranges and normalizes requested sampling without changing the source', async () => {
    const test = await previewFixture(source, 'job')
    expect(test.bundle.sampleFrames).toEqual([6, 23, 41])
    await validatePreview(test.input, source, test.bundle)
    expect(
      await previewIdentity(
        { ...test.input, sampleFrames: [41, 6, 23] },
        source,
      ),
    ).toBe(test.bundle.bundleId)
    expect(
      await previewIdentity(test.input, { ...source, sha256: 'b'.repeat(64) }),
    ).not.toBe(test.bundle.bundleId)
  })
  it('rejects oversize ranges, duplicate samples, source gaps and false review assertions', async () => {
    const test = await previewFixture(source, 'job')
    expect(() =>
      Schema.decodeUnknownSync(Preview)({ ...test.input, frames: 241 }),
    ).toThrow()
    expect(() => previewSamples({ ...test.input, frames: 48 }, source)).toThrow(
      'exact range',
    )
    expect(() =>
      previewSamples({ ...test.input, sampleFrames: [6, 6] }, source),
    ).toThrow('unique source frames')
    expect(() =>
      previewSamples({ ...test.input, sampleFrames: [42] }, source),
    ).toThrow('unique source frames')
    expect(() =>
      Schema.decodeUnknownSync(PreviewBundle)({
        ...test.bundle,
        motionReviewed: true,
      }),
    ).toThrow()
    await expect(
      validatePreview(
        test.input,
        { ...source, sha256: 'b'.repeat(64) },
        test.bundle,
      ),
    ).rejects.toMatchObject({ code: 'preview_binding' })
  })
  it('rejects omitted samples, altered timing, wrong canvases and an unbounded bundle', async () => {
    const test = await previewFixture(source, 'job')
    await expect(
      validatePreview(test.input, source, {
        ...test.bundle,
        files: test.bundle.files.slice(0, 2),
      }),
    ).rejects.toMatchObject({ code: 'preview_binding' })
    for (const change of [{ sourceFrame: 7 }, { width: 960 }, { frames: 2 }]) {
      const files = test.bundle.files.map((file, index) =>
        index === 1 ? { ...file, ...change } : file,
      )
      await expect(
        validatePreview(test.input, source, { ...test.bundle, files }),
      ).rejects.toMatchObject({ code: 'preview_measurement' })
    }
    await expect(
      validatePreview(test.input, source, {
        ...test.bundle,
        files: test.bundle.files.map(file => ({ ...file, bytes: 16777216 })),
      }),
    ).rejects.toMatchObject({ code: 'preview_binding' })
  })
  it('handles still artwork as one original frame with no invented audio or motion', async () => {
    const still = {
      ...source,
      id: 'artwork' as const,
      width: 1920,
      height: 1920,
      frames: 1,
    }
    const test = await previewFixture(still, 'job', {
      startFrame: 0,
      frames: 1,
    })
    await validatePreview(test.input, still, test.bundle)
    expect(test.bundle.files).toHaveLength(2)
    expect(test.bundle.files[0]).toMatchObject({
      name: 'preview.jpg',
      width: 960,
      height: 960,
      fps: 0,
      audioComparison: null,
    })
  })
  it('serves only the owning tenant and preserves private byte ranges and original-source headers', async () => {
    const test = await kitFixture()
    try {
      const artifact = test.receipt.outputs.find(item => item.id === 'film')!
      const preview = await previewFixture(
        { ...artifact, id: 'film', frames: 48 },
        test.job.id,
      )
      const prefix = previewPrefix('one', test.job.id, preview.bundle.bundleId)
      test.objects.set(prefix + 'receipt.json', canonicalJson(preview.bundle))
      for (const [name, content] of preview.content)
        test.objects.set(prefix + name, content)
      const media = {
        ...test.media,
        get: async (
          key: string,
          options: Parameters<typeof test.media.get>[1],
        ) => {
          const object = await test.media.get(key, options)
          if (!object || !options.range) return object
          const data = await new Response(object.body).arrayBuffer()
          return {
            ...object,
            body: new Blob([
              data.slice(
                options.range.offset,
                options.range.offset +
                  (options.range.length ?? data.byteLength),
              ),
            ]).stream(),
          }
        },
      }
      const api = makeEditorApi(
        { MEDIA: media, STUDIO_OPERATOR_TOKEN: 'x'.repeat(32) },
        test.store,
      )
      const url = `https://editor.test/v1/jobs/${test.job.id}/previews/${preview.bundle.bundleId}/preview.mp4`
      test.reads.length = 0
      expect(
        (
          await api(
            new Request(url, {
              headers: { Authorization: 'Bearer private-two' },
            }),
          )
        ).status,
      ).toBe(404)
      expect(test.reads).toHaveLength(0)
      const partial = await api(
        new Request(url, {
          headers: { Authorization: 'Bearer private-one', Range: 'bytes=2-7' },
        }),
      )
      expect(partial.status).toBe(206)
      expect(partial.headers.get('X-Source-Sha256')).toBe(artifact.sha256)
      expect(await partial.text()).toBe(
        preview.content.get('preview.mp4')!.slice(2, 8),
      )
      const head = await api(
        new Request(url, {
          method: 'HEAD',
          headers: { Authorization: 'Bearer private-one' },
        }),
      )
      expect(head.status).toBe(200)
      expect(head.body).toBeNull()
      expect(
        (
          await api(
            new Request(url, {
              headers: {
                Authorization: 'Bearer private-one',
                Range: 'bytes=999-1000',
              },
            }),
          )
        ).status,
      ).toBe(416)
    } finally {
      test.database.close()
    }
  })
})
