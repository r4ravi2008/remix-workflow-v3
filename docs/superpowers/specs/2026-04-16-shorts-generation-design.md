# Shorts Generation Design — Steps 10 & 11

## Summary

Add two new pipeline steps (10 & 11) that generate a YouTube Shorts-format (9:16) short video
from the full music video produced in Step 8. Step 10 selects the most interesting clip segment
using audio energy analysis and section metadata. Step 11 renders a vertical-format video with
a new `CoverArtVerticalLayout` in the existing Remotion project.

## Pipeline Position

```
[Step 9] YouTube Metadata
    |
    v
[Step 10] Select Short Clip  (autonomous by default)
    |
    v
[Step 11] Generate Short Video
    |
    v
Done
```

Both steps are autonomous after Step 9. No user interaction unless the user opted into
manual segment selection during Step 0.

---

## Step 0 Changes

### New Optional Inputs

| Input | Required | Default | Example |
|---|---|---|---|
| Short clip selection mode | No | `auto` | `auto`, `manual` |
| Short clip duration (seconds) | No | `30` | `15`, `30`, `60` |

Stored in `meta.json` as `"shorts_clip_mode": "auto"` and `"shorts_duration": 30`.

- `auto` (default): Step 10 auto-selects the highest-scoring segment and continues to Step 11.
- `manual`: Step 10 presents 3-5 scored candidates and waits for the user to choose.

The user signals `manual` mode in their initial prompt (e.g., "Present me the segments").

---

## Step 10: Select Short Clip

### Objective

Analyze the remix audio and lyrics timestamps to identify the most engaging 30-second segment
for a YouTube Short.

### Prerequisites

- `workspaces/<slug>/<slug>-remix-v1.mp3` exists
- `workspaces/<slug>/lyrics-timestamps.json` exists (produced in Step 6)
- `workspaces/<slug>/meta.json` exists

### Segment Detection Algorithm

Two data sources are combined:

1. **`lyrics-timestamps.json`** — Section labels (Chorus, Verse, Bridge) with start/end times.
   Choruses are the most recognizable/catchy parts of a song.

2. **FFmpeg EBU R128 loudness analysis** — Sustained loudness data per time window.
   Higher loudness correlates with musical peaks.

   ```bash
   ffmpeg -i <slug>-remix-v1.mp3 -af ebur128 -f null - 2>&1
   ```

### Scoring Heuristic

Each candidate segment receives a score:

| Factor | Score |
|---|---|
| Section is Chorus | +10 |
| Section is Verse | +5 |
| Section is Bridge/Outro/Intro | +3 |
| Energy bonus (normalized EBU R128 loudness, 0-5 scale) | +0 to +5 |
| Segment starts/ends on section boundary (clean cut) | +1 |

If a chorus is longer than the target duration, the loudest contiguous window within it is used.

### Segment Selection Logic

1. Parse `lyrics-timestamps.json` to extract sections with start/end times
2. Run FFmpeg `ebur128` analysis to get per-second loudness
3. Generate candidate segments (one per section, or sliding window for long sections)
4. Score each candidate
5. Select top-scoring segment
6. If `shorts_clip_mode == "manual"` in `meta.json`: present all candidates, wait for user choice
7. If `shorts_clip_mode == "auto"` (default): auto-select best, continue to Step 11

### Target Duration

Default: **30 seconds**. Configurable — if the user specifies a different duration in Step 0
(15s or 60s), it is stored in `meta.json` as `"shorts_duration": 30` and used here.

### Output: `shorts-segments.json`

```json
{
  "selected": {
    "start_time": 45.2,
    "end_time": 75.2,
    "duration": 30,
    "section": "Chorus 1",
    "score": 14.2,
    "lyrics_line_start": 12,
    "lyrics_line_end": 20
  },
  "candidates": [
    { "start_time": 45.2, "end_time": 75.2, "section": "Chorus 1", "score": 14.2 },
    { "start_time": 120.5, "end_time": 150.5, "section": "Chorus 2", "score": 13.8 },
    { "start_time": 0, "end_time": 30, "section": "Intro + Verse 1", "score": 7.1 }
  ],
  "config": {
    "duration": 30,
    "auto_selected": true
  }
}
```

### Metadata Update

