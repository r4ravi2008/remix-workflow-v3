PRAGMA foreign_keys = ON;
CREATE TABLE tenants (id TEXT PRIMARY KEY, name TEXT NOT NULL, created_at INTEGER NOT NULL);
CREATE TABLE invites (hash TEXT PRIMARY KEY, tenant_id TEXT NOT NULL REFERENCES tenants(id), expires_at INTEGER NOT NULL, used_at INTEGER);
CREATE TABLE sessions (hash TEXT PRIMARY KEY, tenant_id TEXT NOT NULL REFERENCES tenants(id), expires_at INTEGER NOT NULL);
CREATE TABLE devices (id TEXT PRIMARY KEY, token_hash TEXT UNIQUE NOT NULL, name TEXT NOT NULL, enabled INTEGER NOT NULL DEFAULT 1, last_seen_at INTEGER);
CREATE TABLE releases (
 id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL REFERENCES tenants(id), request_key TEXT NOT NULL,
 brief_json TEXT NOT NULL, state TEXT NOT NULL DEFAULT 'uploading', created_at INTEGER NOT NULL,
 UNIQUE(tenant_id, request_key)
);
CREATE TABLE jobs (
 id TEXT PRIMARY KEY, release_id TEXT NOT NULL UNIQUE REFERENCES releases(id), state TEXT NOT NULL DEFAULT 'queued',
 device_id TEXT REFERENCES devices(id), lease_hash TEXT, lease_until INTEGER, attempt INTEGER NOT NULL DEFAULT 0,
 phase TEXT NOT NULL DEFAULT 'Waiting for workstation', progress REAL NOT NULL DEFAULT 0,
 receipt_json TEXT, error TEXT, created_at INTEGER NOT NULL, updated_at INTEGER NOT NULL
);
CREATE INDEX jobs_claim ON jobs(state, lease_until, created_at);
CREATE TABLE job_events (id INTEGER PRIMARY KEY AUTOINCREMENT, job_id TEXT NOT NULL REFERENCES jobs(id), attempt INTEGER NOT NULL, phase TEXT NOT NULL, detail_json TEXT NOT NULL, created_at INTEGER NOT NULL);
CREATE TABLE assets (
 id TEXT PRIMARY KEY, release_id TEXT NOT NULL REFERENCES releases(id), job_id TEXT REFERENCES jobs(id),
 attempt INTEGER, kind TEXT NOT NULL, output_id TEXT, object_key TEXT NOT NULL UNIQUE,
 bytes INTEGER NOT NULL, sha256 TEXT NOT NULL, content_type TEXT NOT NULL, state TEXT NOT NULL DEFAULT 'uploading',
 upload_id TEXT, verified INTEGER NOT NULL DEFAULT 0, measurement_json TEXT, created_at INTEGER NOT NULL
);
CREATE UNIQUE INDEX release_audio ON assets(release_id) WHERE kind = 'audio';
CREATE INDEX release_outputs ON assets(release_id, output_id, state);
CREATE TABLE asset_parts (asset_id TEXT NOT NULL REFERENCES assets(id), part_number INTEGER NOT NULL, etag TEXT NOT NULL, bytes INTEGER NOT NULL, sha256 TEXT NOT NULL, PRIMARY KEY(asset_id, part_number));
CREATE TABLE completions (job_id TEXT NOT NULL PRIMARY KEY REFERENCES jobs(id), attempt INTEGER NOT NULL, created_at INTEGER NOT NULL);
