CREATE TABLE editor_capacity (
  slot TEXT PRIMARY KEY CHECK(slot='native-renderer'),
  tenant_id TEXT NOT NULL,
  job_id TEXT NOT NULL REFERENCES editor_jobs(id),
  fingerprint TEXT NOT NULL,
  purpose TEXT NOT NULL CHECK(purpose IN ('render','verify')),
  token TEXT NOT NULL UNIQUE,
  started_at INTEGER NOT NULL
);
CREATE TABLE editor_capacity_cursor (
  slot TEXT PRIMARY KEY CHECK(slot='native-renderer'),
  last_tenant TEXT NOT NULL
);
INSERT INTO editor_capacity_cursor(slot,last_tenant) VALUES('native-renderer','');
CREATE TABLE editor_capacity_waiters (
  sequence INTEGER PRIMARY KEY AUTOINCREMENT,
  job_id TEXT NOT NULL UNIQUE REFERENCES editor_jobs(id),
  tenant_id TEXT NOT NULL,
  fingerprint TEXT NOT NULL
);
CREATE INDEX editor_queued_order ON editor_jobs(state,tenant_id,created_at,id);
