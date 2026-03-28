#!/usr/bin/env node
/**
 * Generate design.json from meta.json
 * 
 * Usage:
 *   node generate-design.js <workspace-slug>
 * 
 * This script reads meta.json and generates a design.json file
 * based on the song's genre, mood, tempo, and language.
 */

const fs = require('fs');
const path = require('path');

const workspaceSlug = process.argv[2];
if (!workspaceSlug) {
  console.error('Usage: node generate-design.js <workspace-slug>');
  process.exit(1);
}

const workspaceDir = path.join(__dirname, '..', '..', 'workspaces', workspaceSlug);
const metaPath = path.join(workspaceDir, 'meta.json');
const designPath = path.join(workspaceDir, 'design.json');

if (!fs.existsSync(metaPath)) {
  console.error(`meta.json not found at ${metaPath}`);
  process.exit(1);
}

// Read meta.json
const meta = JSON.parse(fs.readFileSync(metaPath, 'utf-8'));

// Seeded random number generator
function seededRandom(seed) {
  let s = seed;
  return () => {
    s = (s * 1664525 + 1013904223) & 0xffffffff;
    return (s >>> 0) / 0xffffffff;
  };
}

// Generate seed from slug and duration
const seed = workspaceSlug.length * (meta.duration || 180);
const rng = seededRandom(seed);

// Determine genre category
const genre = (meta.genre || 'unknown').toLowerCase();
const mood = (meta.mood || 'neutral').toLowerCase();
const language = (meta.language || 'unknown').toLowerCase();
const isIndic = ['telugu', 'hindi', 'tamil', 'kannada', 'malayalam', 'sanskrit'].includes(language);

// Design decisions based on genre/mood
function determineDesign() {
  // Genre-based mappings
  const isLofi = genre.includes('lofi') || genre.includes('lo-fi') || mood.includes('chill') || mood.includes('relaxed');
  const isEdm = genre.includes('edm') || genre.includes('electronic') || genre.includes('dance') || genre.includes('house');
  const isHiphop = genre.includes('hiphop') || genre.includes('hip-hop') || genre.includes('rap') || genre.includes('trap');
  const isCarnatic = genre.includes('carnatic') || genre.includes('classical') || genre.includes('devotional');
  const isPop = genre.includes('pop') || genre.includes('bollywood');
  const isAggressive = mood.includes('aggressive') || mood.includes('intense') || mood.includes('energetic');
  const isDreamy = mood.includes('dreamy') || mood.includes('calm') || mood.includes('peaceful');

  // Layout selection
  let layout = 'center-stage';
  if (isEdm && isAggressive) layout = 'full-bleed';
  else if (isHiphop) layout = 'sidebar';
  else if (isCarnatic || isLofi && isDreamy) layout = 'minimal';
  else if (isPop) layout = 'stacked';

  // Motif selection
  let primaryMotif = 'particles';
  if (isEdm) primaryMotif = rng() > 0.5 ? 'aurora' : 'geometric-burst';
  else if (isHiphop) primaryMotif = 'geometric-burst';
  else if (isCarnatic) primaryMotif = 'waveform-rings';
  else if (isLofi) primaryMotif = 'particles';

  // Secondary motif (40% chance of none)
  let secondaryMotif = null;
  if (rng() > 0.4) {
    const options = ['noise-field', 'particles', 'waveform-rings'];
    secondaryMotif = options[Math.floor(rng() * options.length)];
  }

  // Animation personality
  let personality = 'smooth';
  if (isAggressive) personality = 'aggressive';
  else if (isDreamy || isLofi) personality = 'dreamy';
  else if (isPop || isEdm) personality = 'bouncy';
  else if (isHiphop) personality = 'sharp';

  // Font selection
  let googleFont = 'Space Grotesk';
  if (isCarnatic) googleFont = 'Cormorant Garamond';
  else if (isEdm) googleFont = 'Orbitron';
  else if (isHiphop) googleFont = 'Exo 2';
  else if (isLofi) googleFont = 'Lora';
  else if (isPop) googleFont = 'Space Grotesk';

  // Override for Indic scripts
  if (isIndic) {
    // Keep the chosen font but Noto Sans will be in the fallback stack
  }

  // Color palette
  let palette = generatePalette(genre, mood, rng);

  return {
    layout,
    primaryMotif,
    secondaryMotif,
    personality,
    googleFont,
    palette,
  };
}

