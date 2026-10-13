CREATE TABLE artist_profiles (
 tenant_id TEXT NOT NULL PRIMARY KEY REFERENCES tenants(id),
 profile_json TEXT NOT NULL, revision INTEGER NOT NULL DEFAULT 1,
 updated_at INTEGER NOT NULL
);
