# Video Visual System — Design Plan

## Problem Statement

The current Remotion template generates the same static visual layout for every song:
- 16 bars that animate via frame math (`(frame + i * 3) % 45`) — no connection to the audio
- 7 hardcoded genre → color presets that all look the same within a genre
- One fixed layout, one font, one bar style, same component positions every time

## Goal

Every song gets a unique visual identity generated from its metadata, with audio-reactive elements that genuinely respond to the music and abstract visuals that match its energy.

---

## Architecture Overview

```
meta.json (title, genre, language, tempo, mood)
    │
    ▼
[Agent generates design.json]  ← NEW — LLM generates full design spec
    │
    ▼
init-video.js  ← reads design.json, injects into template
    │
    ▼
Remotion template
    ├── design.json loaded at runtime
    ├── useAudioData() → real frequency data per frame  ← NEW
    ├── Layout variant selected from design.json        ← NEW
    ├── Visual motif component rendered                 ← NEW
    └── Typography / colors from design.json            ← NEW
```

---

## Phase 1 — Real Audio Reactivity

**Package to add:** `@remotion/media-utils` (official Remotion package, no conflicts)

**How it works:**

```tsx
import { useAudioData, visualizeAudio } from '@remotion/media-utils';

const audioData = useAudioData(staticFile('audio.mp3'));

const frequencyData = visualizeAudio({
  frame,
  fps,
  audioData,
  numberOfSamples: 64,  // 64 frequency bins
  smoothing: 0.8,
});
// frequencyData[i] is a 0.0–1.0 amplitude value for frequency bin i
```

**What changes:**
- Replace the fake 16-bar oscillation with `frequencyData` slices mapped to bar heights
- Drive background pulse opacity from `frequencyData[0]` (bass bin) instead of `frame % 60`
- Feed `frequencyData` to all visual motif components so everything reacts to the same source

**Frequency band splits:**
| Band | Bins | Drives |
|---|---|---|
| Bass | 0–3 | Background pulse, beat flash, ring expansion |
| Low-mid | 4–15 | Main visualizer bars |
| High-mid | 16–31 | Particle speed / geometric rotation |
| Highs | 32–63 | Shimmer / glow intensity |

---

## Phase 2 — LLM-Generated Design Tokens (`design.json`)

**When:** The agent generates this file as part of Step 6, before calling `init-video.js`.

**Input to the LLM:** The full `meta.json` (song title, genre, language, tempo, mood, Suno style description).

**Output:** A `design.json` file written to the workspace, then copied into `video/public/`.

### `design.json` Schema

```json
{
  "palette": {
    "backgroundType": "gradient",
    "backgroundStops": [
      { "color": "#1a1a2e", "position": "0%" },
      { "color": "#0f3460", "position": "100%" }
    ],
    "backgroundAngle": 135,
    "primaryColor": "#e8e8e8",
    "secondaryColor": "#b8b8b8",
    "accentColor": "#74b9ff",
    "highlightColor": "#ff7675",
    "glowColor": "#74b9ff40"
  },
  "typography": {
    "googleFont": "Space Grotesk",
    "mainLyricSize": 96,
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
    "secondary": "waveform-rings",
    "intensity": "medium"
  },
  "animation": {
    "personality": "smooth",
    "lyricEntrance": "slide-up",
    "beatReactivity": 0.8
  },
  "seed": 4291
}
```

### Design Token Vocabulary

**`backgroundType`:** `gradient` | `mesh-gradient` | `solid` | `dark-noise`

**`googleFont`** (select from this list to guarantee render-time availability):
- Cinematic/dramatic: `Playfair Display`, `Cormorant Garamond`, `Bebas Neue`
- Modern/clean: `Space Grotesk`, `Inter`, `DM Sans`, `Outfit`
- Energetic: `Exo 2`, `Orbitron`, `Rajdhani`
- Warm/organic: `Lora`, `Merriweather`, `Crimson Pro`
- Indic-script-safe: always fall back to `Noto Sans` for Telugu/Hindi/Tamil characters

**`textEffect`:** `glow` | `shadow` | `outline` | `none`

**`lyricEntrance`:** `fade` | `slide-up` | `scale-in` | `glitch` | `word-by-word`