```json
{
  "status": { "shorts_clip_selected": true },
  "files": { "shorts_segments": "workspaces/<slug>/shorts-segments.json" }
}
```

---

## Step 11: Generate Short Video

### Objective

Render a 9:16 vertical music video from the selected clip segment using the existing Remotion
project, with a new vertical layout component.

### Prerequisites

- `workspaces/<slug>/shorts-segments.json` exists (produced in Step 10)
- `workspaces/<slug>/video/` exists (Remotion project from Step 8)
- `workspaces/<slug>/<slug>-cover-art.jpg` already in `video/public/cover-art.jpg`
- `workspaces/<slug>/lyrics-timestamps.json` already in `video/public/`

### Remotion Architecture

A second `<Composition>` is added to the existing `Root.tsx`:

```tsx
<Composition
  id="MusicVideoShort"
  component={MusicVideoShort}
  durationInFrames={Math.ceil(shortConfig.duration * FPS)}
  fps={FPS}
  width={1080}
  height={1920}
  defaultProps={{
    songTitle: config.songTitle,
    audioSrc: "audio.mp3",
    lyricsDataSrc: "lyrics-timestamps.json",
    genre: config.genre,
    clipStartTime: shortConfig.startTime,
    clipEndTime: shortConfig.endTime,
  }}
/>
```

The `MusicVideoShort` composition is registered only when `config.short` exists in
`video-config.json`. This maintains backward compatibility — existing workspaces without
shorts config only see the `MusicVideo` composition.

### video-config.json Extension

After Step 10, the agent merges short config into the existing `video-config.json`:

```json
{
  "audioDuration": 210.5,
  "songTitle": "Meesaala Pilla",
  "genre": "Lo-Fi",
  "short": {
    "startTime": 45.2,
    "endTime": 75.2,
    "duration": 30
  }
}
```

This is a JSON merge into the file that already exists from Step 8. No re-scaffolding needed.

### MusicVideoShort Component

`MusicVideoShort.tsx` is a wrapper around the same audio-reactive logic in `MusicVideo.tsx`:

- **Audio trimming**: Uses Remotion's native `<Audio trimBefore={clipStartTime * fps} trimAfter={clipEndTime * fps} />`
- **Lyrics rebasing**: Filters `lyricsData.lyrics` to only lines within `[clipStartTime, clipEndTime]`, then subtracts `clipStartTime` from all timestamps so they start at 0
- **Layout override**: Forces `layout.variant` to `"cover-art-vertical"` regardless of `design.json`
- **Visual systems**: Same design.json palette, motifs, audio-reactive effects, typography

#### Lyrics Rebasing Example

```
Original:
  { "text": "మీసాల పిల్ల", "start_time": 47.5, "end_time": 49.2, "section": "Chorus" }

After rebasing (clipStartTime = 45.2):
  { "text": "మీసాల పిల్ల", "start_time": 2.3, "end_time": 4.0, "section": "Chorus" }
```

Lines outside `[clipStartTime, clipEndTime]` are excluded entirely.

### CoverArtVerticalLayout Component

New file: `tools/video-generator/template/src/layouts/CoverArtVerticalLayout.tsx`

```
  1080 x 1920 (9:16)
  +----------------------+
  |                      |
  |   cover-art.jpg      |
  |   (inset, rounded,   |  60% (1152px)
  |    feathered edges)   |
  |                      |
  |   title + genre      |
  +----------------------+
  |                      |
  |   scrolling lyrics   |  30% (576px)
  |   (active highlight) |
  |                      |
  +----------------------+
  |   visualizer bars    |  10% (192px)
  |   + progress bar     |
  +----------------------+
```

Adaptations from horizontal `CoverArtLayout`:

| Element | Horizontal (1920x1080) | Vertical (1080x1920) |
|---|---|---|
| Cover art panel | Left 75% (1440x1080) | Top 60% (1080x1152) |
| Lyrics panel | Right 25% (480x1080) | Middle 30% (1080x576) |
| Visualizer | Inside lyrics panel (400x100) | Bottom 10% (1080x192), full width |
| Radial rings SVG | `viewBox="0 0 1440 1080"`, center `(720, 480)` | `viewBox="0 0 1080 1152"`, center `(540, 500)` |
| Lyrics font size | `mainLyricSize * 0.40` active | `mainLyricSize * 0.55` active (wider panel) |
| Song title font | 42px | 36px |
| Layout direction | `flex-direction: row` | `flex-direction: column` |

