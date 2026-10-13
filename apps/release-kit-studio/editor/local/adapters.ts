import { Schema } from 'effect'
import { type ChildProcess, spawn } from 'node:child_process'
import { createHash, randomUUID } from 'node:crypto'
import { once } from 'node:events'
import { createReadStream, createWriteStream } from 'node:fs'
import { mkdir, mkdtemp, open, rename, rm, stat } from 'node:fs/promises'
import { request as httpRequest } from 'node:http'
import { join, resolve } from 'node:path'
import { createInterface } from 'node:readline'
import { Readable } from 'node:stream'
import { pipeline } from 'node:stream/promises'

import type { MediaBucket } from '../../src/server/api'
import type { SqlDatabase } from '../../src/server/store'
import type {
  CoordinatorContext,
  CoordinatorTransaction,
} from '../render-coordinator'
import { EditorError } from '../store'
import type { ArchiveHashFactory } from '../zip'

export const localArchiveHash: ArchiveHashFactory = () => {
  const hash = createHash('sha256')
  return {
    write: async bytes => {
      hash.update(bytes)
    },
    finish: async () => hash.digest('hex'),
    abort: async () => {},
  }
}
export const localFixedStream = (length: number) => {
  const observed = { bytes: 0 }
  return new TransformStream<Uint8Array, Uint8Array>({
    transform(chunk, controller) {
      observed.bytes += chunk.byteLength
      if (observed.bytes > length)
        throw new Error('Stream exceeds its registered byte count.')
      controller.enqueue(chunk)
    },
    flush() {
      if (observed.bytes !== length)
        throw new Error('Stream is shorter than its registered byte count.')
    },
  })
}
const fileHash = async (path: string) => {
  const hash = createHash('sha256')
  for await (const block of createReadStream(path)) hash.update(block)
  return hash.digest('hex')
}
const webBytes = (stream: Readable) => {
  const iterator = stream[Symbol.asyncIterator]()
  return new ReadableStream<Uint8Array>({
    async pull(controller) {
      const result = await iterator.next()
      if (result.done) controller.close()
      else if (result.value instanceof Uint8Array)
        controller.enqueue(result.value)
      else
        controller.error(new Error('Local object returned a non-byte stream.'))
    },
    cancel() {
      stream.destroy()
    },
  })
}
const streamUpload = async (
  url: URL,
  length: string,
  body: ReadableStream<Uint8Array>,
  transfer: string,
) => {
  const child = spawn(
    process.env.EDITOR_PYTHON ?? 'python3',
    [transfer, url.href, length],
    { stdio: ['pipe', 'pipe', 'pipe'] },
  )
  const failure = { text: '' }
  child.stderr!.on('data', data => {
    failure.text = (failure.text + data.toString()).slice(-2000)
  })
  const completion = new Promise<void>((done, fail) => {
    child.once('error', fail)
    child.once('exit', code =>
      code === 0
        ? done()
        : fail(
            new Error('Exact-length local transfer failed: ' + failure.text),
          ),
    )
  })
  void completion.catch(() => {})
  const timer = setTimeout(() => child.kill('SIGTERM'), 600000)
  void completion.finally(() => clearTimeout(timer)).catch(() => {})
  void pipeline(
    Readable.from(
      (async function* () {
        const reader = body.getReader()
        try {
          for (;;) {
            const chunk = await reader.read()
            if (chunk.done) return
            yield chunk.value
          }
        } finally {
          await reader.cancel().catch(() => {})
          reader.releaseLock()
        }
      })(),
    ),
    child.stdin!,
  ).catch(() => child.kill('SIGTERM'))
  const iterator = child.stdout![Symbol.asyncIterator]()
  const framed = { bytes: Buffer.alloc(0) }
  for (;;) {
    const chunk = await iterator.next()
    if (chunk.done) {
      await completion
      throw new Error('Local transfer did not return an HTTP response.')
    }
    framed.bytes = Buffer.concat([framed.bytes, chunk.value])
    const newline = framed.bytes.indexOf(10)
    if (newline >= 0) {
      const metadata = Schema.decodeUnknownSync(
        Schema.Struct({
          status: Schema.Int,
          headers: Schema.Record(Schema.String, Schema.String),
        }),
      )(JSON.parse(framed.bytes.subarray(0, newline).toString()))
      const remainder = framed.bytes.subarray(newline + 1)
      return new Response(
        new ReadableStream<Uint8Array>({
          start(controller) {
            if (remainder.byteLength) controller.enqueue(remainder)
          },
          async pull(controller) {
            const chunk = await iterator.next()
            if (chunk.done) {
              await completion
              controller.close()
            } else if (chunk.value instanceof Uint8Array)
              controller.enqueue(chunk.value)
            else
              controller.error(
                new Error('Invalid local transfer response bytes.'),
              )
          },
          cancel() {
            child.kill('SIGTERM')
          },
        }),
        { status: metadata.status, headers: metadata.headers },
      )
    }
    if (framed.bytes.byteLength > 65536) {
      child.kill('SIGTERM')
      throw new Error('Local transfer response header exceeds 64 KiB.')
    }
  }
}
const nativeRequest = (url: URL, init: RequestInit): Promise<Response> =>
  new Promise((resolveResponse, reject) => {
    const headers = new Headers(init.headers)
    const body = init.body
    if (typeof body === 'string')
      headers.set('Content-Length', String(Buffer.byteLength(body)))
    if (body instanceof ReadableStream && !headers.has('Content-Length')) {
      reject(
        new Error(
          'Local native uploads require their immutable Content-Length.',
        ),
      )
      return
    }
    const outgoing = httpRequest(
      url,
      {
        method: init.method ?? 'GET',
        headers: Object.fromEntries(headers.entries()),
        signal: AbortSignal.timeout(600000),
      },
      incoming => {
        const responseHeaders = new Headers()
        for (const [name, value] of Object.entries(incoming.headers))
          if (value !== undefined)
            responseHeaders.set(
              name,
              Array.isArray(value) ? value.join(', ') : value,
            )
        resolveResponse(
          new Response(webBytes(incoming), {
            status: incoming.statusCode ?? 500,
            headers: responseHeaders,
          }),
        )
      },
    )
    outgoing.once('error', reject)
    void (async () => {
      if (body instanceof ReadableStream) {
        const reader = body.getReader()
        try {
          for (;;) {
            const chunk = await reader.read()
            if (chunk.done) break
            if (!outgoing.write(chunk.value)) await once(outgoing, 'drain')
          }
        } finally {
          await reader.cancel().catch(() => {})
          reader.releaseLock()
        }
        outgoing.end()
      } else if (
        typeof body === 'string' ||
        body === undefined ||
        body === null
      )
        outgoing.end(body)
      else throw new Error('Unsupported local native request body.')
    })().catch(error => {
      outgoing.destroy()
      reject(error)
    })
  })

