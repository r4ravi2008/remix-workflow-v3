// @vitest-environment node
import { readFileSync } from 'node:fs'
import { DatabaseSync } from 'node:sqlite'
import { afterEach, describe, expect, it } from 'vitest'

import { type SqlDatabase } from '../src/server/store'
import { EditorStore } from './store'
import { projectFixture } from './testing'

const databases: Array<DatabaseSync> = []
const fixture = () => {
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
  database.prepare('INSERT INTO tenants(id,name,created_at) VALUES(?,?,0)').run('one', 'One')
  database.prepare('INSERT INTO tenants(id,name,created_at) VALUES(?,?,0)').run('two', 'Two')
  database
    .prepare(
      "INSERT INTO releases(id,tenant_id,request_key,brief_json,state,created_at) VALUES(?,?,?,'{}','draft',0)",
    )
    .run('release-one', 'one', 'one')
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
  return { store: new EditorStore(sql), database }
}
afterEach(() => {
  databases.splice(0).forEach(database => database.close())
})
describe('Cloudflare editor revision and render ledger', () => {
  it('commits atomically, replays exact intents and rejects changed content or stale writers', async () => {
    const { store } = fixture()
    const first = await store.commit(
      'one',
      'project-one',
      0,
      'edit-one',
      projectFixture(),
    )
    expect(first.revision).toBe(1)
    expect(
      await store.commit('one', 'project-one', 0, 'edit-one', projectFixture()),
    ).toEqual(first)
    await expect(
      store.commit('one', 'project-one', 0, 'edit-one', {
        ...projectFixture(),
        lyrics: 'కొత్త పదం',
      }),
    ).rejects.toMatchObject({ code: 'intent_conflict' })
    await expect(
      store.commit('one', 'project-one', 0, 'edit-two', projectFixture()),
    ).rejects.toMatchObject({ code: 'revision_conflict' })
    expect(await store.history('one', 'project-one')).toHaveLength(1)
  })
  it('fences independent edit writers and preserves the winning snapshot', async () => {
    const { store } = fixture()
    await store.commit('one', 'project-one', 0, 'first', projectFixture())
    const attempts = await Promise.allSettled([
      store.commit('one', 'project-one', 1, 'writer-a', projectFixture()),
      store.commit('one', 'project-one', 1, 'writer-b', projectFixture()),
    ])
    expect(
      attempts.filter(result => result.status === 'fulfilled'),
    ).toHaveLength(1)
    expect((await store.inspect('one', 'project-one', null)).revision).toBe(2)
    expect(await store.history('one', 'project-one')).toHaveLength(2)
  })
  it('hides projects, assets and jobs from another tenant', async () => {
    const { store } = fixture()
    await store.commit('one', 'project-one', 0, 'first', projectFixture())
    await expect(
      store.inspect('two', 'project-one', null),
    ).rejects.toMatchObject({ code: 'project_not_found' })
    const asset = projectFixture().assets[1]
    if (!asset) throw new Error('Missing fixture asset')
    await store.registerAsset('one', asset)
    expect(await store.asset('two', asset.id)).toBeNull()
    const job = await store.start('one', 'project-one', 1, 'render-one', {
      mode: 'diagnostic',
    })
    await expect(store.job('two', job.id)).rejects.toMatchObject({
      code: 'job_not_found',
    })
  })
  it('deduplicates render starts and holds the release fence through uncertainty', async () => {
    const { store, database } = fixture()
    await store.commit('one', 'project-one', 0, 'first', projectFixture())
    const first = await store.start('one', 'project-one', 1, 'render-one', {
      mode: 'diagnostic',
    })
    expect(
      (
        await store.start('one', 'project-one', 1, 'render-one', {
          mode: 'diagnostic',
        })
      ).id,
    ).toBe(first.id)
    await expect(
      store.start('one', 'project-one', 1, 'render-one', { mode: 'kit' }),
    ).rejects.toMatchObject({ code: 'intent_conflict' })
    database
      .prepare("UPDATE editor_jobs SET state='uncertain' WHERE id=?")
      .run(first.id)
    await expect(
      store.start('one', 'project-one', 1, 'render-two', {
        mode: 'diagnostic',
      }),
    ).rejects.toMatchObject({ code: 'active_render' })
    database
      .prepare("UPDATE editor_jobs SET state='failed' WHERE id=?")
      .run(first.id)
    expect(
      (
        await store.start('one', 'project-one', 1, 'render-two', {
          mode: 'diagnostic',
        })
      ).id,
    ).not.toBe(first.id)
  })
  it('does not allow a render to reuse an edit intent', async () => {
    const { store } = fixture()
    await store.commit('one', 'project-one', 0, 'first', projectFixture())
    await expect(
      store.start('one', 'project-one', 1, 'first', { mode: 'kit' }),
    ).rejects.toMatchObject({ code: 'intent_conflict' })
  })
})
