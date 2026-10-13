import { createHash } from 'node:crypto'
import { mkdtemp, readFile, rm, stat, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
// @vitest-environment node
import { afterEach, describe, expect, it, vi } from 'vitest'

import { prepareKit } from '../editor/archive'
import { kitFixture, nodeArchiveHash } from '../editor/kit-testing'
import { streamZip } from '../editor/zip'
import { runEditorCli } from './editor-cli'

afterEach(() => vi.unstubAllGlobals())
describe('agent editor CLI', () => {
  it('verifies eight archive entries independently and preserves an existing destination', async () => {
    const fixture = await kitFixture()
    const root = await mkdtemp(join(tmpdir(), 'editor-kit-'))
    try {
      const kit = await prepareKit(
        fixture.store,
        fixture.media,
        'one',
        fixture.job,
      )
      const data = new Uint8Array(
        await new Response(
          streamZip(kit.entries, nodeArchiveHash),
        ).arrayBuffer(),
      )
      const network = vi.fn(async (url: string | URL) =>
        new URL(url).pathname.includes('/tools/')
          ? Response.json(kit.descriptor)
          : new Response(data, {
              headers: {
                'Content-Type': 'application/zip',
                'Content-Length': String(kit.descriptor.bytes),
                'X-Kit-Manifest-Sha256': kit.descriptor.manifestSha256,
              },
            }),
      )
      vi.stubGlobal('fetch', network)
      const env = {
        EDITOR_URL: 'https://editor.example',
        EDITOR_TOKEN: 'private',
      }
      const destination = join(root, 'kit.zip')
      expect(
        await runEditorCli(['archive', fixture.job.id, destination], env),
      ).toMatchObject({
        archiveEntriesVerified: 8,
        downloadedBytesVerified: true,
        bytes: data.length,
        sha256: createHash('sha256').update(data).digest('hex'),
        heard: false,
        creativelyAccepted: false,
      })
      await expect(
        runEditorCli(['archive', fixture.job.id, destination], env),
      ).rejects.toThrow('EEXIST')
      expect(await readFile(destination)).toEqual(Buffer.from(data))
      expect(
        network.mock.calls.filter(([url]) =>
          new URL(url).pathname.endsWith('/archive'),
        ),
      ).toHaveLength(1)
    } finally {
      fixture.database.close()
      await rm(root, { recursive: true })
    }
  })
  it('removes its own partial archive and rejects corrupt ZIP content with valid response metadata', async () => {
    const fixture = await kitFixture()
    const root = await mkdtemp(join(tmpdir(), 'editor-bad-kit-'))
    try {
      const kit = await prepareKit(
        fixture.store,
        fixture.media,
        'one',
        fixture.job,
      )
      const data = Buffer.from(
        await new Response(
          streamZip(kit.entries, nodeArchiveHash),
        ).arrayBuffer(),
      )
      const altered = Buffer.from(data)
      altered[altered.indexOf(Buffer.from('synthetic-film'))] = 0
      for (const [index, content] of [
        data.subarray(0, data.length - 30),
        altered,
      ].entries()) {
        vi.stubGlobal(
          'fetch',
          vi.fn(async (url: string | URL) =>
            new URL(url).pathname.includes('/tools/')
              ? Response.json(kit.descriptor)
              : new Response(content, {
                  headers: {
                    'Content-Type': 'application/zip',
                    'Content-Length': String(kit.descriptor.bytes),
                    'X-Kit-Manifest-Sha256': kit.descriptor.manifestSha256,
                  },
                }),
          ),
        )
        const destination = join(root, `bad-${index}.zip`)
        await expect(
          runEditorCli(['archive', fixture.job.id, destination], {
            EDITOR_URL: 'https://editor.example',
            EDITOR_TOKEN: 'private',
          }),
        ).rejects.toThrow()
        await expect(stat(destination)).rejects.toThrow('ENOENT')
      }
    } finally {
      fixture.database.close()
      await rm(root, { recursive: true })
    }
  })
  it('discovers tool schemas and honest feature progress without credentials', async () => {
    expect(await runEditorCli(['tools'], {})).toMatchObject({
      source: 'local-client',
    })
    expect(await runEditorCli(['progress'], {})).toMatchObject({
      cloudVerified: false,
      fullKitCompleted: false,
    })
    expect(await runEditorCli(['schema', 'project'], {})).toMatchObject({
      $schema: 'https://json-schema.org/draft/2020-12/schema',
      additionalProperties: false,
    })
    expect(await runEditorCli(['schema', 'production-plan'], {})).toMatchObject(
      {
        $schema: 'https://json-schema.org/draft/2020-12/schema',
        additionalProperties: false,
        properties: { schemaVersion: { enum: [2] } },
      },
    )
  })
  it('rejects insecure origins, embedded credentials and unknown tools before network activity', async () => {
    const fetch = vi.fn()
    vi.stubGlobal('fetch', fetch)
    await expect(
      runEditorCli(['health'], { EDITOR_URL: 'http://editor.example' }),
    ).rejects.toThrow('HTTPS')
    await expect(
      runEditorCli(['health'], {
        EDITOR_URL: 'https://user:password@editor.example',
      }),
    ).rejects.toThrow('clean service origin')
    await expect(
      runEditorCli(['call', 'exec'], {
        EDITOR_URL: 'https://editor.example',
        EDITOR_TOKEN: 'private',
      }),
    ).rejects.toThrow('Unknown editor tool')
    expect(fetch).not.toHaveBeenCalled()
  })
  it('reads actual service capabilities without leaking its token into output', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () =>
        Response.json({
          service: 'release-kit-editor',
          cloudRenderVerified: false,
        }),
      ),
    )
    const result = await runEditorCli(['health'], {
      EDITOR_URL: 'https://editor.example',
      EDITOR_TOKEN: 'private-token',
    })
    expect(result).toMatchObject({ cloudRenderVerified: false })
    expect(JSON.stringify(result)).not.toContain('private-token')
  })
  it('checks source bytes before upload and resumes an acknowledged immutable upload', async () => {
    const root = await mkdtemp(join(tmpdir(), 'editor-upload-'))
    try {
      const source = Buffer.from('source-audio-fixture')
      const asset = {
        id: 'audio',
        kind: 'audio',
        sha256: createHash('sha256').update(source).digest('hex'),
        bytes: source.byteLength,
        width: 0,
        height: 0,
        duration: 1,
      }
      const metadata = join(root, 'asset.json')
      const media = join(root, 'source.wav')
      await writeFile(metadata, JSON.stringify(asset))
      await writeFile(media, Buffer.from('x'.repeat(source.byteLength)))
      const network = vi.fn(async (_url: string | URL, _init?: RequestInit) =>
        Response.json({
          uploaded: true,
          metadata: asset,
          mediaProbeVerified: false,
        }),
      )
      vi.stubGlobal('fetch', network)
      const env = {
        EDITOR_URL: 'https://editor.example',
        EDITOR_TOKEN: 'private-token',
      }
      await expect(
        runEditorCli(['upload', metadata, media], env),
      ).rejects.toThrow('checksum')
      expect(network).not.toHaveBeenCalled()
      await writeFile(media, source)
      expect(
        await runEditorCli(['upload', metadata, media], env),
      ).toMatchObject({ uploaded: true, resumedExistingUpload: true })
      expect(network).toHaveBeenCalledTimes(3)
      expect(
        network.mock.calls.some(([, init]) => init?.method === 'PUT'),
      ).toBe(false)
    } finally {
      await rm(root, { recursive: true })
    }
  })
  it('verifies downloaded bytes, preserves existing files and removes failed downloads', async () => {
    const root = await mkdtemp(join(tmpdir(), 'editor-download-'))
    try {
      const source = new TextEncoder().encode('encoded-output-fixture')
      const artifact = {
        id: 'film',
        sha256: createHash('sha256').update(source).digest('hex'),
        bytes: source.byteLength,
      }
      const env = {
        EDITOR_URL: 'https://editor.example',
        EDITOR_TOKEN: 'private-token',
      }
      const serve = (data: Uint8Array<ArrayBuffer>) =>
        vi.fn(async (url: string | URL) =>
          new URL(url).pathname.includes('/tools/')
            ? Response.json({ artifact })
            : new Response(data, {
                headers: { 'Content-Length': String(source.byteLength) },
              }),
        )
      vi.stubGlobal('fetch', serve(source))
      const destination = join(root, 'film.mp4')
      expect(
        await runEditorCli(['download', 'job-1', 'film', destination], env),
      ).toMatchObject({
        downloadedBytesVerified: true,
        creativelyAccepted: false,
      })
      await expect(
        runEditorCli(['download', 'job-1', 'film', destination], env),
      ).rejects.toThrow('EEXIST')
      expect(await readFile(destination)).toEqual(Buffer.from(source))
      vi.stubGlobal('fetch', serve(new Uint8Array(source.byteLength)))
      const corrupt = join(root, 'corrupt.mp4')
      await expect(
        runEditorCli(['download', 'job-1', 'film', corrupt], env),
      ).rejects.toThrow('checksum')
      await expect(stat(corrupt)).rejects.toThrow('ENOENT')
    } finally {
      await rm(root, { recursive: true })
    }
  })
})