Same features preserved:
- Ambient blurred cover art background
- Bass-reactive cover art breathing (scale 1.0 to 1.04)
- Beat-reactive vignette overlay
- Glow ring around cover art
- WaveformRings overlay (resized to 1080x1920)
- Scrolling lyrics with distance-based opacity fade
- Active line highlight with text effects (glow/shadow/outline)
- Frequency bars visualizer
- Progress bar

### Rendering

```bash
cd workspaces/<slug>/video
npx remotion render MusicVideoShort out/short.mp4
```

### Output

Copy rendered short to workspace root:

```bash
cp workspaces/<slug>/video/out/short.mp4 workspaces/<slug>/<slug>-short.mp4
```

### Metadata Update

```json
{
  "status": { "short_video_generated": true },
  "files": { "short_video": "workspaces/<slug>/<slug>-short.mp4" }
}
```

### Present Results

```
Short video generation complete!

Output: workspaces/<slug>/<slug>-short.mp4
  Format   : 1080x1920 (9:16 vertical)
  Duration : 30s
  Segment  : Chorus 1 (45.2s - 75.2s)
  Lyrics   : 8 lines synced
  Layout   : cover-art-vertical

Ready for YouTube Shorts / Instagram Reels upload.
```

---

## New Template Files

```
tools/video-generator/template/src/
  ├── MusicVideoShort.tsx               ← NEW: Wrapper with trim + rebase + vertical layout
  └── layouts/
      ├── ... (existing layouts unchanged)
      ├── CoverArtVerticalLayout.tsx    ← NEW: 9:16 vertical layout
      └── index.ts                      ← UPDATED: export CoverArtVerticalLayout
```

## Workspace File Additions

```
workspaces/<slug>/
  ├── ... (existing files unchanged)
  ├── shorts-segments.json              ← Segment candidates + selected segment
  └── <slug>-short.mp4                  ← Final rendered short video (1080x1920)
```

## meta.json Schema Additions

New top-level fields:
- `"shorts_clip_mode": "auto"` — collected in Step 0
- `"shorts_duration": 30` — optional, collected in Step 0

New status fields:
- `"shorts_clip_selected": false`
- `"short_video_generated": false`

New file fields:
- `"shorts_segments": null`
- `"short_video": null`

## Prompt Files to Create

| File | Purpose |
|---|---|
| `prompts/step-10-select-short-clip.md` | Audio analysis, segment scoring, selection |
| `prompts/step-11-generate-short-video.md` | Render vertical short in existing Remotion project |

## Error Handling

| Problem | Fix |
|---|---|
| No chorus detected in lyrics | Fall back to loudest 30s window from FFmpeg analysis |
| Selected segment shorter than target duration | Expand to nearest section boundaries |
| Lyrics don't cover the selected window | Render short with visualizer only (no lyrics) |
| `ffmpeg ebur128` fails | Fall back to first chorus section from lyrics-timestamps.json |
| Short renders black (no audio data) | Verify `trimBefore`/`trimAfter` are in frames, not seconds |
| `video-config.json` missing after Step 8 | Re-run `init-video.js` before proceeding |
| Vertical layout text too small on mobile | Active lyrics font uses `mainLyricSize * 0.55` (larger ratio than horizontal) |

## Pipeline Summary (Updated)

```
[Step 0]  Prepare Workspace (+ collect shorts_clip_mode)
[Step 1]  Download MP3
[Step 2]  Extract Acapella
[Step 3]  Find Lyrics
[Step 4]  Generate Suno Lyrics + design.json
[Step 5]  Generate Remix on Suno
[Step 5.5] User selects v1 or v2
[Step 6]  Extract Acapella & Align Lyrics
[Step 7]  Fetch & Enhance Cover Art
[Step 8]  Generate Video (1920x1080, landscape)
[Step 9]  Generate YouTube Metadata
[Step 10] Select Short Clip (autonomous or manual)
[Step 11] Generate Short Video (1080x1920, vertical)
```
