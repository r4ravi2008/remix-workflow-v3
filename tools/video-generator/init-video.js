#!/usr/bin/env node
const fs = require('node:fs');
const path = require('node:path');
const {execSync} = require('node:child_process');

const {resolveWorkspaceDir} = require('../shared/workspace-root');

function parseArgs(argv) {
  const workspaceSlug = argv[0];
  if (!workspaceSlug) {
    throw new Error('Usage: node init-video.js <workspace-slug> [--design=<path>] [--image-sequence=<path>] [--stylized-frames=<path>]');
  }

  let designPath = null;
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
}

function initializeVideoProject(options) {
  const {
    workspaceSlug,
    designPath = null,
    imageSequencePath = null,
    stylizedFramesDir = null,
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
  let selectedRemix = 'v1';

  if (fs.existsSync(metadataPath)) {
    const meta = JSON.parse(fs.readFileSync(metadataPath, 'utf8'));
    songTitle = meta.video_title || meta.title || workspaceSlug;
    genre = meta.genre || 'unknown';
    selectedRemix = meta.status?.selected_remix || 'v1';
  }

  const audioFile = path.join(workspaceDir, `${workspaceSlug}-remix-${selectedRemix}.mp3`);
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
    if (fs.existsSync(designSourcePath) && fs.statSync(designSourcePath).isFile()) {
      fs.copyFileSync(designSourcePath, path.join(videoDir, 'public', 'design.json'));
    } else {
      logger.warn(`Design file not found: ${designSourcePath}`);
      logger.warn('Video will use default design settings.');
    }
  } else {
    logger.log('No design.json provided. Video will use default settings.');
  }

  if (imageSequencePath) {
    const sequenceSourcePath = path.resolve(imageSequencePath);
    if (fs.existsSync(sequenceSourcePath) && fs.statSync(sequenceSourcePath).isFile()) {
      fs.copyFileSync(sequenceSourcePath, path.join(videoDir, 'public', 'image-sequence.json'));
    } else {
      logger.warn(`Image sequence file not found: ${sequenceSourcePath}`);
    }
  }

  if (stylizedFramesDir) {
    const framesSourceDir = path.resolve(stylizedFramesDir);
    if (fs.existsSync(framesSourceDir) && fs.statSync(framesSourceDir).isDirectory()) {
      fs.cpSync(framesSourceDir, path.join(videoDir, 'public', 'stylized-frames'), {recursive: true});
    } else {
      logger.warn(`Stylized frames directory not found: ${framesSourceDir}`);
    }
  }

  logger.log(`Video project created at: ${videoDir}`);
  logger.log('Next steps:');
  logger.log(`  cd ${path.relative(processCwd, videoDir)} && npm install`);
  logger.log(`  cp "${path.join(workspaceDir, `${workspaceSlug}-remix-${selectedRemix}.mp3`)}" "${path.join(videoDir, 'public', 'audio.mp3')}"`);
  logger.log(`  cp "${path.join(workspaceDir, 'lyrics-timestamps.json')}" "${path.join(videoDir, 'public')}"`);
  logger.log(`  [ -f "${path.join(workspaceDir, 'image-sequence.json')}" ] && cp "${path.join(workspaceDir, 'image-sequence.json')}" "${path.join(videoDir, 'public', 'image-sequence.json')}"`);
  logger.log(`  [ -d "${path.join(workspaceDir, 'stylized-frames')}" ] && cp -R "${path.join(workspaceDir, 'stylized-frames')}" "${path.join(videoDir, 'public', 'stylized-frames')}"`);
  logger.log('  npx remotion render MusicVideo out/video.mp4');

  return {workspaceDir, videoDir, videoConfigPath};
}

function main(argv = process.argv.slice(2)) {
  const {workspaceSlug, designPath, imageSequencePath, stylizedFramesDir} = parseArgs(argv);
  return initializeVideoProject({workspaceSlug, designPath, imageSequencePath, stylizedFramesDir});
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
