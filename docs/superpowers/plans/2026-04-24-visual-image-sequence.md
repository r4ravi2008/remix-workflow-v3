# Visual Image Sequence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the single-cover-art primary video path with a composable original-video frame sequence that Remotion renders with the existing beat-reactive cover-art layout behavior.

**Architecture:** Add a focused Node visual-sequence tool that downloads the original video, extracts a configurable number of evenly spaced source frames, and writes selection/manifest artifacts. Extend the video scaffolder and Remotion template to copy and consume `image-sequence.json` plus `stylized-frames/`, while falling back to `cover-art.jpg` and the existing placeholder behavior.

**Tech Stack:** Node.js built-ins, `node:test`, `yt-dlp`, FFmpeg/ffprobe, Remotion React template, existing workspace-root helper.

---

## File Structure

- Create `tools/visual-sequence/visual-sequence.js`: pure helpers plus CLI for original-video download, even timestamp generation, source frame extraction, metadata updates, and image-sequence manifest creation.
- Create `tools/visual-sequence/visual-sequence.test.js`: `node:test` coverage for frame count defaults, midpoint timestamp generation, selection metadata, manifest timing, and shortage behavior.
- Modify `tools/video-generator/init-video.js`: parse `--image-sequence=<path>` and `--stylized-frames=<path>` and copy those assets into `video/public/` during scaffold.
- Modify `tools/video-generator/init-video.test.js`: verify sequence manifest and stylized frame directory copying.
- Create `tools/video-generator/template/src/utils/imageSequence.ts`: typed loader/validator for `image-sequence.json`, with invalid entries filtered out.
- Modify `tools/video-generator/template/src/MusicVideo.tsx`: load optional image sequence and pass it to layouts.
- Modify `tools/video-generator/template/src/layouts/CoverArtLayout.tsx`: render active sequence image in the same image slots that currently render `cover-art.jpg`, preserving `artScale`, glow, vignette, rings, lyrics, and visualizer behavior.
- Modify `prompts/step-7-fetch-cover-art.md`: convert Step 7 into visual sequence preparation with cover-art fallback notes.
- Modify `prompts/step-8-generate-video.md`: copy sequence artifacts and document fallback behavior.
- Modify `prompts/references/workspace-conventions.md`: add new artifact/status/config fields.
- Modify `prompts/README.md`: update Step 7 purpose/key outputs.

## Test Commands

- Run focused visual sequence tests: `node --test tools/visual-sequence/visual-sequence.test.js`
- Run focused scaffolder tests: `node --test tools/video-generator/init-video.test.js`
- Run shared workspace tests: `node --test tools/shared/workspace-root.test.js`
- Run all Node tests: `node --test tools/shared/workspace-root.test.js tools/video-generator/init-video.test.js tools/visual-sequence/visual-sequence.test.js`
- Type-check the Remotion template after template changes: `npx tsc --noEmit` from `tools/video-generator/template`

---

### Task 1: Add Visual Sequence Pure Helpers

**Files:**
- Create: `tools/visual-sequence/visual-sequence.js`
- Create: `tools/visual-sequence/visual-sequence.test.js`

- [ ] **Step 1: Write failing tests for frame count and timestamp generation**

Add this initial test file:

```js
const test = require('node:test');
const assert = require('node:assert/strict');

const {
  resolveFrameCount,
  generateEvenTimestamps,
} = require('./visual-sequence');

test('resolveFrameCount defaults to 20 when meta has no override', () => {
  assert.equal(resolveFrameCount({}), 20);
  assert.equal(resolveFrameCount({visual_frame_count: undefined}), 20);
});

test('resolveFrameCount accepts positive integer overrides', () => {
  assert.equal(resolveFrameCount({visual_frame_count: 12}), 12);
  assert.equal(resolveFrameCount({visual_frame_count: 40}), 40);
});

test('resolveFrameCount rejects non-positive and non-integer overrides', () => {
  assert.throws(() => resolveFrameCount({visual_frame_count: 0}), /visual_frame_count must be a positive integer/);
  assert.throws(() => resolveFrameCount({visual_frame_count: -1}), /visual_frame_count must be a positive integer/);
  assert.throws(() => resolveFrameCount({visual_frame_count: 2.5}), /visual_frame_count must be a positive integer/);
});

test('generateEvenTimestamps uses midpoint buckets', () => {
  assert.deepEqual(generateEvenTimestamps(100, 4), [12.5, 37.5, 62.5, 87.5]);
});

test('generateEvenTimestamps rounds to millisecond precision', () => {
  assert.deepEqual(generateEvenTimestamps(10, 3), [1.667, 5, 8.333]);
});

test('generateEvenTimestamps rejects invalid duration and count', () => {
  assert.throws(() => generateEvenTimestamps(0, 3), /duration must be positive/);
  assert.throws(() => generateEvenTimestamps(10, 0), /count must be a positive integer/);
});
```

- [ ] **Step 2: Run the failing tests**

Run: `node --test tools/visual-sequence/visual-sequence.test.js`

Expected: FAIL with `Cannot find module './visual-sequence'`.

- [ ] **Step 3: Implement minimal pure helpers**

Create `tools/visual-sequence/visual-sequence.js` with:

```js
#!/usr/bin/env node
const fs = require('node:fs');
const path = require('node:path');
const {execFileSync} = require('node:child_process');

const {resolveWorkspaceDir} = require('../shared/workspace-root');

function resolveFrameCount(meta) {
  const value = meta?.visual_frame_count ?? 20;
  if (!Number.isInteger(value) || value <= 0) {
    throw new Error('visual_frame_count must be a positive integer.');
  }
  return value;
}

function generateEvenTimestamps(durationSeconds, count) {
  if (typeof durationSeconds !== 'number' || !Number.isFinite(durationSeconds) || durationSeconds <= 0) {
    throw new Error('duration must be positive.');
  }
  if (!Number.isInteger(count) || count <= 0) {
    throw new Error('count must be a positive integer.');
  }

  const bucketSize = durationSeconds / count;
  return Array.from({length: count}, (_, index) => {
    return Number(((index + 0.5) * bucketSize).toFixed(3));
  });
}

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function writeJson(filePath, value) {
  fs.writeFileSync(filePath, `${JSON.stringify(value, null, 2)}\n`);
}

module.exports = {
  resolveFrameCount,
  generateEvenTimestamps,
  readJson,
  writeJson,
};
```

- [ ] **Step 4: Run tests and verify they pass**

Run: `node --test tools/visual-sequence/visual-sequence.test.js`

Expected: PASS for all tests in `visual-sequence.test.js`.

- [ ] **Step 5: Commit**

```bash
git add tools/visual-sequence/visual-sequence.js tools/visual-sequence/visual-sequence.test.js
git commit -m "feat: add visual frame selection helpers"
```

---

### Task 2: Add Selection And Manifest Builders

**Files:**
- Modify: `tools/visual-sequence/visual-sequence.js`
- Modify: `tools/visual-sequence/visual-sequence.test.js`

- [ ] **Step 1: Add failing tests for selected frame and manifest builders**

Append to `tools/visual-sequence/visual-sequence.test.js`:

```js
const {
  buildSelectedFrames,
  buildImageSequence,
} = require('./visual-sequence');

test('buildSelectedFrames creates chronological source frame records', () => {
  const result = buildSelectedFrames({
    slug: 'bella-bella-lofi',
    sourceVideo: 'bella-bella-lofi/bella-bella-lofi-original-video.mp4',
    requestedCount: 3,
    timestamps: [2, 6, 10],
    extractedFrames: [
      {index: 1, requestedTimestamp: 2, resolvedTimestamp: 2.04, sourceImagePath: 'source-frames/bella-bella-lofi-frame-001.jpg'},
      {index: 2, requestedTimestamp: 6, resolvedTimestamp: 6.01, sourceImagePath: 'source-frames/bella-bella-lofi-frame-002.jpg'},
      {index: 3, requestedTimestamp: 10, resolvedTimestamp: 10, sourceImagePath: 'source-frames/bella-bella-lofi-frame-003.jpg'},
    ],
  });

  assert.equal(result.version, 1);
  assert.equal(result.requested_count, 3);
  assert.equal(result.selected_count, 3);
  assert.deepEqual(result.frames.map(frame => frame.id), ['frame-001', 'frame-002', 'frame-003']);
  assert.deepEqual(result.frames.map(frame => frame.source_timestamp), [2.04, 6.01, 10]);
});

test('buildSelectedFrames records shortage when extraction returns fewer frames', () => {
  const result = buildSelectedFrames({
    slug: 'bella-bella-lofi',
    sourceVideo: 'bella-bella-lofi/bella-bella-lofi-original-video.mp4',
    requestedCount: 3,
    timestamps: [2, 6, 10],
    extractedFrames: [
      {index: 1, requestedTimestamp: 2, resolvedTimestamp: 2, sourceImagePath: 'source-frames/bella-bella-lofi-frame-001.jpg'},
      {index: 3, requestedTimestamp: 10, resolvedTimestamp: 10, sourceImagePath: 'source-frames/bella-bella-lofi-frame-003.jpg'},
    ],
  });

  assert.equal(result.selected_count, 2);
  assert.equal(result.shortage, 1);
});

test('buildImageSequence distributes selected frames over remix duration', () => {
  const selected = {
    version: 1,
    source_video: 'bella-bella-lofi/bella-bella-lofi-original-video.mp4',
    requested_count: 3,
    selected_count: 3,
    frames: [
      {id: 'frame-001', source_timestamp: 2, source_image_path: 'source-frames/bella-bella-lofi-frame-001.jpg'},
      {id: 'frame-002', source_timestamp: 6, source_image_path: 'source-frames/bella-bella-lofi-frame-002.jpg'},
      {id: 'frame-003', source_timestamp: 10, source_image_path: 'source-frames/bella-bella-lofi-frame-003.jpg'},
    ],
  };

  const sequence = buildImageSequence({
    slug: 'bella-bella-lofi',
    selectedFrames: selected,
    audioDuration: 90,
  });

  assert.equal(sequence.source.selection, 'evenly-spaced');
  assert.deepEqual(sequence.frames.map(frame => [frame.start_time, frame.end_time]), [[0, 30], [30, 60], [60, 90]]);
  assert.equal(sequence.frames[0].image_path, 'stylized-frames/bella-bella-lofi-frame-001.jpg');
});
```

- [ ] **Step 2: Run tests and verify failure**

Run: `node --test tools/visual-sequence/visual-sequence.test.js`

Expected: FAIL with `buildSelectedFrames is not a function` or `buildImageSequence is not a function`.

- [ ] **Step 3: Implement selected frame and manifest builders**

Add these functions above `module.exports` in `tools/visual-sequence/visual-sequence.js`:

```js
function frameId(index) {
  return `frame-${String(index).padStart(3, '0')}`;
}

function buildSelectedFrames({slug, sourceVideo, requestedCount, timestamps, extractedFrames}) {
  const frames = extractedFrames
    .slice()
    .sort((a, b) => a.index - b.index)
    .map(frame => ({
      id: frameId(frame.index),
      source_timestamp: Number(frame.resolvedTimestamp.toFixed(3)),
      requested_timestamp: Number(frame.requestedTimestamp.toFixed(3)),
      source_image_path: frame.sourceImagePath,
    }));

  const result = {
    version: 1,
    source_video: sourceVideo,
    requested_count: requestedCount,
    selected_count: frames.length,
    frames,
  };

  if (frames.length < requestedCount) {
    result.shortage = requestedCount - frames.length;
  }

  return result;
}

function buildImageSequence({slug, selectedFrames, audioDuration}) {
  if (typeof audioDuration !== 'number' || !Number.isFinite(audioDuration) || audioDuration <= 0) {
    throw new Error('audioDuration must be positive.');
  }

  const frames = selectedFrames.frames || [];
  const segmentDuration = frames.length > 0 ? audioDuration / frames.length : audioDuration;

  return {
    version: 1,
    source: {
      video: selectedFrames.source_video,
      selection: 'evenly-spaced',
      requested_count: selectedFrames.requested_count,
    },
    frames: frames.map((frame, index) => ({
      id: frame.id,
      image_path: `stylized-frames/${slug}-${frame.id}.jpg`,
      source_timestamp: frame.source_timestamp,
      start_time: Number((index * segmentDuration).toFixed(3)),
      end_time: Number(((index + 1) * segmentDuration).toFixed(3)),
      transition: 'crossfade',
    })),
  };
}
```

Update `module.exports` to include:

```js
  buildSelectedFrames,
  buildImageSequence,
```

- [ ] **Step 4: Run tests and verify pass**

Run: `node --test tools/visual-sequence/visual-sequence.test.js`

Expected: PASS for all visual sequence tests.

- [ ] **Step 5: Commit**

```bash
git add tools/visual-sequence/visual-sequence.js tools/visual-sequence/visual-sequence.test.js
git commit -m "feat: build visual sequence manifests"
```

---

### Task 3: Add Visual Sequence CLI For Download, Extraction, And Manifest Creation

**Files:**
- Modify: `tools/visual-sequence/visual-sequence.js`
- Modify: `tools/visual-sequence/visual-sequence.test.js`

- [ ] **Step 1: Add failing tests for CLI argument parsing and workspace output paths**

Append to `tools/visual-sequence/visual-sequence.test.js`:

```js
const {
  parseArgs,
  resolveWorkspacePaths,
} = require('./visual-sequence');

test('parseArgs supports extract and manifest commands', () => {
  assert.deepEqual(parseArgs(['extract', 'bella-bella-lofi']), {
    command: 'extract',
    workspaceSlug: 'bella-bella-lofi',
    frameCountOverride: null,
  });
  assert.deepEqual(parseArgs(['extract', 'bella-bella-lofi', '--frame-count=24']), {
    command: 'extract',
    workspaceSlug: 'bella-bella-lofi',
    frameCountOverride: 24,
  });
  assert.deepEqual(parseArgs(['manifest', 'bella-bella-lofi']), {
    command: 'manifest',
    workspaceSlug: 'bella-bella-lofi',
    frameCountOverride: null,
  });
});

test('parseArgs rejects unknown commands and bad frame count flags', () => {
  assert.throws(() => parseArgs([]), /Usage: node visual-sequence.js/);
  assert.throws(() => parseArgs(['bad', 'bella-bella-lofi']), /Unknown command/);
  assert.throws(() => parseArgs(['extract', 'bella-bella-lofi', '--frame-count=0']), /frame-count must be a positive integer/);
});

test('resolveWorkspacePaths returns all visual sequence paths', () => {
  const workspaceDir = '/tmp/workspaces/bella-bella-lofi';
  const result = resolveWorkspacePaths(workspaceDir, 'bella-bella-lofi');
  assert.equal(result.originalVideoPath, '/tmp/workspaces/bella-bella-lofi/bella-bella-lofi-original-video.mp4');
  assert.equal(result.sourceFramesDir, '/tmp/workspaces/bella-bella-lofi/source-frames');
  assert.equal(result.stylizedFramesDir, '/tmp/workspaces/bella-bella-lofi/stylized-frames');
  assert.equal(result.selectedFramesPath, '/tmp/workspaces/bella-bella-lofi/selected-visual-frames.json');
  assert.equal(result.imageSequencePath, '/tmp/workspaces/bella-bella-lofi/image-sequence.json');
});
```

- [ ] **Step 2: Run tests and verify failure**

Run: `node --test tools/visual-sequence/visual-sequence.test.js`

Expected: FAIL with missing `parseArgs` or `resolveWorkspacePaths` exports.

- [ ] **Step 3: Implement CLI parsing and workspace path helpers**

Add to `tools/visual-sequence/visual-sequence.js`:

