# Workspace Root Configuration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace repo-local `workspaces/<slug>/` storage with a machine-local configured workspace root while keeping `meta.json` paths portable across machines.

**Architecture:** Add one repo-local JSON config file plus a shared CommonJS resolver that reads and validates it. Update `tools/video-generator/init-video.js` to use the resolver, then sweep the operational prompts and docs so filesystem actions resolve against `<workspaceRoot>/<slug>/` at runtime while `meta.json` stores root-relative paths like `<slug>/design.json`.

**Tech Stack:** Markdown prompt docs, CommonJS Node.js scripts, Node built-in `node:test`, gitignored local config, ripgrep for verification.

---

## File Map

| File | Responsibility |
|---|---|
| `.gitignore` | Ignore the real local workspace-root config file |
| `.remix-workspace-root.example.json` | Tracked example config that users copy after cloning |
| `tools/shared/workspace-root.js` | Shared Node helper to locate repo root, read config, validate `workspaceRoot`, and resolve `<workspaceRoot>/<slug>` |
| `tools/shared/workspace-root.test.js` | Unit tests for missing config, invalid root, and slug resolution |
| `tools/video-generator/init-video.js` | Read workspace root from config, scaffold video project in external workspace, export testable functions |
| `tools/video-generator/init-video.test.js` | Integration-style tests for scaffolding into an external workspace root |
| `tools/video-generator/README.md` | Update setup and usage examples to the configured workspace-root model |
| `prompts/references/workspace-conventions.md` | Canonical workspace-root config rules, root-relative `meta.json` schema, updated directory structure |
| `prompts/step-0-prepare-workspace.md` | Validate local config first, create `<workspaceRoot>/<slug>/`, write root-relative `meta.json` |
| `prompts/README.md` | Update pipeline overview and key conventions to the configured workspace-root model |
| `prompts/references/acapella-extractor-usage.md` | Replace repo-root path examples with resolved workspace-dir examples |
| `prompts/references/error-handling-patterns.md` | Replace repo-root permission/path fixes with configured-root fixes |
| `prompts/step-1-download-mp3.md` | Use resolved workspace directory and root-relative metadata examples |
| `prompts/step-2-extract-acapella.md` | Same path model update |
| `prompts/step-3-find-lyrics.md` | Same path model update |
| `prompts/step-4-generate-suno-lyrics.md` | Same path model update |
| `prompts/step-5-upload-to-suno.md` | Same path model update |
| `prompts/step-6-extract-acapella-and-align.md` | Same path model update |
| `prompts/step-7-fetch-cover-art.md` | Same path model update |
| `prompts/step-8-generate-video.md` | Same path model update, including `init-video.js` examples |
| `prompts/step-9-generate-youtube-metadata.md` | Same path model update |
| `prompts/step-10-select-short-clip.md` | Same path model update |
| `prompts/step-11-generate-short-video.md` | Same path model update |
| `README.md` | Update top-level setup and workspace descriptions |
| `AGENTS.md` | Update agent guidance so workspace state points to configured external root |

---

### Task 1: Add Local Config Scaffold And Shared Resolver

**Files:**
- Create: `.remix-workspace-root.example.json`
- Create: `tools/shared/workspace-root.js`
- Test: `tools/shared/workspace-root.test.js`
- Modify: `.gitignore`

- [ ] **Step 1: Write the failing resolver test**

Create `tools/shared/workspace-root.test.js` with this exact content:

```js
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
```

- [ ] **Step 2: Run the resolver test to verify it fails**

Run: `node --test tools/shared/workspace-root.test.js`

Expected: FAIL with `Cannot find module './workspace-root'`.

- [ ] **Step 3: Write the minimal resolver and config scaffold**

Create `.remix-workspace-root.example.json` with this exact content:

```json
{
  "workspaceRoot": "/Users/you/Library/Mobile Documents/com~apple~CloudDocs/remix-workspaces"
}
```

Update `.gitignore` by adding this exact line directly after `workspaces/`:

```gitignore
.remix-workspace-root.json
```

Create `tools/shared/workspace-root.js` with this exact content:

