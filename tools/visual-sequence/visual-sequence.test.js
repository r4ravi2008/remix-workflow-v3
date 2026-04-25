const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const {
  resolveFrameCount,
  generateEvenTimestamps,
  buildSelectedFrames,
  buildImageSequence,
  parseArgs,
  resolveWorkspacePaths,
  getMediaDurationSeconds,
  extractVisualFrames,
  createImageSequence,
} = require('./visual-sequence');

function makeFixture(t, {slug = 'bella-bella-lofi', meta = {}} = {}) {
  const repoRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'visual-sequence-repo-'));
  t.after(() => fs.rmSync(repoRoot, {recursive: true, force: true}));

  fs.mkdirSync(path.join(repoRoot, '.git'));
  const workspaceRoot = path.join(repoRoot, 'workspaces');
  const workspaceDir = path.join(workspaceRoot, slug);
  fs.mkdirSync(workspaceDir, {recursive: true});
  fs.writeFileSync(path.join(repoRoot, '.remix-workspace-root.json'), JSON.stringify({workspaceRoot}, null, 2));
  fs.writeFileSync(path.join(workspaceDir, 'meta.json'), `${JSON.stringify(meta, null, 2)}\n`);

  return {repoRoot, workspaceRoot, workspaceDir, slug, paths: resolveWorkspacePaths(workspaceDir, slug)};
}

function writeFixtureJson(filePath, value) {
  fs.writeFileSync(filePath, `${JSON.stringify(value, null, 2)}\n`);
}

function readFixtureJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function selectedFramesFixture(slug, count = 3) {
  return {
    version: 1,
    source_video: `${slug}/${slug}-original-video.mp4`,
    requested_count: count,
    selected_count: count,
    frames: Array.from({length: count}, (_, index) => {
      const id = `frame-${String(index + 1).padStart(3, '0')}`;
      return {
        id,
        source_timestamp: index + 1,
        requested_timestamp: index + 1,
        source_image_path: `source-frames/${slug}-${id}.jpg`,
      };
    }),
  };
}

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

