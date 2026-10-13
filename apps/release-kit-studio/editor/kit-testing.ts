import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'
import { DatabaseSync } from 'node:sqlite'

import { canonicalJson } from '../src/canonical'
import { defaultProfile, outputs } from '../src/domain'
import type { MediaBucket } from '../src/server/api'
import { type SqlDatabase, Store } from '../src/server/store'
import { type Project } from './project'
import { EditorStore, digest } from './store'
import { projectFixture } from './testing'
import { type ArchiveHashFactory } from './zip'

export const nodeArchiveHash: ArchiveHashFactory = () => {
  const hash = createHash('sha256')
  return {
    write: async data => {
      hash.update(data)
    },
    finish: async () => hash.digest('hex'),
    abort: async () => {},
  }
}
export const kitFixture = async () => {
  const database = new DatabaseSync(':memory:')
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
        for (const item of statements)
          database.prepare(item.sql).run(...item.values)
        database.exec('COMMIT')
      } catch (error) {
        database.exec('ROLLBACK')
        throw error
      }
    },
  }
  const store = new EditorStore(sql)
  const studio = new Store(sql)
  const brief = {
    title: 'Synthetic kit',
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
  database
    .prepare(
      "INSERT INTO releases(id,tenant_id,request_key,brief_json,state,created_at) VALUES('release-one','one','one',?,'review',0)",
    )
    .run(JSON.stringify(brief))
  const base = projectFixture()
  const first = base.compositions[0]!
  const clip = first.clips[0]!
  const project: Project = {
    ...base,
    briefSha256: await digest(canonicalJson(brief)),
    compositions: outputs.map(output => {
      const still = ['thumbnail', 'artwork'].includes(output.id)
      return {
        ...first,
        id: output.id,
        width: output.id.startsWith('short-') ? 1080 : 1920,
        height:
          output.id.startsWith('short-') || output.id === 'artwork'
            ? 1920
            : 1080,
        frames: still ? 1 : 48,
        audio: still ? null : first.audio,
        clips: [{ ...clip, frames: still ? 1 : 48 }],
        captions: [],
        rationale: `Independent ${output.id} composition`,
      }
    }),
  }
  await store.commit('one', 'project-one', 0, 'initial', project)
  const started = await store.start('one', 'project-one', 1, 'render-one', {
    mode: 'kit',
    outputId: null,
  })
  const objects = new Map<string, string>()
  const prefix = `editor/one/jobs/${started.id}/`
  const measured = await Promise.all(
    project.compositions.map(async composition => {
      const content = `synthetic-${composition.id}`
      objects.set(prefix + composition.id, content)
      return {
        id: composition.id,
        sha256: await digest(content),
        bytes: content.length,
        width: composition.width,
        height: composition.height,
        duration: composition.audio ? 2 : 0,
        frames: composition.frames,
        completeDecode: true,
      }
    }),
  )
  const storedReceipt = canonicalJson({
    projectSha256: await digest(canonicalJson(project)),
    outputs: measured,
  })
  objects.set(prefix + 'receipt.json', storedReceipt)
  const receipt = {
    projectSha256: await digest(canonicalJson(project)),
    outputs: measured,
    measured: true,
    storedByteReadback: true,
    receiptStored: true,
    receiptSha256: await digest(storedReceipt),
  }
  await sql.run(
    "UPDATE editor_jobs SET state='ready',receipt_json=? WHERE id=?",
    [JSON.stringify(receipt), started.id],
  )
  for (const [token, tenant] of [
    ['private-one', 'one'],
    ['private-two', 'two'],
  ]) {
    await sql.run(
      'INSERT INTO editor_tokens(hash,tenant_id,expires_at) VALUES(?,?,?)',
      [await digest(token!), tenant!, Math.floor(Date.now() / 1000) + 3600],
    )
    await sql.run(
      'INSERT INTO sessions(hash,tenant_id,expires_at) VALUES(?,?,?)',
      [await digest(token!), tenant!, Math.floor(Date.now() / 1000) + 3600],
    )
  }
  const reads: Array<string> = []
  const media: MediaBucket = {
    head: async key => {
      const content = objects.get(key)
      return content === undefined
        ? null
        : { size: Buffer.byteLength(content), etag: await digest(content) }
    },
    get: async (key, options) => {
      reads.push(key)
      const content = objects.get(key)
      if (
        content === undefined ||
        (options.onlyIf &&
          options.onlyIf.etagMatches !== (await digest(content)))
      )
        return null
      return {
        body: new Blob([content]).stream(),
        size: Buffer.byteLength(content),
        httpEtag: 'test',
      }
    },
    put: async () => {
      throw new Error('Archive must not rewrite media.')
    },
    createMultipartUpload: async () => {
      throw new Error('Archive must not upload media.')
    },
    resumeMultipartUpload: () => {
      throw new Error('Archive must not upload media.')
    },
  }
  return {
    database,
    sql,
    store,
    studio,
    media,
    objects,
    prefix,
    receipt,
    project,
    reads,
    job: await store.job('one', started.id),
  }
}
