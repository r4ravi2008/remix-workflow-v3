# Step 7: Prepare Visual Image Sequence

## Objective

Download the original YouTube video, extract a configurable number of evenly spaced source frames, stylize those frames with one shared prompt/settings set, and write `image-sequence.json` for Step 8. Existing cover art remains a fallback when sequence preparation is skipped or fails.

> **Legacy filename**: This file remains named `step-7-fetch-cover-art.md` for compatibility with existing references. Step 7 now primarily prepares a visual image sequence; cover art is only a fallback path.

## Key Requirements

- **Source video**: Original YouTube video from `meta.json.youtube_url`
- **Frame count**: Use `meta.json.visual_frame_count` when present; default to 20
- **Frame selection**: Deterministically select up to `visual_frame_count` evenly spaced frames from the source video
- **Stylization**: Stylize selected frames with one shared prompt/settings set for visual consistency
- **Primary output**: `image-sequence.json` plus images in `${WORKSPACE_DIR}/stylized-frames/`
- **Fallback output**: `${WORKSPACE_DIR}/${SLUG}-cover-art.jpg` may still be used by Step 8 if sequence preparation is skipped or fails

## Prerequisites

- Extraction, selection, and stylization can start after Step 0 when `${WORKSPACE_DIR}/meta.json` exists with `youtube_url`, `video_title`, `language`, `slug`
- Manifest generation requires Step 5.5 selected remix state: `meta.json.status.selected_remix` is `v1` or `v2`, and the matching selected remix audio file exists as `${WORKSPACE_DIR}/${SLUG}-remix-v1.mp3` or `${WORKSPACE_DIR}/${SLUG}-remix-v2.mp3`

## Workspace Path Resolution

Before using any filesystem path in this step:

1. Read `.remix-workspace-root.json` from the repo root.
2. Resolve `WORKSPACE_ROOT` from its `workspaceRoot` field.
3. Resolve `WORKSPACE_DIR` as `<workspaceRoot>/<slug>/`.
4. Use absolute paths under `WORKSPACE_DIR` for filesystem commands.
5. Keep any stored `meta.json.files.*` values root-relative, for example `<slug>/image-sequence.json`.

**See also**: [Chrome DevTools Patterns](references/chrome-devtools-patterns.md) — Browser automation reference.

---

## Instructions

### 7.1 — Read Workspace Files

Read `meta.json` and extract: `youtube_url`, `video_title`, `language`, `slug`, `visual_frame_count`.

If `visual_frame_count` is missing, use 20.

---

### 7.2 — Extract Source Frames

Run the visual sequence extractor from the repo root:

```bash
node tools/visual-sequence/visual-sequence.js extract <slug>
```

The extractor downloads the original YouTube video, saves it as `${WORKSPACE_DIR}/${SLUG}-original-video.mp4`, deterministically selects up to `visual_frame_count` evenly spaced frames, writes them into `${WORKSPACE_DIR}/source-frames/`, and writes frame metadata.

Expected outputs after extraction:

```text
<slug>-original-video.mp4
source-frames/
visual-frame-candidates.json
selected-visual-frames.json
```

Update `${WORKSPACE_DIR}/meta.json` as outputs become available:

```json
{
  "files": {
    "original_video": "<slug>/<slug>-original-video.mp4",
    "visual_frame_candidates": "<slug>/visual-frame-candidates.json",
    "selected_visual_frames": "<slug>/selected-visual-frames.json"
  },
  "status": {
    "original_video_downloaded": true,
    "visual_frames_extracted": true,
    "visual_frames_selected": true
  }
}
```

---

### 7.3 — Stylize Selected Frames

Stylize the frames listed in `selected-visual-frames.json` with one shared prompt/settings set so the final sequence feels cohesive.

Use the available image-generation workflow for the configured model. Keep the prompt focused on visual style only; do not add lyrics, romanized text, watermarks, logos, or captions.

Save all stylized frame images in:

```text
${WORKSPACE_DIR}/stylized-frames/
```