function generatePalette(genre, mood, rng) {
  const isDark = mood.includes('dark') || mood.includes('aggressive') || genre.includes('hiphop') || genre.includes('metal');
  const isWarm = mood.includes('warm') || genre.includes('carnatic') || genre.includes('classical');
  const isVibrant = genre.includes('pop') || genre.includes('edm');

  // Background stops
  let bgStops;
  if (isDark) {
    bgStops = [
      { color: '#0a0a0a', position: '0%' },
      { color: '#1a1a2e', position: '100%' },
    ];
  } else if (isWarm) {
    bgStops = [
      { color: '#c9a961', position: '0%' },
      { color: '#8b7355', position: '100%' },
    ];
  } else if (isVibrant) {
    bgStops = [
      { color: '#ff6b6b', position: '0%' },
      { color: '#feca57', position: '50%' },
      { color: '#48dbfb', position: '100%' },
    ];
  } else {
    // Default cool gradient
    bgStops = [
      { color: '#1a1a2e', position: '0%' },
      { color: '#16213e', position: '50%' },
      { color: '#0f3460', position: '100%' },
    ];
  }

  // Accent colors
  let accentColor, highlightColor;
  if (isDark) {
    accentColor = ['#ff6b35', '#ff7675', '#a29bfe'][Math.floor(rng() * 3)];
    highlightColor = ['#fdcb6e', '#fab1a0', '#74b9ff'][Math.floor(rng() * 3)];
  } else if (isWarm) {
    accentColor = '#d4af37';
    highlightColor = '#8b4513';
  } else if (isVibrant) {
    accentColor = '#ff9ff3';
    highlightColor = '#6c5ce7';
  } else {
    accentColor = '#74b9ff';
    highlightColor = '#ff7675';
  }

  return {
    backgroundStops: bgStops,
    accentColor,
    highlightColor,
  };
}

// Generate the design
const designChoices = determineDesign();

// Build design.json
const design = {
  palette: {
    backgroundType: 'gradient',
    backgroundStops: designChoices.palette.backgroundStops,
    backgroundAngle: Math.floor(90 + rng() * 90), // 90-180 degrees
    primaryColor: '#ffffff',
    secondaryColor: '#b2bec3',
    accentColor: designChoices.palette.accentColor,
    highlightColor: designChoices.palette.highlightColor,
    glowColor: `${designChoices.palette.accentColor}40`,
  },
  typography: {
    googleFont: designChoices.googleFont,
    mainLyricSize: Math.floor(70 + rng() * 30), // 70-100
    mainLyricWeight: [400, 600, 700, 800][Math.floor(rng() * 4)],
    mainLyricItalic: rng() > 0.7,
    letterSpacing: `${(rng() * 0.04).toFixed(3)}em`, // 0-0.04em
    textEffect: ['glow', 'shadow', 'none'][Math.floor(rng() * 3)],
    sectionBadgeStyle: ['pill', 'box'][Math.floor(rng() * 2)],
  },
  layout: {
    variant: designChoices.layout,
    showSectionBadge: true,
    showNextLyric: rng() > 0.2, // 80% chance
    showProgressBar: true,
    visualizerPosition: designChoices.layout === 'minimal' ? 'hidden' : 'bottom',
  },
  motif: {
    primary: designChoices.primaryMotif,
    secondary: designChoices.secondaryMotif,
    intensity: ['low', 'medium', 'high'][Math.floor(rng() * 3)],
  },
  animation: {
    personality: designChoices.personality,
    lyricEntrance: ['fade', 'slide-up', 'scale-in'][Math.floor(rng() * 3)],
    beatReactivity: 0.5 + rng() * 0.5, // 0.5-1.0
  },
  seed: seed,
};

// Write design.json
fs.writeFileSync(designPath, JSON.stringify(design, null, 2));
console.log(`Design generated: ${designPath}`);
console.log(`  Layout: ${design.layout.variant}`);
console.log(`  Motif: ${design.motif.primary}${design.motif.secondary ? ' + ' + design.motif.secondary : ''}`);
console.log(`  Font: ${design.typography.googleFont}`);
console.log(`  Personality: ${design.animation.personality}`);