export class LocalMedia implements MediaBucket {
  constructor(readonly root: string) {}
  path(key: string) {
    if (
      !/^[a-zA-Z0-9][a-zA-Z0-9/._-]{0,500}$/.test(key) ||
      key.split('/').some(part => ['.', '..', ''].includes(part))
    )
      throw new Error('Invalid private object key.')
    // Object keys remain logical identifiers; files use flat hashed names.
    return join(this.root, createHash('sha256').update(key).digest('hex'))
  }
  async put(
    key: string,
    body: ReadableStream<Uint8Array>,
    options: Parameters<MediaBucket['put']>[2],
  ) {
    await mkdir(this.root, { recursive: true, mode: 0o700 })
    const destination = this.path(key)
    const temporary = destination + '.' + randomUUID() + '.tmp'
    const hash = createHash('sha256')
    try {
      await pipeline(
        Readable.from(
          (async function* () {
            const reader = body.getReader()
            try {
              for (;;) {
                const chunk = await reader.read()
                if (chunk.done) return
                hash.update(chunk.value)
                yield chunk.value
              }
            } finally {
              await reader.cancel().catch(() => {})
              reader.releaseLock()
            }
          })(),
        ),
        createWriteStream(temporary, { flags: 'wx', mode: 0o600 }),
      )
      if (hash.digest('hex') !== options.sha256)
        throw new EditorError(
          422,
          'media_integrity',
          'Local media hash differs from the immutable asset.',
        )
      const handle = await open(temporary, 'r')
      try {
        await handle.sync()
      } finally {
        await handle.close()
      }
      await rename(temporary, destination)
    } finally {
      await rm(temporary, { force: true })
    }
  }
  async head(key: string) {
    const path = this.path(key)
    try {
      return { size: (await stat(path)).size, etag: await fileHash(path) }
    } catch (error) {
      if (
        error &&
        typeof error === 'object' &&
        'code' in error &&
        error.code === 'ENOENT'
      )
        return null
      throw error
    }
  }
  async get(key: string, options: Parameters<MediaBucket['get']>[1]) {
    const head = await this.head(key)
    if (!head || (options.onlyIf && options.onlyIf.etagMatches !== head.etag))
      return null
    const range = options.range
    const end =
      range?.length === undefined
        ? head.size - 1
        : range.offset + range.length - 1
    const stream = createReadStream(
      this.path(key),
      range ? { start: range.offset, end } : {},
    )
    return {
      body: webBytes(stream),
      size: head.size,
      httpEtag: head.etag,
      ...(range
        ? { range: { offset: range.offset, length: end - range.offset + 1 } }
        : {}),
    }
  }
  async createMultipartUpload(): Promise<{ uploadId: string }> {
    throw new Error(
      'The local editor accepts bounded single-part media uploads.',
    )
  }
  resumeMultipartUpload(): ReturnType<MediaBucket['resumeMultipartUpload']> {
    throw new Error(
      'The local editor accepts bounded single-part media uploads.',
    )
  }
}

