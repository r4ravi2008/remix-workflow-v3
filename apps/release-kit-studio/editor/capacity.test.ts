// @vitest-environment node
import { readFileSync } from 'node:fs'
import { DatabaseSync } from 'node:sqlite'
import { afterEach, describe, expect, it } from 'vitest'

import type { SqlDatabase } from '../src/server/store'
import { EditorCapacity } from './capacity'
import { EditorStore } from './store'
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
    '0004_editor_capacity.sql',
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
  const store = new EditorStore(sql)
  const jobs = []
  for (const tenant of ['a', 'b', 'c']) {
    database
      .prepare('INSERT INTO tenants(id,name,created_at) VALUES(?,?,0)')
      .run(tenant, tenant)
    for (const index of [1, 2]) {
      const id = `${tenant}-${index}`
      database
        .prepare(
          "INSERT INTO releases(id,tenant_id,request_key,brief_json,state,created_at) VALUES(?,?,?,'{}','draft',0)",
        )
        .run(id, tenant, id)
      await store.commit(tenant, id, 0, `commit-${id}`, {
        ...projectFixture(),
        releaseId: id,
      })
      jobs.push(
        await store.start(tenant, id, 1, `render-${id}`, {
          mode: 'diagnostic',
        }),
      )
    }
  }
  return { capacity: new EditorCapacity(sql), database, jobs }
}
describe('shared Editor render admission', () => {
  it('admits one renderer across concurrent tenants and reuses the exact owned grant', async () => {
    const { capacity, jobs } = await fixture()
    const first = jobs[0]!,
      other = jobs[2]!
    const grants = await Promise.all([
      capacity.claim(first, 'render'),
      capacity.claim(other, 'render'),
    ])
    expect(grants.filter(Boolean)).toHaveLength(1)
    const holder = await capacity.holder()
    expect(holder).not.toBeNull()
    const owned = jobs.find(job => job.id === holder?.job_id)!
    expect(await capacity.claim(owned, 'render')).toEqual(holder)
    expect(
      await capacity.claim(other.id === owned.id ? first : other, 'render'),
    ).toBeNull()
  })
  it('rotates tenants and preserves FIFO within each registered tenant', async () => {
    const { capacity, jobs, database } = await fixture()
    const first = await capacity.claim(jobs[0]!, 'render')
    expect(first).not.toBeNull()
    for (const job of jobs.slice(1))
      expect(await capacity.claim(job, 'render')).toBeNull()
    const order = [jobs[0]!.project_id]
    let grant = first!
    for (const index of [2, 4, 1, 3, 5]) {
      database
        .prepare("UPDATE editor_jobs SET state='ready' WHERE id=?")
        .run(grant.job_id)
      await capacity.release(grant)
      for (const earlier of jobs.filter(
        job =>
          job.id !== jobs[index]!.id &&
          database
            .prepare('SELECT state FROM editor_jobs WHERE id=?')
            .get(job.id)?.state === 'queued',
      ))
        expect(await capacity.claim(earlier, 'render')).toBeNull()
      const next = await capacity.claim(jobs[index]!, 'render')
      expect(next).not.toBeNull()
      grant = next!
      order.push(jobs[index]!.project_id)
    }
    expect(order).toEqual(['a-1', 'b-1', 'c-1', 'a-2', 'b-2', 'c-2'])
  })
  it('unattached queued jobs do not block actors that registered a wakeup', async () => {
    const { capacity, jobs } = await fixture()
    const grant = await capacity.claim(jobs[4]!, 'render')
    expect(grant?.job_id).toBe(jobs[4]!.id)
  })
  it('keeps unknown render outcomes reserved until exact owned termination releases capacity', async () => {
    const { capacity, database, jobs } = await fixture()
    const grant = (await capacity.claim(jobs[0]!, 'render'))!
    database
      .prepare(
        "UPDATE editor_jobs SET state='uncertain',updated_at=0 WHERE id=?",
      )
      .run(grant.job_id)
    expect(await capacity.claim(jobs[2]!, 'render')).toBeNull()
    await capacity.release({ ...grant, token: crypto.randomUUID() })
    expect(await capacity.holder()).toEqual(grant)
    await capacity.release({ ...grant, tenant_id: 'b' })
    expect(await capacity.holder()).toEqual(grant)
    database
      .prepare("UPDATE editor_jobs SET state='cancelled' WHERE id=?")
      .run(grant.job_id)
    await capacity.release(grant)
    expect((await capacity.claim(jobs[2]!, 'render'))?.job_id).toBe(jobs[2]!.id)
  })
  it('includes cold verification in the same capacity gate and rejects stale or foreign job bindings', async () => {
    const { capacity, database, jobs } = await fixture()
    database
      .prepare("UPDATE editor_jobs SET state='ready' WHERE id=?")
      .run(jobs[0]!.id)
    const ready = { ...jobs[0]!, state: 'ready' }
    expect(
      await capacity.claim({ ...ready, fingerprint: 'foreign' }, 'verify'),
    ).toBeNull()
    expect(
      await capacity.claim({ ...ready, tenant_id: 'b' }, 'verify'),
    ).toBeNull()
    const verifier = (await capacity.claim(ready, 'verify'))!
    expect(verifier.purpose).toBe('verify')
    expect(await capacity.claim(ready, 'verify')).toBeNull()
    expect(await capacity.claim(jobs[2]!, 'render')).toBeNull()
    await capacity.release(verifier)
    expect((await capacity.claim(jobs[2]!, 'render'))?.purpose).toBe('render')
  })
  it('defers admission around legacy or unclaimed active runtime outcomes', async () => {
    const { capacity, database, jobs } = await fixture()
    for (const state of [
      'staging',
      'running',
      'verifying',
      'cancel-requested',
      'uncertain',
    ]) {
      database
        .prepare('UPDATE editor_jobs SET state=? WHERE id=?')
        .run(state, jobs[0]!.id)
      expect(await capacity.claim(jobs[2]!, 'render')).toBeNull()
    }
    database
      .prepare("UPDATE editor_jobs SET state='cancelled' WHERE id=?")
      .run(jobs[0]!.id)
    expect((await capacity.claim(jobs[2]!, 'render'))?.job_id).toBe(jobs[2]!.id)
  })
})