```js
const fs = require('node:fs');
const path = require('node:path');

const CONFIG_FILE = '.remix-workspace-root.json';

function findRepoRoot(startDir = __dirname) {
  let currentDir = path.resolve(startDir);

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
    throw new Error(
      `Missing workspace root config at ${configPath}. Copy .remix-workspace-root.example.json to .remix-workspace-root.json and set workspaceRoot.`
    );
  }

  let parsed;
  try {
    parsed = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  } catch (error) {
    throw new Error(`Failed to parse ${configPath}: ${error.message}`);
  }

  if (!parsed || typeof parsed.workspaceRoot !== 'string' || !parsed.workspaceRoot.trim()) {
    throw new Error(`Invalid ${configPath}: expected a non-empty workspaceRoot string.`);
  }

  const workspaceRoot = path.resolve(parsed.workspaceRoot);
  if (!fs.existsSync(workspaceRoot) || !fs.statSync(workspaceRoot).isDirectory()) {
    throw new Error(`Configured workspace root does not exist: ${workspaceRoot}`);
  }

  return {
    repoRoot,
    configPath,
    workspaceRoot,
  };
}

function resolveWorkspaceDir(workspaceSlug, options = {}) {
  if (typeof workspaceSlug !== 'string' || !workspaceSlug.trim()) {
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
```

- [ ] **Step 4: Run the resolver test to verify it passes**

Run: `node --test tools/shared/workspace-root.test.js`

Expected: PASS with 4 passing tests.

- [ ] **Step 5: Commit**

```bash
git add .gitignore .remix-workspace-root.example.json tools/shared/workspace-root.js tools/shared/workspace-root.test.js
git commit -m "feat: add local workspace root resolver"
```

### Task 2: Update The Video Scaffolder To Use The Configured Workspace Root

**Files:**
- Modify: `tools/video-generator/init-video.js`
- Create: `tools/video-generator/init-video.test.js`
- Test: `tools/shared/workspace-root.test.js`
- Test: `tools/video-generator/init-video.test.js`

- [ ] **Step 1: Write the failing video scaffolder tests**

Create `tools/video-generator/init-video.test.js` with this exact content:

```js
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const {initializeVideoProject} = require('./init-video');

function makeFixture() {
  const repoRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'init-video-repo-'));
  fs.mkdirSync(path.join(repoRoot, '.git'));

  const workspaceRoot = path.join(repoRoot, 'icloud-root');
  const workspaceSlug = 'bella-bella-lofi';
  const workspaceDir = path.join(workspaceRoot, workspaceSlug);
  const templateDir = path.join(repoRoot, 'template');

  fs.mkdirSync(workspaceRoot);
  fs.mkdirSync(workspaceDir, {recursive: true});
  fs.mkdirSync(path.join(templateDir, 'src'), {recursive: true});
  fs.writeFileSync(path.join(templateDir, 'package.json'), '{"name":"fixture-template"}');
  fs.writeFileSync(path.join(templateDir, 'src', 'index.tsx'), 'export {};');
  fs.writeFileSync(
    path.join(repoRoot, '.remix-workspace-root.json'),
    JSON.stringify({workspaceRoot}, null, 2)
  );
  fs.writeFileSync(
    path.join(workspaceDir, 'meta.json'),
    JSON.stringify({video_title: 'Bella Bella', genre: 'Lo-Fi'}, null, 2)
  );
  fs.writeFileSync(path.join(workspaceDir, `${workspaceSlug}-remix-v1.mp3`), 'fake mp3');
  fs.writeFileSync(path.join(workspaceDir, 'design.json'), JSON.stringify({layout: {variant: 'cover-art'}}, null, 2));

  return {repoRoot, workspaceSlug, workspaceDir, templateDir};
}

test('scaffolds the video project inside the configured workspace root', () => {
  const fixture = makeFixture();

  const result = initializeVideoProject({
    workspaceSlug: fixture.workspaceSlug,
    designPath: path.join(fixture.workspaceDir, 'design.json'),
    repoRoot: fixture.repoRoot,
    templateDir: fixture.templateDir,
    execSyncImpl: () => '180.25',
    logger: {log() {}, warn() {}, error() {}},
    processCwd: fixture.repoRoot,
  });

  assert.equal(result.videoDir, path.join(fixture.workspaceDir, 'video'));
  assert.ok(fs.existsSync(path.join(result.videoDir, 'public', 'video-config.json')));
  assert.ok(fs.existsSync(path.join(result.videoDir, 'public', 'design.json')));
});

test('throws a clear error when the slug workspace does not exist', () => {
  const fixture = makeFixture();

  assert.throws(
    () => initializeVideoProject({
      workspaceSlug: 'missing-slug',
      repoRoot: fixture.repoRoot,
      templateDir: fixture.templateDir,
      execSyncImpl: () => '180.25',
      logger: {log() {}, warn() {}, error() {}},
      processCwd: fixture.repoRoot,
    }),
    /Workspace "missing-slug" not found/
  );
});
```

