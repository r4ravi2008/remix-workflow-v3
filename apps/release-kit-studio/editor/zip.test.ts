import { execFileSync } from 'node:child_process'
// @vitest-environment node
import { createHash } from 'node:crypto'
import { mkdtemp, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { describe, expect, it, vi } from 'vitest'

import { nodeArchiveHash } from './kit-testing'
import { type ArchiveEntry, streamZip, zipBytes } from './zip'

const entry = (name: string, content: string): ArchiveEntry => ({
  name,
  bytes: Buffer.byteLength(content),
  sha256: createHash('sha256').update(content).digest('hex'),
  open: async () => new Blob([content]).stream(),
})
describe('streaming ZIP64', () => {
  it('round-trips UTF-8 bytes through the independent Python ZIP reader with exact lengths and CRCs', async () => {
    const entries = [
      entry('film.mp4', 'binary-fixture'),
      entry('project.json', 'ప్రతి నిమిషం'),
    ]
    const bytes = new Uint8Array(
      await new Response(streamZip(entries, nodeArchiveHash)).arrayBuffer(),
    )
    expect(bytes.length).toBe(zipBytes(entries))
    const root = await mkdtemp(join(tmpdir(), 'zip64-'))
    try {
      const path = join(root, 'kit.zip')
      await writeFile(path, bytes)
      const result = execFileSync(
        'python3',
        [
          '-c',
          'import zipfile,sys,json; z=zipfile.ZipFile(sys.argv[1]); assert z.testzip() is None; print(json.dumps({i.filename:z.read(i).decode() for i in z.infolist()},ensure_ascii=False))',
          path,
        ],
        { encoding: 'utf8' },
      )
      expect(JSON.parse(result)).toEqual({
        'film.mp4': 'binary-fixture',
        'project.json': 'ప్రతి నిమిషం',
      })
    } finally {
      await rm(root, { recursive: true })
    }
    expect(
      zipBytes(
        Array.from({ length: 6 }, (_, index) => ({
          ...entries[0]!,
          name: `output-${index}.mp4`,
          bytes: 2147483648,
        })),
      ),
    ).toBeGreaterThan(4294967295)
    expect(() => zipBytes([entry('../escape', 'x')])).toThrow('safe')
  })
  it('rejects same-size corruption and truncation before a ZIP can complete', async () => {
    for (const content of ['tampered', 'short']) {
      const source = {
        ...entry('film.mp4', 'original'),
        open: async () => new Blob([content]).stream(),
      }
      await expect(
        new Response(streamZip([source], nodeArchiveHash)).arrayBuffer(),
      ).rejects.toThrow('checksum or byte count')
    }
  })
  it('cancels a pending source read promptly and leaves later entries unopened', async () => {
    const cancelled = vi.fn()
    const next = vi.fn(async () => new Blob(['later']).stream())
    const started = { resolve: () => {} }
    const reading = new Promise<void>(resolve => {
      started.resolve = resolve
    })
    const source = {
      ...entry('film.mp4', 'original'),
      open: async () =>
        new ReadableStream<Uint8Array>({
          pull: () => started.resolve(),
          cancel: cancelled,
        }),
    }
    const reader = streamZip(
      [source, { ...entry('other.mp4', 'later'), open: next }],
      nodeArchiveHash,
    ).getReader()
    await reader.read()
    const pending = reader.read()
    await reading
    await reader.cancel('consumer stopped')
    await pending
    expect(cancelled).toHaveBeenCalledOnce()
    expect(next).not.toHaveBeenCalled()
  })
})