```js
function parseArgs(argv) {
  const [command, workspaceSlug, ...rest] = argv;
  if (!command || !workspaceSlug) {
    throw new Error('Usage: node visual-sequence.js <extract|manifest> <workspace-slug> [--frame-count=N]');
  }
  if (!['extract', 'manifest'].includes(command)) {
    throw new Error(`Unknown command: ${command}`);
  }

  let frameCountOverride = null;
  for (const arg of rest) {
    if (arg.startsWith('--frame-count=')) {
      frameCountOverride = Number.parseInt(arg.replace('--frame-count=', ''), 10);
      if (!Number.isInteger(frameCountOverride) || frameCountOverride <= 0) {
        throw new Error('frame-count must be a positive integer.');
      }
    } else {
      throw new Error(`Unknown argument: ${arg}`);
    }
  }

  return {command, workspaceSlug, frameCountOverride};
}

function resolveWorkspacePaths(workspaceDir, slug) {
  return {
    metaPath: path.join(workspaceDir, 'meta.json'),
    originalVideoPath: path.join(workspaceDir, `${slug}-original-video.mp4`),
    sourceFramesDir: path.join(workspaceDir, 'source-frames'),
    stylizedFramesDir: path.join(workspaceDir, 'stylized-frames'),
    candidatesPath: path.join(workspaceDir, 'visual-frame-candidates.json'),
    selectedFramesPath: path.join(workspaceDir, 'selected-visual-frames.json'),
    imageSequencePath: path.join(workspaceDir, 'image-sequence.json'),
  };
}
```

Update `module.exports` to include:

```js
  parseArgs,
  resolveWorkspacePaths,
```

- [ ] **Step 4: Add extraction and manifest command implementation**

Add to `tools/visual-sequence/visual-sequence.js`:

```js
function runCommand(execFileSyncImpl, command, args, options = {}) {
  execFileSyncImpl(command, args, {stdio: 'pipe', encoding: 'utf8', ...options});
}

function getMediaDurationSeconds(filePath, execFileSyncImpl = execFileSync) {
  const raw = execFileSyncImpl(
    'ffprobe',
    ['-v', 'quiet', '-show_entries', 'format=duration', '-of', 'csv=p=0', filePath],
    {encoding: 'utf8'}
  ).trim();
  const duration = Number.parseFloat(raw);
  if (!Number.isFinite(duration) || duration <= 0) {
    throw new Error(`Could not determine media duration for ${filePath}`);
  }
  return duration;
}

function updateMeta(metaPath, updater) {
  const meta = readJson(metaPath);
  const next = updater(meta);
  writeJson(metaPath, next);
  return next;
}

function ensureOriginalVideo({meta, paths, execFileSyncImpl = execFileSync, logger = console}) {
  if (fs.existsSync(paths.originalVideoPath)) {
    logger.log(`Original video already exists: ${paths.originalVideoPath}`);
    return;
  }
  if (!meta.youtube_url) {
    throw new Error('meta.json is missing youtube_url; cannot download original video.');
  }
  runCommand(execFileSyncImpl, 'yt-dlp', [
    '-f', 'bv*+ba/b',
    '--merge-output-format', 'mp4',
    '-o', paths.originalVideoPath,
    meta.youtube_url,
  ]);
}

function extractFrame({videoPath, outputPath, timestamp, execFileSyncImpl = execFileSync}) {
  fs.mkdirSync(path.dirname(outputPath), {recursive: true});
  runCommand(execFileSyncImpl, 'ffmpeg', [
    '-y',
    '-ss', String(timestamp),
    '-i', videoPath,
    '-frames:v', '1',
    '-q:v', '2',
    outputPath,
  ]);
}

function extractVisualFrames(options) {
  const {
    workspaceSlug,
    frameCountOverride = null,
    repoRoot,
    execFileSyncImpl = execFileSync,
    logger = console,
  } = options;
  const {workspaceDir} = resolveWorkspaceDir(workspaceSlug, {repoRoot});
  const paths = resolveWorkspacePaths(workspaceDir, workspaceSlug);
  const meta = readJson(paths.metaPath);
  const requestedCount = frameCountOverride ?? resolveFrameCount(meta);

  ensureOriginalVideo({meta, paths, execFileSyncImpl, logger});
  const duration = getMediaDurationSeconds(paths.originalVideoPath, execFileSyncImpl);
  const timestamps = generateEvenTimestamps(duration, requestedCount);
  const extractedFrames = [];

  fs.mkdirSync(paths.sourceFramesDir, {recursive: true});
  timestamps.forEach((timestamp, index) => {
    const frameIndex = index + 1;
    const fileName = `${workspaceSlug}-${frameId(frameIndex)}.jpg`;
    const absoluteOutputPath = path.join(paths.sourceFramesDir, fileName);
    const relativeOutputPath = `source-frames/${fileName}`;
    try {
      extractFrame({
        videoPath: paths.originalVideoPath,
        outputPath: absoluteOutputPath,
        timestamp,
        execFileSyncImpl,
      });
      extractedFrames.push({
        index: frameIndex,
        requestedTimestamp: timestamp,
        resolvedTimestamp: timestamp,
        sourceImagePath: relativeOutputPath,
      });
    } catch (error) {
      logger.warn(`Failed to extract frame ${frameIndex} at ${timestamp}s: ${error.message}`);
    }
  });

  const sourceVideo = `${workspaceSlug}/${workspaceSlug}-original-video.mp4`;
  const selectedFrames = buildSelectedFrames({
    slug: workspaceSlug,
    sourceVideo,
    requestedCount,
    timestamps,
    extractedFrames,
  });
  const candidates = {
    version: 1,
    source_video: sourceVideo,
    duration,
    requested_count: requestedCount,
    attempted_timestamps: timestamps,
    extracted_frames: extractedFrames,
    shortage: requestedCount - extractedFrames.length,
  };

  writeJson(paths.candidatesPath, candidates);
  writeJson(paths.selectedFramesPath, selectedFrames);
  updateMeta(paths.metaPath, current => ({
    ...current,
    visual_frame_count: requestedCount,
    files: {
      ...current.files,
      original_video: `${workspaceSlug}/${workspaceSlug}-original-video.mp4`,
      visual_frame_candidates: `${workspaceSlug}/visual-frame-candidates.json`,
      selected_visual_frames: `${workspaceSlug}/selected-visual-frames.json`,
    },
    status: {
      ...current.status,
      original_video_downloaded: true,
      visual_frames_extracted: extractedFrames.length > 0,
      visual_frames_selected: selectedFrames.selected_count > 0,
    },
  }));

  logger.log(`Selected ${selectedFrames.selected_count}/${requestedCount} visual frames.`);
  return {paths, candidates, selectedFrames};
}

function createImageSequence(options) {
  const {
    workspaceSlug,
    repoRoot,
    execFileSyncImpl = execFileSync,
    logger = console,
  } = options;
  const {workspaceDir} = resolveWorkspaceDir(workspaceSlug, {repoRoot});
  const paths = resolveWorkspacePaths(workspaceDir, workspaceSlug);
  const meta = readJson(paths.metaPath);
  const selectedRemix = meta.status?.selected_remix || 'v1';
  const audioPath = path.join(workspaceDir, `${workspaceSlug}-remix-${selectedRemix}.mp3`);
  const audioDuration = getMediaDurationSeconds(audioPath, execFileSyncImpl);
  const selectedFrames = readJson(paths.selectedFramesPath);
  const sequence = buildImageSequence({slug: workspaceSlug, selectedFrames, audioDuration});

  writeJson(paths.imageSequencePath, sequence);
  updateMeta(paths.metaPath, current => ({
    ...current,
    files: {
      ...current.files,
      image_sequence: `${workspaceSlug}/image-sequence.json`,
    },
    status: {
      ...current.status,
      visual_frames_stylized: fs.existsSync(paths.stylizedFramesDir),
    },
  }));
  logger.log(`Wrote image sequence manifest: ${paths.imageSequencePath}`);
  return {paths, sequence};
}

function main(argv = process.argv.slice(2)) {
  const args = parseArgs(argv);
  if (args.command === 'extract') {
    return extractVisualFrames(args);
  }
  return createImageSequence(args);
}

if (require.main === module) {
  try {
    main();
  } catch (error) {
    console.error(error.message);
    process.exit(1);
  }
}
```