- [ ] **Step 2: Run the video scaffolder tests to verify they fail**

Run: `node --test tools/video-generator/init-video.test.js`

Expected: FAIL with `initializeVideoProject is not a function`.

- [ ] **Step 3: Refactor `init-video.js` into a testable workspace-root-aware module**

Replace the contents of `tools/video-generator/init-video.js` with this exact code:

```js
#!/usr/bin/env node
const fs = require('node:fs');
const path = require('node:path');
const {execSync} = require('node:child_process');

const {resolveWorkspaceDir} = require('../shared/workspace-root');

function parseArgs(argv) {
  const workspaceSlug = argv[0];
  if (!workspaceSlug) {
    throw new Error('Usage: node init-video.js <workspace-slug> [--design=<path>]');
  }

  let designPath = null;
  argv.slice(1).forEach(arg => {
    if (arg.startsWith('--design=')) {
      designPath = arg.replace('--design=', '');
    }
  });

  return {workspaceSlug, designPath};
}

function initializeVideoProject(options) {
  const {
    workspaceSlug,
    designPath = null,
    repoRoot,
    templateDir = path.join(__dirname, 'template'),
    execSyncImpl = execSync,
    logger = console,
    processCwd = process.cwd(),
  } = options;

  const {workspaceDir, workspaceRoot} = resolveWorkspaceDir(workspaceSlug, {repoRoot});
  const videoDir = path.join(workspaceDir, 'video');

  if (!fs.existsSync(workspaceDir)) {
    throw new Error(`Workspace "${workspaceSlug}" not found at ${workspaceDir}`);
  }

  if (fs.existsSync(videoDir)) {
    throw new Error(`Video project already exists at ${videoDir}`);
  }

  const metadataPath = path.join(workspaceDir, 'meta.json');
  let songTitle = workspaceSlug;
  let genre = 'unknown';

  if (fs.existsSync(metadataPath)) {
    const meta = JSON.parse(fs.readFileSync(metadataPath, 'utf8'));
    songTitle = meta.video_title || meta.title || workspaceSlug;
    genre = meta.genre || 'unknown';
  }

  const audioFile = path.join(workspaceDir, `${workspaceSlug}-remix-v1.mp3`);
  let audioDuration = 180;

  if (fs.existsSync(audioFile)) {
    try {
      const raw = execSyncImpl(
        `ffprobe -i "${audioFile}" -show_entries format=duration -v quiet -of csv=p=0`,
        {encoding: 'utf8'}
      ).trim();
      const parsed = Number.parseFloat(raw);
      if (!Number.isNaN(parsed)) {
        audioDuration = parsed;
      }
      logger.log(`Audio duration: ${audioDuration.toFixed(3)}s`);
    } catch {
      logger.warn(`ffprobe failed. Defaulting to ${audioDuration}s. Edit video-config.json to fix.`);
    }
  } else {
    logger.warn(`Audio file not found: ${audioFile}`);
    logger.warn(`Defaulting to ${audioDuration}s. Edit video-config.json to fix.`);
  }

  logger.log(`Scaffolding video project for "${workspaceSlug}" in ${workspaceRoot}...`);
  fs.cpSync(templateDir, videoDir, {recursive: true});
  fs.mkdirSync(path.join(videoDir, 'public'), {recursive: true});

  const videoConfigPath = path.join(videoDir, 'public', 'video-config.json');
  fs.writeFileSync(
    videoConfigPath,
    JSON.stringify(
      {
        audioDuration: Number.parseFloat(audioDuration.toFixed(3)),
        songTitle,
        genre,
      },
      null,
      2
    )
  );

  if (designPath) {
    const designSourcePath = path.resolve(designPath);
    if (fs.existsSync(designSourcePath)) {
      fs.copyFileSync(designSourcePath, path.join(videoDir, 'public', 'design.json'));
    } else {
      logger.warn(`Design file not found: ${designSourcePath}`);
      logger.warn('Video will use default design settings.');
    }
  } else {
    logger.log('No design.json provided. Video will use default settings.');
  }

  logger.log(`Video project created at: ${videoDir}`);
  logger.log('Next steps:');
  logger.log(`  cd ${path.relative(processCwd, videoDir)} && npm install`);
  logger.log(`  cp "${path.join(workspaceDir, `${workspaceSlug}-remix-v1.mp3`)}" "${path.join(videoDir, 'public', 'audio.mp3')}"`);
  logger.log(`  cp "${path.join(workspaceDir, 'lyrics-timestamps.json')}" "${path.join(videoDir, 'public')}"`);
  logger.log('  npx remotion render MusicVideo out/video.mp4');

  return {workspaceDir, videoDir, videoConfigPath};
}

function main(argv = process.argv.slice(2)) {
  const {workspaceSlug, designPath} = parseArgs(argv);
  return initializeVideoProject({workspaceSlug, designPath});
}

if (require.main === module) {
  try {
    main();
  } catch (error) {
    console.error(error.message);
    process.exit(1);
  }
}

module.exports = {
  parseArgs,
  initializeVideoProject,
  main,
};
```