test('buildSelectedFrames creates chronological source frame records', () => {
  const result = buildSelectedFrames({
    slug: 'bella-bella-lofi',
    sourceVideo: 'bella-bella-lofi/bella-bella-lofi-original-video.mp4',
    requestedCount: 3,
    timestamps: [2, 6, 10],
    extractedFrames: [
      {index: 3, requestedTimestamp: 10, resolvedTimestamp: 10, sourceImagePath: 'source-frames/bella-bella-lofi-frame-003.jpg'},
      {index: 1, requestedTimestamp: 2, resolvedTimestamp: 2.04, sourceImagePath: 'source-frames/bella-bella-lofi-frame-001.jpg'},
      {index: 2, requestedTimestamp: 6, resolvedTimestamp: 6.01, sourceImagePath: 'source-frames/bella-bella-lofi-frame-002.jpg'},
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

test('buildImageSequence rejects selected frames with no frames', () => {
  assert.throws(() => buildImageSequence({
    slug: 'bella-bella-lofi',
    selectedFrames: {
      version: 1,
      source_video: 'bella-bella-lofi/bella-bella-lofi-original-video.mp4',
      requested_count: 3,
      selected_count: 0,
      frames: [],
    },
    audioDuration: 90,
  }), /selectedFrames must contain at least one frame/);
});

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
  assert.throws(() => parseArgs(['extract', 'bella-bella-lofi', '--frame-count=2.5']), /frame-count must be a positive integer/);
  assert.throws(() => parseArgs(['extract', 'bella-bella-lofi', '--frame-count=24abc']), /frame-count must be a positive integer/);
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

test('getMediaDurationSeconds parses ffprobe output and rejects invalid output', () => {
  const calls = [];
  const duration = getMediaDurationSeconds('/tmp/song.mp3', (command, args, options) => {
    calls.push({command, args, options});
    assert.equal(command, 'ffprobe');
    assert.deepEqual(args, ['-v', 'quiet', '-show_entries', 'format=duration', '-of', 'csv=p=0', '/tmp/song.mp3']);
    return '60\n';
  });

  assert.equal(duration, 60);
  assert.equal(calls.length, 1);
  assert.throws(() => getMediaDurationSeconds('/tmp/bad.mp3', () => 'not-a-duration\n'), /Could not determine media duration/);
});

test('extractVisualFrames downloads video, extracts frames, and updates workspace manifests', t => {
  const fixture = makeFixture(t, {
    meta: {
      youtube_url: 'https://youtu.be/example',
      visual_frame_count: 3,
      files: {},
      status: {},
    },
  });
  const calls = [];
  const execFileSyncImpl = (command, args) => {
    calls.push({command, args});
    if (command === 'yt-dlp') {
      assert.equal(args.at(-1), 'https://youtu.be/example');
      assert.equal(args[args.indexOf('-o') + 1], fixture.paths.originalVideoPath);
      return '';
    }
    if (command === 'ffprobe') {
      assert.equal(args.at(-1), fixture.paths.originalVideoPath);
      return '60\n';
    }
    if (command === 'ffmpeg') {
      assert.equal(args[args.indexOf('-i') + 1], fixture.paths.originalVideoPath);
      const outputPath = args.at(-1);
      fs.mkdirSync(path.dirname(outputPath), {recursive: true});
      fs.writeFileSync(outputPath, 'frame');
      return '';
    }
    throw new Error(`Unexpected command: ${command}`);
  };

  const result = extractVisualFrames({
    workspaceSlug: fixture.slug,
    frameCountOverride: 2,
    repoRoot: fixture.repoRoot,
    execFileSyncImpl,
    logger: {log() {}, warn() {}},
  });

  assert.equal(result.candidates.requested_count, 2);
  assert.equal(result.selectedFrames.selected_count, 2);
  assert.equal(fs.existsSync(fixture.paths.candidatesPath), true);
  assert.equal(fs.existsSync(fixture.paths.selectedFramesPath), true);
  assert.equal(fs.existsSync(path.join(fixture.paths.sourceFramesDir, `${fixture.slug}-frame-001.jpg`)), true);
  assert.equal(fs.existsSync(path.join(fixture.paths.sourceFramesDir, `${fixture.slug}-frame-002.jpg`)), true);

  const meta = readFixtureJson(fixture.paths.metaPath);
  assert.equal(meta.visual_frame_count, 2);
  assert.equal(meta.files.original_video, `${fixture.slug}/${fixture.slug}-original-video.mp4`);
  assert.equal(meta.files.visual_frame_candidates, `${fixture.slug}/visual-frame-candidates.json`);
  assert.equal(meta.files.selected_visual_frames, `${fixture.slug}/selected-visual-frames.json`);
  assert.equal(meta.status.original_video_downloaded, true);
  assert.equal(meta.status.visual_frames_extracted, true);
  assert.equal(meta.status.visual_frames_selected, true);
  assert.deepEqual(calls.map(call => call.command), ['yt-dlp', 'ffprobe', 'ffmpeg', 'ffmpeg']);
});

test('createImageSequence rejects missing or invalid selected remix', t => {
  const missing = makeFixture(t, {meta: {files: {}, status: {}}});
  writeFixtureJson(missing.paths.selectedFramesPath, selectedFramesFixture(missing.slug));
  fs.mkdirSync(missing.paths.stylizedFramesDir, {recursive: true});
  fs.writeFileSync(path.join(missing.paths.stylizedFramesDir, `${missing.slug}-frame-001.jpg`), 'frame');

  assert.throws(() => createImageSequence({
    workspaceSlug: missing.slug,
    repoRoot: missing.repoRoot,
    execFileSyncImpl: () => '90\n',
    logger: {log() {}},
  }), /meta\.json status\.selected_remix must be v1 or v2/);

  const invalid = makeFixture(t, {meta: {files: {}, status: {selected_remix: 'v3'}}});
  writeFixtureJson(invalid.paths.selectedFramesPath, selectedFramesFixture(invalid.slug));
  fs.mkdirSync(invalid.paths.stylizedFramesDir, {recursive: true});
  fs.writeFileSync(path.join(invalid.paths.stylizedFramesDir, `${invalid.slug}-frame-001.jpg`), 'frame');

  assert.throws(() => createImageSequence({
    workspaceSlug: invalid.slug,
    repoRoot: invalid.repoRoot,
    execFileSyncImpl: () => '90\n',
    logger: {log() {}},
  }), /meta\.json status\.selected_remix must be v1 or v2/);
});

test('createImageSequence filters missing stylized frame files from manifest', t => {
  const fixture = makeFixture(t, {meta: {files: {}, status: {selected_remix: 'v2'}}});
  writeFixtureJson(fixture.paths.selectedFramesPath, selectedFramesFixture(fixture.slug, 3));
  fs.mkdirSync(fixture.paths.stylizedFramesDir, {recursive: true});
  fs.writeFileSync(path.join(fixture.paths.stylizedFramesDir, `${fixture.slug}-frame-001.jpg`), 'frame');
  fs.writeFileSync(path.join(fixture.paths.stylizedFramesDir, `${fixture.slug}-frame-003.jpg`), 'frame');

  const calls = [];
  const result = createImageSequence({
    workspaceSlug: fixture.slug,
    repoRoot: fixture.repoRoot,
    execFileSyncImpl: (command, args) => {
      calls.push({command, args});
      assert.equal(command, 'ffprobe');
      assert.equal(args.at(-1), path.join(fixture.workspaceDir, `${fixture.slug}-remix-v2.mp3`));
      return '90\n';
    },
    logger: {log() {}},
  });

  assert.deepEqual(result.sequence.frames.map(frame => frame.id), ['frame-001', 'frame-003']);
  assert.deepEqual(result.sequence.frames.map(frame => frame.image_path), [
    `stylized-frames/${fixture.slug}-frame-001.jpg`,
    `stylized-frames/${fixture.slug}-frame-003.jpg`,
  ]);
  assert.deepEqual(result.sequence.frames.map(frame => [frame.start_time, frame.end_time]), [[0, 45], [45, 90]]);
  assert.deepEqual(readFixtureJson(fixture.paths.imageSequencePath).frames.map(frame => frame.id), ['frame-001', 'frame-003']);

  const meta = readFixtureJson(fixture.paths.metaPath);
  assert.equal(meta.files.image_sequence, `${fixture.slug}/image-sequence.json`);
  assert.equal(meta.status.visual_frames_stylized, true);
  assert.equal(calls.length, 1);
});

test('createImageSequence preserves stylized frame extension in manifest', t => {
  const fixture = makeFixture(t, {meta: {files: {}, status: {selected_remix: 'v1'}}});
  writeFixtureJson(fixture.paths.selectedFramesPath, selectedFramesFixture(fixture.slug, 2));
  fs.mkdirSync(fixture.paths.stylizedFramesDir, {recursive: true});
  fs.writeFileSync(path.join(fixture.paths.stylizedFramesDir, `${fixture.slug}-frame-001.png`), 'frame');

  const result = createImageSequence({
    workspaceSlug: fixture.slug,
    repoRoot: fixture.repoRoot,
    execFileSyncImpl: (command, args) => {
      assert.equal(command, 'ffprobe');
      assert.equal(args.at(-1), path.join(fixture.workspaceDir, `${fixture.slug}-remix-v1.mp3`));
      return '60\n';
    },
    logger: {log() {}},
  });

  assert.deepEqual(result.sequence.frames.map(frame => frame.id), ['frame-001']);
  assert.equal(result.sequence.frames[0].image_path, `stylized-frames/${fixture.slug}-frame-001.png`);
  assert.equal(readFixtureJson(fixture.paths.imageSequencePath).frames[0].image_path, `stylized-frames/${fixture.slug}-frame-001.png`);
});

test('createImageSequence rejects when no stylized frame files exist', t => {
  const fixture = makeFixture(t, {meta: {files: {}, status: {selected_remix: 'v1'}}});
  writeFixtureJson(fixture.paths.selectedFramesPath, selectedFramesFixture(fixture.slug, 2));
  fs.mkdirSync(fixture.paths.stylizedFramesDir, {recursive: true});

  assert.throws(() => createImageSequence({
    workspaceSlug: fixture.slug,
    repoRoot: fixture.repoRoot,
    execFileSyncImpl: () => '90\n',
    logger: {log() {}},
  }), /selectedFrames must contain at least one frame/);
});