export class NativeProcess {
  child: ChildProcess | undefined
  origin: string | undefined
  booting: Promise<void> | undefined
  constructor(
    readonly state: string,
    readonly engine: string,
    readonly fontConfig: string,
  ) {}
  get running() {
    return (
      !!this.child &&
      this.child.exitCode === null &&
      this.child.signalCode === null &&
      !!this.origin
    )
  }
  start() {
    this.booting ??= this.launch().finally(() => {
      this.booting = undefined
    })
    return this.booting
  }
  async launch() {
    if (this.running) return
    await mkdir(join(this.state, 'scratch'), { recursive: true, mode: 0o700 })
    const scratch = await mkdtemp(join(this.state, 'scratch', 'native-'))
    const child = spawn(
      process.env.EDITOR_PYTHON ?? 'python3',
      [resolve(this.engine, 'server.py'), '--host', '127.0.0.1', '--port', '0'],
      {
        env: {
          ...process.env,
          EDITOR_SCRATCH: scratch,
          FONTCONFIG_FILE: this.fontConfig,
        },
        stdio: ['ignore', 'pipe', 'pipe'],
        detached: true,
      },
    )
    this.child = child
    const output = createInterface({ input: child.stdout! })
    const log = createWriteStream(join(scratch, 'native.log'), {
      flags: 'a',
      mode: 0o600,
    })
    child.stderr!.pipe(log)
    child.once('exit', () => {
      if (this.child === child) this.origin = undefined
      output.close()
      log.end()
    })
    await new Promise<void>((done, fail) => {
      const timer = setTimeout(
        () =>
          fail(
            new Error('Local native engine did not start within 15 seconds.'),
          ),
        15000,
      )
      const finish = (error?: Error) => {
        clearTimeout(timer)
        child.off('error', onError)
        child.off('exit', onExit)
        output.off('line', onLine)
        error ? fail(error) : done()
      }
      const onError = (error: Error) => finish(error)
      const onExit = () =>
        finish(new Error('Local native engine exited before startup.'))
      const onLine = (line: string) => {
        try {
          const value = JSON.parse(line)
          if (
            value.host !== '127.0.0.1' ||
            !Number.isInteger(value.port) ||
            value.port < 1
          )
            return
          this.origin = `http://127.0.0.1:${value.port}`
          finish()
        } catch {}
      }
      child.once('error', onError)
      child.once('exit', onExit)
      output.on('line', onLine)
    }).catch(async error => {
      await this.destroy()
      throw error
    })
  }
  async setInactivityTimeout() {}
  getTcpPort() {
    return {
      fetch: async (url: string, init: RequestInit) => {
        await this.booting
        if (!this.running || !this.origin)
          throw new Error(
            'Owned local native process is unavailable. Reconcile before replaying.',
          )
        const headers = new Headers(init.headers)
        const target = new URL(new URL(url).pathname, this.origin)
        if (init.body instanceof ReadableStream)
          return streamUpload(
            target,
            headers.get('Content-Length') ?? '0',
            init.body,
            resolve(this.engine, '../local/transfer.py'),
          )
        return nativeRequest(target, { ...init, headers })
      },
    }
  }
  async destroy() {
    const child = this.child
    if (!child || child.exitCode !== null || child.signalCode !== null) {
      this.origin = undefined
      return
    }
    await new Promise<void>(done => {
      const timer = setTimeout(() => {
        if (child.pid) process.kill(-child.pid, 'SIGKILL')
      }, 10000)
      child.once('exit', () => {
        clearTimeout(timer)
        done()
      })
      if (child.pid) process.kill(-child.pid, 'SIGTERM')
    })
    this.child = undefined
    this.origin = undefined
  }
}

