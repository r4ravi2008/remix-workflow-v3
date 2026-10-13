import { mkdir, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises'
// @vitest-environment node
import { type Server, createServer } from 'node:http'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { afterEach, describe, expect, it } from 'vitest'

import { defaultProfile, outputs } from '../src/domain'
import { command } from './gpu'
import { briefFingerprint } from './plan'
import { superviseCycle } from './supervisor'
import { fileReceipt } from './transfer'

const servers: Array<Server> = []
const directories: Array<string> = []
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
const brief = {
  title: 'పల్ పల్',
  lyrics: 'ప్రతి నిమిషం',
  language: 'Telugu',
  audioName: 'song.wav',
  audioSha256: 'a'.repeat(64),
  audioDuration: 239.68,
  audioBytes: 46018732,
  profile: defaultProfile,
}
const job = {
  id: 'job-one',
  releaseId: 'release-one',
  state: 'waiting-for-direction',
  attempt: 1,
  brief,
}
const plan = {
  schemaVersion: 2,
  releaseId: job.releaseId,
  briefSha256: briefFingerprint(brief),
  audioSha256: brief.audioSha256,
  approvedForBulk: false,
  reviewEvidence: '',
  shots: [],
  editor: {
    projectId: 'project-one',
    expectedRevision: 0,
    projectPath: '/private/project.json',
    assets: [],
  },
}
const fixture = async () => {
  const directory = await mkdtemp(join(tmpdir(), 'release-kit-supervisor-'))
  directories.push(directory)
  const state = {
    holds: [job],
    calls: new Array<string>(),
    resumeBodies: new Array<unknown>(),
    current: {
      state: 'running',
      attempt: 1,
      assets: new Array<{ outputId: string; verified: boolean }>(),
    },
    produced: 0,
  }
  const server = createServer((request, response) => {
    state.calls.push(`${request.method} ${request.url}`)
    response.setHeader('Content-Type', 'application/json')
    if (request.headers.authorization !== `Bearer ${'b'.repeat(64)}`) {
      response
        .writeHead(401)
        .end(JSON.stringify({ error: 'Worker authentication is required.' }))
      return
    }
    if (request.method === 'GET' && request.url === '/api/worker/holds')
      response.end(JSON.stringify({ jobs: state.holds }))
    else if (request.method === 'GET')
      response.end(JSON.stringify(state.current))
    else {
      const chunks: Array<Buffer> = []
      request.on('data', chunk => chunks.push(chunk))
      request.on('end', () => {
        state.resumeBodies.push(
          JSON.parse(Buffer.concat(chunks).toString('utf8')),
        )
        response.end(JSON.stringify({ state: 'queued' }))
      })
    }
  })
  servers.push(server)
  await new Promise<void>(resolve => server.listen(0, '127.0.0.1', resolve))
  const address = server.address()
  if (!address || typeof address === 'string')
    throw new Error('Test server failed to bind')
  const config = {
    baseUrl: `http://127.0.0.1:${address.port}`,
    token: 'b'.repeat(64),
    workstationConfig: '/private/workstation.json',
    localState: directory,
    planRegistry: directory,
  }
  const produce = async () => {
    state.produced += 1
    return { state: 'idle' }
  }
  return {
    directory,
    state,
    config,
    produce,
    signal: new AbortController().signal,
  }
}

describe('outbound worker supervision', () => {
  it('does not resume a reviewed generated plan when its recipe is missing or incomplete', async () => {
    const test = await fixture()
    const recipePath = join(test.directory, 'recipe.json')
    await writeFile(
      join(test.directory, `${job.releaseId}.json`),
      JSON.stringify({
        ...plan,
        schemaVersion: 3,
        approvedForBulk: true,
        reviewEvidence: 'test-only review',
        editor: { projectId: 'project-one', expectedRevision: 0, recipePath },
      }),
    )
    const missing = await superviseCycle(test.config, test.signal, test.produce)
    expect(missing.held[0]?.state).toBe('plan-needs-correction')
    await writeFile(recipePath, JSON.stringify({ schemaVersion: 1 }))
    const incomplete = await superviseCycle(
      test.config,
      test.signal,
      test.produce,
    )
    expect(incomplete.held[0]?.state).toBe('plan-needs-correction')
    expect(test.state.resumeBodies).toEqual([])
    expect(test.state.produced).toBe(2)
  })
  it('holds legacy Resolve plans even when reviewed', async () => {
    const test = await fixture()
    const { editor, ...fields } = plan
    expect(editor.projectId).toBe('project-one')
    await writeFile(
      join(test.directory, `${job.releaseId}.json`),
      JSON.stringify({
        ...fields,
        schemaVersion: 1,
        approvedForBulk: true,
        reviewEvidence: 'test-only review',
        resolvePlan: '/private/resolve.json',
      }),
    )
    const result = await superviseCycle(test.config, test.signal, test.produce)
    expect(result.held[0]?.state).toBe('plan-needs-correction')
    expect(test.state.resumeBodies).toEqual([])
  })
  it('prepares a held release automatically across polls without resuming it or changing its attempt', async () => {
    const test = await fixture()
    const root = join(test.directory, job.id)
    await mkdir(root)
    const source = join(root, 'canonical-audio')
    await command('ffmpeg', [
      '-v',
      'error',
      '-f',
      'lavfi',
      '-i',
      'anullsrc=r=48000:cl=stereo',
      '-t',
      '2',
      '-f',
      'wav',
      source,
    ])
    const receipt = await fileReceipt(source)
    test.state.holds = [
      {
        ...job,
        brief: {
          ...brief,
          audioBytes: receipt.bytes,
          audioSha256: receipt.sha256,
          audioDuration: 2,
        },
      },
    ]
    const first = await superviseCycle(test.config, test.signal, test.produce)
    const second = await superviseCycle(test.config, test.signal, test.produce)
    expect(second.held).toEqual(first.held)
    expect(first.held[0]?.direction?.state).toBe('direction-prepared')
    expect(first.resumed).toBe(0)
    expect(test.state.resumeBodies).toEqual([])
    expect(test.state.holds[0]?.attempt).toBe(1)
    expect(test.state.produced).toBe(2)
  })

  it('keeps unreviewed and mismatched plans held while checking for other queued work', async () => {
    const test = await fixture()
    const path = join(test.directory, `${job.releaseId}.json`)
    await writeFile(path, JSON.stringify(plan))
    const unreviewed = await superviseCycle(
      test.config,
      test.signal,
      test.produce,
    )
    expect(unreviewed.resumed).toBe(0)
    expect(unreviewed.held[0]?.state).toBe('waiting-for-review')
    await writeFile(
      path,
      JSON.stringify({
        ...plan,
        approvedForBulk: true,
        reviewEvidence: 'test-only review',
        briefSha256: 'c'.repeat(64),
      }),
    )
    const mismatched = await superviseCycle(
      test.config,
      test.signal,
      test.produce,
    )
    expect(mismatched.held[0]?.state).toBe('plan-needs-correction')
    expect(test.state.resumeBodies).toEqual([])
    expect(test.state.produced).toBe(2)
  })

  it('resumes a reviewed release using its complete fingerprint before dispatch', async () => {
    const test = await fixture()
    await writeFile(
      join(test.directory, `${job.releaseId}.json`),
      JSON.stringify({
        ...plan,
        approvedForBulk: true,
        reviewEvidence: 'test-only review',
      }),
    )
    const result = await superviseCycle(test.config, test.signal, test.produce)
    expect(result.resumed).toBe(1)
    expect(test.state.resumeBodies).toEqual([
      {
        briefSha256: plan.briefSha256,
        audioSha256: plan.audioSha256,
        reviewEvidence: 'test-only review',
      },
    ])
    expect(test.state.calls).toEqual([
      'GET /api/worker/holds',
      'POST /api/worker/jobs/job-one/resume',
    ])
    expect(test.state.produced).toBe(1)
  })

  it('never automatically resumes uncertain work even when a reviewed plan exists', async () => {
    const test = await fixture()
    test.state.holds = [{ ...job, state: 'needs-reconciliation' }]
    await writeFile(
      join(test.directory, `${job.releaseId}.json`),
      JSON.stringify({
        ...plan,
        approvedForBulk: true,
        reviewEvidence: 'test-only review',
      }),
    )
    const result = await superviseCycle(test.config, test.signal, test.produce)
    expect(result.held[0]?.state).toBe('needs-reconciliation')
    expect(test.state.resumeBodies).toEqual([])
  })

  it('keeps interrupted dispatch fenced until the exact attempt has six verified review assets', async () => {
    const test = await fixture()
    const attention = join(test.directory, 'worker-attention.json')
    await writeFile(
      attention,
      JSON.stringify({ jobId: job.id, attempt: job.attempt }),
    )
    test.state.current = {
      state: 'review',
      attempt: 1,
      assets: outputs
        .slice(0, 5)
        .map(output => ({ outputId: output.id, verified: true })),
    }
    expect(
      (await superviseCycle(test.config, test.signal, test.produce)).state,
    ).toBe('needs-reconciliation')
    expect(test.state.produced).toBe(0)
    test.state.current.assets = outputs.map(output => ({
      outputId: output.id,
      verified: true,
    }))
    test.state.holds = []
    expect(
      (await superviseCycle(test.config, test.signal, test.produce)).state,
    ).toBe('idle')
    await expect(readFile(attention, 'utf8')).rejects.toThrow('ENOENT')
    expect(test.state.produced).toBe(1)
  })
})