- [ ] **Step 4: Run the Node tests to verify they pass**

Run: `node --test tools/shared/workspace-root.test.js tools/video-generator/init-video.test.js`

Expected: PASS with 6 passing tests.

- [ ] **Step 5: Commit**

```bash
git add tools/video-generator/init-video.js tools/video-generator/init-video.test.js tools/shared/workspace-root.js tools/shared/workspace-root.test.js
git commit -m "feat: resolve video workspaces from local config"
```

### Task 3: Rewrite The Canonical Workspace Conventions And Step 0 Prompt

**Files:**
- Modify: `prompts/references/workspace-conventions.md`
- Modify: `prompts/step-0-prepare-workspace.md`
- Modify: `prompts/README.md`

- [ ] **Step 1: Replace the canonical workspace-root conventions**

In `prompts/references/workspace-conventions.md`, replace the existing directory-structure and `meta.json` path sections with this exact markdown block:

````md
## Workspace Root Configuration

Each cloned repo uses a local, untracked config file at the repo root:

```json
{
  "workspaceRoot": "/absolute/path/to/your/remix-workspaces"
}
```

- The file name is `.remix-workspace-root.json`.
- Copy it from `.remix-workspace-root.example.json` after cloning.
- `workspaceRoot` is the parent directory that contains all slug folders.
- If the file is missing, malformed, or points to a missing directory, stop and fix local setup before running any pipeline step.

## Directory Structure

```text
<workspaceRoot>/
└── <slug>/
    ├── meta.json
    ├── <slug>-original.mp3
    ├── <slug>-acapella.mp3
    ├── <slug>-lyrics.txt
    ├── <slug>-suno-lyrics.txt
    ├── <slug>-suno-style.txt
    ├── <slug>-remix-v1.mp3
    ├── <slug>-remix-v2.mp3
    ├── <slug>-remix-v1-acapella.mp3
    ├── lyrics-timestamps.json
    ├── <slug>-cover-art.jpg
    ├── <slug>-video.mp4
    ├── design.json
    ├── youtube-metadata.json
    ├── youtube-metadata-artifact.md
    ├── shorts-segments.json
    └── <slug>-short.mp4
```

## meta.json Schema

