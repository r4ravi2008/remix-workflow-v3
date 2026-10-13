import { Schema } from 'effect'
import { readFileSync } from 'node:fs'
// @vitest-environment node
import { DatabaseSync } from 'node:sqlite'
import { afterEach, describe, expect, it } from 'vitest'

import { defaultProfile, outputs } from '../domain'
import {
  AssetRow,
  type ReleaseBrief,
  validateBrief,
  validateMeasurement,
} from './contracts'
import { type SqlDatabase, Store } from './store'

const databases: Array<DatabaseSync> = []
const fixture = () => {
  const database = new DatabaseSync(':memory:')
  databases.push(database)
  database.exec(
    readFileSync(
      new URL('../../migrations/0001_studio.sql', import.meta.url),
      'utf8',
    ),
  )
  database.exec(
    readFileSync(
      new URL('../../migrations/0002_artist_profiles.sql', import.meta.url),
      'utf8',
    ),
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
  return { store: new Store(sql), database }
}
afterEach(() => {
  databases.splice(0).forEach(database => database.close())
})
const brief: ReleaseBrief = {
  title: 'పల్ పల్',
  lyrics: 'ప్రతి నిమిషం నువ్వ్లేని లోటే వేదిస్తూ ఉందే',
  language: 'Telugu',
  audioName: 'song.wav',
  audioSha256: 'a'.repeat(64),
  audioBytes: 100,
  audioDuration: 239.68,
  profile: defaultProfile,
}
const prepare = async (
  store: Store,
  tenantId = 'tenant-one',
  releaseId = 'release-one',
) => {
  await store.issueInvite(tenantId, tenantId, `invite-${tenantId}`, 10)
  await store.createRelease(
    tenantId,
    releaseId,
    `request-${releaseId}`,
    brief,
    11,
  )
  await store.insertAsset(
    Schema.decodeUnknownSync(AssetRow)({
      id: `audio-${releaseId}`,
      release_id: releaseId,
      job_id: null,
      attempt: null,
      kind: 'audio',
      output_id: null,
      object_key: `${tenantId}/${releaseId}/audio`,
      bytes: 100,
      sha256: brief.audioSha256,
      content_type: 'audio/wav',
      state: 'uploading',
      upload_id: null,
      verified: 0,
      measurement_json: null,
      created_at: 12,
    }),
  )
  await store.markUploaded(`audio-${releaseId}`, true)
  await store.startRelease(releaseId, `job-${releaseId}`, 13)
}
const completeOutputs = async (
  store: Store,
  job: NonNullable<Awaited<ReturnType<Store['claim']>>>,
) =>
  Promise.all(
    outputs.map(async output => {
      const asset = Schema.decodeUnknownSync(AssetRow)({
        id: `output-${output.id}`,
        release_id: job.release_id,
        job_id: job.id,
        attempt: job.attempt,
        kind: 'output',
        output_id: output.id,
        object_key: `outputs/${job.attempt}/${output.id}`,
        bytes: 200,
        sha256: 'b'.repeat(64),
        content_type:
          output.id === 'artwork' || output.id === 'thumbnail'
            ? 'image/jpeg'
            : 'video/mp4',
        state: 'uploading',
        upload_id: 'upload-id',
        verified: 0,
        measurement_json: null,
        created_at: 15,
      })
      await store.insertAsset(asset)
      await store.markUploaded(asset.id, false)
      return {
        asset: { ...asset, state: 'uploaded' },
        measurement: {
          width: 1920,
          height: 1080,
          duration: brief.audioDuration,
          sha256: 'b'.repeat(64),
          storageSha256: 'b'.repeat(64),
          decoded: true,
          composition: `native-${output.id}`,
        },
      }
    }),
  )

describe('durable studio isolation and recovery', () => {
  it('exchanges an invitation once and keeps tenant release queries isolated', async () => {
    const { store } = fixture()
    await prepare(store)
    await prepare(store, 'tenant-two', 'release-two')
    expect(
      await store.exchangeInvite('invite-tenant-one', 'session-one', 20),
    ).toEqual({ id: 'tenant-one', name: 'tenant-one' })
    await expect(
      store.exchangeInvite('invite-tenant-one', 'session-replay', 21),
    ).rejects.toThrow('already used')
    expect(await store.session('session-replay', 21)).toBeNull()
    expect(await store.release('tenant-two', 'release-one')).toBeNull()
    expect((await store.list('tenant-one')).map(release => release.id)).toEqual(
      ['release-one'],
    )
    expect(await store.session('session-one', 20 + 7 * 86400)).toBeNull()
  })
  it('deduplicates identical submissions and refuses changed briefs with the same key', async () => {
    const { store } = fixture()
    await prepare(store)
    expect(
      (
        await store.createRelease(
          'tenant-one',
          'duplicate',
          'request-release-one',
          brief,
          30,
        )
      ).id,
    ).toBe('release-one')
    await expect(
      store.createRelease(
        'tenant-one',
        'duplicate',
        'request-release-one',
        { ...brief, audioSha256: 'c'.repeat(64) },
        31,
      ),
    ).rejects.toThrow('different brief')
  })
  it('returns to the same studio with a fresh one-time invitation and preserves its releases', async () => {
    const { store } = fixture()
    await prepare(store)
    await store.exchangeInvite('invite-tenant-one', 'first-session', 20)
    await store.logout('first-session')
    await store.issueReturnInvite('tenant-one', 'return-invite', 21)
    expect(
      await store.exchangeInvite('return-invite', 'return-session', 22),
    ).toEqual({ id: 'tenant-one', name: 'tenant-one' })
    expect((await store.list('tenant-one'))[0]?.id).toBe('release-one')
    await expect(
      store.exchangeInvite('return-invite', 'replay-session', 23),
    ).rejects.toThrow('already used')
  })
  it('scopes artist identity to the studio, fences conflicting saves, and preserves frozen release direction', async () => {
    const { store } = fixture()
    await prepare(store)
    await prepare(store, 'tenant-two', 'release-two')
    const original = await store.saveArtist('tenant-one', brief.profile, 0, 20)
    expect(original.revision).toBe(1)
    expect(await store.artist('tenant-two')).toBeNull()
    const changed = {
      ...brief.profile,
      identity: 'A new visual world for future songs.',
    }
    expect(
      (await store.saveArtist('tenant-one', changed, 1, 21)).revision,
    ).toBe(2)
    await expect(
      store.saveArtist('tenant-one', brief.profile, 1, 22),
    ).rejects.toThrow('another tab')
    await expect(
      store.saveArtist('tenant-one', brief.profile, 0, 22),
    ).rejects.toThrow('another tab')
    expect((await store.artist('tenant-one'))?.profile).toEqual(changed)
    expect(
      JSON.parse(
        (await store.release('tenant-one', 'release-one'))?.brief_json ?? '{}',
      ).profile,
    ).toEqual(brief.profile)
  })
  it('claims one attempt atomically and fences stale workers after expiry', async () => {
    const { store } = fixture()
    await prepare(store)
    await store.enroll('worker-one', 'token-one', 'GPU and Resolve')
    await store.enroll('worker-two', 'token-two', 'Another worker')
    const claims = await Promise.all([
      store.claim('worker-one', 'lease-one', 20),
      store.claim('worker-two', 'lease-two', 20),
    ])
    expect(claims.filter(Boolean)).toHaveLength(1)
    const first = claims.find(claim => claim !== null)
    expect(first?.attempt).toBe(1)
    const recovered = await store.claim('worker-two', 'lease-recovery', 201)
    expect(recovered?.attempt).toBe(2)
    await expect(
      store.lease('job-release-one', 'worker-one', 'lease-one', 202),
    ).rejects.toThrow('expired')
    expect(
      (
        await store.lease(
          'job-release-one',
          'worker-two',
          'lease-recovery',
          202,
        )
      ).attempt,
    ).toBe(2)
  })
  it('requires the complete kit and rolls back completion if its lease expires', async () => {
    const { store } = fixture()
    await prepare(store)
    await store.enroll('worker-one', 'token-one', 'GPU and Resolve')
    const job = await store.claim('worker-one', 'lease-one', 20)
    if (!job) throw new Error('Expected a claimed job')
    const measured = await completeOutputs(store, job)
    await expect(
      store.complete(job, 'lease-one', measured.slice(0, 1), {}, 21),
    ).rejects.toThrow('six unique')
    await expect(
      store.complete(job, 'lease-one', measured, {}, 201),
    ).rejects.toThrow('not committed')
    expect((await store.jobForRelease(job.release_id))?.state).toBe('running')
    expect(
      (await store.assets(job.release_id)).filter(
        asset => asset.state === 'ready',
      ),
    ).toHaveLength(0)
    await store.complete(
      job,
      'lease-one',
      measured,
      { provider: 'tailscale', finisher: 'resolve' },
      22,
    )
    expect((await store.release('tenant-one', job.release_id))?.state).toBe(
      'review',
    )
    expect(
      (await store.assets(job.release_id)).filter(
        asset => asset.state === 'ready',
      ),
    ).toHaveLength(6)
  })
  it('holds direction durably without repeated claims and resumes only for the assigned worker', async () => {
    const { store } = fixture()
    await prepare(store)
    await store.enroll('worker-one', 'token-one', 'GPU and Resolve')
    await store.enroll('worker-two', 'token-two', 'Another worker')
    const job = await store.claim('worker-one', 'lease-one', 20)
    if (!job) throw new Error('Expected a claimed job')
    await store.hold(
      job,
      'lease-one',
      'waiting-for-direction',
      { sourceVerified: true },
      21,
    )
    expect(await store.claim('worker-two', 'lease-two', 9999)).toBeNull()
    expect((await store.jobForRelease(job.release_id))?.attempt).toBe(1)
    expect((await store.release('tenant-one', job.release_id))?.state).toBe(
      'waiting-for-direction',
    )
    expect(await store.holds('worker-two')).toEqual([])
    const held = await store.resumable(job.id, 'worker-one')
    await expect(store.resumable(job.id, 'worker-two')).rejects.toThrow(
      'owned by this worker',
    )
    await expect(store.resume(held, 'worker-two', {}, 22)).rejects.toThrow(
      'not committed',
    )
    await store.resume(held, 'worker-one', { briefSha256: 'a'.repeat(64) }, 23)
    const resumed = await store.claim('worker-one', 'lease-new', 24)
    expect(resumed?.attempt).toBe(2)
    expect((await store.release('tenant-one', job.release_id))?.state).toBe(
      'running',
    )
    await expect(store.resume(held, 'worker-one', {}, 25)).rejects.toThrow(
      'not committed',
    )
    await expect(
      store.lease(job.id, 'worker-one', 'lease-one', 25),
    ).rejects.toThrow('expired')
  })
  it('rolls back a stale hold and excludes uncertain work from automatic resume', async () => {
    const { store, database } = fixture()
    await prepare(store)
    await store.enroll('worker-one', 'token-one', 'GPU and Resolve')
    const job = await store.claim('worker-one', 'lease-one', 20)
    if (!job) throw new Error('Expected a claimed job')
    await expect(
      store.hold(job, 'lease-one', 'waiting-for-review', {}, 201),
    ).rejects.toThrow('not committed')
    expect((await store.jobForRelease(job.release_id))?.state).toBe('running')
    expect((await store.release('tenant-one', job.release_id))?.state).toBe(
      'running',
    )
    expect(
      database.prepare('SELECT COUNT(*) AS total FROM job_events').get()?.total,
    ).toBe(0)
    await store.hold(
      job,
      'lease-one',
      'needs-reconciliation',
      { requestId: 'known-request' },
      21,
    )
    expect((await store.holds('worker-one'))[0]?.state).toBe(
      'needs-reconciliation',
    )
    await expect(store.resumable(job.id, 'worker-one')).rejects.toThrow(
      'direction or review hold',
    )
    expect(await store.claim('worker-one', 'another-lease', 1000)).toBeNull()
  })
  it('rejects romanized lyrics, shortened full films and missing storage readbacks', () => {
    expect(() => validateBrief({ ...brief, lyrics: 'prati nimisham' })).toThrow(
      'native script',
    )
    const measurement = {
      width: 1920,
      height: 1080,
      duration: 3.875,
      decoded: true,
      sha256: 'b'.repeat(64),
      storageSha256: 'b'.repeat(64),
      composition: 'resolve-pilot',
    }
    expect(() =>
      validateMeasurement('film', measurement, brief.audioDuration),
    ).toThrow('full song')
    expect(() =>
      validateMeasurement(
        'thumbnail',
        { ...measurement, duration: 0, storageSha256: 'c'.repeat(64) },
        brief.audioDuration,
      ),
    ).toThrow('Read back')
  })
  it('revokes a worker credential without changing another device', async () => {
    const { store } = fixture()
    await store.enroll('worker-one', 'token-one', 'Production')
    await store.enroll('worker-two', 'token-two', 'Isolation diagnostic')
    expect(await store.device('token-two', 20)).toEqual({
      id: 'worker-two',
      name: 'Isolation diagnostic',
    })
    await store.revokeDevice('worker-two')
    expect(await store.device('token-two', 21)).toBeNull()
    expect(await store.device('token-one', 21)).toEqual({
      id: 'worker-one',
      name: 'Production',
    })
  })
})
