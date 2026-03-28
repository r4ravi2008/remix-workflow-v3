# Step 8: Generate Video with Remotion

## Objective

Create a music video with full audio duration and karaoke-style synchronized lyrics using the
Remotion video template. The template handles all synced-lyrics rendering logic — this step
focuses on running the pipeline and wiring up the correct data.

## Key Requirements

- **Full audio duration**: Video must match the complete audio length (not hardcoded)
- **Lyrics synchronization**: Uses the `lyrics-timestamps.json` produced in Step 6
- **Cover art background**: Uses `<slug>-cover-art.jpg` produced in Step 7 — **mandatory**
- **Section display**: Show current section (Verse, Chorus, etc.) prominently
- **Indic script support**: Telugu/Hindi/Tamil text renders correctly via system fonts

## Prerequisites

- `workspaces/<slug>/<slug>-remix-v1.mp3` exists
- `workspaces/<slug>/<slug>-suno-lyrics.txt` exists
- `workspaces/<slug>/lyrics-timestamps.json` exists (produced in Step 6)
- `workspaces/<slug>/meta.json` exists with `genre`, `slug`, `language`
- `workspaces/<slug>/<slug>-cover-art.jpg` exists (produced in Step 7, **required**)

---

## Instructions

### 8.1 — Read Workspace Files

Read `meta.json` and extract: `songTitle`, `genre`, `language`, `slug`.

---

### 8.2 — Generate Visual Design Configuration

Generate a unique visual design for this song based on its metadata:

```bash
cd tools/video-generator
node generate-design.js <slug>
```

This creates `workspaces/<slug>/design.json` with:
- **Layout variant**: center-stage, full-bleed, minimal, sidebar, or stacked
- **Visual motif**: particles, geometric-burst, aurora, waveform-rings, or noise-field
- **Color palette**: Generated from genre and mood
- **Typography**: Font, sizing, and text effects
- **Animation personality**: smooth, bouncy, sharp, dreamy, or aggressive

The design is seeded from the song slug and duration, ensuring the same song always gets
the same visual identity.

---

### 8.3 — Scaffold Remotion Project

The `init-video.js` scaffolder copies the template, detects the audio duration from the remix
file via ffprobe, injects song title and genre into `Root.tsx`, and copies the design.json
automatically. No manual code editing needed.

```bash
cd tools/video-generator
node init-video.js <slug> --design=../../workspaces/<slug>/design.json
```

This creates `workspaces/<slug>/video/` with everything wired up, including the visual design
configuration.

---

### 8.4 — Copy Assets to Video Project

```bash
cp workspaces/<slug>/<slug>-remix-v1.mp3          workspaces/<slug>/video/public/audio.mp3
cp workspaces/<slug>/lyrics-timestamps.json        workspaces/<slug>/video/public/
cp workspaces/<slug>/design.json                   workspaces/<slug>/video/public/
cp workspaces/<slug>/<slug>-suno-lyrics.txt        workspaces/<slug>/video/public/suno-lyrics.txt
cp workspaces/<slug>/<slug>-cover-art.jpg          workspaces/<slug>/video/public/cover-art.jpg
```

The file **must** be named `cover-art.jpg` — that is the exact filename the `CoverArtLayout`
template looks for via `staticFile('cover-art.jpg')`.

---

### 8.5 — Install Dependencies and Render

```bash
cd workspaces/<slug>/video
npm install
npx remotion render MusicVideo out/video.mp4
```

Rendering takes 1–2 minutes for a typical 3–4 minute song.

---

### 8.6 — Copy Output to Workspace

```bash
cp workspaces/<slug>/video/out/video.mp4 workspaces/<slug>/<slug>-video.mp4
```

---

### 8.7 — Update Metadata

Update `workspaces/<slug>/meta.json` to record the video output:

```json
{
  "status": { "video_generated": true },
  "outputs": {
    "final_video": "workspaces/<slug>/<slug>-video.mp4",
    "design_config": "workspaces/<slug>/design.json"
  }
}
```

---

### 8.8 — Present Final Results

```
Video generation complete!

Outputs in workspaces/<slug>/:
   <slug>-video.mp4                  — Final music video (1920×1080) with audio-reactive visuals
   <slug>-remix-v1.mp3               — Remix audio
   <slug>-remix-v1-acapella.mp3      — Vocals extracted from remix
   lyrics-timestamps.json            — Word+line timestamps (CTC aligned)
   design.json                       — LLM-generated visual design configuration
   <slug>-cover-art.jpg              — Enhanced cover art (SeedVR2 1080p)
   video/                            — Remotion project

Duration: <duration>s  |  Lyrics: <n> lines synced  |  Layout: <layout>  |  Motif: <motif>
```

---

## How the Template Works

The video template in `tools/video-generator/template/` is self-contained:

- **`Root.tsx`** — sets composition duration (in frames) and passes song metadata as props.
  `init-video.js` fills in `AUDIO_DURATION`, `SONG_TITLE`, and `GENRE` automatically.

- **`MusicVideo.tsx`** — handles all synced-lyrics rendering with audio-reactive visuals:
  - Uses `useAudioData()` from `@remotion/media-utils` to get real frequency data
  - Loads `design.json` for layout, colors, fonts, and visual motifs
  - Renders one of 6 layout variants; default is `cover-art`
  - Displays audio-reactive visual motifs (particles, geometric-burst, aurora, waveform-rings, noise-field)
  - Uses Remotion's `delayRender` / `continueRender` for async data loading
  - Finds the active lyric line and section for the current timestamp

- **`CoverArtLayout.tsx`** (default layout) — two-panel layout: 75% / 25%:
  - **Left 75%**: renders `public/cover-art.jpg` full-bleed via Remotion's `<Img>` component,
    with a right-edge dark gradient overlay and song title + genre badge overlaid at bottom-left
  - **Right 25%**: scrolling karaoke lyrics + frequency bars visualizer + progress bar
  - Falls back gracefully to a ♪ placeholder if `cover-art.jpg` fails to load

- **`design.json`** — LLM-generated design configuration with palette, typography, layout,
  animation personality, and visual motif selection. Generated by `generate-design.js`.

Do not edit the generated video project manually unless customizing visuals. Re-scaffold from
the template if the project gets into a broken state.

---

## Error Handling

| Problem | Fix |
|---|---|
| Cover art not showing (left panel blank) | Ensure `cover-art.jpg` is in `video/public/` with that exact filename |
| Cover art distorted / wrong crop | SeedVR2 output is already 1080p — `objectFit: cover` handles any ratio |
| Lyrics not syncing | Check `lyrics-timestamps.json` is in `video/public/` |
| No lyrics visible in rendered video | Missing `delayRender` — re-scaffold from template |
| Telugu text garbled | Font issue — system-ui fallback handles it; no fix needed |
| ffprobe not found | `brew install ffmpeg` |
