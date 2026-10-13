// @vitest-environment node
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises'
import { type Server, createServer } from 'node:http'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { afterEach, describe, expect, it } from 'vitest'

import { defaultProfile } from '../src/domain'
import { command } from './gpu'
import { briefFingerprint } from './plan'
import { runWorker } from './production'
import { fileReceipt } from './transfer'

const directories: Array<string> = []
const servers: Array<Server> = []
afterEach(async () => {
  await Promise.all(
    servers.splice(0).map(
      server =>
        new Promise<void>((resolve, reject) => {
          server.closeAllConnections()
          server.close(error => (error ? reject(error) : resolve()))
        }),
    ),
  )
  await Promise.all(
    directories
      .splice(0)
      .map(path => rm(path, { recursive: true, force: true })),
  )
})

describe('claimed job direction handoff', () => {
  it('downloads canonical bytes, prepares the director input, reports a fenced hold and performs no generation', async () => {
    const root = await mkdtemp(join(tmpdir(), 'release-kit-production-'))
    directories.push(root)
    const source = join(root, 'source.wav')
    await command('ffmpeg', [
      '-v',
      'error',
      '-f',
      'lavfi',
      '-i',
      'anullsrc=r=48000:cl=stereo',
      '-t',
      '2',
      source,
    ])
    const audio = await readFile(source)
    const measured = await fileReceipt(source)
    const brief = {
      title: 'పల్ పల్',
      lyrics: 'ప్రతి నిమిషం',
      language: 'Telugu',
      audioName: 'song.wav',
      audioSha256: measured.sha256,
      audioBytes: measured.bytes,
      audioDuration: 2,
      profile: defaultProfile,
    }
    const job = {
      id: 'job-one',
      releaseId: 'release-one',
      attempt: 1,
      lease: 'c'.repeat(64),
      expiresAt: Date.now() + 180000,
      brief,
      audioAssetId: 'asset-one',
      contract: 'release-kit-v1',
    }
    const records: Array<{
      path: string
      body: unknown
      lease: string | string[] | undefined
    }> = []
    const server = createServer((request, response) => {
      if (request.headers.authorization !== `Bearer ${'b'.repeat(64)}`) {
        response.writeHead(401).end('{}')
        return
      }
      if (
        request.method === 'GET' &&
        request.url === '/api/worker/assets/asset-one' &&
        request.headers['x-job-lease'] === job.lease
      ) {
        response.writeHead(200, { 'Content-Type': 'audio/wav' }).end(audio)
        return
      }
      const chunks: Array<Buffer> = []
      request.on('data', chunk => chunks.push(chunk))
      request.on('end', () => {
        records.push({
          path: request.url ?? '',
          body: JSON.parse(Buffer.concat(chunks).toString('utf8')),
          lease: request.headers['x-job-lease'],
        })
        response.setHeader('Content-Type', 'application/json')
        if (request.url === '/api/worker/claim')
          response.end(JSON.stringify({ job }))
        else if (
          request.headers['x-job-lease'] === job.lease &&
          [
            '/api/worker/jobs/job-one/heartbeat',
            '/api/worker/jobs/job-one/hold',
          ].includes(request.url ?? '')
        )
          response.end('{}')
        else
          response
            .writeHead(409)
            .end(JSON.stringify({ error: 'Unexpected production request' }))
      })
    })
    servers.push(server)
    await new Promise<void>(resolve => server.listen(0, '127.0.0.1', resolve))
    const address = server.address()
    if (!address || typeof address === 'string')
      throw new Error('Test server did not bind')
    const workstationConfig = join(root, 'workstation.json')
    await writeFile(
      workstationConfig,
      JSON.stringify({
        machine: 'unused',
        pane: 'unused',
        sshAlias: 'unused',
        expectedTailscaleHost: 'unused',
        remoteRoot: 'unused',
        localState: 'unused',
      }),
    )
    const config = {
      baseUrl: `http://127.0.0.1:${address.port}`,
      token: 'b'.repeat(64),
      workstationConfig,
      localState: join(root, 'worker'),
      planRegistry: join(root, 'plans'),
    }
    const result = await runWorker(config)
    expect(result.state).toBe('waiting-for-direction')
    expect(
      await fileReceipt(join(config.localState, job.id, 'canonical-audio')),
    ).toEqual(measured)
    expect(records.at(-1)).toEqual({
      path: '/api/worker/jobs/job-one/hold',
      lease: job.lease,
      body: { reason: 'waiting-for-direction', receipt: result },
    })
    expect(JSON.stringify(records)).not.toContain(root)
    const packet = JSON.parse(
      await readFile(
        join(
          config.localState,
          job.id,
          `direction-v2-${briefFingerprint(brief)}`,
          'direction-input.json',
        ),
        'utf8',
      ),
    )
    expect(packet.brief).toEqual(brief)
    expect(packet.review.approvedForBulk).toBe(false)
    expect(
      records
        .filter(record => !record.path.endsWith('/claim'))
        .every(record => record.lease === job.lease),
    ).toBe(true)
    expect(records.some(record => /uploads|complete/u.test(record.path))).toBe(
      false,
    )
  })
})
