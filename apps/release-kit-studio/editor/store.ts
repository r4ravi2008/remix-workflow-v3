import { Schema } from 'effect'

import { canonicalJson } from '../src/canonical'
import { type SqlDatabase } from '../src/server/store'
import { type Asset, type Project, decodeProject } from './project'

export const digest = async (value: string | ArrayBuffer) =>
  Array.from(
    new Uint8Array(
      await crypto.subtle.digest(
        'SHA-256',
        typeof value === 'string' ? new TextEncoder().encode(value) : value,
      ),
    ),
    byte => byte.toString(16).padStart(2, '0'),
  ).join('')
export class EditorError extends Error {
  constructor(
    readonly status: number,
    readonly code: string,
    message: string,
  ) {
    super(message)
  }
}
const IntentRow = Schema.Struct({
  fingerprint: Schema.String,
  result_json: Schema.String,
})
const RevisionRow = Schema.Struct({
  revision: Schema.Number,
  fingerprint: Schema.String,
  document_json: Schema.String,
})
export const JobRow = Schema.Struct({
  id: Schema.String,
  tenant_id: Schema.String,
  release_id: Schema.String,
  project_id: Schema.String,
  revision: Schema.Number,
  intent_id: Schema.String,
  fingerprint: Schema.String,
  request_json: Schema.String,
  state: Schema.String,
  progress_json: Schema.String,
  receipt_json: Schema.NullOr(Schema.String),
  error: Schema.NullOr(Schema.String),
  created_at: Schema.Number,
  updated_at: Schema.Number,
})
export type JobRow = typeof JobRow.Type
const AssetRow = Schema.Struct({
  metadata_json: Schema.String,
  object_key: Schema.String,
  uploaded: Schema.Number,
})
const nullable = <S extends Schema.ConstraintDecoder<unknown>>(
  schema: S,
  value: unknown,
) => Schema.decodeUnknownSync(Schema.NullOr(schema))(value)
export class EditorStore {
  constructor(readonly db: SqlDatabase) {}
  async principal(hash: string, now: number, session: boolean) {
    const query = session
      ? 'SELECT tenant_id FROM sessions WHERE hash=? AND expires_at>?'
      : 'SELECT tenant_id FROM editor_tokens WHERE hash=? AND expires_at>? AND enabled=1'
    return nullable(
      Schema.Struct({ tenant_id: Schema.String }),
      await this.db.first(query, [hash, now]),
    )
  }
  async prior(tenant: string, intent: string, fingerprint: string) {
    const row = nullable(
      IntentRow,
      await this.db.first(
        'SELECT fingerprint,result_json FROM editor_intents WHERE tenant_id=? AND id=?',
        [tenant, intent],
      ),
    )
    if (row && row.fingerprint !== fingerprint)
      throw new EditorError(
        409,
        'intent_conflict',
        'This intent was already used for different content.',
      )
    return row ? row.result_json : null
  }
  async inspect(tenant: string, id: string, revision: number | null) {
    const row = nullable(
      RevisionRow,
      await this.db.first(
        'SELECT r.revision,r.fingerprint,r.document_json FROM editor_revisions r JOIN editor_projects p ON p.tenant_id=r.tenant_id AND p.id=r.project_id WHERE r.tenant_id=? AND r.project_id=? AND r.revision=COALESCE(?,p.revision)',
        [tenant, id, revision],
      ),
    )
    if (!row)
      throw new EditorError(
        404,
        'project_not_found',
        'Project revision not found.',
      )
    return {
      projectId: id,
      revision: row.revision,
      fingerprint: row.fingerprint,
      project: decodeProject(JSON.parse(row.document_json)),
    }
  }
  async commit(
    tenant: string,
    id: string,
    expected: number,
    intent: string,
    project: Project,
  ) {
    const fingerprint = await digest(canonicalJson({ id, expected, project }))
    const previous = await this.prior(tenant, intent, fingerprint)
    if (previous)
      return this.inspect(
        tenant,
        id,
        Schema.decodeUnknownSync(Schema.Struct({ revision: Schema.Number }))(
          JSON.parse(previous),
        ).revision,
      )
    const revision = expected + 1
    const time = Math.floor(Date.now() / 1000)
    await this.db.batch([
      {
        sql: 'INSERT OR IGNORE INTO editor_projects(tenant_id,id,release_id,revision) SELECT ?,?,id,0 FROM releases WHERE tenant_id=? AND id=?',
        values: [tenant, id, tenant, project.releaseId],
      },
      {
        sql: 'INSERT INTO editor_revisions(tenant_id,project_id,revision,intent_id,fingerprint,document_json,created_at) SELECT ?,?,?,?,?,?,? WHERE EXISTS(SELECT 1 FROM editor_projects WHERE tenant_id=? AND id=? AND revision=? AND release_id=?) AND NOT EXISTS(SELECT 1 FROM editor_intents WHERE tenant_id=? AND id=?)',
        values: [
          tenant,
          id,
          revision,
          intent,
          fingerprint,
          canonicalJson(project),
          time,
          tenant,
          id,
          expected,
          project.releaseId,
          tenant,
          intent,
        ],
      },
      {
        sql: 'UPDATE editor_projects SET revision=? WHERE tenant_id=? AND id=? AND revision=? AND EXISTS(SELECT 1 FROM editor_revisions WHERE tenant_id=? AND project_id=? AND revision=? AND intent_id=? AND fingerprint=?)',
        values: [
          revision,
          tenant,
          id,
          expected,
          tenant,
          id,
          revision,
          intent,
          fingerprint,
        ],
      },
      {
        sql: 'INSERT INTO editor_intents(tenant_id,id,fingerprint,result_json) SELECT ?,?,?,? WHERE EXISTS(SELECT 1 FROM editor_revisions WHERE tenant_id=? AND project_id=? AND revision=? AND intent_id=? AND fingerprint=?)',
        values: [
          tenant,
          intent,
          fingerprint,
          JSON.stringify({ projectId: id, revision }),
          tenant,
          id,
          revision,
          intent,
          fingerprint,
        ],
      },
    ])
    const result = await this.prior(tenant, intent, fingerprint)
    if (!result)
      throw new EditorError(
        409,
        'revision_conflict',
        'Project changed. Inspect its current revision before retrying.',
      )
    return this.inspect(tenant, id, revision)
  }
  async history(tenant: string, id: string) {
    return this.db.all(
      'SELECT revision,fingerprint,created_at FROM editor_revisions WHERE tenant_id=? AND project_id=? ORDER BY revision DESC LIMIT 100',
      [tenant, id],
    )
  }
  async asset(tenant: string, id: string) {
    const own = nullable(
      AssetRow,
      await this.db.first(
        'SELECT metadata_json,object_key,uploaded FROM editor_assets WHERE tenant_id=? AND id=?',
        [tenant, id],
      ),
    )
    if (own) return { ...own, metadata: JSON.parse(own.metadata_json) }
    const source = nullable(
      Schema.Struct({
        object_key: Schema.String,
        bytes: Schema.Number,
        sha256: Schema.String,
      }),
      await this.db.first(
        "SELECT a.object_key,a.bytes,a.sha256 FROM assets a JOIN releases r ON r.id=a.release_id WHERE r.tenant_id=? AND a.id=? AND a.state='uploaded' AND a.verified=1 AND a.kind='audio'",
        [tenant, id],
      ),
    )
    return source
      ? {
          metadata: { sha256: source.sha256, bytes: source.bytes },
          object_key: source.object_key,
          uploaded: 1,
        }
      : null
  }
  async registerAsset(tenant: string, asset: Asset) {
    const existing = await this.asset(tenant, asset.id)
    if (existing && canonicalJson(existing.metadata) !== canonicalJson(asset))
      throw new EditorError(
        409,
        'asset_conflict',
        'This asset ID already refers to different immutable metadata.',
      )
    await this.db.run(
      'INSERT OR IGNORE INTO editor_assets(tenant_id,id,metadata_json,object_key) VALUES(?,?,?,?)',
      [
        tenant,
        asset.id,
        canonicalJson(asset),
        `editor/${tenant}/source/${asset.sha256}`,
      ],
    )
    return {
      id: asset.id,
      uploadPath: `/v1/media/${asset.id}`,
      maximumBytes: 100 * 1024 * 1024,
    }
  }
  async job(tenant: string, id: string) {
    const row = nullable(
      JobRow,
      await this.db.first(
        'SELECT * FROM editor_jobs WHERE tenant_id=? AND id=?',
        [tenant, id],
      ),
    )
    if (!row)
      throw new EditorError(404, 'job_not_found', 'Render job not found.')
    return row
  }
  async start(
    tenant: string,
    projectId: string,
    revision: number,
    intent: string,
    request: unknown,
  ) {
    const snapshot = await this.inspect(tenant, projectId, revision)
    const fingerprint = await digest(
      canonicalJson({
        projectId,
        revision,
        request,
        snapshot: snapshot.fingerprint,
      }),
    )
    await this.prior(tenant, intent, fingerprint)
    const previous = nullable(
      JobRow,
      await this.db.first(
        'SELECT * FROM editor_jobs WHERE tenant_id=? AND intent_id=?',
        [tenant, intent],
      ),
    )
    if (previous) {
      if (previous.fingerprint !== fingerprint)
        throw new EditorError(
          409,
          'intent_conflict',
          'Render intent refers to different content.',
        )
      return previous
    }
    const id = crypto.randomUUID()
    const time = Math.floor(Date.now() / 1000)
    try {
      await this.db.batch([
        {
          sql: "INSERT INTO editor_jobs(id,tenant_id,release_id,project_id,revision,intent_id,fingerprint,request_json,state,progress_json,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,'queued',?, ?,?)",
          values: [
            id,
            tenant,
            snapshot.project.releaseId,
            projectId,
            revision,
            intent,
            fingerprint,
            canonicalJson(request),
            JSON.stringify({ completedOutputs: 0, phase: 'queued' }),
            time,
            time,
          ],
        },
        {
          sql: 'INSERT INTO editor_intents(tenant_id,id,fingerprint,result_json) VALUES(?,?,?,?)',
          values: [tenant, intent, fingerprint, JSON.stringify({ jobId: id })],
        },
      ])
    } catch {
      const replay = nullable(
        JobRow,
        await this.db.first(
          'SELECT * FROM editor_jobs WHERE tenant_id=? AND intent_id=?',
          [tenant, intent],
        ),
      )
      if (replay && replay.fingerprint === fingerprint) return replay
      throw new EditorError(
        409,
        'active_render',
        'This release already has an active or uncertain render. Reconcile it before starting another.',
      )
    }
    return this.job(tenant, id)
  }
}
