#!/usr/bin/env node
/**
 * Initialize a Remotion video project in a workspace.
 *
 * Usage:
 *   node init-video.js <workspace-slug> [--design=<path>]
 *
 * Example:
 *   node init-video.js bella-bella-lofi --design=../../workspaces/bella-bella-lofi/design.json
 *
 * What it does:
 *   1. Copies the template into workspaces/<slug>/video/
 *   2. Detects audio duration from <slug>-remix-v1.mp3 via ffprobe
 *   3. Writes public/video-config.json with duration, title, and genre
 *   4. Copies design.json to public/ folder (if provided)
 *   5. Creates public/ folder ready for asset copy
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const workspaceSlug = process.argv[2];
if (!workspaceSlug) {
  console.error('Usage: node init-video.js <workspace-slug> [--design=<path>]');
  process.exit(1);
}

// Parse optional flags
let designPath = null;
process.argv.slice(3).forEach(arg => {
  if (arg.startsWith('--design=')) designPath = arg.replace('--design=', '');
});

const templateDir = path.join(__dirname, 'template');
const workspaceDir = path.join(__dirname, '..', '..', 'workspaces', workspaceSlug);
const videoDir = path.join(workspaceDir, 'video');

if (!fs.existsSync(workspaceDir)) {
  console.error(`Workspace "${workspaceSlug}" not found in workspaces/`);
  process.exit(1);
}
if (fs.existsSync(videoDir)) {
  console.error(`Video project already exists at ${videoDir}`);
  console.error('Delete it first if you want to re-initialize.');
  process.exit(1);
}

// ---------------------------------------------------------------------------
// Read workspace metadata
// ---------------------------------------------------------------------------
const metadataPath = path.join(workspaceDir, 'meta.json');
let songTitle = workspaceSlug;
let genre = 'unknown';
if (fs.existsSync(metadataPath)) {
  const meta = JSON.parse(fs.readFileSync(metadataPath, 'utf-8'));
  songTitle = meta.video_title || meta.title || workspaceSlug;
  genre = meta.genre || 'unknown';
}

// ---------------------------------------------------------------------------
// Detect audio duration via ffprobe
// ---------------------------------------------------------------------------
const audioFile = path.join(workspaceDir, `${workspaceSlug}-remix-v1.mp3`);
let audioDuration = 180; // fallback: 3 minutes

if (fs.existsSync(audioFile)) {
  try {
    const raw = execSync(
      `ffprobe -i "${audioFile}" -show_entries format=duration -v quiet -of csv=p=0`,
      { encoding: 'utf-8' }
    ).trim();
    const parsed = parseFloat(raw);
    if (!isNaN(parsed)) audioDuration = parsed;
    console.log(`Audio duration: ${audioDuration.toFixed(3)}s`);
  } catch {
    console.warn(`ffprobe failed — defaulting to ${audioDuration}s. Edit video-config.json to fix.`);
  }
} else {
  console.warn(`Audio file not found: ${audioFile}`);
  console.warn(`Defaulting to ${audioDuration}s. Edit video-config.json to fix.`);
}

// ---------------------------------------------------------------------------
// Copy template and substitute placeholders
// ---------------------------------------------------------------------------
console.log(`Scaffolding video project for "${workspaceSlug}"...`);
fs.cpSync(templateDir, videoDir, { recursive: true });
fs.mkdirSync(path.join(videoDir, 'public'), { recursive: true });

// Write video-config.json (read at runtime by Root.tsx)
const videoConfigPath = path.join(videoDir, 'public', 'video-config.json');
fs.writeFileSync(videoConfigPath, JSON.stringify({
  audioDuration: parseFloat(audioDuration.toFixed(3)),
  songTitle,
  genre,
}, null, 2));
console.log(`Video config written: ${videoConfigPath}`);

// ---------------------------------------------------------------------------
// Copy design.json if provided
// ---------------------------------------------------------------------------
if (designPath) {
  const designSourcePath = path.resolve(designPath);
  if (fs.existsSync(designSourcePath)) {
    const designDestPath = path.join(videoDir, 'public', 'design.json');
    fs.copyFileSync(designSourcePath, designDestPath);
    console.log(`Design config copied: ${designSourcePath} → ${designDestPath}`);
  } else {
    console.warn(`Design file not found: ${designSourcePath}`);
    console.warn('Video will use default design settings.');
  }
} else {
  console.log('No design.json provided — video will use default settings.');
}

// ---------------------------------------------------------------------------
// Done
// ---------------------------------------------------------------------------
console.log(`Video project created at: ${videoDir}`);
console.log('');
console.log('Next steps:');
console.log(`  cd ${path.relative(process.cwd(), videoDir)} && npm install`);
console.log('');
console.log('Copy assets to public/:');
console.log(`  cp workspaces/${workspaceSlug}/${workspaceSlug}-remix-v1.mp3  workspaces/${workspaceSlug}/video/public/audio.mp3`);
console.log(`  cp workspaces/${workspaceSlug}/lyrics-timestamps.json          workspaces/${workspaceSlug}/video/public/`);
console.log('');
console.log('Render:');
console.log(`  npx remotion render MusicVideo out/video.mp4`);