Update `module.exports` to include:

```js
  getMediaDurationSeconds,
  extractVisualFrames,
  createImageSequence,
  main,
```

- [ ] **Step 5: Run tests**

Run: `node --test tools/visual-sequence/visual-sequence.test.js`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add tools/visual-sequence/visual-sequence.js tools/visual-sequence/visual-sequence.test.js
git commit -m "feat: add visual sequence workspace CLI"
```

---

### Task 4: Extend Video Scaffolder To Copy Sequence Assets

**Files:**
- Modify: `tools/video-generator/init-video.js`
- Modify: `tools/video-generator/init-video.test.js`

- [ ] **Step 1: Add failing scaffolder test**

Append to `tools/video-generator/init-video.test.js`:

```js
test('copies image sequence manifest and stylized frames when provided', () => {
  const fixture = makeFixture();
  const imageSequencePath = path.join(fixture.workspaceDir, 'image-sequence.json');
  const stylizedFramesDir = path.join(fixture.workspaceDir, 'stylized-frames');
  fs.mkdirSync(stylizedFramesDir);
  fs.writeFileSync(
    imageSequencePath,
    JSON.stringify({version: 1, frames: [{id: 'frame-001', image_path: 'stylized-frames/bella-bella-lofi-frame-001.jpg'}]}, null, 2)
  );
  fs.writeFileSync(path.join(stylizedFramesDir, 'bella-bella-lofi-frame-001.jpg'), 'fake jpg');

  const result = initializeVideoProject({
    workspaceSlug: fixture.workspaceSlug,
    designPath: path.join(fixture.workspaceDir, 'design.json'),
    imageSequencePath,
    stylizedFramesDir,
    repoRoot: fixture.repoRoot,
    templateDir: fixture.templateDir,
    execSyncImpl: () => '180.25',
    logger: {log() {}, warn() {}, error() {}},
    processCwd: fixture.repoRoot,
  });

  assert.ok(fs.existsSync(path.join(result.videoDir, 'public', 'image-sequence.json')));
  assert.equal(
    fs.readFileSync(path.join(result.videoDir, 'public', 'stylized-frames', 'bella-bella-lofi-frame-001.jpg'), 'utf8'),
    'fake jpg'
  );
});
```

- [ ] **Step 2: Run the failing test**

Run: `node --test tools/video-generator/init-video.test.js`

Expected: FAIL because `initializeVideoProject` ignores `imageSequencePath` and `stylizedFramesDir`.

- [ ] **Step 3: Implement argument parsing and copying**

In `tools/video-generator/init-video.js`, update `parseArgs`:

```js
  let imageSequencePath = null;
  let stylizedFramesDir = null;
  argv.slice(1).forEach(arg => {
    if (arg.startsWith('--design=')) {
      designPath = arg.replace('--design=', '');
    } else if (arg.startsWith('--image-sequence=')) {
      imageSequencePath = arg.replace('--image-sequence=', '');
    } else if (arg.startsWith('--stylized-frames=')) {
      stylizedFramesDir = arg.replace('--stylized-frames=', '');
    }
  });

  return {workspaceSlug, designPath, imageSequencePath, stylizedFramesDir};