export const localContext = (
  name: string,
  db: SqlDatabase,
  native: NativeProcess,
): CoordinatorContext & { onAlarm?: () => Promise<unknown>; close(): void } => {
  const timers: { alarm: ReturnType<typeof setTimeout> | undefined } = {
    alarm: undefined,
  }
  const pending = new Set<Promise<unknown>>()
  const storage: CoordinatorContext['storage'] = {
    get: async <T>(key: string): Promise<T | undefined> => {
      const row = Schema.decodeUnknownSync(
        Schema.NullOr(Schema.Struct({ value: Schema.String })),
      )(
        await db.first(
          'SELECT value FROM local_renderer_state WHERE name=? AND key=?',
          [name, key],
        ),
      )
      return row ? JSON.parse(row.value) : undefined
    },
    put: async (key, value) =>
      db.run(
        'INSERT INTO local_renderer_state(name,key,value) VALUES(?,?,?) ON CONFLICT(name,key) DO UPDATE SET value=excluded.value',
        [name, key, JSON.stringify(value)],
      ),
    delete: async key =>
      db.run('DELETE FROM local_renderer_state WHERE name=? AND key=?', [
        name,
        key,
      ]),
    transaction: async <T>(
      action: (value: CoordinatorTransaction) => Promise<T>,
    ) => action(storage),
    setAlarm: async time => {
      await storage.put('alarm', time)
      if (timers.alarm) clearTimeout(timers.alarm)
      timers.alarm = setTimeout(
        () => {
          timers.alarm = undefined
          const action = context.onAlarm?.() ?? Promise.resolve()
          context.waitUntil(action)
        },
        Math.max(1, time - Date.now()),
      )
    },
    deleteAlarm: async () => {
      if (timers.alarm) clearTimeout(timers.alarm)
      timers.alarm = undefined
      await storage.delete('alarm')
    },
  }
  const context: CoordinatorContext & {
    onAlarm?: () => Promise<unknown>
    close(): void
  } = {
    storage,
    container: native,
    waitUntil(action) {
      pending.add(action)
      void action
        .catch(error =>
          console.error(
            'Local renderer operation failed:',
            error instanceof Error ? error.message : 'unknown error',
          ),
        )
        .finally(() => pending.delete(action))
    },
    close() {
      if (timers.alarm) clearTimeout(timers.alarm)
    },
  }
  return context
}
