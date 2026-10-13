export interface ArchiveEntry {
  name: string
  bytes: number
  sha256: string
  open: () => Promise<ReadableStream<Uint8Array>>
}
export interface ArchiveHasher {
  write: (data: Uint8Array) => Promise<void>
  finish: () => Promise<string>
  abort: (reason: unknown) => Promise<void>
}
export type ArchiveHashFactory = () => ArchiveHasher
type DigestWritable = WritableStream<Uint8Array> & {
  digest: Promise<ArrayBuffer>
}
declare global {
  interface Crypto {
    DigestStream: new (algorithm: string) => DigestWritable
  }
}
const text = new TextEncoder()
const crcTable = Uint32Array.from({ length: 256 }, (_, index) => {
  const state = { value: index }
  for (const _ of Array.from({ length: 8 }))
    state.value = (state.value >>> 1) ^ (state.value & 1 ? 0xedb88320 : 0)
  return state.value >>> 0
})
const crcUpdate = (crc: number, bytes: Uint8Array) => {
  const state = { value: crc }
  for (const byte of bytes)
    state.value = (state.value >>> 8) ^ crcTable[(state.value ^ byte) & 255]!
  return state.value >>> 0
}
const packet = (length: number) => {
  const data = new Uint8Array(length)
  const view = new DataView(data.buffer)
  return { data, view }
}
const safeEntries = (entries: ReadonlyArray<ArchiveEntry>) => {
  if (
    !entries.length ||
    entries.length > 16 ||
    new Set(entries.map(entry => entry.name)).size !== entries.length
  )
    throw new Error('Archive entries must be distinct and bounded.')
  for (const entry of entries)
    if (
      !/^[a-zA-Z0-9][a-zA-Z0-9._-]{0,99}$/.test(entry.name) ||
      !Number.isSafeInteger(entry.bytes) ||
      entry.bytes < 1 ||
      entry.bytes > 2147483648 ||
      !/^[a-f0-9]{64}$/.test(entry.sha256)
    )
      throw new Error(
        'Archive entry names, sizes and checksums must be safe and measured.',
      )
}
export const zipBytes = (entries: ReadonlyArray<ArchiveEntry>) => {
  safeEntries(entries)
  // Every entry uses ZIP64, even when small. Length is known before streaming.
  return (
    entries.reduce(
      (sum, entry) =>
        sum +
        entry.bytes +
        30 +
        text.encode(entry.name).length +
        20 +
        24 +
        46 +
        text.encode(entry.name).length +
        28,
      0,
    ) +
    56 +
    20 +
    22
  )
}
const localHeader = (entry: ArchiveEntry) => {
  const name = text.encode(entry.name)
  const result = packet(30 + name.length + 20)
  result.view.setUint32(0, 0x04034b50, true)
  result.view.setUint16(4, 45, true)
  result.view.setUint16(6, 0x0808, true)
  result.view.setUint16(12, 33, true)
  result.view.setUint32(18, 0xffffffff, true)
  result.view.setUint32(22, 0xffffffff, true)
  result.view.setUint16(26, name.length, true)
  result.view.setUint16(28, 20, true)
  result.data.set(name, 30)
  const extra = 30 + name.length
  result.view.setUint16(extra, 1, true)
  result.view.setUint16(extra + 2, 16, true)
  result.view.setBigUint64(extra + 4, BigInt(entry.bytes), true)
  result.view.setBigUint64(extra + 12, BigInt(entry.bytes), true)
  return result.data
}
const descriptor = (entry: ArchiveEntry, crc: number) => {
  const result = packet(24)
  result.view.setUint32(0, 0x08074b50, true)
  result.view.setUint32(4, crc, true)
  result.view.setBigUint64(8, BigInt(entry.bytes), true)
  result.view.setBigUint64(16, BigInt(entry.bytes), true)
  return result.data
}
const directoryHeader = (entry: ArchiveEntry, crc: number, offset: number) => {
  const name = text.encode(entry.name)
  const result = packet(46 + name.length + 28)
  result.view.setUint32(0, 0x02014b50, true)
  result.view.setUint16(4, 45, true)
  result.view.setUint16(6, 45, true)
  result.view.setUint16(8, 0x0808, true)
  result.view.setUint16(14, 33, true)
  result.view.setUint32(16, crc, true)
  result.view.setUint32(20, 0xffffffff, true)
  result.view.setUint32(24, 0xffffffff, true)
  result.view.setUint16(28, name.length, true)
  result.view.setUint16(30, 28, true)
  result.view.setUint32(42, 0xffffffff, true)
  result.data.set(name, 46)
  const extra = 46 + name.length
  result.view.setUint16(extra, 1, true)
  result.view.setUint16(extra + 2, 24, true)
  result.view.setBigUint64(extra + 4, BigInt(entry.bytes), true)
  result.view.setBigUint64(extra + 12, BigInt(entry.bytes), true)
  result.view.setBigUint64(extra + 20, BigInt(offset), true)
  return result.data
}
const ending = (count: number, size: number, offset: number) => {
  const result = packet(98)
  result.view.setUint32(0, 0x06064b50, true)
  result.view.setBigUint64(4, 44n, true)
  result.view.setUint16(12, 45, true)
  result.view.setUint16(14, 45, true)
  result.view.setBigUint64(24, BigInt(count), true)
  result.view.setBigUint64(32, BigInt(count), true)
  result.view.setBigUint64(40, BigInt(size), true)
  result.view.setBigUint64(48, BigInt(offset), true)
  result.view.setUint32(56, 0x07064b50, true)
  result.view.setBigUint64(64, BigInt(offset + size), true)
  result.view.setUint32(72, 1, true)
  result.view.setUint32(76, 0x06054b50, true)
  result.view.setUint16(84, 0xffff, true)
  result.view.setUint16(86, 0xffff, true)
  result.view.setUint32(88, 0xffffffff, true)
  result.view.setUint32(92, 0xffffffff, true)
  return result.data
}
export const workerArchiveHash: ArchiveHashFactory = () => {
  const writable = new crypto.DigestStream('SHA-256')
  void writable.digest.catch(() => {})
  const writer = writable.getWriter()
  return {
    write: bytes => writer.write(bytes),
    finish: async () => {
      await writer.close()
      return Array.from(new Uint8Array(await writable.digest), byte =>
        byte.toString(16).padStart(2, '0'),
      ).join('')
    },
    abort: reason => writer.abort(reason).catch(() => {}),
  }
}
export const streamZip = (
  entries: ReadonlyArray<ArchiveEntry>,
  hashFactory: ArchiveHashFactory = workerArchiveHash,
) => {
  safeEntries(entries)
  const active: {
    cancelled: boolean
    reader: ReadableStreamDefaultReader<Uint8Array> | null
    hash: ArchiveHasher | null
  } = {
    cancelled: false,
    reader: null,
    hash: null,
  }
  const generate = async function* () {
    const directory: Array<Uint8Array> = []
    const position = { bytes: 0 }
    for (const entry of entries) {
      if (active.cancelled) return
      const start = position.bytes
      const header = localHeader(entry)
      position.bytes += header.byteLength
      yield header
      const reader = (await entry.open()).getReader()
      active.reader = reader
      if (active.cancelled) {
        await reader.cancel()
        reader.releaseLock()
        active.reader = null
        return
      }
      const hash = hashFactory()
      active.hash = hash
      const observed = { bytes: 0, crc: 0xffffffff, complete: false }
      try {
        for (;;) {
          const part = await reader.read()
          if (active.cancelled) throw new Error('Archive read cancelled.')
          if (part.done) break
          observed.bytes += part.value.byteLength
          if (observed.bytes > entry.bytes)
            throw new Error('Archive source exceeds its verified byte count.')
          observed.crc = crcUpdate(observed.crc, part.value)
          await hash.write(part.value)
          position.bytes += part.value.byteLength
          yield part.value
        }
        if (
          observed.bytes !== entry.bytes ||
          (await hash.finish()) !== entry.sha256
        )
          throw new Error(
            'Archive source differs from its verified checksum or byte count.',
          )
        observed.complete = true
      } finally {
        if (!observed.complete)
          await hash.abort('Archive read cancelled or failed.')
        await reader.cancel().catch(() => {})
        reader.releaseLock()
        active.reader = null
        active.hash = null
      }
      const crc = (observed.crc ^ 0xffffffff) >>> 0
      const footer = descriptor(entry, crc)
      position.bytes += footer.byteLength
      yield footer
      directory.push(directoryHeader(entry, crc, start))
    }
    const offset = position.bytes
    for (const entry of directory) {
      position.bytes += entry.byteLength
      yield entry
    }
    yield ending(entries.length, position.bytes - offset, offset)
  }
  const iterator = generate()
  return new ReadableStream<Uint8Array>(
    {
      pull: async controller => {
        try {
          const next = await iterator.next()
          if (next.done) controller.close()
          else controller.enqueue(next.value)
        } catch (error) {
          controller.error(error)
          await iterator.return(undefined)
        }
      },
      cancel: async reason => {
        active.cancelled = true
        await Promise.allSettled([
          active.reader?.cancel(reason),
          active.hash?.abort(reason),
        ])
        await iterator.return(undefined)
      },
    },
    { highWaterMark: 0 },
  )
}
