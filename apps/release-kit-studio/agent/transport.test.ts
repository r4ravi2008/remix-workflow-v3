// @vitest-environment node
import { mkdtemp, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { afterEach, describe, expect, it } from 'vitest'

import {
  readTransport,
  releaseTransport,
  reserveTransport,
  transportPath,
} from './transport'

const directories: Array<string> = []
afterEach(async () => {
  await Promise.all(
    directories
      .splice(0)
      .map(path => rm(path, { recursive: true, force: true })),
  )
})
const fixture = async () => {
  const root = await mkdtemp(join(tmpdir(), 'release-kit-transport-test-'))
  directories.push(root)
  return transportPath('workstation.ts.net', 'w3:p8', root)
}
const intent = {
  id: 'request-1',
  action: 'ensure',
  attemptId: 'scene-1',
  request: '/private/request-1.json',
  response: '/private/response-1.json',
  remoteResponse: '/runs/service/requests/request-1.response.json',
}

describe('shared Herdr pane ownership', () => {
  it('prevents a second request from entering the pane and releases a terminal response', async () => {
    const path = await fixture()
    const first = await reserveTransport(path, intent)
    await expect(
      reserveTransport(path, { ...intent, id: 'request-2' }),
    ).rejects.toThrow('active or uncertain')
    await first.dispatched()
    first.terminal()
    await first.close()
    const second = await reserveTransport(path, { ...intent, id: 'request-2' })
    await second.close()
  })

  it('keeps an uncertain dispatch reserved until its exact request is reconciled', async () => {
    const path = await fixture()
    const lease = await reserveTransport(path, intent)
    await lease.dispatched()
    await lease.close()
    const saved = await readTransport(path)
    expect(saved.status).toBe('uncertain')
    expect(saved.id).toBe(intent.id)
    await expect(releaseTransport(path, 'another-request')).rejects.toThrow(
      'another request',
    )
    await expect(reserveTransport(path, intent)).rejects.toThrow('Reconcile')
    await releaseTransport(path, intent.id)
  })
})
