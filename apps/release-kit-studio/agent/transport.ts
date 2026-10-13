import { Schema } from 'effect'
import { createHash } from 'node:crypto'
import {
  mkdir,
  readFile,
  readdir,
  rename,
  rmdir,
  unlink,
  writeFile,
} from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { dirname, join } from 'node:path'

export const TransportIntent = Schema.Struct({
  id: Schema.String,
  action: Schema.String,
  attemptId: Schema.NullOr(Schema.String),
  request: Schema.String,
  response: Schema.String,
  remoteResponse: Schema.String,
})
export const TransportRecord = Schema.Struct({
  ...TransportIntent.fields,
  status: Schema.Literals(['reserved', 'dispatched', 'uncertain']),
  pid: Schema.Number,
})

export const transportPath = (
  hostname: string,
  pane: string,
  root = join(
    tmpdir(),
    `release-kit-transport-${process.getuid?.() ?? 'user'}`,
  ),
) =>
  join(
    root,
    `${createHash('sha256')
      .update(JSON.stringify([hostname, pane]))
      .digest('hex')}.lock`,
  )

const recordPath = (path: string, id: string) => {
  if (!/^[a-zA-Z0-9-]+$/.test(id))
    throw new Error('Invalid transport request ID.')
  return join(path, `${id}.json`)
}

export const readTransport = async (path: string) => {
  const files = (await readdir(path)).filter(name => name.endsWith('.json'))
  if (files.length !== 1 || !files[0])
    throw new Error(
      'The transport record is missing or ambiguous; preserve its reservation.',
    )
  return Schema.decodeUnknownSync(TransportRecord)(
    JSON.parse(await readFile(join(path, files[0]), 'utf8')),
  )
}

export const releaseTransport = async (path: string, id: string) => {
  const value = await readFile(recordPath(path, id), 'utf8').catch(error => {
    if (error.code === 'ENOENT') return null
    throw error
  })
  if (!value) {
    const remaining = await readdir(path).catch(error => {
      if (error.code === 'ENOENT') return []
      throw error
    })
    if (remaining.length)
      throw new Error(
        'The GPU transport reservation belongs to another request.',
      )
    return
  }
  const owner = Schema.decodeUnknownSync(TransportRecord)(JSON.parse(value))
  if (owner.id !== id)
    throw new Error('The GPU transport reservation belongs to another request.')
  const removed = await unlink(recordPath(path, id))
    .then(() => true)
    .catch(error => {
      if (error.code === 'ENOENT') return false
      throw error
    })
  if (removed) await rmdir(path)
}

export const reserveTransport = async (
  path: string,
  intent: typeof TransportIntent.Type,
) => {
  await mkdir(dirname(path), { recursive: true, mode: 0o700 })
  const state = { dispatched: false, terminal: false }
  const record = (status: (typeof TransportRecord.Type)['status']) => ({
    ...intent,
    status,
    pid: process.pid,
  })
  await mkdir(path, { mode: 0o700 }).catch(error => {
    if (error.code === 'EEXIST')
      throw new Error(
        'The GPU transport has an active or uncertain request. Reconcile its saved response before running another command.',
      )
    throw error
  })
  await writeFile(
    recordPath(path, intent.id),
    JSON.stringify(record('reserved')),
    { mode: 0o600, flag: 'wx' },
  )
  const update = async (status: (typeof TransportRecord.Type)['status']) => {
    const owner = await readTransport(path)
    if (owner.id !== intent.id)
      throw new Error('GPU transport ownership changed.')
    const temporary = join(path, `${intent.id}.tmp`)
    await writeFile(temporary, JSON.stringify(record(status)), { mode: 0o600 })
    await rename(temporary, recordPath(path, intent.id))
  }
  return {
    dispatched: async () => {
      state.dispatched = true
      await update('dispatched')
    },
    terminal: () => {
      state.terminal = true
    },
    close: async () => {
      if (!state.dispatched || state.terminal)
        await releaseTransport(path, intent.id)
      else await update('uncertain')
    },
  }
}
