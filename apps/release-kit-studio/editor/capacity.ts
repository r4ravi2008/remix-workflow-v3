import { Schema } from 'effect'

import type { SqlDatabase } from '../src/server/store'
import { type JobRow } from './store'

const Grant = Schema.Struct({
  tenant_id: Schema.String,
  job_id: Schema.String,
  fingerprint: Schema.String,
  purpose: Schema.Literals(['render', 'verify']),
  token: Schema.String,
  started_at: Schema.Number,
})
export type CapacityGrant = typeof Grant.Type
export class EditorCapacity {
  constructor(readonly db: SqlDatabase) {}
  async holder() {
    return Schema.decodeUnknownSync(Schema.NullOr(Grant))(
      await this.db.first('SELECT * FROM editor_capacity WHERE slot=?', [
        'native-renderer',
      ]),
    )
  }
  async claim(job: JobRow, purpose: 'render' | 'verify') {
    if (purpose === 'render')
      await this.db.run(
        `INSERT OR IGNORE INTO editor_capacity_waiters(job_id,tenant_id,fingerprint)
        SELECT id,tenant_id,fingerprint FROM editor_jobs WHERE id=? AND tenant_id=? AND fingerprint=? AND state='queued'`,
        [job.id, job.tenant_id, job.fingerprint],
      )
    const prior = await this.holder()
    if (prior) {
      return purpose === 'render' &&
        prior.purpose === purpose &&
        prior.job_id === job.id &&
        prior.tenant_id === job.tenant_id &&
        prior.fingerprint === job.fingerprint
        ? prior
        : null
    }
    const token = crypto.randomUUID()
    const now = Math.floor(Date.now() / 1000)
    await this.db.batch([
      {
        sql: `INSERT INTO editor_capacity(slot,tenant_id,job_id,fingerprint,purpose,token,started_at)
       SELECT 'native-renderer',tenant_id,id,fingerprint,?,?,? FROM editor_jobs
       WHERE id=? AND tenant_id=? AND fingerprint=? AND state=?
       AND NOT EXISTS(SELECT 1 FROM editor_jobs WHERE state IN ('staging','running','verifying','cancel-requested','uncertain'))
       AND (?='verify' OR id=(SELECT j.id FROM editor_jobs j JOIN editor_capacity_waiters w ON w.job_id=j.id AND w.tenant_id=j.tenant_id AND w.fingerprint=j.fingerprint WHERE j.state='queued'
         ORDER BY CASE WHEN j.tenant_id>(SELECT last_tenant FROM editor_capacity_cursor WHERE slot='native-renderer') THEN 0 ELSE 1 END,j.tenant_id,w.sequence LIMIT 1))
       ON CONFLICT(slot) DO NOTHING`,
        values: [
          purpose,
          token,
          now,
          job.id,
          job.tenant_id,
          job.fingerprint,
          purpose === 'render' ? 'queued' : 'ready',
          purpose,
        ],
      },
      ...(purpose === 'render'
        ? [
            {
              sql: "UPDATE editor_capacity_cursor SET last_tenant=? WHERE slot='native-renderer' AND EXISTS(SELECT 1 FROM editor_capacity WHERE token=?)",
              values: [job.tenant_id, token],
            },
          ]
        : []),
    ])
    const grant = await this.holder()
    if (grant?.token !== token) return null
    return grant
  }
  async release(grant: CapacityGrant) {
    await this.db.batch([
      {
        sql: 'DELETE FROM editor_capacity_waiters WHERE job_id=? AND tenant_id=? AND fingerprint=? AND EXISTS(SELECT 1 FROM editor_capacity WHERE token=? AND job_id=? AND tenant_id=? AND fingerprint=? AND purpose=?)',
        values: [
          grant.job_id,
          grant.tenant_id,
          grant.fingerprint,
          grant.token,
          grant.job_id,
          grant.tenant_id,
          grant.fingerprint,
          grant.purpose,
        ],
      },
      {
        sql: 'DELETE FROM editor_capacity WHERE slot=? AND token=? AND job_id=? AND tenant_id=? AND fingerprint=? AND purpose=?',
        values: [
          'native-renderer',
          grant.token,
          grant.job_id,
          grant.tenant_id,
          grant.fingerprint,
          grant.purpose,
        ],
      },
    ])
  }
}
