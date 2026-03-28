# Video Generator

Remotion-based video generation for music remixes with **audio-reactive visuals** and **AI-generated design configurations**.

## Features

- **Audio-Reactive Visuals**: Real frequency analysis drives visualizer bars, background pulses, and animated motifs
- **LLM-Generated Designs**: Each song gets a unique visual identity based on genre, mood, and tempo
- **5 Layout Variants**: center-stage, full-bleed, minimal, sidebar, stacked
- **6 Visual Motifs**: particles, geometric-burst, aurora, waveform-rings, noise-field, frequency-bars
- **Seeded Randomness**: Same song always gets the same visual layout

## Architecture

```
meta.json → generate-design.js → design.json
                                     ↓
init-video.js → Remotion template
                    ↓
              MusicVideo.tsx
                    ↓
              ├─ useAudioData() → frequency data
              ├─ load design.json → layout + motif + colors
              └─ Render layout variant with audio-reactive components
```

## Structure

```
tools/video-generator/
├── README.md
├── init-video.js              # Scaffold video project with design.json
├── generate-design.js         # Generate design.json from meta.json
├── template/                  # Base Remotion project template
│   ├── package.json
│   ├── tsconfig.json
│   └── src/
│       ├── index.tsx
│       ├── Root.tsx           # Composition config
│       ├── MusicVideo.tsx     # Main video component (audio-reactive)
│       ├── components/        # Visual motif components
│       │   ├── ParticleField.tsx
│       │   ├── GeometricBurst.tsx
│       │   ├── AuroraBackground.tsx
│       │   ├── WaveformRings.tsx
│       │   ├── NoiseField.tsx
│       │   └── FrequencyBarsVisualizer.tsx
│       ├── layouts/           # Layout variants
│       │   ├── CenterStageLayout.tsx
│       │   ├── FullBleedLayout.tsx
│       │   ├── MinimalLayout.tsx
│       │   ├── SidebarLayout.tsx
│       │   └── StackedLayout.tsx
│       └── utils/
│           ├── seededRandom.ts
│           ├── audioUtils.ts
│           └── designLoader.ts
└── shared-components/
```

## Usage

### Step 1: Generate Design Configuration

```bash
cd tools/video-generator
node generate-design.js <workspace-slug>

# Example:
node generate-design.js bella-bella-lofi
# Creates: workspaces/bella-bella-lofi/design.json
```

This generates a unique design based on the song's metadata (genre, mood, tempo, language).

### Step 2: Scaffold Video Project

```bash
node init-video.js <workspace-slug> --design=../../workspaces/<slug>/design.json

# Example:
node init-video.js bella-bella-lofi --design=../../workspaces/bella-bella-lofi/design.json
```

### Step 3: Copy Assets

```bash
cp workspaces/<slug>/<slug>-remix-v1.mp3  workspaces/<slug>/video/public/audio.mp3
cp workspaces/<slug>/lyrics-timestamps.json workspaces/<slug>/video/public/
# design.json is automatically copied by init-video.js
```

### Step 4: Render

```bash
cd workspaces/<slug>/video
npm install
npx remotion render MusicVideo out/video.mp4
```

## Design Configuration (design.json)

```json
{
  "palette": {
    "backgroundType": "gradient",
    "backgroundStops": [
      { "color": "#1a1a2e", "position": "0%" },
      { "color": "#0f3460", "position": "100%" }
    ],
    "backgroundAngle": 135,
    "primaryColor": "#ffffff",
    "secondaryColor": "#b2bec3",
    "accentColor": "#74b9ff",
    "highlightColor": "#ff7675",
    "glowColor": "#74b9ff40"
  },
  "typography": {
    "googleFont": "Space Grotesk",
    "mainLyricSize": 80,
    "mainLyricWeight": 700,
    "mainLyricItalic": false,
    "letterSpacing": "0.02em",
    "textEffect": "glow",
    "sectionBadgeStyle": "pill"
  },
  "layout": {
    "variant": "center-stage",
    "showSectionBadge": true,
    "showNextLyric": true,
    "showProgressBar": true,
    "visualizerPosition": "bottom"
  },
  "motif": {
    "primary": "particles",
    "secondary": "noise-field",
    "intensity": "medium"
  },
  "animation": {
    "personality": "smooth",
    "lyricEntrance": "slide-up",
    "beatReactivity": 0.8
  },
  "seed": 12345
}
```

