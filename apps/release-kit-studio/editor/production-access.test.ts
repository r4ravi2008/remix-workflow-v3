// @vitest-environment node
import { readFileSync } from 'node:fs'
import { DatabaseSync } from 'node:sqlite'
import { afterEach, describe, expect, it } from 'vitest'

import { canonicalJson } from '../src/canonical'
import { defaultProfile, outputs } from '../src/domain'
import type { MediaBucket } from '../src/server/api'
import { type SqlDatabase, Store } from '../src/server/store'
import { makeProductionEditorApi } from './production-access'
import { productionAssetPrefix } from './production-contract'
import { type Project, validateProject } from './project'
import { EditorStore, digest } from './store'
import { projectFixture } from './testing'

const databases: Array<DatabaseSync> = []
afterEach(() => databases.splice(0).forEach(database => database.close()))

const fixture = async () => {
  const database = new DatabaseSync(':memory:')
  databases.push(database)
  for (const name of [
    '0001_studio.sql',
    '0002_artist_profiles.sql',
    '0003_editor.sql',
  ])
    database.exec(
      readFileSync(new URL(`../migrations/${name}`, import.meta.url), 'utf8'),
    )
  const sql: SqlDatabase = {
    first: async (query, values) =>
      database.prepare(query).get(...values) ?? null,
    all: async (query, values) => database.prepare(query).all(...values),
    run: async (query, values) => {
      database.prepare(query).run(...values)
    },
    batch: async statements => {
      database.exec('BEGIN')
      try {
        statements.forEach(statement =>
          database.prepare(statement.sql).run(...statement.values),
        )
        database.exec('COMMIT')
      } catch (error) {
        database.exec('ROLLBACK')
        throw error
      }
    },
  }
  const studio = new Store(sql)
  const editor = new EditorStore(sql)
  const time = Math.floor(Date.now() / 1000)
  const token = 'b'.repeat(64)
  const lease = 'lease-one'
  const brief = {
    title: 'Synthetic test',
    lyrics: 'ప్రతి నిమిషం',
    language: 'Telugu',
    audioName: 'song.wav',
    audioSha256: 'a'.repeat(64),
    audioDuration: 2,
    audioBytes: 100,
    profile: defaultProfile,
  }
  for (const tenant of ['one', 'two'])
    database
      .prepare('INSERT INTO tenants(id,name,created_at) VALUES(?,?,0)')
      .run(tenant, tenant)
  for (const [id, tenant] of [
    ['release-one', 'one'],
    ['release-two', 'one'],
    ['release-three', 'two'],
  ])
    database
      .prepare(
        'INSERT INTO releases(id,tenant_id,request_key,brief_json,state,created_at) VALUES(?,?,?,?,?,0)',
      )
      .run(id ?? '', tenant ?? '', id ?? '', JSON.stringify(brief), 'running')
  database
    .prepare('INSERT INTO devices(id,name,token_hash) VALUES(?,?,?)')
    .run('device-one', 'Test', await digest(token))
  database
    .prepare(
      "INSERT INTO jobs(id,release_id,state,device_id,lease_hash,lease_until,attempt,created_at,updated_at) VALUES(?,?,'running',?,?,?,1,0,0)",
    )
    .run(
      'job-one',
      'release-one',
      'device-one',
      await digest(lease),
      time + 180,
    )
  const base = projectFixture()
  const first = base.compositions[0]
  const clip = first?.clips[0]
  if (!first || !clip) throw new Error('Missing fixture composition')
  const prefix = productionAssetPrefix('release-one')
  const project: Project = {
    ...base,
    briefSha256: await digest(canonicalJson(brief)),
    assets: base.assets.map(asset => ({ ...asset, id: prefix + asset.id })),
    compositions: outputs.map(output => {
      const still = ['thumbnail', 'artwork'].includes(output.id)
      return {
        ...first,
        id: output.id,
        width: output.id.startsWith('short-') ? 1080 : 1920,
        height:
          output.id === 'artwork' || output.id.startsWith('short-')
            ? 1920
            : 1080,
        frames: still ? 1 : 48,
        rationale: `Independent ${output.id} composition`,
        audio: still ? null : { assetId: prefix + 'audio', startSeconds: 0 },
        clips: [{ ...clip, assetId: prefix + 'scene', frames: still ? 1 : 48 }],
        captions: [],
      }
    }),
  }
  expect(validateProject(project, 'kit')).toEqual([])
  await editor.commit('one', 'project-one', 0, 'initial', project)
  await editor.commit('one', 'project-two', 0, 'other-release', {
    ...project,
    releaseId: 'release-two',
  })
  await editor.commit('two', 'project-three', 0, 'other-tenant', {
    ...project,
    releaseId: 'release-three',
  })
  const render = await editor.start('one', 'project-one', 1, 'render-one', {
    mode: 'kit',
    outputId: null,
  })
  const otherRender = await editor.start(
    'one',
    'project-two',
    1,
    'render-two',
    { mode: 'kit', outputId: null },
  )
  const objects = new Map<string, string>()
  const key = (id: string) => `editor/one/jobs/${render.id}/${id}`
  const measured = await Promise.all(
    project.compositions.map(async composition => {
      const bytes = `synthetic-${composition.id}`
      objects.set(key(composition.id), bytes)
      return {
        id: composition.id,
        sha256: await digest(bytes),
        bytes: bytes.length,
        width: composition.width,
        height: composition.height,
        duration: composition.audio ? 2 : 0,
        completeDecode: true,
      }
    }),
  )
  const storedReceipt = JSON.stringify({
    projectSha256: await digest(canonicalJson(project)),
    outputs: measured,
  })
  const receipt = {
    measured: true,
    storedByteReadback: true,
    receiptStored: true,
    receiptSha256: await digest(storedReceipt),
    projectSha256: await digest(canonicalJson(project)),
    outputs: measured,
  }
  objects.set(key('receipt.json'), storedReceipt)
  database
    .prepare("UPDATE editor_jobs SET state='ready',receipt_json=? WHERE id=?")
    .run(JSON.stringify(receipt), render.id)
  const events = { onGet: (_key: string) => {} }
  const media: MediaBucket = {
    head: async objectKey => {
      const content = objects.get(objectKey)
      return content === undefined
        ? null
        : { size: new TextEncoder().encode(content).length }
    },
    get: async objectKey => {
      events.onGet(objectKey)
      const content = objects.get(objectKey)
      if (content === undefined) return null
      const body = new Response(content).body
      if (!body) throw new Error('Missing test stream')
      return {
        body,
        size: new TextEncoder().encode(content).length,
        httpEtag: 'test',
      }
    },
    put: async () => {
      throw new Error('Unexpected output rewrite')
    },
    createMultipartUpload: async () => {
      throw new Error('Unexpected upload')
    },
    resumeMultipartUpload: () => {
      throw new Error('Unexpected upload')
    },
  }
  const api = makeProductionEditorApi(
    { MEDIA: media, STUDIO_OPERATOR_TOKEN: 'o'.repeat(64) },
    studio,
    editor,
  )
  const request = (
    path: string,
    value: unknown,
    overrides: Record<string, string> = {},
  ) =>
    api(
      new Request(`https://editor.example/v1/production/jobs/job-one/${path}`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'X-Job-Lease': lease,
          'Content-Type': 'application/json',
          ...overrides,
        },
        body: JSON.stringify(value),
      }),
    )
  const promote = () => request('promote', { editorJobId: render.id })
  return {
    database,
    studio,
    project,
    render,
    otherRender,
    objects,
    key,
    receipt,
    events,
    request,
    promote,
  }
}

