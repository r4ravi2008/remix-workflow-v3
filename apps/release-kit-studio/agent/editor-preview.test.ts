// @vitest-environment node
import { mkdtemp, readFile, rm, stat, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { previewFixture } from '../editor/preview-testing'
import { runEditorCli } from './editor-cli'

afterEach(() => vi.unstubAllGlobals())
describe('agent review downloads', () => {
  it('binds the independently located source, verifies files and preserves an existing directory', async () => {
    const root = await mkdtemp(join(tmpdir(), 'editor-preview-'))
    try {
      const source = {
        id: 'film' as const,
        sha256: 'a'.repeat(64),
        bytes: 100,
        width: 1920,
        height: 1080,
        frames: 48,
      }
      const fixture = await previewFixture(source, 'job')
      const request = join(root, 'request.json')
      await writeFile(request, JSON.stringify(fixture.input))
      let corrupt = false
      const fetch = vi.fn(async (url: string | URL) => {
        const path = new URL(url).pathname
        if (path.endsWith('artifact.locate'))
          return Response.json({ artifact: source })
        if (path.endsWith('artifact.preview'))
          return Response.json({ bundle: fixture.bundle, reused: false })
        const name = path.split('/').at(-1)!
        const file = fixture.bundle.files.find(item => item.name === name)!
        const content = fixture.content.get(name)!
        return new Response(corrupt ? content.replace('s', 'x') : content, {
          headers: {
            'Content-Type': name.endsWith('.mp4') ? 'video/mp4' : 'image/jpeg',
            'Content-Length': String(file.bytes),
            'X-Content-Sha256': file.sha256,
            'X-Source-Sha256': source.sha256,
          },
        })
      })
      vi.stubGlobal('fetch', fetch)
      const env = {
        EDITOR_URL: 'https://editor.test',
        EDITOR_TOKEN: 'private-test',
      }
      const destination = join(root, 'review')
      expect(
        await runEditorCli(['preview', request, destination], env),
      ).toMatchObject({
        filesVerified: 4,
        sourceSha256: source.sha256,
        heard: false,
        motionReviewed: false,
      })
      const calls = fetch.mock.calls.length
      await expect(
        runEditorCli(['preview', request, destination], env),
      ).rejects.toThrow('EEXIST')
      expect(fetch).toHaveBeenCalledTimes(calls)
      expect(await readFile(join(destination, 'preview.mp4'), 'utf8')).toBe(
        fixture.content.get('preview.mp4'),
      )
      corrupt = true
      const failed = join(root, 'failed')
      await expect(
        runEditorCli(['preview', request, failed], env),
      ).rejects.toThrow('checksum')
      await expect(stat(failed)).rejects.toMatchObject({ code: 'ENOENT' })
    } finally {
      await rm(root, { recursive: true, force: true })
    }
  })
})
