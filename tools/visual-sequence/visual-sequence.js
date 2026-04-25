#!/usr/bin/env node
const fs = require('node:fs');
const path = require('node:path');
const {execFileSync} = require('node:child_process');

const {resolveWorkspaceDir} = require('../shared/workspace-root');

const STYLIZED_FRAME_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp'];

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
      const rawFrameCount = arg.replace('--frame-count=', '');
      if (!/^[1-9]\d*$/.test(rawFrameCount)) {
        throw new Error('frame-count must be a positive integer.');
      }
      frameCountOverride = Number.parseInt(rawFrameCount, 10);
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

function frameId(index) {
  return `frame-${String(index).padStart(3, '0')}`;
}

function buildSelectedFrames({sourceVideo, requestedCount, extractedFrames}) {
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
  if (frames.length === 0) {
    throw new Error('selectedFrames must contain at least one frame.');
  }

  const segmentDuration = audioDuration / frames.length;

  return {
    version: 1,
    source: {
      video: selectedFrames.source_video,
      selection: 'evenly-spaced',
      requested_count: selectedFrames.requested_count,
    },
    frames: frames.map((frame, index) => ({
      id: frame.id,
      image_path: frame.stylized_image_path || `stylized-frames/${slug}-${frame.id}.jpg`,
      source_timestamp: frame.source_timestamp,
      start_time: Number((index * segmentDuration).toFixed(3)),
      end_time: Number(((index + 1) * segmentDuration).toFixed(3)),
      transition: 'crossfade',
    })),
  };
}

function findStylizedFramePath({stylizedFramesDir, slug, frameId: selectedFrameId}) {
  for (const extension of STYLIZED_FRAME_EXTENSIONS) {
    const fileName = `${slug}-${selectedFrameId}${extension}`;
    const absolutePath = path.join(stylizedFramesDir, fileName);
    if (fs.existsSync(absolutePath)) {
      return {
        absolutePath,
        relativePath: `stylized-frames/${fileName}`,
      };
    }
  }

  return null;
}

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
    sourceVideo,
    requestedCount,
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
  const selectedRemix = meta.status?.selected_remix;
  if (!['v1', 'v2'].includes(selectedRemix)) {
    throw new Error('meta.json status.selected_remix must be v1 or v2');
  }
  const audioPath = path.join(workspaceDir, `${workspaceSlug}-remix-${selectedRemix}.mp3`);
  const audioDuration = getMediaDurationSeconds(audioPath, execFileSyncImpl);
  const selectedFrames = readJson(paths.selectedFramesPath);
  const stylizedFrames = (selectedFrames.frames || []).flatMap(frame => {
    const stylizedFramePath = findStylizedFramePath({
      stylizedFramesDir: paths.stylizedFramesDir,
      slug: workspaceSlug,
      frameId: frame.id,
    });
    if (!stylizedFramePath) {
      return [];
    }
    return [{...frame, stylized_image_path: stylizedFramePath.relativePath}];
  });
  const sequence = buildImageSequence({
    slug: workspaceSlug,
    selectedFrames: {
      ...selectedFrames,
      selected_count: stylizedFrames.length,
      frames: stylizedFrames,
    },
    audioDuration,
  });

  writeJson(paths.imageSequencePath, sequence);
  updateMeta(paths.metaPath, current => ({
    ...current,
    files: {
      ...current.files,
      image_sequence: `${workspaceSlug}/image-sequence.json`,
    },
    status: {
      ...current.status,
      visual_frames_stylized: sequence.frames.length > 0,
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

module.exports = {
  resolveFrameCount,
  generateEvenTimestamps,
  buildSelectedFrames,
  buildImageSequence,
  parseArgs,
  resolveWorkspacePaths,
  getMediaDurationSeconds,
  extractVisualFrames,
  createImageSequence,
  findStylizedFramePath,
  main,
  readJson,
  writeJson,
};