describe('leased Cloudflare production editor', () => {
  it('requires an enrolled device and the exact unexpired job lease', async () => {
    const test = await fixture()
    const input = { projectId: 'project-one', revision: null }
    expect(
      (
        await test.request('tools/project.inspect', input, {
          Authorization: 'Bearer invalid',
        })
      ).status,
    ).toBe(401)
    expect(
      (
        await test.request('tools/project.inspect', input, {
          'X-Job-Lease': '',
        })
      ).status,
    ).toBe(409)
    expect((await test.request('tools/project.inspect', input)).status).toBe(
      200,
    )
    test.database
      .prepare('UPDATE jobs SET lease_until=0 WHERE id=?')
      .run('job-one')
    expect((await test.request('tools/project.inspect', input)).status).toBe(
      409,
    )
  })
  it('rejects another release in the same tenant, another tenant, foreign media and operator routes', async () => {
    const test = await fixture()
    for (const projectId of ['project-two', 'project-three'])
      expect(
        (
          await test.request('tools/project.inspect', {
            projectId,
            revision: null,
          })
        ).status,
      ).toBe(404)
    expect(
      (
        await test.request('tools/render.status', {
          jobId: test.otherRender.id,
        })
      ).status,
    ).toBe(404)
    expect(
      (
        await test.request('tools/media.inspect', {
          assetId: 'p_release-two_scene',
        })
      ).status,
    ).toBe(404)
    expect(
      (
        await test.request('tools/media.register', {
          ...test.project.assets[1],
          id: 'foreign-scene',
        })
      ).status,
    ).toBe(404)
    expect(
      (await test.request('operator/tokens', { tenantId: 'two' })).status,
    ).toBe(404)
    expect(
      (
        await test.request('tools/project.commit', {
          projectId: 'project-two',
          expectedRevision: 1,
          intentId: 'overwrite-other',
          project: test.project,
        })
      ).status,
    ).toBe(404)
    expect(
      (
        await test.request('tools/project.commit', {
          projectId: 'new-project',
          expectedRevision: 0,
          intentId: 'foreign-release',
          project: { ...test.project, releaseId: 'release-two' },
        })
      ).status,
    ).toBe(404)
  })
  it('promotes six immutable private outputs atomically without creative acceptance or reupload', async () => {
    const test = await fixture()
    const response = await test.promote()
    expect(response.status).toBe(200)
    expect(await response.json()).toMatchObject({
      state: 'review',
      outputCount: 6,
      humanAccepted: false,
    })
    const assets = await test.studio.assets('release-one')
    expect(assets).toHaveLength(6)
    expect(
      assets.every(
        asset =>
          asset.state === 'ready' &&
          asset.verified === 1 &&
          asset.object_key.startsWith(`editor/one/jobs/${test.render.id}/`),
      ),
    ).toBe(true)
    expect((await test.studio.jobForRelease('release-one'))?.state).toBe(
      'review',
    )
    expect((await test.promote()).status).toBe(409)
    expect(
      (await test.studio.assets('release-one')).every(
        asset => asset.state === 'ready',
      ),
    ).toBe(true)
  })
  it('rejects altered receipts, incomplete kits and missing private output bytes', async () => {
    const test = await fixture()
    const receiptText = test.objects.get(test.key('receipt.json')) ?? ''
    test.objects.set(test.key('receipt.json'), receiptText + ' ')
    expect((await test.promote()).status).toBe(409)
    test.objects.set(test.key('receipt.json'), receiptText)
    test.database
      .prepare('UPDATE editor_jobs SET receipt_json=? WHERE id=?')
      .run(
        JSON.stringify({
          ...test.receipt,
          outputs: test.receipt.outputs.slice(0, 5),
        }),
        test.render.id,
      )
    expect((await test.promote()).status).toBe(409)
    test.database
      .prepare('UPDATE editor_jobs SET receipt_json=? WHERE id=?')
      .run(JSON.stringify(test.receipt), test.render.id)
    test.objects.delete(test.key('film'))
    expect((await test.promote()).status).toBe(409)
    expect((await test.studio.jobForRelease('release-one'))?.state).toBe(
      'running',
    )
    expect(await test.studio.assets('release-one')).toHaveLength(0)
  })
  it('does not publish when the lease expires during private receipt readback', async () => {
    const test = await fixture()
    test.events.onGet = () => {
      test.database
        .prepare('UPDATE jobs SET lease_until=0 WHERE id=?')
        .run('job-one')
    }
    expect((await test.promote()).status).toBe(409)
    expect(
      (await test.studio.assets('release-one')).some(
        asset => asset.state === 'ready',
      ),
    ).toBe(false)
    expect((await test.studio.jobForRelease('release-one'))?.state).toBe(
      'running',
    )
  })
  it('recovers a partial promotion on a new attempt without duplicate assets', async () => {
    const test = await fixture()
    const artwork = test.objects.get(test.key('artwork')) ?? ''
    test.objects.delete(test.key('artwork'))
    expect((await test.promote()).status).toBe(409)
    expect(await test.studio.assets('release-one')).toHaveLength(5)
    test.objects.set(test.key('artwork'), artwork)
    test.database.prepare('UPDATE jobs SET attempt=2 WHERE id=?').run('job-one')
    expect((await test.promote()).status).toBe(200)
    const assets = await test.studio.assets('release-one')
    expect(assets).toHaveLength(6)
    expect(
      assets.every(asset => asset.attempt === 2 && asset.state === 'ready'),
    ).toBe(true)
  })
  it('keeps completed outputs ready when two promotions race', async () => {
    const test = await fixture()
    const attempts = await Promise.all([test.promote(), test.promote()])
    expect(attempts.map(response => response.status).sort()).toEqual([200, 409])
    expect(
      (await test.studio.assets('release-one')).every(
        asset => asset.state === 'ready' && asset.verified === 1,
      ),
    ).toBe(true)
    expect(
      test.database.prepare('SELECT COUNT(*) AS count FROM completions').get(),
    ).toMatchObject({ count: 1 })
  })
})
