import { Database } from 'bun:sqlite'
import { Clock, Effect } from 'effect'
import assert from 'node:assert/strict'
import { execFile, spawn } from 'node:child_process'
import { createHash, randomUUID } from 'node:crypto'
import { cp, mkdir, readFile, readdir, writeFile } from 'node:fs/promises'
import { dirname, join, resolve } from 'node:path'
import { createInterface } from 'node:readline'
import { fileURLToPath } from 'node:url'
import { promisify } from 'node:util'

const app = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const state = join(app, '.local', 'editor-local-check-' + randomUUID())
const command = join(app, 'agent/editor-local.mjs')
const env = {
  ...process.env,
  EDITOR_LOCAL_STATE: state,
  EDITOR_LOCAL_PORT: '0',
}
const execute = promisify(execFile)

const save = async (name, value) => {
  const path = join(state, name)
  await writeFile(path, JSON.stringify(value, null, 2))
  return path
}
const cli = async (...args) =>
  JSON.parse(
    (
      await execute(process.execPath, [command, 'cli', ...args], {
        cwd: app,
        env,
        timeout: 180000,
        maxBuffer: 8 * 1024 * 1024,
      })
    ).stdout,
  )
const checks = []
const live = { server: undefined }
async function launch() {
  live.server = spawn(process.execPath, [command, 'serve'], {
    cwd: app,
    env,
    stdio: ['ignore', 'pipe', 'pipe'],
  })
  let errors = ''
  live.server.stderr.on('data', chunk => {
    errors = (errors + chunk).slice(-4000)
  })
  return new Promise((done, fail) => {
    const lines = createInterface({ input: live.server.stdout })
    const timer = setTimeout(
      () => fail(new Error('Local editor startup timed out: ' + errors)),
      30000,
    )
    live.server.once('exit', () => {
      clearTimeout(timer)
      fail(new Error('Local editor exited: ' + errors))
    })
    lines.on('line', line => {
      try {
        const ready = JSON.parse(line)
        if (ready.ready) {
          clearTimeout(timer)
          lines.close()
          done(ready)
        }
      } catch {}
    })
  })
}
async function stop() {
  if (
    !live.server ||
    live.server.exitCode !== null ||
    live.server.signalCode !== null
  )
    return
  const target = live.server
  await new Promise((done, fail) => {
    const timer = setTimeout(() => {
      target.kill('SIGKILL')
      fail(new Error('Graceful local editor shutdown timed out.'))
    }, 15000)
    target.once('exit', code => {
      clearTimeout(timer)
      code === 0
        ? done()
        : fail(new Error('Local editor did not shut down cleanly.'))
    })
    target.kill('SIGTERM')
  })
}
try {
  await mkdir(state, { recursive: true, mode: 0o700 })
  await cp(join(app, '.local/editor-local/fonts'), join(state, 'fonts'), {
    recursive: true,
  })
  await execute(process.execPath, [command, 'setup'], {
    cwd: app,
    env,
    timeout: 180000,
  })
  const ready = await launch()
  assert.equal(ready.dockerRequired, false)
  assert.equal(ready.cloudflareRequired, false)
  const health = await cli('health')
  assert.equal(health.hosting, 'local-bun')
  assert.equal(health.rendering, 'local-python-ffmpeg')
  checks.push('real standalone loopback HTTP service; no Workerd or Docker')
  const project = await cli(
    'call',
    'project.inspect',
    join(state, 'demo/inspect.json'),
  )
  assert.equal(project.revision, 1)
  const asset = {
    ...project.project.assets.find(asset => asset.kind === 'video'),
    id: 'extra-upload',
  }
  await save('extra-asset.json', asset)
  assert.equal(
    (
      await cli(
        'upload',
        join(state, 'extra-asset.json'),
        join(state, 'demo/scene.mp4'),
      )
    ).uploaded,
    true,
  )
  assert.equal(
    (
      await cli(
        'upload',
        join(state, 'extra-asset.json'),
        join(state, 'demo/scene.mp4'),
      )
    ).resumedExistingUpload,
    true,
  )
  const denied = await fetch(ready.url + '/v1/tools/project.inspect', {
    method: 'POST',
    body: JSON.stringify({ projectId: 'local-demo', revision: null }),
    headers: { Authorization: 'Bearer invalid' },
  })
  assert.equal(denied.status, 401)
  checks.push('real CLI upload, immutable replay and authentication boundary')
  const edited = await cli(
    'call',
    'project.edit',
    join(state, 'demo/apply-edits.json'),
  )
  assert.equal(edited.revision, 2)
  assert.equal(
    (await cli('call', 'project.edit', join(state, 'demo/apply-edits.json')))
      .revision,
    2,
  )
  const snapshot = await cli(
    'call',
    'project.inspect',
    join(state, 'demo/inspect.json'),
  )
  assert.equal(
    snapshot.project.compositions
      .find(comp => comp.id === 'film')
      .clips.find(clip => clip.id === 'scene-1').transform.zoom,
    1.1,
  )
  checks.push('CLI edit, immutable revision and intent replay')
  const renderPath = await save('render.json', {
    projectId: 'local-demo',
    revision: 2,
    intentId: 'local-check-kit',
    mode: 'kit',
    outputId: null,
  })
  const started = await cli('call', 'render.start', renderPath)
  assert.equal(
    (await cli('call', 'render.start', renderPath)).jobId,
    started.jobId,
  )
  const jobPath = await save('job.json', { jobId: started.jobId })
  const deadline = (await Effect.runPromise(Clock.currentTimeMillis)) + 180000
  let status
  do {
    status = await cli('call', 'render.reconcile', jobPath)
    if (['ready', 'failed', 'cancelled', 'uncertain'].includes(status.state))
      break
    assert.ok(
      (await Effect.runPromise(Clock.currentTimeMillis)) < deadline,
      'Native canary render deadline',
    )
    await new Promise(done => setTimeout(done, 500))
  } while (true)
  assert.equal(
    status.state,
    'ready',
    status.error ?? 'Native render did not complete',
  )
  assert.equal(status.receipt.outputs.length, 6)
  assert.equal(status.receipt.storedByteReadback, true)
  assert.equal(status.motionReviewed, false)
  assert.equal(status.heard, false)
  const artifactPath = await save('artifact.json', {
    jobId: started.jobId,
    outputId: 'film',
  })
  const verified = await cli('call', 'artifact.verify', artifactPath)
  assert.equal(verified.completeDecode, true)
  assert.equal(verified.frames, 48)
  assert.equal(verified.frameDiagnostics.sampledFrames, 48)
  const film = status.receipt.outputs.find(output => output.id === 'film')
  assert.equal(verified.sha256, film.sha256)
  checks.push(
    'six native Mac outputs with stored-byte decode, frame and audio verification',
  )
  const previewPath = await save('preview.json', {
    jobId: started.jobId,
    outputId: 'film',
    startFrame: 6,
    frames: 36,
    sampleFrames: [6, 23, 24, 41],
  })
  const preview = await cli('preview', previewPath, join(state, 'review'))
  assert.equal(preview.reused, false)
  assert.equal(
    (await cli('preview', previewPath, join(state, 'review-cached'))).reused,
    true,
  )
  await cli('download', started.jobId, 'film', join(state, 'film.mp4'))
  await execute(
    'ffmpeg',
    [
      '-v',
      'error',
      '-xerror',
      '-i',
      join(state, 'film.mp4'),
      '-f',
      'null',
      '-',
    ],
    { timeout: 30000 },
  )
  const archive = await cli('archive', started.jobId, join(state, 'kit.zip'))
  assert.equal(archive.archiveEntriesVerified, 8)
  checks.push(
    'CLI preview cache, four source frames, film download and independent eight-entry ZIP verification',
  )
  await stop()
  await launch()
  const restored = await cli('call', 'render.status', jobPath)
  assert.equal(restored.receipt.receiptSha256, status.receipt.receiptSha256)
  assert.equal(
    (await cli('call', 'project.inspect', join(state, 'demo/inspect.json')))
      .revision,
    2,
  )
  const scratchCount = (await readdir(join(state, 'scratch'))).length
  assert.equal(
    (await cli('call', 'render.start', renderPath)).jobId,
    started.jobId,
  )
  assert.equal((await readdir(join(state, 'scratch'))).length, scratchCount)
  assert.equal(
    (await cli('call', 'artifact.verify', artifactPath)).sha256,
    film.sha256,
  )
  checks.push(
    'SQLite restart preserves revision and receipts; render replay does not execute twice; fresh verifier restores inputs',
  )
  const cancelPath = await save('cancel-render.json', {
    projectId: 'local-demo',
    revision: 2,
    intentId: 'local-check-cancel',
    mode: 'kit',
    outputId: null,
  })
  const cancellable = await cli('call', 'render.start', cancelPath)
  const cancelled = await cli(
    'call',
    'render.cancel',
    await save('cancel-job.json', { jobId: cancellable.jobId }),
  )
  assert.equal(cancelled.state, 'cancelled')
  const database = new Database(join(state, 'editor.sqlite'), {
    readonly: true,
  })
  assert.equal(
    database.query('SELECT count(*) AS count FROM editor_capacity').get().count,
    0,
  )
  database.close()
  checks.push('owned native cancellation releases local capacity')
  await stop()
  const sourceFiles = [
    'agent/editor-local.mjs',
    'editor/local/adapters.ts',
    'editor/local/setup.py',
    'editor/local/transfer.py',
    'editor/render-coordinator.ts',
    'editor/render-object.ts',
    'editor/api.ts',
    'editor/engine/server.py',
    'editor/engine/engine.py',
    'agent/check-editor-local.mjs',
  ]
  const sources = Object.fromEntries(
    await Promise.all(
      sourceFiles.map(async name => [
        name,
        createHash('sha256')
          .update(await readFile(join(app, name)))
          .digest('hex'),
      ]),
    ),
  )
  const receipt = {
    scope: 'standalone local Mac editor and real CLI integration',
    passed: true,
    checks,
    jobId: started.jobId,
    revision: 2,
    outputs: status.receipt.outputs,
    renderReceiptSha256: status.receipt.receiptSha256,
    state,
    sources,
    cloudVerified: false,
    palPalKitCompleted: false,
    motionReviewed: false,
    heard: false,
    creativelyAccepted: false,
  }
  await save('receipt.json', receipt)
  await writeFile(
    join(app, 'docs/editor/local-standalone-receipt.json'),
    JSON.stringify(receipt, null, 2) + '\n',
  )
  console.log(
    JSON.stringify({
      passed: true,
      checks: checks.length,
      outputs: 6,
      state,
      cloudVerified: false,
    }),
  )
} finally {
  await stop()
}