## Layout Variants

| Layout | Description | Best For |
|--------|-------------|----------|
| `center-stage` | Lyrics centered, visualizer at bottom | All genres (default) |
| `full-bleed` | Motif fills background behind lyrics | EDM, pop, energetic |
| `minimal` | Large lyrics, no visualizer, thin progress | Classical, ballads, carnatic |
| `sidebar` | Lyrics left (55%), motif right (45%) | Hiphop, chill, lo-fi |
| `stacked` | Title top, lyrics middle, visualizer bottom | Pop, standard karaoke |

## Visual Motifs

| Motif | Description | Reactivity |
|-------|-------------|------------|
| `particles` | Floating dots that drift and pulse | Bass = size/opacity, Highs = jitter |
| `geometric-burst` | Rotating polygons centered on screen | Bass = scale, Mid = rotation speed |
| `aurora` | Animated turbulence gradient overlay | Bass = opacity |
| `waveform-rings` | Expanding concentric circles | Triggered by bass transients |
| `noise-field` | Subtle animated noise texture | Bass = opacity |
| `frequency-bars` | 32-bar spectrum visualizer | Direct frequency mapping |

## Animation Personalities

| Personality | Easing | Beat Response | Best For |
|-------------|--------|---------------|----------|
| `smooth` | Bezier(0.4, 0, 0.2, 1) | Soft | Most genres |
| `bouncy` | Spring | Punchy | Pop, EDM |
| `sharp` | Linear | Hard cut | Hiphop, trap |
| `dreamy` | Bezier(0.8, 0, 0.2, 1) | None | Lo-fi, ballads |
| `aggressive` | Bezier(0.9, 0, 0.1, 1) | Strobe | Metal, dubstep |

## Available Fonts

Fonts are loaded from Google Fonts at render time:

- **Cinematic**: Playfair Display, Cormorant Garamond, Bebas Neue
- **Modern**: Space Grotesk, Inter, DM Sans, Outfit
- **Energetic**: Exo 2, Orbitron, Rajdhani
- **Warm**: Lora, Merriweather, Crimson Pro

**Note**: Indic scripts (Telugu, Hindi, Tamil) automatically fall back to Noto Sans.

## Development

### Preview Video

```bash
cd workspaces/<slug>/video
npm run dev      # Opens Remotion Studio at http://localhost:3000
```

### Customize Design

Edit `workspaces/<slug>/design.json` and re-render:

```bash
cd workspaces/<slug>/video
npx remotion render MusicVideo out/video.mp4
```

### Test Audio Reactivity

The Remotion Studio shows real-time preview with actual frequency data. Visuals will
react to the audio when scrubbing through the timeline.

## Frequency Band Mapping

Frequency data is split into bands for different visual effects:

| Band | Bins | Drives |
|------|------|--------|
| Bass | 0-3 | Background pulse, beat flash, ring expansion |
| Low-mid | 4-15 | Main visualizer bars |
| High-mid | 16-31 | Particle speed, geometric rotation |
| Highs | 32-63 | Shimmer, glow intensity |

## Rendering Options

```bash
# High quality (slower)
npx remotion render MusicVideo out/video.mp4 --quality=high

# H265 codec (smaller file)
npx remotion render MusicVideo out/video.mp4 --codec=h265

# Specific frame range
npx remotion render MusicVideo out/video.mp4 --frames=0-900
```

## Integration with Remix Pipeline

This is automatically called as part of Step 6 (Generate Video):

1. Extract acapella from remix audio
2. Generate lyrics timestamps via CTC alignment
3. **Generate design.json from meta.json** ← NEW
4. Scaffold video project with design
5. Copy assets (audio, lyrics, design)
6. Render video

See `prompts/step-6-generate-video.md` for full workflow.

## Migration from Old Themes

The old hardcoded themes (lofi, edm, hiphop, etc.) are replaced by dynamic design.json
generation. The `generate-design.js` script creates appropriate designs based on genre
and mood metadata.

To migrate existing projects:
1. Run `generate-design.js` to create design.json
2. Re-run `init-video.js` with `--design` flag
3. Re-render
