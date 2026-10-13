import { mkdtemp, readdir, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { afterEach, describe, expect, it } from 'vitest'

import { digest } from '../store'
import { LocalMedia, localFixedStream } from './adapters'

const directories: Array<string> = []
const fixture = async () => {
  const root = await mkdtemp(join(tmpdir(), 'editor-local-'))
  directories.push(root)
  return { root, media: new LocalMedia(root) }
}
const options = async (text: string) => ({
  sha256: await digest(text),
  httpMetadata: { contentType: 'text/plain' },
  customMetadata: {},
})
afterEach(async () => {
  for (const root of directories.splice(0))
    await rm(root, { recursive: true, force: true })
})
describe('standalone local media', () => {
  it('stores exact bytes and supports the shared API range and etag contract', async () => {
    const { media } = await fixture()
    await media.put(
      'editor/one/asset',
      new Blob(['abcdef']).stream(),
      await options('abcdef'),
    )
    const head = await media.head('editor/one/asset')
    expect(head?.size).toBe(6)
    const range = await media.get('editor/one/asset', {
      range: { offset: 2, length: 3 },
      onlyIf: { etagMatches: head!.etag! },
    })
    expect(range?.size).toBe(6)
    expect(await new Response(range!.body).text()).toBe('cde')
    expect(
      await media.get('editor/one/asset', { onlyIf: { etagMatches: 'wrong' } }),
    ).toBeNull()
  })
  it('rejects corrupt uploads before publishing and preserves the previous object', async () => {
    const { root, media } = await fixture()
    await media.put(
      'editor/one/asset',
      new Blob(['good']).stream(),
      await options('good'),
    )
    await expect(
      media.put(
        'editor/one/asset',
        new Blob(['bad']).stream(),
        await options('good'),
      ),
    ).rejects.toThrow('hash differs')
    expect(
      await new Response(
        (await media.get('editor/one/asset', {}))!.body,
      ).text(),
    ).toBe('good')
    expect((await readdir(root)).filter(name => name.endsWith('.tmp'))).toEqual(
      [],
    )
    expect(() => media.path('../outside')).toThrow('Invalid private object key')
  })
  it('rejects truncated streams without publishing a partial object', async () => {
    const { root, media } = await fixture()
    const stream = localFixedStream(6)
    const results = await Promise.allSettled([
      media.put('editor/one/asset', stream.readable, await options('abcdef')),
      new Blob(['abc']).stream().pipeTo(stream.writable),
    ])
    expect(results.every(result => result.status === 'rejected')).toBe(true)
    expect(await media.head('editor/one/asset')).toBeNull()
    expect(await readdir(root)).toEqual([])
  })
  it('rejects oversized streams instead of accepting matching prefix bytes', async () => {
    const { media } = await fixture()
    const stream = localFixedStream(3)
    const results = await Promise.allSettled([
      media.put('editor/one/asset', stream.readable, await options('abc')),
      new Blob(['abcdef']).stream().pipeTo(stream.writable),
    ])
    expect(results.every(result => result.status === 'rejected')).toBe(true)
    expect(await media.head('editor/one/asset')).toBeNull()
  })
})