```

Update the usage error to:

```js
throw new Error('Usage: node init-video.js <workspace-slug> [--design=<path>] [--image-sequence=<path>] [--stylized-frames=<path>]');
```

Add destructured options in `initializeVideoProject`:

```js
    imageSequencePath = null,
    stylizedFramesDir = null,
```

After the design copy block, add:

```js
  if (imageSequencePath) {
    const sequenceSourcePath = path.resolve(imageSequencePath);
    if (fs.existsSync(sequenceSourcePath)) {
      fs.copyFileSync(sequenceSourcePath, path.join(videoDir, 'public', 'image-sequence.json'));
    } else {
      logger.warn(`Image sequence file not found: ${sequenceSourcePath}`);
    }
  }

  if (stylizedFramesDir) {
    const framesSourceDir = path.resolve(stylizedFramesDir);
    if (fs.existsSync(framesSourceDir)) {
      fs.cpSync(framesSourceDir, path.join(videoDir, 'public', 'stylized-frames'), {recursive: true});
    } else {
      logger.warn(`Stylized frames directory not found: ${framesSourceDir}`);
    }
  }
```

Update `main`:

```js
  const {workspaceSlug, designPath, imageSequencePath, stylizedFramesDir} = parseArgs(argv);
  return initializeVideoProject({workspaceSlug, designPath, imageSequencePath, stylizedFramesDir});
```

Update next-step logs to include:

```js
  logger.log(`  [ -f "${path.join(workspaceDir, 'image-sequence.json')}" ] && cp "${path.join(workspaceDir, 'image-sequence.json')}" "${path.join(videoDir, 'public', 'image-sequence.json')}"`);
  logger.log(`  [ -d "${path.join(workspaceDir, 'stylized-frames')}" ] && cp -R "${path.join(workspaceDir, 'stylized-frames')}" "${path.join(videoDir, 'public', 'stylized-frames')}"`);
```

- [ ] **Step 4: Run scaffolder tests**

Run: `node --test tools/video-generator/init-video.test.js`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/video-generator/init-video.js tools/video-generator/init-video.test.js
git commit -m "feat: scaffold visual sequence assets"
```

---

### Task 5: Add Remotion Image Sequence Loader

**Files:**
- Create: `tools/video-generator/template/src/utils/imageSequence.ts`
- Modify: `tools/video-generator/template/src/MusicVideo.tsx`

- [ ] **Step 1: Create sequence loader utility**

Create `tools/video-generator/template/src/utils/imageSequence.ts`:

```ts
export interface ImageSequenceFrame {
  id: string;
  image_path: string;
  source_timestamp: number;
  start_time: number;
  end_time: number;
  transition?: 'crossfade' | string;
}

export interface ImageSequence {
  version: number;
  source?: {
    video?: string;
    selection?: string;
    requested_count?: number;
  };
  frames: ImageSequenceFrame[];
}

function isValidFrame(frame: Partial<ImageSequenceFrame>): frame is ImageSequenceFrame {
  return typeof frame.id === 'string'
    && typeof frame.image_path === 'string'
    && typeof frame.source_timestamp === 'number'
    && typeof frame.start_time === 'number'
    && typeof frame.end_time === 'number'
    && frame.end_time > frame.start_time;
}

export function validateImageSequence(value: unknown): ImageSequence | null {
  if (typeof value !== 'object' || value == null) return null;
  const raw = value as {version?: unknown; source?: ImageSequence['source']; frames?: unknown};
  if (raw.version !== 1 || !Array.isArray(raw.frames)) return null;

  const frames = raw.frames
    .filter((frame): frame is ImageSequenceFrame => isValidFrame(frame as Partial<ImageSequenceFrame>))
    .sort((a, b) => a.start_time - b.start_time);

  if (frames.length === 0) return null;

  return {
    version: 1,
    source: raw.source,
    frames,
  };
}

export async function loadImageSequence(staticFileFn: (path: string) => string): Promise<ImageSequence | null> {
  try {
    const response = await fetch(staticFileFn('image-sequence.json'));
    if (!response.ok) return null;
    return validateImageSequence(await response.json());
  } catch {
    return null;
  }
}
```

- [ ] **Step 2: Wire loader into `MusicVideo.tsx`**

Modify imports:

```ts
import { loadImageSequence, ImageSequence } from './utils/imageSequence';
```

Add state after design state:

```ts
  const [sequenceHandle] = useState(() => delayRender('Loading image sequence'));
  const [imageSequence, setImageSequence] = useState<ImageSequence | null>(null);
```

Add loader after `loadDesignConfig`:

```ts
  const loadSequenceConfig = useCallback(async () => {
    setImageSequence(await loadImageSequence(staticFile));
    continueRender(sequenceHandle);
  }, [sequenceHandle]);
```

Update the effect:

```ts
  useEffect(() => { loadLyrics(); loadDesignConfig(); loadSequenceConfig(); }, [loadLyrics, loadDesignConfig, loadSequenceConfig]);
```

Add `imageSequence` to layout props:

```ts
      imageSequence,
```

- [ ] **Step 3: Type-check template**