**`motif.primary`** (see Phase 4 below):
`particles` | `geometric-burst` | `aurora` | `waveform-rings` | `frequency-bars-only` | `noise-field`

**`animation.personality`:**
| Value | Easing | Beat flash | Transitions |
|---|---|---|---|
| `smooth` | `Easing.bezier(0.4, 0, 0.2, 1)` | Soft | Cross-fade |
| `bouncy` | `Easing.spring` | Punchy | Bounce |
| `sharp` | `Easing.linear` | Hard cut | Instant |
| `dreamy` | `Easing.bezier(0.8, 0, 0.2, 1)` | None | Slow fade |
| `aggressive` | `Easing.bezier(0.9, 0, 0.1, 1)` | Strobe | Snap |

**`seed`:** Integer seeded from `slug.length * audio_duration` — ensures the same song always gets the same randomized positions/angles, but different songs differ.

---

## Phase 3 — Layout Variants

Five layout presets. The agent picks one based on the song's energy and genre.

### `center-stage` (default, current-ish)
- Section badge top-center
- Lyrics huge and centered
- Visualizer/motif along the bottom strip
- Good for: all genres

### `full-bleed`
- Abstract visual motif fills the entire background (behind lyrics)
- Lyrics in the lower third with a semi-transparent backdrop blur panel
- No explicit visualizer strip — the background IS the visualizer
- Good for: EDM, pop, energetic tracks

