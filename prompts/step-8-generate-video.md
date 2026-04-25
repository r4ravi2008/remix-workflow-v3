# Step 8: Generate Video with Remotion

## Objective

Create a music video with full audio duration and karaoke-style synchronized lyrics using the
Remotion video template. The template handles all synced-lyrics rendering logic — this step
focuses on running the pipeline and wiring up the correct data.

## Key Requirements

- **Full audio duration**: Video must match the complete audio length (not hardcoded)
- **Lyrics synchronization**: Uses the `lyrics-timestamps.json` produced in Step 6
- **Visual image sequence**: Uses `image-sequence.json` and `stylized-frames/` from Step 7 when available; the template falls back to cover art, then to a placeholder
- **Section display**: Show current section (Verse, Chorus, etc.) prominently
- **Indic script support**: Telugu/Hindi/Tamil text renders correctly via system fonts

## Prerequisites

- `${WORKSPACE_DIR}/${SLUG}-remix-${SELECTED_REMIX}.mp3` exists (`SELECTED_REMIX` comes from `meta.json.status.selected_remix`, set after Step 5.5)
- `${WORKSPACE_DIR}/${SLUG}-suno-lyrics.txt` exists
- `${WORKSPACE_DIR}/lyrics-timestamps.json` exists (produced in Step 6)
- `${WORKSPACE_DIR}/meta.json` exists with `genre`, `slug`, `language`
- `${WORKSPACE_DIR}/image-sequence.json` and `${WORKSPACE_DIR}/stylized-frames/` may exist if Step 7 prepared a visual sequence
- `${WORKSPACE_DIR}/${SLUG}-cover-art.jpg` may exist as a fallback if Step 7 found artwork

## Workspace Path Resolution

Before using any filesystem path in this step:

1. Read `.remix-workspace-root.json` from the repo root.
2. Resolve `WORKSPACE_ROOT` from its `workspaceRoot` field.
3. Resolve `WORKSPACE_DIR` as `<workspaceRoot>/<slug>/`.
4. Use absolute paths under `WORKSPACE_DIR` for filesystem commands.
5. Keep any stored `meta.json.files.*` values root-relative, for example `<slug>/design.json`.

**See also**: Load the `remotion-best-practices` skill when working on this step.

---

## Instructions

### 8.1 — Read Workspace Files

Read `meta.json` and extract: `video_title`, `genre`, `language`, `slug`, `status.selected_remix`.

Resolve `SELECTED_REMIX` from `meta.json.status.selected_remix` first. It must be `v1` or `v2`. If it is missing, stop and go back to Step 5 to persist the user's chosen remix before continuing.

---

### 8.2 — Verify Design Configuration

`design.json` is generated in **Step 4** (section 4.11) based on the Suno style descriptors.
Verify it exists at `${WORKSPACE_DIR}/design.json` before proceeding.

> **Cover-art behavior**: The CoverArtLayout renders `image-sequence.json` when present,
> then falls back to `cover-art.jpg`, then falls back gracefully to a placeholder.

---

### 8.3 — Scaffold Remotion Project

The `init-video.js` scaffolder copies the template, detects the audio duration from the remix
file via ffprobe, writes a `video-config.json` with song title, genre, and duration, copies
`design.json`, and copies optional image sequence assets when the sequence flags point to
existing files/directories. No manual code editing needed.

```bash
cd tools/video-generator
node init-video.js <slug> \
  --design="${WORKSPACE_DIR}/design.json" \
  --image-sequence="${WORKSPACE_DIR}/image-sequence.json" \
  --stylized-frames="${WORKSPACE_DIR}/stylized-frames"
```

This creates `<workspaceRoot>/<slug>/video/` with everything wired up, including the visual design
configuration and image sequence assets when they exist.

---

### 8.4 — Copy Assets to Video Project

Always copy the required runtime assets after scaffolding: `audio.mp3`, `lyrics-timestamps.json`,
and `suno-lyrics.txt`. `init-video.js` does not copy these files.

Fresh scaffolds normally already have `design.json`, `image-sequence.json`, and `stylized-frames/`
copied when the flags in step 8.3 were provided and the source paths existed. Use the manual
commands for those optional assets only for existing scaffolds, recovery, or if assets were created
after running `init-video.js`.

```bash
cp "${WORKSPACE_DIR}/${SLUG}-remix-${SELECTED_REMIX}.mp3"   "${WORKSPACE_DIR}/video/public/audio.mp3"
cp "${WORKSPACE_DIR}/lyrics-timestamps.json" "${WORKSPACE_DIR}/video/public/"
cp "${WORKSPACE_DIR}/design.json"            "${WORKSPACE_DIR}/video/public/"
cp "${WORKSPACE_DIR}/${SLUG}-suno-lyrics.txt" "${WORKSPACE_DIR}/video/public/suno-lyrics.txt"
[ -f "${WORKSPACE_DIR}/image-sequence.json" ] && cp "${WORKSPACE_DIR}/image-sequence.json" "${WORKSPACE_DIR}/video/public/image-sequence.json"
[ -d "${WORKSPACE_DIR}/stylized-frames" ] && cp -R "${WORKSPACE_DIR}/stylized-frames" "${WORKSPACE_DIR}/video/public/stylized-frames"
[ -f "${WORKSPACE_DIR}/${SLUG}-cover-art.jpg" ] && cp "${WORKSPACE_DIR}/${SLUG}-cover-art.jpg" "${WORKSPACE_DIR}/video/public/cover-art.jpg"
```