Run from `tools/video-generator/template`: `npx tsc --noEmit`

Expected: FAIL because layout prop types do not yet accept `imageSequence`.

- [ ] **Step 4: Commit loader wiring after Task 6 fixes types**

Do not commit yet if TypeScript fails. Continue to Task 6, then commit both tasks together if preferred.

---

### Task 6: Render Active Sequence Images In CoverArtLayout

**Files:**
- Modify: `tools/video-generator/template/src/layouts/CoverArtLayout.tsx`

- [ ] **Step 1: Add prop type and active image calculation**

Add import:

```ts
import type { ImageSequence, ImageSequenceFrame } from '../utils/imageSequence';
```

Add prop to `CoverArtLayoutProps`:

```ts
  imageSequence?: ImageSequence | null;
```

Add to destructuring:

```ts
  imageSequence,
```

Replace `useCurrentFrame();` with:

```ts
  const frame = useCurrentFrame();
```

Add these helpers before render:

```ts
  const activeSequenceFrame: ImageSequenceFrame | null = useMemo(() => {
    const frames = imageSequence?.frames ?? [];
    return frames.find((item) => currentTime >= item.start_time && currentTime < item.end_time)
      ?? frames[frames.length - 1]
      ?? null;
  }, [imageSequence, currentTime]);

  const previousSequenceFrame: ImageSequenceFrame | null = useMemo(() => {
    const frames = imageSequence?.frames ?? [];
    if (!activeSequenceFrame) return null;
    const activeIndex = frames.indexOf(activeSequenceFrame);
    return activeIndex > 0 ? frames[activeIndex - 1] : null;
  }, [imageSequence, activeSequenceFrame]);

  const transitionProgress = activeSequenceFrame
    ? interpolate(currentTime, [activeSequenceFrame.start_time, activeSequenceFrame.start_time + 0.8], [0, 1], {
        extrapolateLeft: 'clamp',
        extrapolateRight: 'clamp',
      })
    : 1;

  const activeImageSrc = activeSequenceFrame?.image_path ?? 'cover-art.jpg';
```

- [ ] **Step 2: Replace blurred background image with active sequence image**

In the blurred background `<Img>`, replace:

```tsx
src={staticFile('cover-art.jpg')}
```

with:

```tsx
src={staticFile(activeImageSrc)}
```

- [ ] **Step 3: Replace main inset image with crossfade stack**

Replace the current successful main `<Img>` block:

```tsx
<Img
  src={staticFile('cover-art.jpg')}
  onError={() => setCoverArtError(true)}
  style={{
    width: '100%',
    height: '100%',
    objectFit: 'cover',
    objectPosition: 'center',
  }}
/>
```

with:

```tsx
<>
  {previousSequenceFrame && transitionProgress < 1 && (
    <Img
      src={staticFile(previousSequenceFrame.image_path)}
      onError={() => setCoverArtError(true)}
      style={{
        position: 'absolute',
        inset: 0,
        width: '100%',
        height: '100%',
        objectFit: 'cover',
        objectPosition: 'center',
        opacity: 1 - transitionProgress,
      }}
    />
  )}
  <Img
    src={staticFile(activeImageSrc)}
    onError={() => setCoverArtError(true)}
    style={{
      position: 'absolute',
      inset: 0,
      width: '100%',
      height: '100%',
      objectFit: 'cover',
      objectPosition: 'center',
      opacity: previousSequenceFrame ? transitionProgress : 1,
    }}
  />
</>
```

This preserves the existing outer wrapper transform:

```tsx
transform: `scale(${artScale})`,
```

- [ ] **Step 4: Type-check template**

Run from `tools/video-generator/template`: `npx tsc --noEmit`

Expected: PASS.

- [ ] **Step 5: Commit Remotion sequence rendering**

```bash
git add tools/video-generator/template/src/utils/imageSequence.ts tools/video-generator/template/src/MusicVideo.tsx tools/video-generator/template/src/layouts/CoverArtLayout.tsx
git commit -m "feat: render visual image sequences"
```

---

### Task 7: Update Pipeline Documentation And Workspace Schema

**Files:**
- Modify: `prompts/step-7-fetch-cover-art.md`
- Modify: `prompts/step-8-generate-video.md`
- Modify: `prompts/references/workspace-conventions.md`
- Modify: `prompts/README.md`
- Modify: `tools/video-generator/README.md`

- [ ] **Step 1: Update workspace conventions**

In `prompts/references/workspace-conventions.md`, add these files to the directory tree after `<slug>-lyrics.txt` or near visual outputs:

```text
    ├── <slug>-original-video.mp4
    ├── source-frames/
    ├── visual-frame-candidates.json
    ├── selected-visual-frames.json
    ├── stylized-frames/
    ├── image-sequence.json
```

Add `visual_frame_count` to the meta schema near `shorts_duration`:

```json
  "visual_frame_count": 20,
```

Add file fields:

```json
    "original_video": null,
    "visual_frame_candidates": null,
    "selected_visual_frames": null,
    "image_sequence": null,
```

Add status fields:

```json
    "original_video_downloaded": false,
    "visual_frames_extracted": false,
    "visual_frames_selected": false,
    "visual_frames_stylized": false,
```

Add suffix descriptions:

```markdown
| `original-video` | Original YouTube video used for visual frame extraction |
```

- [ ] **Step 2: Rewrite Step 7 objective and commands**

In `prompts/step-7-fetch-cover-art.md`, change the title to:

