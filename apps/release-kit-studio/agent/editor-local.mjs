import { serve } from 'bun'
import { Database } from 'bun:sqlite'
import { Clock, Effect } from 'effect'
import { execFile } from 'node:child_process'
import { createHash, randomBytes, randomUUID } from 'node:crypto'
import {
  chmod,
  mkdir,
  open,
  readFile,
  readdir,
  rename,
  rm,
  writeFile,
} from 'node:fs/promises'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { promisify } from 'node:util'

import { makeEditorApi } from '../editor/api.ts'
import {
  LocalMedia,
  NativeProcess,
  localArchiveHash,
  localContext,
  localFixedStream,
} from '../editor/local/adapters.ts'
import { RenderCoordinator } from '../editor/render-coordinator.ts'
import { EditorStore, digest } from '../editor/store.ts'
import { canonicalJson } from '../src/canonical.ts'
import { defaultProfile } from '../src/domain.ts'
import { runEditorCli } from './editor-cli.ts'

const app = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const state = resolve(
  process.env.EDITOR_LOCAL_STATE ?? join(app, '.local/editor-local'),
)
const connectionPath = join(state, 'connection.json')
const mode = process.argv[2] ?? 'serve'
const readJson = async path => JSON.parse(await readFile(path, 'utf8'))
const save = (path, data, flag = 'w') =>
  writeFile(path, JSON.stringify(data, null, 2) + '\n', { mode: 0o600, flag })
const missing = async (path, data) => {
  try {
    await save(path, data, 'wx')
  } catch (error) {
    if (error.code !== 'EEXIST') throw error
  }
}

