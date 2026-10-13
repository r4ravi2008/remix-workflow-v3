import assert from 'node:assert/strict'
import { serve, sleep, version } from 'bun'
import { Clock, Effect } from 'effect'

import { editorFetch, editorRequest } from './editor-request.ts'

const requests = []
const server = serve({
  hostname: '127.0.0.1',
  port: 0,
  idleTimeout: 0,
  async fetch(request) {
    requests.push({ path: new URL(request.url).pathname, lease: request.headers.get('X-Job-Lease') })
    await sleep(200)
    return Response.json({ verified: true })
  },
})
const config = { baseUrl: server.url.toString(), token: 'synthetic-client', workstationConfig: '/unused', localState: '/unused', planRegistry: '/unused' }
const job = { id: 'synthetic-job', lease: 'synthetic-lease' }
try {
  assert.deepEqual(await editorRequest(config, job, '/assigned', 'tools/artifact.preview',
    { jobId: 'synthetic-editor-job' }, new AbortController().signal), { verified: true })
  assert.equal(requests[0].lease, job.lease)
  assert.equal(requests[0].path, '/assigned/tools/artifact.preview')
  const before = await Effect.runPromise(Clock.currentTimeMillis)
  await assert.rejects(editorFetch(server.url, { signal: AbortSignal.timeout(50) }), { name: 'TimeoutError' })
  assert.ok((await Effect.runPromise(Clock.currentTimeMillis)) - before < 2000)
  const controller = new AbortController()
  const lost = new Error('synthetic-lease-lost')
  const operation = editorRequest(config, job, '/assigned', 'tools/artifact.preview', {}, controller.signal)
  const timer = setTimeout(() => controller.abort(lost), 50)
  try { await assert.rejects(operation, { message: lost.message }) }
  finally { clearTimeout(timer) }
  console.log(JSON.stringify({ scope: 'real Bun local HTTP deadline and lease-cancellation checks only', runtime: version,
    checks: ['actual-editor-client-preserves-path-and-owning-lease', 'explicit-deadline-still-cancels-with-idle-timer-disabled',
      'owning-lease-cancellation-still-aborts-actual-request'], passed: true, requests: requests.length, cloudVerified: false }))
} finally { server.stop(true) }
