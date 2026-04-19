const fs = require('node:fs');
const path = require('node:path');

const CONFIG_FILE = '.remix-workspace-root.json';

function findRepoRoot(startDir = __dirname) {
  let currentDir = startDir;

  while (true) {
    if (fs.existsSync(path.join(currentDir, '.git'))) {
      return currentDir;
    }

    const parentDir = path.dirname(currentDir);
    if (parentDir === currentDir) {
      throw new Error(`Could not find repo root from ${startDir}`);
    }

    currentDir = parentDir;
  }
}

function readWorkspaceRootConfig(options = {}) {
  const repoRoot = options.repoRoot || findRepoRoot(options.startDir || __dirname);
  const configPath = path.join(repoRoot, CONFIG_FILE);

  if (!fs.existsSync(configPath)) {
    throw new Error(`Missing workspace root config at ${configPath}. Copy .remix-workspace-root.example.json to .remix-workspace-root.json and set workspaceRoot.`);
  }

  let config;
  try {
    config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  } catch (error) {
    throw new Error(`Failed to parse ${configPath}: ${error.message}`);
  }

  if (typeof config.workspaceRoot !== 'string' || config.workspaceRoot.trim() === '') {
    throw new Error(`Invalid ${configPath}: expected a non-empty workspaceRoot string.`);
  }

  const workspaceRoot = path.resolve(config.workspaceRoot);

  let stats;
  try {
    stats = fs.statSync(workspaceRoot);
  } catch {
    throw new Error(`Configured workspace root does not exist: ${workspaceRoot}`);
  }

  if (!stats.isDirectory()) {
    throw new Error(`Configured workspace root does not exist: ${workspaceRoot}`);
  }

  return {repoRoot, configPath, workspaceRoot};
}

function resolveWorkspaceDir(workspaceSlug, options = {}) {
  if (typeof workspaceSlug !== 'string' || workspaceSlug.trim() === '') {
    throw new Error('Workspace slug is required.');
  }

  const config = readWorkspaceRootConfig(options);

  return {
    ...config,
    workspaceDir: path.join(config.workspaceRoot, workspaceSlug),
  };
}

module.exports = {
  CONFIG_FILE,
  findRepoRoot,
  readWorkspaceRootConfig,
  resolveWorkspaceDir,
};
