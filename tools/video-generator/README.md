# Video Generator

Remotion-based video generation for music remixes with **audio-reactive visuals** and **AI-generated design configurations**.

## Features

- **Audio-Reactive Visuals**: Real frequency analysis drives visualizer bars, background pulses, and animated motifs
- **LLM-Generated Designs**: Each song gets a unique visual identity based on genre, mood, and tempo
- **5 Layout Variants**: center-stage, full-bleed, minimal, sidebar, stacked
- **6 Visual Motifs**: particles, geometric-burst, aurora, waveform-rings, noise-field, frequency-bars
- **Dynamic Color Palette**: Colors are generated based on Suno style descriptors (dark, warm, dreamy, etc.)

## Architecture

```
Step 4: Generate Suno Lyrics
    ↓
Generate design.json dynamically from Suno style block
    ↓
Step 8: init-video.js → Remotion template
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
├── init-video.js              # Scaffold video project, write video-config.json + design.json
├── template/                  # Base Remotion project template
│   ├── package.json
│   ├── tsconfig.json
│   └── src/
│       ├── index.tsx
│       ├── Root.tsx           # Composition config (loads video-config.json at runtime)
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

### Step 1: Generate design.json (in Step 4)

design.json is now generated automatically by the sub-agent in Step 4 when generating Suno lyrics. The agent reads the Suno style block and creates appropriate colors, motifs, and typography based on descriptors like "dark", "warm", "dreamy", etc.

Before using this tool, configure `.remix-workspace-root.json` at the repo root so `init-video.js` can resolve `<workspaceRoot>/<slug>/`.

### Step 2: Scaffold Video Project

```bash
cd tools/video-generator
node init-video.js <workspace-slug> --design="/absolute/path/to/<workspaceRoot>/<slug>/design.json"
```

The generated video project is created in `<workspaceRoot>/<slug>/video/`.

### Step 3: Copy Assets

```bash
cp <workspaceRoot>/<slug>/<slug>-remix-v1.mp3  <workspaceRoot>/<slug>/video/public/audio.mp3
cp <workspaceRoot>/<slug>/lyrics-timestamps.json <workspaceRoot>/<slug>/video/public/
# design.json is automatically copied by init-video.js
```

### Step 4: Render

```bash
cd <workspaceRoot>/<slug>/video
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
  }
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

## Color Palette Guidelines

design.json colors are generated based on Suno style descriptors:

| Style Descriptor | Suggested Palette |
|---|---|
| "dark", "nocturnal", "smoky", "moody" | Deep navy, charcoal, dark purples |
| "warm", "golden hour", "sunset" | Amber, rust, warm browns |
| "bright", "vibrant", "energetic" | Coral, yellow, cyan |
| "dreamy", "ethereal", "lo-fi" | Soft pastels, muted blues, lavender |
| "romantic", "melancholic" | Rose, dusty pink, soft grays |
| "carnatic", "classical", "devotional" | Gold, saffron, deep maroon |

## Development

### Preview Video

```bash
cd <workspaceRoot>/<slug>/video
npm run dev      # Opens Remotion Studio at http://localhost:3000
```

### Customize Design

Edit `<workspaceRoot>/<slug>/design.json` and re-render:

```bash
cd <workspaceRoot>/<slug>/video
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

This is automatically called as part of Steps 4 and 8:

**Step 4 (Generate Suno Lyrics):**
1. Read raw lyrics from lyrics.txt
2. Generate Suno meta-tag format
3. **Generate design.json dynamically from Suno style block**
4. Save files to workspace

**Step 8 (Generate Video):**
5. Scaffold video project with design.json
6. Copy assets (audio, lyrics, cover art, design)
7. Render video

See `prompts/step-4-generate-suno-lyrics.md` and `prompts/step-8-generate-video.md` for full workflow.

## Migration Notes

The old `generate-design.js` script has been removed. design.json is now generated dynamically by the sub-agent in Step 4 based on the Suno style descriptors. This ensures each song gets colors and visuals that match its actual aesthetic rather than static genre-based defaults.

To migrate existing projects:
1. Re-run Step 4 to generate a new design.json
2. Re-run `init-video.js` with `--design` flag
3. Re-render