If `image-sequence.json` and `stylized-frames/` are available, they are the primary visual input.
If cover art is available as a fallback, copy it as `cover-art.jpg`. If both are missing, the
template falls back gracefully to its placeholder.

---

### 8.5 — Install Dependencies and Render

```bash
cd "${WORKSPACE_DIR}/video"
npm install
npx remotion render MusicVideo out/video.mp4
```

Rendering takes 1–2 minutes for a typical 3–4 minute song.

---

### 8.6 — Copy Output to Workspace

```bash
cp "${WORKSPACE_DIR}/video/out/video.mp4" "${WORKSPACE_DIR}/${SLUG}-video.mp4"
```

---

### 8.7 — Update Metadata

Update `${WORKSPACE_DIR}/meta.json` to record the video output:

```json
{
  "status": { "video_generated": true },
  "files": {
    "final_video": "<slug>/<slug>-video.mp4",
    "design_config": "<slug>/design.json"
  }
}
```

---

### 8.8 — Present Final Results

```
Video generation complete!

Outputs in <workspaceRoot>/<slug>/:
   <slug>-video.mp4                  — Final music video (1920×1080) with audio-reactive visuals
   <slug>-remix-${SELECTED_REMIX}.mp3               — Remix audio
   <slug>-remix-${SELECTED_REMIX}-acapella.mp3      — Vocals extracted from remix
   lyrics-timestamps.json            — Word+line timestamps (CTC aligned)
   design.json                       — LLM-generated visual design configuration
   image-sequence.json               — Optional visual sequence manifest, if available
   stylized-frames/                  — Optional stylized frame sequence, if available
   <slug>-cover-art.jpg              — Optional fallback cover art, if available
   video/                            — Remotion project

Duration: <duration>s  |  Lyrics: <n> lines synced  |  Layout: <layout>  |  Motif: <motif>
```

---

## How the Template Works

The video template in `tools/video-generator/template/` is self-contained:

- **`Root.tsx`** — loads `public/video-config.json` at runtime to get audio duration, song title,
  and genre. Sets composition duration (in frames) and passes song metadata as props.
  `init-video.js` writes `video-config.json` automatically; for local dev, a default file is
  included in the template.

- **`MusicVideo.tsx`** — handles all synced-lyrics rendering with audio-reactive visuals:
  - Uses `useAudioData()` from `@remotion/media-utils` to get real frequency data
  - Loads `design.json` for layout, colors, fonts, and visual motifs
  - Renders one of 6 layout variants; default is `cover-art`
  - Displays audio-reactive visual motifs (particles, geometric-burst, aurora, waveform-rings, noise-field)
  - Uses Remotion's `delayRender` / `continueRender` for async data loading
  - Finds the active lyric line and section for the current timestamp

- **`CoverArtLayout.tsx`** (default layout) — two-panel layout: 75% / 25%:
  - **Left 75%**: renders `public/image-sequence.json` when present, using images from
    `public/stylized-frames/`; otherwise renders `public/cover-art.jpg`; otherwise shows a
    placeholder. The visual area uses a right-edge dark gradient overlay and song title + genre
    badge overlaid at bottom-left
  - **Right 25%**: scrolling karaoke lyrics + frequency bars visualizer + progress bar
  - Falls back gracefully to a ♪ placeholder if neither `image-sequence.json` nor `cover-art.jpg` can load

- **`design.json`** — LLM-generated design configuration with palette, typography, layout,
  animation personality, and visual motif selection. Generated in Step 4 (section 4.11).

Do not edit the generated video project manually unless customizing visuals. Re-scaffold from
the template if the project gets into a broken state.

---

## Error Handling

**See**: [Error Handling Patterns > Video Generation Errors](references/error-handling-patterns.md#video-generation-errors-step-8)

| Problem | Fix |
|---|---|
| Image sequence not showing | Ensure `image-sequence.json` and `stylized-frames/` are in `${WORKSPACE_DIR}/video/public/` |
| Cover art fallback not showing | Ensure `cover-art.jpg` is in `${WORKSPACE_DIR}/video/public/` with that exact filename |
| Cover art distorted / wrong crop | Nano Banana Pro output is 2048×2048 — `objectFit: cover` handles any ratio |
| Lyrics not syncing | Check `lyrics-timestamps.json` is in `${WORKSPACE_DIR}/video/public/` |
| No lyrics visible in rendered video | Missing `delayRender` — re-scaffold from template |
| Telugu text garbled | Font issue — system-ui fallback handles it; no fix needed |
| ffprobe not found | `brew install ffmpeg` |

---

## Reference

- [Workspace Conventions](references/workspace-conventions.md) — File naming
- [Error Handling Patterns](references/error-handling-patterns.md) — Common errors
- Load `remotion-best-practices` skill for Remotion-specific guidance