```markdown
# Step 7: Prepare Visual Image Sequence
```

Replace the objective with:

```markdown
Download the original YouTube video, extract a configurable number of evenly spaced source frames, stylize those frames with one shared prompt/settings set, and write `image-sequence.json` for Step 8. Existing cover art remains a fallback when sequence preparation is skipped or fails.
```

Add commands:

```bash
node tools/visual-sequence/visual-sequence.js extract <slug>
```

After stylized images exist in `${WORKSPACE_DIR}/stylized-frames/`, add:

```bash
node tools/visual-sequence/visual-sequence.js manifest <slug>
```

Document expected outputs:

```text
<slug>-original-video.mp4
source-frames/
visual-frame-candidates.json
selected-visual-frames.json
stylized-frames/
image-sequence.json
```

- [ ] **Step 3: Update Step 8 asset copying**

In `prompts/step-8-generate-video.md`, update the scaffold command to:

```bash
node init-video.js <slug> \
  --design="${WORKSPACE_DIR}/design.json" \
  --image-sequence="${WORKSPACE_DIR}/image-sequence.json" \
  --stylized-frames="${WORKSPACE_DIR}/stylized-frames"
```

Add manual copy fallback:

```bash
[ -f "${WORKSPACE_DIR}/image-sequence.json" ] && cp "${WORKSPACE_DIR}/image-sequence.json" "${WORKSPACE_DIR}/video/public/image-sequence.json"
[ -d "${WORKSPACE_DIR}/stylized-frames" ] && cp -R "${WORKSPACE_DIR}/stylized-frames" "${WORKSPACE_DIR}/video/public/stylized-frames"
```

Update the description of `CoverArtLayout` to say it renders `image-sequence.json` when present, then falls back to `cover-art.jpg`, then to the placeholder.

- [ ] **Step 4: Update pipeline index and video-generator README**

In `prompts/README.md`, change Step 7 row purpose to:

```markdown
| 7 | `step-7-fetch-cover-art.md` | Prepare original-video visual image sequence | `<slug>-original-video.mp4`, `selected-visual-frames.json`, `stylized-frames/`, `image-sequence.json` | Step 0 |
```

In `tools/video-generator/README.md`, add `image-sequence.json` and `stylized-frames/` to the Step 8 copy/scaffold instructions and document that `cover-art.jpg` remains fallback.

- [ ] **Step 5: Verify docs have no stale hard requirement**

Run: `rg "Hard requirement.*cover-art|layout.variant.*must be.*cover-art" prompts tools/video-generator/README.md`

Expected: no lines claiming the layout must only use static cover art. Lines that say `cover-art` layout is the compatibility base are acceptable.

- [ ] **Step 6: Commit docs**

```bash
git add prompts/step-7-fetch-cover-art.md prompts/step-8-generate-video.md prompts/references/workspace-conventions.md prompts/README.md tools/video-generator/README.md
git commit -m "docs: describe visual image sequence pipeline"
```

---

### Task 8: Run Full Verification

**Files:**
- No new files.

- [ ] **Step 1: Run all Node tests**

Run: `node --test tools/shared/workspace-root.test.js tools/video-generator/init-video.test.js tools/visual-sequence/visual-sequence.test.js`

Expected: PASS.

- [ ] **Step 2: Type-check Remotion template**

Run from `tools/video-generator/template`: `npx tsc --noEmit`

Expected: PASS.

- [ ] **Step 3: Smoke-test scaffold asset copying with a temporary workspace**

Use the existing `init-video.test.js` coverage as the automated smoke test. If manual verification is needed, create a local workspace with `image-sequence.json` and `stylized-frames/`, run `node tools/video-generator/init-video.js <slug> --design=<path> --image-sequence=<path> --stylized-frames=<path>`, and verify `video/public/image-sequence.json` and `video/public/stylized-frames/` exist.

- [ ] **Step 4: Final status check**

Run: `git status --short`

Expected: only intended files are modified. Do not revert unrelated user changes.

- [ ] **Step 5: Commit final verification fixes if any were needed**

If Step 1 or Step 2 required fixes after the previous task commits, run this command with the complete implementation file set so no verification fix is missed:

```bash
git add tools/visual-sequence/visual-sequence.js tools/visual-sequence/visual-sequence.test.js tools/video-generator/init-video.js tools/video-generator/init-video.test.js tools/video-generator/template/src/utils/imageSequence.ts tools/video-generator/template/src/MusicVideo.tsx tools/video-generator/template/src/layouts/CoverArtLayout.tsx prompts/step-7-fetch-cover-art.md prompts/step-8-generate-video.md prompts/references/workspace-conventions.md prompts/README.md tools/video-generator/README.md
git commit -m "fix: complete visual sequence verification"
```

Only run this commit if verification fixes were actually made.

---

## Self-Review

- Spec coverage: The plan covers original-video source frames, configurable default frame count, evenly spaced selection, source/stylized artifacts, image-sequence manifest, Remotion fallback behavior, and preservation of beat-reactive cover-art behavior.
- Placeholder scan: No `TBD`, `TODO`, or unspecified implementation steps remain. Each code-changing task includes concrete snippets and commands.
- Type consistency: Artifact names match the spec: `visual_frame_count`, `selected-visual-frames.json`, `image-sequence.json`, `source-frames/`, and `stylized-frames/`. Remotion uses `ImageSequence` and `ImageSequenceFrame` consistently.