async function credentials() {
  const path = join(state, 'credentials.json')
  try {
    const value = await readJson(path)
    await chmod(path, 0o600)
    return value
  } catch (error) {
    if (error.code !== 'ENOENT') throw error
  }
  const value = {
    tenantId: 'local-editor',
    token: randomBytes(32).toString('hex'),
  }
  await missing(path, value)
  return readJson(path)
}
async function setup() {
  await mkdir(state, { recursive: true, mode: 0o700 })
  await chmod(state, 0o700)
  const result = await promisify(execFile)(
    process.env.EDITOR_PYTHON ?? 'python3',
    [join(app, 'editor/local/setup.py'), state],
    { timeout: 180000, maxBuffer: 1024 * 1024 },
  )
  await credentials()
  console.log(result.stdout.trim())
}
async function cli() {
  const connection = await readJson(connectionPath)
  const url = new URL(connection.url)
  if (
    url.protocol !== 'http:' ||
    url.hostname !== '127.0.0.1' ||
    url.pathname !== '/'
  )
    throw new Error(
      'The local wrapper requires the standalone loopback editor. Start bun run editor:local.',
    )
  const result = await runEditorCli(process.argv.slice(3), {
    ...process.env,
    EDITOR_URL: url.origin,
    EDITOR_TOKEN: connection.token,
  })
  console.log(JSON.stringify(result, null, 2))
  if (result?.valid === false) process.exitCode = 2
}
async function localHttpResponse(request, response) {
  const length = Number(response.headers.get('Content-Length'))
  if (!response.body || !response.headers.has('Content-Length')) return response
  if (!Number.isSafeInteger(length) || length < 1)
    throw new Error('Invalid local response byte count.')
  // Bun drops Content-Length for arbitrary streams. File blobs preserve the exact
  // shared CLI contract while bounded writes keep large media off the JS heap.
  const directory = join(state, 'http')
  await mkdir(directory, { recursive: true, mode: 0o700 })
  const key = createHash('sha256')
    .update(request.url + JSON.stringify([...response.headers]))
    .digest('hex')
  const destination = join(directory, key)
  const temporary = destination + '.' + randomUUID() + '.tmp'
  try {
    const file = await open(temporary, 'wx', 0o600)
    const reader = response.body.getReader()
    let written = 0
    try {
      for (;;) {
        const chunk = await reader.read()
        if (chunk.done) break
        written += chunk.value.byteLength
        if (written > length)
          throw new Error('Local HTTP output exceeds its registered size.')
        await file.writeFile(chunk.value)
      }
      if (written !== length)
        throw new Error('Local HTTP output differs from its registered size.')
      await file.sync()
    } finally {
      await reader.cancel().catch(() => {})
      reader.releaseLock()
      await file.close()
    }
    await rename(temporary, destination)
    return new Response(Bun.file(destination), {
      status: response.status,
      headers: response.headers,
    })
  } finally {
    await rm(temporary, { force: true })
  }
}
async function start() {
  await readFile(join(state, 'setup-receipt.json'))
  const identity = await credentials()
  const lockPath = join(state, 'runtime.lock')
  try {
    const lock = await readJson(lockPath)
    try {
      process.kill(lock.pid, 0)
      throw new Error(
        `This local editor state is already owned by process ${lock.pid}.`,
      )
    } catch (error) {
      if (error.code !== 'ESRCH') throw error
    }
    await rm(lockPath)
  } catch (error) {
    if (error.code !== 'ENOENT') throw error
  }
  const lock = await open(lockPath, 'wx', 0o600)
  await lock.writeFile(JSON.stringify({ pid: process.pid }))
  await lock.close()
  const database = new Database(join(state, 'editor.sqlite'), { create: true })
  database.exec(
    'PRAGMA journal_mode=WAL; PRAGMA foreign_keys=ON; CREATE TABLE IF NOT EXISTS local_migrations(name TEXT PRIMARY KEY); CREATE TABLE IF NOT EXISTS local_renderer_state(name TEXT NOT NULL,key TEXT NOT NULL,value TEXT NOT NULL,PRIMARY KEY(name,key));',
  )
  for (const name of (await readdir(join(app, 'migrations')))
    .filter(name => /^\d+.*\.sql$/.test(name))
    .sort()) {
    if (
      !database
        .query('SELECT name FROM local_migrations WHERE name=?')
        .get(name)
    ) {
      const source = await readFile(join(app, 'migrations', name), 'utf8')
      database.transaction(() => {
        database.exec(source)
        database.query('INSERT INTO local_migrations(name) VALUES(?)').run(name)
      })()
    }
  }
  const db = {
    first: async (sql, values) => database.query(sql).get(...values) ?? null,
    all: async (sql, values) => database.query(sql).all(...values),
    run: async (sql, values) => {
      database.query(sql).run(...values)
    },
    batch: async statements => {
      database.transaction(() => {
        for (const item of statements)
          database.query(item.sql).run(...item.values)
      })()
    },
  }
  const store = new EditorStore(db)
  const media = new LocalMedia(join(state, 'objects'))
  const renderers = new Map()
  const env = {
    MEDIA: media,
    STUDIO_OPERATOR_TOKEN: '',
    runtimeInfo: { hosting: 'local-bun', rendering: 'local-python-ffmpeg' },
    fixedLengthStream: localFixedStream,
    archiveHashFactory: localArchiveHash,
    RENDERER: {
      getByName(name) {
        if (!renderers.has(name)) {
          const native = new NativeProcess(
            state,
            join(app, 'editor/engine'),
            join(state, 'fonts.conf'),
          )
          const context = localContext(name, db, native)
          const coordinator = new RenderCoordinator(context, env, store)
          context.onAlarm = () => coordinator.alarm()
          renderers.set(name, { coordinator, context, native })
        }
        return renderers.get(name).coordinator
      },
    },
  }
  const api = makeEditorApi(env, store)
  const time = Math.floor(
    (await Effect.runPromise(Clock.currentTimeMillis)) / 1000,
  )
  await db.run(
    'INSERT OR IGNORE INTO tenants(id,name,created_at) VALUES(?,?,?)',
    [identity.tenantId, 'Local editor testing', time],
  )
  await db.run(
    'INSERT INTO editor_tokens(hash,tenant_id,expires_at) VALUES(?,?,?) ON CONFLICT(hash) DO UPDATE SET expires_at=excluded.expires_at',
    [await digest(identity.token), identity.tenantId, time + 30 * 86400],
  )
  const port = Number(process.env.EDITOR_LOCAL_PORT ?? 1340)
  if (!Number.isInteger(port) || port < 0 || port > 65535)
    throw new Error('EDITOR_LOCAL_PORT must be 0–65535.')
  const server = serve({
    hostname: '127.0.0.1',
    port,
    idleTimeout: 0,
    maxRequestBodySize: 104857600,
    async fetch(request) {
      if (new URL(request.url).pathname === '/')
        return new Response(
          'Standalone local editor\nBun + SQLite + local files + Python/FFmpeg\n\nCLI: bun run editor:local:cli help\nHealth: /v1/health\nGuide: agent/LOCAL_CLI.md\n',
          { headers: { 'Content-Type': 'text/plain; charset=utf-8' } },
        )
      return localHttpResponse(request, await api(request))
    },
  })
  const connection = {
    url: server.url.origin,
    token: identity.token,
    tenantId: identity.tenantId,
    runtime: 'standalone-local',
  }
  await save(connectionPath, connection)
  const authenticated = (path, body, method = 'POST', headers = {}) =>
    api(
      new Request(server.url.origin + path, {
        method,
        headers: { Authorization: `Bearer ${identity.token}`, ...headers },
        body:
          typeof body === 'object' && !(body instanceof ReadableStream)
            ? JSON.stringify(body)
            : body,
      }),
    )
  const recipe = await readJson(join(state, 'demo/recipe.json'))
  const brief = {
    title: 'Local editor synthetic demo',
    lyrics: recipe.lyrics,
    language: recipe.language,
    audioName: 'master.wav',
    audioSha256: recipe.audioSha256,
    audioDuration: 2,
    audioBytes: recipe.assets.find(asset => asset.kind === 'audio').bytes,
    profile: defaultProfile,
  }
  await db.run(
    'INSERT OR IGNORE INTO releases(id,tenant_id,request_key,brief_json,created_at) VALUES(?,?,?,?,?)',
    [
      recipe.releaseId,
      identity.tenantId,
      'local-demo',
      JSON.stringify(brief),
      time,
    ],
  )
  const project = { ...recipe, briefSha256: await digest(canonicalJson(brief)) }
  const files = {
    'demo-master': 'master.wav',
    'demo-scene': 'scene.mp4',
    'demo-mask': 'mask.png',
  }
  for (const asset of project.assets) {
    const existing = await store.asset(identity.tenantId, asset.id)
    if (!existing?.uploaded) {
      const registered = await authenticated('/v1/tools/media.register', asset)
      if (!registered.ok)
        throw new Error(
          'Local demo media registration failed: ' + (await registered.text()),
        )
      const uploaded = await authenticated(
        `/v1/media/${asset.id}`,
        Bun.file(join(state, 'demo', files[asset.id])).stream(),
        'PUT',
        { 'Content-Length': String(asset.bytes) },
      )
      if (!uploaded.ok)
        throw new Error(
          'Local demo media upload failed: ' + (await uploaded.text()),
        )
    }
  }
  const exists = await db.first(
    'SELECT id FROM editor_projects WHERE tenant_id=? AND id=?',
    [identity.tenantId, 'local-demo'],
  )
  if (!exists) {
    const committed = await authenticated('/v1/tools/project.commit', {
      projectId: 'local-demo',
      expectedRevision: 0,
      intentId: 'local-demo-initial',
      project,
    })
    if (!committed.ok)
      throw new Error(
        'Local demo project could not be saved: ' + (await committed.text()),
      )
  }
  const demo = join(state, 'demo')
  await missing(join(demo, 'project.json'), project)
  await missing(join(demo, 'inspect.json'), {
    projectId: 'local-demo',
    revision: null,
  })
  await missing(join(demo, 'render.json'), {
    projectId: 'local-demo',
    revision: 1,
    intentId: 'local-demo-kit-v1',
    mode: 'kit',
    outputId: null,
  })
  const edits = [
    {
      tool: 'transform.set',
      outputId: 'film',
      clipId: 'scene-1',
      transform: { centerX: 0.4, centerY: 0.5, zoom: 1.1 },
    },
  ]
  await missing(join(demo, 'edits.json'), edits)
  await missing(join(demo, 'apply-edits.json'), {
    projectId: 'local-demo',
    expectedRevision: 1,
    intentId: 'local-demo-edit-v2',
    edits,
  })
  for (const row of await db.all(
    "SELECT name,value FROM local_renderer_state WHERE key='alarm'",
    [],
  )) {
    env.RENDERER.getByName(row.name)
    await renderers
      .get(row.name)
      .context.storage.setAlarm(
        Math.max(
          (await Effect.runPromise(Clock.currentTimeMillis)) + 250,
          JSON.parse(row.value),
        ),
      )
  }
  let stopping = false
  const stop = async () => {
    if (stopping) return
    stopping = true
    server.stop(true)
    for (const row of await db.all(
      "SELECT * FROM editor_jobs WHERE state IN ('queued','staging','running','verifying','cancel-requested','uncertain')",
      [],
    )) {
      await env.RENDERER.getByName(`${row.tenant_id}/${row.release_id}`).fetch(
        new Request('http://local-renderer/cancel', {
          method: 'POST',
          body: JSON.stringify({ jobId: row.id, tenant: row.tenant_id }),
        }),
      )
    }
    for (const renderer of renderers.values()) {
      renderer.context.close()
      await renderer.native.destroy()
    }
    database.close()
    await rm(lockPath, { force: true })
    process.exit(0)
  }
  process.once('SIGTERM', () => {
    void stop()
  })
  process.once('SIGINT', () => {
    void stop()
  })
  console.log(
    JSON.stringify({
      ready: true,
      url: server.url.origin,
      hosting: 'local-bun',
      rendering: 'local-python-ffmpeg',
      state,
      demoProject: 'local-demo',
      credentialsPrinted: false,
      cloudflareRequired: false,
      dockerRequired: false,
      gpuRequired: false,
    }),
  )
}

try {
  if (mode === 'setup') await setup()
  else if (mode === 'cli') await cli()
  else if (mode === 'serve') await start()
  else
    throw new Error(
      'Usage: bun agent/editor-local.mjs [setup|serve|cli <editor command...>]',
    )
} catch (error) {
  console.error(
    JSON.stringify({
      ok: false,
      error: error.message,
      hint: 'Run bun run editor:local:setup, then bun run editor:local in a separate terminal.',
    }),
  )
  process.exit(1)
}