### `minimal`
- No visualizer bars
- Lyrics take up 80% of the screen height
- Word-by-word karaoke highlight (each word lights up as it's sung)
- Thin progress line at the very bottom
- Good for: carnatic, classical, slow ballads

### `sidebar`
- Left 55%: lyrics, section badge, progress
- Right 45%: abstract visual motif (audio-reactive)
- Good for: hiphop, chill, lo-fi

### `stacked`
- Top 20%: section badge + song title
- Middle 60%: current lyric very large
- Bottom 20%: next lyric preview + visualizer bars
- Good for: pop, standard karaoke feel

---

## Phase 4 — Visual Motif Components

All components are driven purely by `frame`, `frequencyData` from `useAudioData`, and `design.json` values. No external animation library — pure Remotion `interpolate` + SVG/CSS.

### `ParticleField.tsx`
- N floating dots (N from `seed`-randomized, typically 30–80)
- Each particle has a fixed `(x, y)` starting position and `angle` derived from the seed
- Particles drift slowly based on frame; speed multiplied by `frequencyData[highBin]`
- Opacity and size pulse to bass (`frequencyData[0]`)
- Good for: lo-fi, chill, dreamy

### `GeometricBurst.tsx`
- 3–7 rotating polygons (triangles, hexagons, rings) centered at the screen
- Rotation speed driven by `frequencyData[midBin]`
- Scale pulsed by `frequencyData[bassBin]`
- Stroke color from `accentColor`, fill transparent
- Good for: EDM, hiphop, aggressive

### `AuroraBackground.tsx`
- SVG `<feTurbulence>` noise filter animating over time (baseFrequency changes with frame)
- Layered with the palette gradient via `mix-blend-mode: screen`
- Pulses opacity to bass frequency
- Good for: pop, dreamy, psychedelic

### `WaveformRings.tsx`
- Concentric SVG circles expanding outward from center
- Each ring's radius = `baseBeatAmplitude * ringIndex * scale`
- Rings triggered by bass transients (when `frequencyData[0]` exceeds threshold)
- Fade out as they expand
- Good for: carnatic, classical, meditative

### `NoiseField.tsx`
- CSS `backdrop-filter` + animated `background-position` on a noise texture
- Subtle — used as `secondary` motif alongside another primary
- Good for: any genre, adds texture

### `FrequencyBarsVisualizer.tsx`
- The upgraded real bars (replaces the current fake ones)
- Always rendered, even when another motif is primary
- Bar count: 32 by default, configurable
- Heights directly from `frequencyData` slices
- Color gradient from `accentColor` → `highlightColor`
- Optional: mirror mode (bars grow from center up and down)

---

## Phase 5 — Seeded Randomness

A small `seededRandom(seed)` utility generates deterministic pseudo-random sequences:

```ts
// utils/seededRandom.ts
export function seededRandom(seed: number) {
  let s = seed;
  return () => {
    s = (s * 1664525 + 1013904223) & 0xffffffff;
    return (s >>> 0) / 0xffffffff;
  };
}
```

Every component that needs random values (particle positions, polygon counts, rotation offsets) calls this with `design.seed`. This means:
- Same song → same `seed` → same visual layout every render
- Different songs → different `seed` → different random positions, shapes, counts

---

## File Changes

### New files in `tools/video-generator/template/src/`

```
src/
  components/
    ParticleField.tsx
    GeometricBurst.tsx
    AuroraBackground.tsx
    WaveformRings.tsx
    NoiseField.tsx
    FrequencyBarsVisualizer.tsx
  layouts/
    CenterStageLayout.tsx
    FullBleedLayout.tsx
    MinimalLayout.tsx
    SidebarLayout.tsx
    StackedLayout.tsx
  utils/
    seededRandom.ts
    audioUtils.ts          ← band-split helpers
    designLoader.ts        ← loads + validates design.json
```

### Modified files

| File | Change |
|---|---|
| `template/package.json` | Add `@remotion/media-utils` |
| `template/src/MusicVideo.tsx` | Route to layout variant, pass audioData + design to all children |
| `template/src/Root.tsx` | Pass `designSrc` prop (path to `design.json`) |
| `tools/video-generator/init-video.js` | Accept `--design=<path>` flag, copy `design.json` to `public/`, remove hardcoded theme map |
| `prompts/step-6-generate-video.md` | Add new sub-step 6.4.5: agent generates `design.json` |

### Removed

- The hardcoded `themes` map in both `MusicVideo.tsx` and `init-video.js` — fully replaced by `design.json`

---

## Updated Step 6 Flow

```
6.1  Read meta.json
6.2  Extract remix acapella
6.3  Generate lyrics-timestamps.json
6.4  Verify alignment
6.4.5  [NEW] Agent generates design.json from meta.json
         → Writes workspaces/<slug>/design.json
6.5  Scaffold Remotion project (init-video.js reads design.json)
6.6  Copy assets: audio.mp3 + lyrics-timestamps.json + design.json → video/public/
6.7  npm install && remotion render
6.8  Copy output
6.9  Update meta.json
6.10 Present results
```

---

## Design Guidance for the Agent (Step 6.4.5)

When generating `design.json`, the agent should reason about:

| Song characteristic | Design decision |
|---|---|
| Dark/aggressive genre (hiphop, metal) | Dark backgrounds, high contrast, `geometric-burst`, `aggressive` personality |
| Dreamy/slow (lo-fi, ballad) | Soft gradients, `particles`, `dreamy` personality, large font weight |
| Energetic/electronic (EDM, dance) | Near-black bg, neon accents, `full-bleed` layout, `aurora` or `waveform-rings` |
| Classical/devotional (carnatic) | Warm earth tones, `minimal` layout, `waveform-rings`, `Cormorant Garamond` font |
| Pop/mainstream | Vibrant multi-stop gradient, `center-stage`, `particles` + `noise-field`, `bouncy` |
| Indic language song | Always ensure `Noto Sans` in font stack regardless of `googleFont` choice |

**Randomness budget:** The agent should randomize within constraints:
- Background angle: pick any value from 90–180
- Particle count: 30–80 (from seed)
- Primary motif: pick from the list, don't always pick the "safe" one
- Secondary motif: 40% chance of `null` (some songs need just one motif)
- Font weight: vary between 400, 600, 700, 800 based on energy

---

## What This Looks Like in Practice

| Song | Layout | Motif | Palette | Font |
|---|---|---|---|---|
| Lo-fi Telugu ballad | `minimal` | `particles` | Navy → midnight blue, soft blue accent | Lora 400 |
| EDM Telugu remix | `full-bleed` | `aurora` + `waveform-rings` | Black → deep purple, neon cyan | Orbitron 700 |
| Hiphop Carnatic fusion | `sidebar` | `geometric-burst` | Charcoal → near-black, orange accent | Exo 2 800 |
| Pop Bollywood remix | `center-stage` | `particles` + `noise-field` | Pink → yellow → aqua, magenta accent | Space Grotesk 600 |
| Carnatic classical | `minimal` | `waveform-rings` | Gold → brown, deep amber | Cormorant Garamond 400 italic |
