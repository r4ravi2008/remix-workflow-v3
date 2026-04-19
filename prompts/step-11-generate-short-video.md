# Step 11: Generate Short Video

## Objective

Render a 9:16 vertical music video (YouTube Short) from the selected clip segment using the
existing Remotion project.

## Key Requirements

- Vertical format: 1080x1920 (9:16)
- Clip duration: Uses segment from Step 10
- Audio trimming: Remotion's native `trimBefore`/`trimAfter`
- Lyrics sync: Only lyrics within clip window, rebased to start at 0
- Same visuals: Same design.json, motifs, effects, typography

## Prerequisites

- `${WORKSPACE_DIR}/shorts-segments.json` exists
- `${WORKSPACE_DIR}/video/` exists (Remotion project from Step 8)
- `${WORKSPACE_DIR}/video/public/video-config.json` includes `short` config

## Workspace Path Resolution

Before using any filesystem path in this step:

1. Read `.remix-workspace-root.json` from the repo root.
2. Resolve `WORKSPACE_ROOT` from its `workspaceRoot` field.
3. Resolve `WORKSPACE_DIR` as `<workspaceRoot>/<slug>/`.
4. Use absolute paths under `WORKSPACE_DIR` for filesystem commands.
5. Keep any stored `meta.json.files.*` values root-relative, for example `<slug>/design.json`.

---

## Instructions

### 11.1 — Verify Prerequisites

Check `video-config.json` has the `short` key with startTime, endTime, duration.

### 11.2 — Verify Template Has Short Components

Check that MusicVideoShort.tsx and CoverArtVerticalLayout.tsx exist in the project.
If missing, copy from `tools/video-generator/template/src/`.

### 11.3 — Render Short Video

```bash
cd "${WORKSPACE_DIR}/video"
npx remotion render MusicVideoShort out/short.mp4
```

### 11.4 — Copy Output

```bash
cp "${WORKSPACE_DIR}/video/out/short.mp4" "${WORKSPACE_DIR}/${SLUG}-short.mp4"
```

### 11.5 — Update meta.json

Set `status.short_video_generated: true` and `files.short_video`.

### 11.6 — Present Results

```
Short video generation complete!

Output: <workspaceRoot>/<slug>/<slug>-short.mp4
  Format   : 1080x1920 (9:16 vertical)
  Duration : 30s
  Segment  : Chorus 1 (45.2s - 75.2s)
  Lyrics   : 8 lines synced

Ready for YouTube Shorts upload.
```

---

## Error Handling

| Problem | Fix |
|---|---|
| MusicVideoShort composition not found | Check Root.tsx and video-config.json |
| Black frames | Check trimBefore/trimAfter are in frames |
| No lyrics visible | Verify lyrics within clip window |
| Template missing components | Copy from tools/video-generator/template/src/ |
