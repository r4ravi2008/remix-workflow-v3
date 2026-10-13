import { Context, Schema } from 'effect'

import { ArtistProfile, outputs } from '../domain'
import {
  ApiError,
  ArtistRow,
  AssetRow,
  DeviceRow,
  type HoldReason,
  JobRow,
  type Measurement,
  PartRow,
  type ReleaseBrief,
  ReleaseRow,
  TenantRow,
  requireCondition,
} from './contracts'

export type SqlValue = string | number | null
export interface SqlDatabase {
  first(sql: string, values: Array<SqlValue>): Promise<unknown>
  all(sql: string, values: Array<SqlValue>): Promise<Array<unknown>>
  run(sql: string, values: Array<SqlValue>): Promise<void>
  batch(
    statements: Array<{ sql: string; values: Array<SqlValue> }>,
  ): Promise<void>
}
const nullable =
  <S extends Schema.ConstraintDecoder<unknown>>(schema: S) =>
  (value: unknown): S['Type'] | null =>
    value === null ? null : Schema.decodeUnknownSync(schema)(value)

export class StudioStore extends Context.Service<StudioStore, Store>()(
  'release-kit/StudioStore',
) {}
export class Store {
  constructor(readonly db: SqlDatabase) {}
  async issueInvite(tenantId: string, name: string, hash: string, now: number) {
    await this.db.batch([
      {
        sql: 'INSERT INTO tenants(id,name,created_at) VALUES(?,?,?)',
        values: [tenantId, name, now],
      },
      {
        sql: 'INSERT INTO invites(hash,tenant_id,expires_at) VALUES(?,?,?)',
        values: [hash, tenantId, now + 86400],
      },
    ])
  }
  async exchangeInvite(hash: string, sessionHash: string, now: number) {
    await this.db.batch([
      {
        sql: 'INSERT INTO sessions(hash,tenant_id,expires_at) SELECT ?,tenant_id,? FROM invites WHERE hash=? AND used_at IS NULL AND expires_at>?',
        values: [sessionHash, now + 7 * 86400, hash, now],
      },
      {
        sql: 'UPDATE invites SET used_at=? WHERE hash=? AND used_at IS NULL AND expires_at>? AND EXISTS(SELECT 1 FROM sessions WHERE hash=?)',
        values: [now, hash, now, sessionHash],
      },
    ])
    const account = await this.session(sessionHash, now)
    requireCondition(
      account,
      401,
      'The invitation has expired or was already used.',
    )
    return account
  }
  async issueReturnInvite(tenantId: string, hash: string, now: number) {
    requireCondition(await this.tenant(tenantId), 404, 'Studio not found.')
    await this.db.run(
      'INSERT INTO invites(hash,tenant_id,expires_at) VALUES(?,?,?)',
      [hash, tenantId, now + 86400],
    )
  }
  async artist(tenantId: string) {
    const row = nullable(ArtistRow)(
      await this.db.first(
        'SELECT profile_json,revision,updated_at FROM artist_profiles WHERE tenant_id=?',
        [tenantId],
      ),
    )
    return row
      ? {
          profile: Schema.decodeUnknownSync(ArtistProfile)(
            JSON.parse(row.profile_json),
          ),
          revision: row.revision,
          updatedAt: row.updated_at,
        }
      : null
  }
  async saveArtist(
    tenantId: string,
    profile: ArtistProfile,
    expectedRevision: number,
    now: number,
  ) {
    const row = nullable(ArtistRow)(
      await this.db.first(
        expectedRevision === 0
          ? 'INSERT INTO artist_profiles(tenant_id,profile_json,revision,updated_at) VALUES(?,?,1,?) ON CONFLICT(tenant_id) DO NOTHING RETURNING profile_json,revision,updated_at'
          : 'UPDATE artist_profiles SET profile_json=?,revision=revision+1,updated_at=? WHERE tenant_id=? AND revision=? RETURNING profile_json,revision,updated_at',
        expectedRevision === 0
          ? [tenantId, JSON.stringify(profile), now]
          : [JSON.stringify(profile), now, tenantId, expectedRevision],
      ),
    )
    requireCondition(
      row,
      409,
      'Artist identity changed in another tab. Reload the studio identity before saving again.',
    )
    return {
      profile: Schema.decodeUnknownSync(ArtistProfile)(
        JSON.parse(row.profile_json),
      ),
      revision: row.revision,
      updatedAt: row.updated_at,
    }
  }
  async tenant(id: string) {
    return nullable(TenantRow)(
      await this.db.first('SELECT id,name FROM tenants WHERE id=?', [id]),
    )
  }
  async session(hash: string, now: number) {
    return nullable(TenantRow)(
      await this.db.first(
        'SELECT t.id,t.name FROM sessions s JOIN tenants t ON t.id=s.tenant_id WHERE s.hash=? AND s.expires_at>?',
        [hash, now],
      ),
    )
  }
  async logout(hash: string) {
    await this.db.run('DELETE FROM sessions WHERE hash=?', [hash])
  }
  async enroll(id: string, hash: string, name: string) {
    await this.db.run('INSERT INTO devices(id,token_hash,name) VALUES(?,?,?)', [
      id,
      hash,
      name,
    ])
  }
  async revokeDevice(id: string) {
    const device = nullable(DeviceRow)(
      await this.db.first(
        'UPDATE devices SET enabled=0 WHERE id=? RETURNING id,name',
        [id],
      ),
    )
    requireCondition(device, 404, 'Worker device not found.')
    return device
  }
  async device(hash: string, now: number) {
    const row = nullable(DeviceRow)(
      await this.db.first(
        'UPDATE devices SET last_seen_at=? WHERE token_hash=? AND enabled=1 RETURNING id,name',
        [now, hash],
      ),
    )
    return row
  }
  async createRelease(
    tenantId: string,
    id: string,
    requestKey: string,
    brief: ReleaseBrief,
    now: number,
  ) {
    await this.db.run(
      'INSERT INTO releases(id,tenant_id,request_key,brief_json,created_at) VALUES(?,?,?,?,?) ON CONFLICT(tenant_id,request_key) DO NOTHING',
      [id, tenantId, requestKey, JSON.stringify(brief), now],
    )
    const row = nullable(ReleaseRow)(
      await this.db.first(
        'SELECT * FROM releases WHERE tenant_id=? AND request_key=?',
        [tenantId, requestKey],
      ),
    )
    requireCondition(row, 500, 'The release could not be saved.')
    requireCondition(
      row.brief_json === JSON.stringify(brief),
      409,
      'This request key belongs to a different brief.',
    )
    return row
  }
  async release(tenantId: string, id: string) {
    return nullable(ReleaseRow)(
      await this.db.first('SELECT * FROM releases WHERE tenant_id=? AND id=?', [
        tenantId,
        id,
      ]),
    )
  }
  async releaseById(id: string) {
    return nullable(ReleaseRow)(
      await this.db.first('SELECT * FROM releases WHERE id=?', [id]),
    )
  }
  async list(tenantId: string) {
    return (
      await this.db.all(
        'SELECT * FROM releases WHERE tenant_id=? ORDER BY created_at DESC LIMIT 100',
        [tenantId],
      )
    ).map(value => Schema.decodeUnknownSync(ReleaseRow)(value))
  }
  async jobForRelease(id: string) {
    return nullable(JobRow)(
      await this.db.first('SELECT * FROM jobs WHERE release_id=?', [id]),
    )
  }
  async asset(id: string) {
    return nullable(AssetRow)(
      await this.db.first('SELECT * FROM assets WHERE id=?', [id]),
    )
  }
  async audio(id: string) {
    return nullable(AssetRow)(
      await this.db.first(
        "SELECT * FROM assets WHERE release_id=? AND kind='audio'",
        [id],
      ),
    )
  }
  async assets(id: string) {
    return (
      await this.db.all(
        'SELECT * FROM assets WHERE release_id=? ORDER BY created_at',
        [id],
      )
    ).map(value => Schema.decodeUnknownSync(AssetRow)(value))
  }
  async insertAsset(asset: AssetRow) {
    await this.db.run(
      'INSERT INTO assets(id,release_id,job_id,attempt,kind,output_id,object_key,bytes,sha256,content_type,upload_id,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',
      [
        asset.id,
        asset.release_id,
        asset.job_id,
        asset.attempt,
        asset.kind,
        asset.output_id,
        asset.object_key,
        asset.bytes,
        asset.sha256,
        asset.content_type,
        asset.upload_id,
        asset.created_at,
      ],
    )
  }
  async markUploaded(id: string, verified: boolean) {
    await this.db.run(
      "UPDATE assets SET state='uploaded', verified=? WHERE id=?",
      [verified ? 1 : 0, id],
    )
  }
  async startRelease(id: string, jobId: string, now: number) {
    const audio = await this.audio(id)
    requireCondition(
      audio?.state === 'uploaded' && audio.verified === 1,
      409,
      'Upload and verify the canonical audio first.',
    )
    await this.db.batch([
      {
        sql: 'INSERT INTO jobs(id,release_id,created_at,updated_at) VALUES(?,?,?,?) ON CONFLICT(release_id) DO NOTHING',
        values: [jobId, id, now, now],
      },
      {
        sql: "UPDATE releases SET state='queued' WHERE id=? AND state='uploading'",
        values: [id],
      },
    ])
    return this.jobForRelease(id)
  }
  async claim(deviceId: string, leaseHash: string, now: number) {
    const job = nullable(JobRow)(
      await this.db.first(
        "UPDATE jobs SET state='running',device_id=?,lease_hash=?,lease_until=?,attempt=attempt+1,phase='Preparing production',progress=0,updated_at=? WHERE id=(SELECT id FROM jobs WHERE state='queued' OR (state='running' AND lease_until<?) ORDER BY created_at LIMIT 1) AND (state='queued' OR (state='running' AND lease_until<?)) RETURNING *",
        [deviceId, leaseHash, now + 180, now, now, now],
      ),
    )
    if (job)
      await this.db.run(
        "UPDATE releases SET state='running' WHERE id=? AND EXISTS(SELECT 1 FROM jobs WHERE id=? AND state='running' AND lease_hash=?)",
        [job.release_id, job.id, leaseHash],
      )
    return job
  }
  async holds(deviceId: string) {
    return (
      await this.db.all(
        "SELECT * FROM jobs WHERE device_id=? AND state IN ('waiting-for-direction','waiting-for-review','needs-reconciliation') ORDER BY updated_at LIMIT 100",
        [deviceId],
      )
    ).map(value => Schema.decodeUnknownSync(JobRow)(value))
  }
  async ownedJob(jobId: string, deviceId: string) {
    return nullable(JobRow)(
      await this.db.first('SELECT * FROM jobs WHERE id=? AND device_id=?', [
        jobId,
        deviceId,
      ]),
    )
  }
  async resumable(jobId: string, deviceId: string) {
    const job = nullable(JobRow)(
      await this.db.first(
        "SELECT * FROM jobs WHERE id=? AND device_id=? AND state IN ('waiting-for-direction','waiting-for-review')",
        [jobId, deviceId],
      ),
    )
    requireCondition(
      job,
      409,
      'The job is not a direction or review hold owned by this worker.',
    )
    return job
  }
  async hold(
    job: JobRow,
    leaseHash: string,
    reason: HoldReason,
    receipt: unknown,
    now: number,
  ) {
    const phase = {
      'waiting-for-direction': 'Preparing the production direction',
      'waiting-for-review': 'Reviewing the motion pilot',
      'needs-reconciliation': 'Production needs attention',
    }[reason]
    try {
      await this.db.batch([
        {
          sql: "INSERT INTO job_events(job_id,attempt,phase,detail_json,created_at) VALUES((SELECT id FROM jobs WHERE id=? AND state='running' AND lease_hash=? AND lease_until>?),?,?,?,?)",
          values: [
            job.id,
            leaseHash,
            now,
            job.attempt,
            phase,
            JSON.stringify(receipt),
            now,
          ],
        },
        {
          sql: 'UPDATE jobs SET state=?,phase=?,receipt_json=?,lease_hash=NULL,lease_until=NULL,updated_at=? WHERE id=?',
          values: [reason, phase, JSON.stringify(receipt), now, job.id],
        },
        {
          sql: 'UPDATE releases SET state=? WHERE id=?',
          values: [reason, job.release_id],
        },
      ])
    } catch {
      throw new ApiError(
        409,
        'The hold was not committed; reconcile the current job ownership.',
      )
    }
  }
  async resume(job: JobRow, deviceId: string, receipt: unknown, now: number) {
    try {
      await this.db.batch([
        {
          sql: "INSERT INTO job_events(job_id,attempt,phase,detail_json,created_at) VALUES((SELECT id FROM jobs WHERE id=? AND device_id=? AND state IN ('waiting-for-direction','waiting-for-review')),?,?,?,?)",
          values: [
            job.id,
            deviceId,
            job.attempt,
            'Production plan registered',
            JSON.stringify(receipt),
            now,
          ],
        },
        {
          sql: "UPDATE jobs SET state='queued',device_id=NULL,lease_hash=NULL,lease_until=NULL,phase='Waiting for workstation',error=NULL,updated_at=? WHERE id=?",
          values: [now, job.id],
        },
        {
          sql: "UPDATE releases SET state='queued' WHERE id=?",
          values: [job.release_id],
        },
      ])
    } catch {
      throw new ApiError(
        409,
        'The resume was not committed; reconcile the current hold.',
      )
    }
  }
  async lease(jobId: string, deviceId: string, leaseHash: string, now: number) {
    const job = nullable(JobRow)(
      await this.db.first(
        "SELECT * FROM jobs WHERE id=? AND state='running' AND device_id=? AND lease_hash=? AND lease_until>?",
        [jobId, deviceId, leaseHash, now],
      ),
    )
    requireCondition(
      job,
      409,
      'The production lease expired or belongs to another attempt.',
    )
    return job
  }
  async heartbeat(
    job: JobRow,
    leaseHash: string,
    phase: string,
    progress: number,
    receipt: unknown,
    now: number,
  ) {
    const updated = nullable(JobRow)(
      await this.db.first(
        "UPDATE jobs SET lease_until=?,phase=?,progress=?,receipt_json=?,updated_at=? WHERE id=? AND state='running' AND lease_hash=? AND lease_until>? RETURNING *",
        [
          now + 180,
          phase,
          progress,
          JSON.stringify(receipt),
          now,
          job.id,
          leaseHash,
          now,
        ],
      ),
    )
    requireCondition(updated, 409, 'The production lease expired.')
    await this.db.run(
      'INSERT INTO job_events(job_id,attempt,phase,detail_json,created_at) VALUES(?,?,?,?,?)',
      [job.id, job.attempt, phase, JSON.stringify(receipt), now],
    )
    return updated
  }
  async part(
    assetId: string,
    number: number,
    etag: string,
    bytes: number,
    sha256: string,
  ) {
    await this.db.run(
      'INSERT INTO asset_parts(asset_id,part_number,etag,bytes,sha256) VALUES(?,?,?,?,?) ON CONFLICT(asset_id,part_number) DO UPDATE SET etag=excluded.etag,bytes=excluded.bytes,sha256=excluded.sha256',
      [assetId, number, etag, bytes, sha256],
    )
  }
  async parts(assetId: string) {
    return (
      await this.db.all(
        'SELECT part_number,etag,bytes,sha256 FROM asset_parts WHERE asset_id=? ORDER BY part_number',
        [assetId],
      )
    ).map(value => Schema.decodeUnknownSync(PartRow)(value))
  }
  async complete(
    job: JobRow,
    leaseHash: string,
    measured: Array<{ asset: AssetRow; measurement: Measurement }>,
    receipt: unknown,
    now: number,
  ) {
    requireCondition(
      measured.length === outputs.length &&
        outputs.every(
          output =>
            measured.filter(m => m.asset.output_id === output.id).length === 1,
        ),
      409,
      'All six unique outputs are required before review.',
    )
    const eligible = measured.every(
      m =>
        m.asset.job_id === job.id &&
        m.asset.attempt === job.attempt &&
        m.asset.state === 'uploaded' &&
        m.asset.sha256 === m.measurement.sha256,
    )
    requireCondition(
      eligible,
      409,
      'Outputs must belong to this attempt and match their hashes.',
    )
    try {
      await this.db.batch([
        {
          sql: "INSERT INTO completions(job_id,attempt,created_at) VALUES((SELECT id FROM jobs WHERE id=? AND state='running' AND lease_hash=? AND lease_until>?),?,?)",
          values: [job.id, leaseHash, now, job.attempt, now],
        },
        ...measured.map(m => ({
          sql: "UPDATE assets SET state='ready',verified=1,measurement_json=? WHERE id=?",
          values: [JSON.stringify(m.measurement), m.asset.id],
        })),
        {
          sql: "UPDATE jobs SET state='review',phase='Ready for review',progress=1,receipt_json=?,updated_at=? WHERE id=?",
          values: [JSON.stringify(receipt), now, job.id],
        },
        {
          sql: "UPDATE releases SET state='review' WHERE id=?",
          values: [job.release_id],
        },
      ])
    } catch {
      throw new ApiError(
        409,
        'Completion transaction was not committed; preserve outputs and reconcile the job before retrying.',
      )
    }
  }
  async fail(job: JobRow, leaseHash: string, reason: string, now: number) {
    const result = await this.db.first(
      "UPDATE jobs SET state='failed',error=?,phase='Needs attention',updated_at=? WHERE id=? AND state='running' AND lease_hash=? AND lease_until>? RETURNING id",
      [reason, now, job.id, leaseHash, now],
    )
    requireCondition(result, 409, 'The production lease expired.')
    await this.db.run("UPDATE releases SET state='failed' WHERE id=?", [
      job.release_id,
    ])
  }
}