```json
{
  "youtube_url": "https://www.youtube.com/watch?v=...",
  "video_title": "Cleaned Video Title",
  "slug": "song-name-genre",
  "genre": "Lo-Fi",
  "language": "Telugu",
  "tempo": "medium",
  "song_length": "full",
  "shorts_clip_mode": "auto",
  "shorts_duration": 30,
  "workspace": "song-name-genre/",
  "files": {
    "original_mp3": "<slug>/<slug>-original.mp3",
    "acapella": "<slug>/<slug>-acapella.mp3",
    "lyrics": "<slug>/<slug>-lyrics.txt",
    "suno_lyrics": "<slug>/<slug>-suno-lyrics.txt",
    "suno_style": "<slug>/<slug>-suno-style.txt",
    "design": "<slug>/design.json",
    "remix_acapella": null,
    "lyrics_timestamps": null,
    "cover_art": null,
    "final_video": null,
    "shorts_segments": null,
    "short_video": null
  },
  "status": {
    "mp3_downloaded": false,
    "acapella_extracted": false,
    "lyrics_saved": false,
    "suno_lyrics_generated": false,
    "remix_uploaded": false,
    "remix_v1_downloaded": false,
    "remix_v2_downloaded": false,
    "acapella_aligned": false,
    "cover_art_fetched": false,
    "video_generated": false,
    "youtube_metadata_generated": false,
    "shorts_clip_selected": false,
    "short_video_generated": false,
    "suno_remix_url_v1": null,
    "suno_remix_url_v2": null,
    "suno_cdn_v1": null,
    "suno_cdn_v2": null,
    "selected_remix": null,
    "lyrics_source_url": null,
    "cover_art_skipped": false
  },
  "created_at": "2026-03-27T12:00:00Z"
}
```
````

- [ ] **Step 2: Rewrite Step 0 so config validation happens before workspace creation**

In `prompts/step-0-prepare-workspace.md`, make these exact changes:

1. Replace the prerequisite bullet list with:

```md
## Prerequisites

- Access to the local filesystem (Bash tool)
- `.remix-workspace-root.json` exists at the repo root and contains a valid `workspaceRoot`
- The configured `workspaceRoot` directory already exists and is writable
```

2. Replace section `0.4 — Create Workspace Directory` with:

````md
### 0.4 — Resolve Workspace Root And Create Workspace Directory

Read `.remix-workspace-root.json` from the repo root and extract `workspaceRoot`.

- If the file is missing: stop and tell the user to copy `.remix-workspace-root.example.json` to `.remix-workspace-root.json`.
- If the JSON is invalid: stop and tell the user to fix the file.
- If the configured root does not exist: stop and tell the user to create that directory first.

Resolve the workspace directory as:

```text
<workspaceRoot>/<slug>/
```

Create that directory and verify it exists.
````

3. Replace the `meta.json` template paths so they are root-relative, not `workspaces/...`, using this exact block:

```json
{
  "workspace": "<slug>/",
  "files": {
    "original_mp3": "<slug>/<slug>-original.mp3",
    "acapella": "<slug>/<slug>-acapella.mp3",
    "lyrics": "<slug>/<slug>-lyrics.txt",
    "suno_lyrics": "<slug>/<slug>-suno-lyrics.txt",
    "suno_style": "<slug>/<slug>-suno-style.txt",
    "design": "<slug>/design.json",
    "remix_acapella": null,
    "lyrics_timestamps": null,
    "cover_art": null,
    "final_video": null,
    "shorts_segments": null,
    "short_video": null
  }
}
```

4. Replace the final confirmation block with:

```md
Workspace ready: <workspaceRoot>/<slug>/
  Video        : <video_title>
  Genre        : <genre>
  Language     : <language>
  Tempo        : <tempo>
  Length       : <song_length>
  Shorts Mode  : <shorts_clip_mode>
  Shorts Dur   : <shorts_duration>s

Proceeding to Step 1: Download MP3...
```

- [ ] **Step 3: Update the prompt index to the new storage model**

In `prompts/README.md`, make these exact replacements:

```md
| 0 | `step-0-prepare-workspace.md` | Collect inputs, resolve configured workspace root, create workspace, write meta.json | `<workspaceRoot>/<slug>/`, `meta.json` | None |
```

```md
- **Workspace state**: `meta.json` inside `<workspaceRoot>/<slug>/` is the single source of truth
```

```md
3. **Check meta.json**: Always read the workspace's `meta.json` before acting
```

- [ ] **Step 4: Verify the canonical docs no longer hard-code repo-root workspaces**

Run: `rg 'workspaces/<slug>|workspaces/' prompts/references/workspace-conventions.md prompts/step-0-prepare-workspace.md prompts/README.md`

Expected: no matches.

- [ ] **Step 5: Commit**

```bash
git add prompts/references/workspace-conventions.md prompts/step-0-prepare-workspace.md prompts/README.md
git commit -m "docs: switch workspace conventions to local config"
```

### Task 4: Sweep The Remaining Operational Prompts And Reference Guides

