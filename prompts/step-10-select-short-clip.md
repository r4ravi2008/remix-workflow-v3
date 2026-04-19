# Step 10: Select Short Clip

## Objective

Analyze the remix audio and lyrics timestamps to identify the most engaging segment for a
YouTube Short. By default, auto-select the best segment. If the user opted into manual mode
during Step 0, present candidates for selection.

## Prerequisites

- `${WORKSPACE_DIR}/${SLUG}-remix-${SELECTED_REMIX}.mp3` exists (`SELECTED_REMIX` is `v1` or `v2` from the user's Step 5.5 choice)
- `${WORKSPACE_DIR}/lyrics-timestamps.json` exists (produced in Step 6)
- `${WORKSPACE_DIR}/meta.json` exists with `shorts_clip_mode` and `shorts_duration`

## Workspace Path Resolution

Before using any filesystem path in this step:

1. Read `.remix-workspace-root.json` from the repo root.
2. Resolve `WORKSPACE_ROOT` from its `workspaceRoot` field.
3. Resolve `WORKSPACE_DIR` as `<workspaceRoot>/<slug>/`.
4. Use absolute paths under `WORKSPACE_DIR` for filesystem commands.
5. Keep any stored `meta.json.files.*` values root-relative, for example `<slug>/design.json`.

---

## Instructions

### 10.1 — Read Workspace State

Read `meta.json` and extract:
- `shorts_clip_mode` (default: `"auto"`)
- `shorts_duration` (default: `30`)
- `slug`
- Selected remix file path

Resolve `SELECTED_REMIX` as `v1` or `v2` from the user's Step 5.5 choice, then substitute it into remix file paths below.

Read `lyrics-timestamps.json` and extract all sections with their start/end times.

---

### 10.2 — Analyze Audio Energy

Run FFmpeg EBU R128 loudness analysis on the remix audio:

```bash
ffmpeg -i "${WORKSPACE_DIR}/${SLUG}-remix-${SELECTED_REMIX}.mp3" -af ebur128 -f null - 2>&1
```

Parse the output to extract per-second loudness values. If `ffmpeg ebur128` fails, skip energy
analysis and rely solely on section metadata (Step 10.3).

---

### 10.3 — Generate Candidate Segments

For each section in `lyrics-timestamps.json`, generate a candidate segment:

1. If the section duration matches the target duration (within ±5s), use the section as-is
2. If the section is longer, find the loudest contiguous window of target duration within it
3. If the section is shorter, extend to include adjacent sections up to target duration

**Scoring heuristic:**

| Factor | Score |
|---|---|
| Section is Chorus | +10 |
| Section is Verse | +5 |
| Section is Bridge/Outro/Intro | +3 |
| Energy bonus (normalized EBU R128 loudness, 0-5 scale) | +0 to +5 |
| Segment starts/ends on section boundary | +1 |

Sort candidates by score descending. Keep top 5.

---

### 10.4 — Select Segment

**If `shorts_clip_mode == "auto"` (default):**

Select the highest-scoring candidate. Log the selection and continue to Step 11.

```
Auto-selected short clip segment:
  Section  : Chorus 1
  Time     : 45.2s - 75.2s (30.0s)
  Score    : 14.2
  Lyrics   : 8 lines

Proceeding to Step 11: Generate Short Video...
```

**If `shorts_clip_mode == "manual"`:**

Present all candidates to the user and wait for selection.

---

### 10.5 — Write shorts-segments.json

Save the analysis results with selected segment, candidates array, and config.

### 10.6 — Update video-config.json

Merge short config into existing video-config.json in the Remotion project.

### 10.7 — Update meta.json

Set `status.shorts_clip_selected: true` and `files.shorts_segments`.

---

## Error Handling

| Error | Solution |
|---|---|
| No chorus detected | Fall back to loudest 30s window from FFmpeg analysis |
| All sections shorter than target | Merge adjacent sections |
| ffmpeg ebur128 fails | Skip energy scoring, use section-type only |
| Lyrics don't cover window | Acceptable — renders with visualizer only |
