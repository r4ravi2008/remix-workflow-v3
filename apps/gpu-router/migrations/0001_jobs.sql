CREATE TABLE IF NOT EXISTS api_keys (
  token_hash TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  enabled INTEGER NOT NULL DEFAULT 1 CHECK (enabled IN (0, 1))
);
CREATE TABLE IF NOT EXISTS jobs (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  intent_id TEXT NOT NULL,
  fingerprint TEXT NOT NULL,
  version INTEGER NOT NULL,
  active INTEGER NOT NULL CHECK (active IN (0, 1)),
  document_json TEXT NOT NULL,
  UNIQUE (tenant_id, intent_id)
);
CREATE INDEX IF NOT EXISTS jobs_active ON jobs(active, id);
