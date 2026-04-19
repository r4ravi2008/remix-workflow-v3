const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const {
  readWorkspaceRootConfig,
  resolveWorkspaceDir,
} = require('./workspace-root');

function makeRepoFixture() {
  const repoRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'workspace-root-repo-'));
  fs.mkdirSync(path.join(repoRoot, '.git'));
  return repoRoot;
}

test('reads workspaceRoot from repo-local config', () => {
  const repoRoot = makeRepoFixture();
  const workspaceRoot = path.join(repoRoot, 'icloud-root');
  fs.mkdirSync(workspaceRoot);
  fs.writeFileSync(
    path.join(repoRoot, '.remix-workspace-root.json'),
    JSON.stringify({workspaceRoot}, null, 2)
  );

  const result = readWorkspaceRootConfig({repoRoot});

  assert.equal(result.repoRoot, repoRoot);
  assert.equal(result.workspaceRoot, workspaceRoot);
  assert.equal(
    result.configPath,
    path.join(repoRoot, '.remix-workspace-root.json')
  );
});

test('throws a clear error when the local config file is missing', () => {
  const repoRoot = makeRepoFixture();

  assert.throws(
    () => readWorkspaceRootConfig({repoRoot}),
    /Missing workspace root config/
  );
});

test('throws a clear error when workspaceRoot does not exist', () => {
  const repoRoot = makeRepoFixture();
  fs.writeFileSync(
    path.join(repoRoot, '.remix-workspace-root.json'),
    JSON.stringify({workspaceRoot: path.join(repoRoot, 'missing-root')}, null, 2)
  );

  assert.throws(
    () => readWorkspaceRootConfig({repoRoot}),
    /Configured workspace root does not exist/
  );
});

test('resolves a workspace slug to an absolute workspace directory', () => {
  const repoRoot = makeRepoFixture();
  const workspaceRoot = path.join(repoRoot, 'icloud-root');
  fs.mkdirSync(workspaceRoot);
  fs.writeFileSync(
    path.join(repoRoot, '.remix-workspace-root.json'),
    JSON.stringify({workspaceRoot}, null, 2)
  );

  const result = resolveWorkspaceDir('bella-bella-lofi', {repoRoot});

  assert.equal(result.workspaceDir, path.join(workspaceRoot, 'bella-bella-lofi'));
});

test('rejects workspace slugs that are not lowercase hyphenated names', () => {
  const repoRoot = makeRepoFixture();
  const workspaceRoot = path.join(repoRoot, 'icloud-root');
  fs.mkdirSync(workspaceRoot);
  fs.writeFileSync(
    path.join(repoRoot, '.remix-workspace-root.json'),
    JSON.stringify({workspaceRoot}, null, 2)
  );

  assert.throws(
    () => resolveWorkspaceDir('../other-dir', {repoRoot}),
    /Workspace slug must be lowercase hyphenated/
  );
});
