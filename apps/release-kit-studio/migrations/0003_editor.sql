CREATE TABLE editor_projects (
  tenant_id TEXT NOT NULL REFERENCES tenants(id),
  id TEXT NOT NULL,
  release_id TEXT NOT NULL REFERENCES releases(id),
  revision INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY(tenant_id,id)
);
CREATE TABLE editor_revisions (
  tenant_id TEXT NOT NULL,
  project_id TEXT NOT NULL,
  revision INTEGER NOT NULL,
  intent_id TEXT NOT NULL,
  fingerprint TEXT NOT NULL,
  document_json TEXT NOT NULL,
  created_at INTEGER NOT NULL,
  PRIMARY KEY(tenant_id,project_id,revision),
  FOREIGN KEY(tenant_id,project_id) REFERENCES editor_projects(tenant_id,id)
);
CREATE TABLE editor_intents (
  tenant_id TEXT NOT NULL,
  id TEXT NOT NULL,
  fingerprint TEXT NOT NULL,
  result_json TEXT NOT NULL,
  PRIMARY KEY(tenant_id,id)
);
CREATE TABLE editor_tokens (
  hash TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL REFERENCES tenants(id),
  expires_at INTEGER NOT NULL,
  enabled INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE editor_assets (
  tenant_id TEXT NOT NULL REFERENCES tenants(id),
  id TEXT NOT NULL,
  metadata_json TEXT NOT NULL,
  object_key TEXT NOT NULL,
  uploaded INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY(tenant_id,id)
);
CREATE TABLE editor_jobs (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  release_id TEXT NOT NULL,
  project_id TEXT NOT NULL,
  revision INTEGER NOT NULL,
  intent_id TEXT NOT NULL,
  fingerprint TEXT NOT NULL,
  request_json TEXT NOT NULL,
  state TEXT NOT NULL,
  progress_json TEXT NOT NULL,
  receipt_json TEXT,
  error TEXT,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL,
  UNIQUE(tenant_id,intent_id),
  FOREIGN KEY(tenant_id,project_id,revision) REFERENCES editor_revisions(tenant_id,project_id,revision)
);
CREATE UNIQUE INDEX editor_one_active_render ON editor_jobs(tenant_id,release_id)
WHERE state IN ('queued','staging','running','verifying','cancel-requested','uncertain');
CREATE TABLE editor_reviews (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  job_id TEXT NOT NULL REFERENCES editor_jobs(id),
  output_id TEXT NOT NULL,
  sha256 TEXT NOT NULL,
  kind TEXT NOT NULL,
  detail_json TEXT NOT NULL,
  created_at INTEGER NOT NULL
);
