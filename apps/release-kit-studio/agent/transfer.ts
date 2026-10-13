import { createHash } from 'node:crypto'
import { createReadStream, createWriteStream } from 'node:fs'
import { open, rename, stat, unlink } from 'node:fs/promises'
import { Readable, Transform, Writable } from 'node:stream'
import { pipeline } from 'node:stream/promises'

export interface FileReceipt {
  bytes: number
  sha256: string
}

const responseStream = (response: Response, signal: AbortSignal) => {
  signal.throwIfAborted()
  if (!response.body) throw new Error('The asset response has no body.')
  const reader = response.body.getReader()
  const abort = () => {
    void reader.cancel().catch(() => undefined)
  }
  signal.addEventListener('abort', abort, { once: true })
  const stream = Readable.from({
    [Symbol.asyncIterator]: () => ({
      next: () => reader.read(),
      return: async (): Promise<IteratorResult<Uint8Array>> => {
        await reader.cancel()
        return { done: true, value: undefined }
      },
    }),
  })
  stream.once('close', () => signal.removeEventListener('abort', abort))
  return stream
}

const digestStream = (limit: number) => {
  const hash = createHash('sha256')
  const count = { bytes: 0 }
  const stream = new Transform({
    transform(chunk: Buffer, _encoding, callback) {
      count.bytes += chunk.byteLength
      if (count.bytes > limit) {
        callback(new Error('The asset exceeds its declared byte count.'))
        return
      }
      hash.update(chunk)
      callback(null, chunk)
    },
  })
  return {
    stream,
    receipt: (): FileReceipt => ({
      bytes: count.bytes,
      sha256: hash.digest('hex'),
    }),
  }
}

export const fileReceipt = async (
  path: string,
  signal: AbortSignal = new AbortController().signal,
): Promise<FileReceipt> => {
  const before = await stat(path)
  if (!before.isFile()) throw new Error('An output must be a regular file.')
  const digest = digestStream(before.size)
  const discard = new Writable({
    write(_chunk, _encoding, callback) {
      callback()
    },
  })
  await pipeline(createReadStream(path), digest.stream, discard, { signal })
  const after = await stat(path)
  const receipt = digest.receipt()
  if (
    before.ino !== after.ino ||
    before.mtimeMs !== after.mtimeMs ||
    before.size !== after.size ||
    receipt.bytes !== before.size
  )
    throw new Error('The file changed while its receipt was measured.')
  return receipt
}

export const responseReceipt = async (
  response: Response,
  bytes: number,
  signal: AbortSignal,
): Promise<FileReceipt> => {
  const digest = digestStream(bytes)
  const discard = new Writable({
    write(_chunk, _encoding, callback) {
      callback()
    },
  })
  await pipeline(responseStream(response, signal), digest.stream, discard, {
    signal,
  })
  const receipt = digest.receipt()
  if (receipt.bytes !== bytes)
    throw new Error('The stored asset is shorter than its declared byte count.')
  return receipt
}

export const downloadVerified = async (
  response: Response,
  destination: string,
  expected: FileReceipt,
  signal: AbortSignal,
) => {
  const temporary = `${destination}.incoming-${crypto.randomUUID()}`
  try {
    const digest = digestStream(expected.bytes)
    await pipeline(
      responseStream(response, signal),
      digest.stream,
      createWriteStream(temporary, { mode: 0o600, flags: 'wx' }),
      { signal },
    )
    const actual = digest.receipt()
    if (actual.bytes !== expected.bytes || actual.sha256 !== expected.sha256)
      throw new Error(
        'Downloaded audio differs from the immutable release brief.',
      )
    signal.throwIfAborted()
    await rename(temporary, destination)
  } finally {
    await unlink(temporary).catch(error => {
      if (error.code !== 'ENOENT') throw error
    })
  }
}

export const readPart = async (
  path: string,
  offset: number,
  bytes: number,
  signal: AbortSignal,
): Promise<Uint8Array<ArrayBuffer>> => {
  if (!Number.isSafeInteger(bytes) || bytes <= 0 || bytes > 8 * 1024 * 1024)
    throw new Error('An upload part must be between 1 byte and 8 MiB.')
  const file = await open(path, 'r')
  try {
    const buffer = Buffer.allocUnsafe(bytes)
    const fill = async (position: number): Promise<Uint8Array<ArrayBuffer>> => {
      signal.throwIfAborted()
      const result = await file.read(
        buffer,
        position,
        bytes - position,
        offset + position,
      )
      if (result.bytesRead === 0)
        throw new Error('The rendered file was truncated during upload.')
      const next = position + result.bytesRead
      return next === bytes ? new Uint8Array(buffer) : fill(next)
    }
    return await fill(0)
  } finally {
    await file.close()
  }
}