**Files:**
- Modify: `prompts/references/acapella-extractor-usage.md`
- Modify: `prompts/references/error-handling-patterns.md`
- Modify: `prompts/step-1-download-mp3.md`
- Modify: `prompts/step-2-extract-acapella.md`
- Modify: `prompts/step-3-find-lyrics.md`
- Modify: `prompts/step-4-generate-suno-lyrics.md`
- Modify: `prompts/step-5-upload-to-suno.md`
- Modify: `prompts/step-6-extract-acapella-and-align.md`
- Modify: `prompts/step-7-fetch-cover-art.md`
- Modify: `prompts/step-8-generate-video.md`
- Modify: `prompts/step-9-generate-youtube-metadata.md`
- Modify: `prompts/step-10-select-short-clip.md`
- Modify: `prompts/step-11-generate-short-video.md`

- [ ] **Step 1: Add the shared path-resolution rule to each operational step**

Near the top of each step file listed above, insert this exact markdown block after prerequisites:

```md
## Workspace Path Resolution

Before using any filesystem path in this step:

1. Read `.remix-workspace-root.json` from the repo root.
2. Resolve `WORKSPACE_ROOT` from its `workspaceRoot` field.
3. Resolve `WORKSPACE_DIR` as `<workspaceRoot>/<slug>/`.
4. Use absolute paths under `WORKSPACE_DIR` for filesystem commands.
5. Keep any stored `meta.json.files.*` values root-relative, for example `<slug>/design.json`.
```

- [ ] **Step 2: Replace repo-root command examples with `WORKSPACE_DIR` examples**

Make these exact replacements across the listed files:

1. In shell command blocks, replace path forms like:

```bash
workspaces/<slug>/<slug>-original.mp3
workspaces/<slug>/lyrics-timestamps.json
workspaces/<slug>/video/public/
```

with path forms like:

```bash
"${WORKSPACE_DIR}/${SLUG}-original.mp3"
"${WORKSPACE_DIR}/lyrics-timestamps.json"
"${WORKSPACE_DIR}/video/public/"
```

2. In prose and output examples, replace references like:

```md
Outputs in workspaces/<slug>/:
```

with:

```md
Outputs in <workspaceRoot>/<slug>/:
```

3. In `meta.json` update snippets, replace values like:

```json
"final_video": "workspaces/<slug>/<slug>-video.mp4"
```

with:

```json
"final_video": "<slug>/<slug>-video.mp4"
```

- [ ] **Step 3: Update the two shared reference docs with configured-root examples**

In `prompts/references/acapella-extractor-usage.md`, replace all command examples that use `workspaces/<slug>/...` with `${WORKSPACE_DIR}`-based examples, including:

```bash
uv run python extract.py \
  "${WORKSPACE_DIR}/${SLUG}-original.mp3" \
  -o "${WORKSPACE_DIR}"
```

```bash
uv run python align_lyrics.py \
  --audio "${WORKSPACE_DIR}/${SLUG}-remix-v1-acapella.mp3" \
  --lyrics "${WORKSPACE_DIR}/${SLUG}-suno-lyrics.txt" \
  --output "${WORKSPACE_DIR}/lyrics-timestamps.json"
```

In `prompts/references/error-handling-patterns.md`, replace repo-root permission/path fixes with this exact style of example:

```md
1. Check that `.remix-workspace-root.json` exists and points to a valid directory.
2. Check write permissions on the configured root: `ls -ld "<workspaceRoot>"`
3. Create the resolved workspace directory explicitly: `mkdir -p "<workspaceRoot>/<slug>"`
```

- [ ] **Step 4: Update the Step 8 `init-video.js` examples to the resolved workspace model**

In `prompts/step-8-generate-video.md`, replace the existing scaffolding and copy commands with these exact examples:

```bash
cd tools/video-generator
node init-video.js <slug> --design="${WORKSPACE_DIR}/design.json"
```

```bash
cp "${WORKSPACE_DIR}/${SLUG}-remix-v1.mp3"   "${WORKSPACE_DIR}/video/public/audio.mp3"
cp "${WORKSPACE_DIR}/lyrics-timestamps.json" "${WORKSPACE_DIR}/video/public/"
cp "${WORKSPACE_DIR}/design.json"            "${WORKSPACE_DIR}/video/public/"
cp "${WORKSPACE_DIR}/${SLUG}-suno-lyrics.txt" "${WORKSPACE_DIR}/video/public/suno-lyrics.txt"
cp "${WORKSPACE_DIR}/${SLUG}-cover-art.jpg"   "${WORKSPACE_DIR}/video/public/cover-art.jpg"
```

