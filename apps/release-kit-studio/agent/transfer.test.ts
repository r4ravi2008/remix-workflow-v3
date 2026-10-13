// @vitest-environment node
import { createHash } from 'node:crypto'
import {
  mkdtemp,
  readFile,
  readdir,
  rm,
  stat,
  writeFile,
} from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { afterEach, describe, expect, it } from 'vitest'

import {
  downloadVerified,
  fileReceipt,
  readPart,
  responseReceipt,
} from './transfer'

const temporaryDirectories: Array<string> = []
const fixture = async () => {
  const directory = await mkdtemp(join(tmpdir(), 'release-kit-transfer-'))
  temporaryDirectories.push(directory)
  return directory
}
afterEach(async () => {
  await Promise.all(
    temporaryDirectories
      .splice(0)
      .map(directory => rm(directory, { recursive: true, force: true })),
  )
})
const digest = (bytes: Uint8Array) =>
  createHash('sha256').update(bytes).digest('hex')

describe('bounded asset transfer', () => {
  it('reads an 11 MiB file in two bounded parts and hashes the full stream', async () => {
    const directory = await fixture()
    const path = join(directory, 'original.mp4')
    const source = Buffer.alloc(11 * 1024 * 1024, 73)
    await writeFile(path, source)
    const signal = new AbortController().signal
    const first = await readPart(path, 0, 8 * 1024 * 1024, signal)
    const last = await readPart(path, first.byteLength, 3 * 1024 * 1024, signal)
    expect(first.byteLength).toBe(8 * 1024 * 1024)
    expect(last.byteLength).toBe(3 * 1024 * 1024)
    expect(digest(Buffer.concat([first, last]))).toBe(digest(source))
    expect(await fileReceipt(path)).toEqual({
      bytes: source.byteLength,
      sha256: digest(source),
    })
    const response = new Response(
      new ReadableStream<Uint8Array>({
        start(controller) {
          controller.enqueue(first)
          controller.enqueue(last)
          controller.close()
        },
      }),
    )
    expect(await responseReceipt(response, source.byteLength, signal)).toEqual(
      await fileReceipt(path),
    )
    await expect(readPart(path, 0, 9 * 1024 * 1024, signal)).rejects.toThrow(
      '8 MiB',
    )
    await expect(
      readPart(path, source.byteLength - 1, 2, signal),
    ).rejects.toThrow('truncated')
  })

  it('publishes only a hash-verified source and preserves it after corrupted or oversized downloads', async () => {
    const directory = await fixture()
    const destination = join(directory, 'canonical-audio')
    const source = new TextEncoder().encode('the immutable song')
    const expected = { bytes: source.byteLength, sha256: digest(source) }
    const signal = new AbortController().signal
    await downloadVerified(new Response(source), destination, expected, signal)
    expect((await stat(destination)).mode & 0o777).toBe(0o600)
    await expect(
      downloadVerified(
        new Response(new Uint8Array(source.byteLength)),
        destination,
        expected,
        signal,
      ),
    ).rejects.toThrow('immutable release brief')
    await expect(
      downloadVerified(
        new Response(new Uint8Array(source.byteLength + 1)),
        destination,
        expected,
        signal,
      ),
    ).rejects.toThrow('declared byte count')
    expect(await readFile(destination)).toEqual(Buffer.from(source))
    expect(await readdir(directory)).toEqual(['canonical-audio'])
    await expect(
      responseReceipt(new Response(source.slice(1)), source.byteLength, signal),
    ).rejects.toThrow('shorter')
  })

  it('cancels a stalled source stream and removes its partial file when the lease is lost', async () => {
    const directory = await fixture()
    const controller = new AbortController()
    const state = { cancelled: false }
    const response = new Response(
      new ReadableStream<Uint8Array>({
        start(stream) {
          stream.enqueue(new Uint8Array([1, 2]))
        },
        cancel() {
          state.cancelled = true
        },
      }),
    )
    const result = downloadVerified(
      response,
      join(directory, 'canonical-audio'),
      { bytes: 4, sha256: 'a'.repeat(64) },
      controller.signal,
    )
    controller.abort()
    await expect(result).rejects.toThrow()
    expect(state.cancelled).toBe(true)
    expect(await readdir(directory)).toEqual([])
  })
})
