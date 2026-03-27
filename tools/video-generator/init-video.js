#!/usr/bin/env node
/**
 * Initialize a Remotion video project in a workspace.
 *
 * Usage:
 *   node init-video.js <workspace-slug> [--theme=<theme>]
 *
 * Example:
 *   node init-video.js bella-bella-lofi --theme=lofi
 *
 * What it does:
 *   1. Copies the template into workspaces/<slug>/video/
 *   2. Detects audio duration from <slug>-remix-v1.mp3 via ffprobe
 *   3. Substitutes all {{PLACEHOLDERS}} in Root.tsx and MusicVideo.tsx
 *   4. Creates public/ folder ready for asset copy
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const workspaceSlug = process.argv[2];
if (!workspaceSlug) {
  console.error('Usage: node init-video.js <workspace-slug> [--theme=<theme>]');
  process.exit(1);
}

// Parse optional flags
let theme = 'default';
process.argv.slice(3).forEach(arg => {
  if (arg.startsWith('--theme=')) theme = arg.replace('--theme=', '');
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
  // Use genre as theme if no explicit --theme was given
  if (theme === 'default' && meta.genre) {
    theme = meta.genre.toLowerCase().replace(/[^a-z]/g, '') || 'default';
  }
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
    console.warn(`ffprobe failed — defaulting to ${audioDuration}s. Set AUDIO_DURATION manually in Root.tsx.`);
  }
} else {
  console.warn(`Audio file not found: ${audioFile}`);
  console.warn(`Defaulting to ${audioDuration}s. Set AUDIO_DURATION manually in Root.tsx.`);
}

// ---------------------------------------------------------------------------
// Theme configuration
// ---------------------------------------------------------------------------
const themes = {
  lofi:     { background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)', primaryColor: '#e8e8e8', accentColor: '#74b9ff', highlightColor: '#ff7675', sectionBackground: 'rgba(116, 185, 255, 0.15)' },
  chill:    { background: 'linear-gradient(135deg, #a8e6cf 0%, #dcedc1 100%)',              primaryColor: '#2d3436', accentColor: '#ff8b94', highlightColor: '#e17055', sectionBackground: 'rgba(255, 139, 148, 0.15)' },
  edm:      { background: 'linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 100%)',              primaryColor: '#ffffff', accentColor: '#00d2ff', highlightColor: '#a29bfe', sectionBackground: 'rgba(0, 210, 255, 0.1)' },
  hiphop:   { background: 'linear-gradient(135deg, #1a1a1a 0%, #4a4a4a 100%)',              primaryColor: '#f1f1f1', accentColor: '#ff6b35', highlightColor: '#fdcb6e', sectionBackground: 'rgba(255, 107, 53, 0.1)' },
  carnatic: { background: 'linear-gradient(135deg, #c9a961 0%, #8b7355 100%)',              primaryColor: '#2c2416', accentColor: '#d4af37', highlightColor: '#8b4513', sectionBackground: 'rgba(212, 175, 55, 0.15)' },
  pop:      { background: 'linear-gradient(135deg, #ff6b6b 0%, #feca57 50%, #48dbfb 100%)',primaryColor: '#2d3436', accentColor: '#ff9ff3', highlightColor: '#6c5ce7', sectionBackground: 'rgba(255, 159, 243, 0.15)' },
  default:  { background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',              primaryColor: '#ffffff', accentColor: '#74b9ff', highlightColor: '#ff7675', sectionBackground: 'rgba(116, 185, 255, 0.15)' },
};
const selectedTheme = themes[theme] || themes.default;

// ---------------------------------------------------------------------------
// Copy template and substitute placeholders
// ---------------------------------------------------------------------------
console.log(`Scaffolding video project for "${workspaceSlug}" (theme: ${theme})...`);
fs.cpSync(templateDir, videoDir, { recursive: true });
fs.mkdirSync(path.join(videoDir, 'public'), { recursive: true });

// Root.tsx substitutions
const rootPath = path.join(videoDir, 'src', 'Root.tsx');
let root = fs.readFileSync(rootPath, 'utf-8');
root = root
  .replace(/\{\{AUDIO_DURATION\}\}/g, audioDuration.toFixed(3))
  .replace(/\{\{SONG_TITLE\}\}/g, songTitle)
  .replace(/\{\{THEME\}\}/g, theme)
  .replace(/\{\{GENRE\}\}/g, genre);
fs.writeFileSync(rootPath, root);

// MusicVideo.tsx has no placeholders — it reads theme from props passed by Root.tsx.
// (Theme colors are resolved at runtime from the themes map in MusicVideo.tsx.)

// Write theme.json for reference
fs.writeFileSync(
  path.join(videoDir, 'public', 'theme.json'),
  JSON.stringify({ theme, genre, ...selectedTheme }, null, 2)
);

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