```json
{
  "status": { "video_generated": true },
  "files": {
    "final_video": "<slug>/<slug>-video.mp4",
    "design_config": "<slug>/design.json"
  }
}
```

- [ ] **Step 5: Verify the operational prompt sweep**

Run: `rg 'workspaces/<slug>|workspaces/\$|workspaces/\$\{' prompts/step-*.md prompts/references/*.md`

Expected: no matches.

- [ ] **Step 6: Commit**

```bash
git add prompts/references/acapella-extractor-usage.md prompts/references/error-handling-patterns.md prompts/step-1-download-mp3.md prompts/step-2-extract-acapella.md prompts/step-3-find-lyrics.md prompts/step-4-generate-suno-lyrics.md prompts/step-5-upload-to-suno.md prompts/step-6-extract-acapella-and-align.md prompts/step-7-fetch-cover-art.md prompts/step-8-generate-video.md prompts/step-9-generate-youtube-metadata.md prompts/step-10-select-short-clip.md prompts/step-11-generate-short-video.md
git commit -m "docs: resolve prompt workspaces from configured root"
```

### Task 5: Update Top-Level Docs And Tool README, Then Run Final Verification

**Files:**
- Modify: `tools/video-generator/README.md`
- Modify: `README.md`
- Modify: `AGENTS.md`
- Test: `tools/shared/workspace-root.test.js`
- Test: `tools/video-generator/init-video.test.js`

- [ ] **Step 1: Update the video generator README to the new setup flow**

In `tools/video-generator/README.md`, make these exact replacements:

```md
Before using this tool, configure `.remix-workspace-root.json` at the repo root so `init-video.js` can resolve `<workspaceRoot>/<slug>/`.
```

```bash
cd tools/video-generator
node init-video.js <workspace-slug> --design="/absolute/path/to/<workspaceRoot>/<slug>/design.json"
```

```md
The generated video project is created in `<workspaceRoot>/<slug>/video/`.
```

- [ ] **Step 2: Update top-level repo docs and agent instructions**

In `README.md`, replace the operational workspace language with this exact content:

```md
Step 0 resolves a machine-local workspace root from `.remix-workspace-root.json`, then creates `<workspaceRoot>/<slug>/` with a `meta.json` tracking all inputs and pipeline state.
```

```md
- **Workspace isolation**: All files for a remix stay together in the configured external workspace root under `<workspaceRoot>/<slug>/`
```

Add this setup snippet under Getting Started:

```bash
cp .remix-workspace-root.example.json .remix-workspace-root.json
```

In `AGENTS.md`, replace the workspace rule with this exact line:

```md
1. **Workspace is state.** Each remix lives in `<workspaceRoot>/<slug>/`, where `workspaceRoot` comes from the repo-local `.remix-workspace-root.json`. The `meta.json` inside tracks all inputs, outputs, and step completion status. Always read it before acting.
```

- [ ] **Step 3: Run the final verification suite**

Run these commands exactly:

```bash
node --test tools/shared/workspace-root.test.js tools/video-generator/init-video.test.js
```

```bash
rg 'workspaces/<slug>|workspaces/\$|workspaces/\$\{' README.md AGENTS.md prompts/ tools/video-generator/README.md tools/video-generator/init-video.js
```

Expected:

- Node tests PASS.
- `rg` returns no matches in the listed operational files.

- [ ] **Step 4: Commit**

```bash
git add tools/video-generator/README.md README.md AGENTS.md
git commit -m "docs: document configured workspace root setup"
```

## Self-Review Checklist

- Spec coverage: the plan includes the config file, gitignore, shared helper, `init-video.js`, canonical prompt docs, the operational prompt sweep, top-level docs, and final verification.
- Placeholder scan: there are no placeholder markers; all commands, file paths, and code snippets are concrete.
- Type consistency: `workspaceRoot`, `workspaceDir`, `resolveWorkspaceDir`, and root-relative `meta.json` values are named consistently across all tasks.