Use the selected frame basename `${SLUG}-${frame.id}` and preserve the image generator's output extension. Supported stylized frame extensions for manifest generation are `.jpg`, `.jpeg`, `.png`, and `.webp`.

You may complete extraction, selection, and stylization before the user chooses the selected remix. Wait until Step 5.5 has set the selected remix before writing the sequence manifest, because the manifest is timed against the selected remix audio duration.

When the stylized images exist in `${WORKSPACE_DIR}/stylized-frames/`, write the sequence manifest:

```bash
node tools/visual-sequence/visual-sequence.js manifest <slug>
```

Expected outputs after stylization and manifest creation:

```text
stylized-frames/
image-sequence.json
```

Update `${WORKSPACE_DIR}/meta.json`:

```json
{
  "files": {
    "image_sequence": "<slug>/image-sequence.json"
  },
  "status": {
    "visual_frames_stylized": true
  }
}
```

---

### 7.4 — Verify Sequence Outputs

Confirm these files and directories exist:

```text
<slug>-original-video.mp4
source-frames/
visual-frame-candidates.json
selected-visual-frames.json
stylized-frames/
image-sequence.json
```

`image-sequence.json` is the primary Step 8 visual input.

---

### 7.5 — Optional Fallback: Cover Art

If visual sequence preparation is skipped or fails, Step 8 can still use the existing cover-art fallback path.

To prepare fallback cover art, find the original song's cover art from JioSaavn (preferred) or Google Images, then stylize it into Japanese anime style using the Nano Banana Pro model on fal.ai.

Requirements for fallback cover art:

- **Source**: JioSaavn CDN (preferred) or Google Images — official album/single artwork only
- **Stylization**: Japanese anime style via `fal-ai/nano-banana-pro/edit` at 2K resolution
- **Text on image**: Song title only — no watermarks, logos, artist names, or other text
- **Output format**: JPEG saved as `${WORKSPACE_DIR}/${SLUG}-cover-art.jpg`

Update `${WORKSPACE_DIR}/meta.json` if fallback cover art is created:

```json
{
  "status": { "cover_art_fetched": true },
  "files": {
    "cover_art": "<slug>/<slug>-cover-art.jpg"
  }
}
```

---

### 7.6 — Confirm Ready for Video

```
Visual image sequence ready!

   <slug>-original-video.mp4       — Original video used for frame extraction
   selected-visual-frames.json     — Selected source frame metadata
   stylized-frames/                — Stylized frame images
   image-sequence.json             — Sequence manifest for Step 8
   <slug>-cover-art.jpg            — Optional fallback cover art, if available

Proceeding to Step 8: Generate Video with Remotion.
```

---

## Fallback: No Visual Sequence Available

If the original video cannot be downloaded, no usable frames can be selected, or stylization fails:

1. Try fallback cover art using JioSaavn or Google Images.
2. If no suitable fallback cover art can be found, skip visual preparation and note it in meta.json:
   ```json
   { "status": { "cover_art_fetched": false, "cover_art_skipped": true } }
   ```
3. The Remotion cover-art layout renders `image-sequence.json` when present, then falls back to `cover-art.jpg`, then to its placeholder.

---

## Error Handling

**See**: [Error Handling Patterns](references/error-handling-patterns.md)

| Problem | Fix |
|---|---|
| Original video download fails | Confirm `meta.json.youtube_url`; retry with the video URL directly if the tool supports it |
| Extracted frames are too dark or repetitive | Increase `visual_frame_count` in `meta.json` and rerun extraction |
| Stylized frames are inconsistent | Reuse one shared prompt/settings set for all selected frames |
| `image-sequence.json` missing | Confirm stylized images and the selected remix audio exist, then rerun `node tools/visual-sequence/visual-sequence.js manifest <slug>` |
| Cover art fallback not showing | Ensure `${WORKSPACE_DIR}/${SLUG}-cover-art.jpg` exists before Step 8 copies assets |

---

## Reference

- [Chrome DevTools Patterns](references/chrome-devtools-patterns.md) — Browser automation
- [Workspace Conventions](references/workspace-conventions.md) — File naming
- [Error Handling Patterns](references/error-handling-patterns.md) — Common errors
