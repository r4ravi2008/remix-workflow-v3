# Step 11: Generate and Validate the Vertical Video

## Objective

Build an intelligently reframed 1080x1920 Resolve picture master, prove every
scene's framing with an independent contact-sheet review, then render a mobile
Remotion version whose picture occupies 80% of the canvas, with lyrics and the
equalizer in dedicated 10% bands.

## Key Requirements

- Resolve master: 1080x1920, shot-specific focal reframing
- Remotion output: 1080x1920
- Picture band: top 1536px (80%)
- Active lyric band: next 192px (10%)
- Equalizer/progress band: bottom 192px (10%)
- Audio trimming: Remotion `trimBefore`/`trimAfter`
- Lyrics sync: only lyrics within the clip window, rebased to zero
- Review: head, middle, and tail samples from every scene, inspected by a
  separate sub-agent before and after the Remotion wrapper

## Prerequisites

- `${WORKSPACE_DIR}/shorts-segments.json` exists
- `${WORKSPACE_DIR}/video/` exists from Step 8
- `${WORKSPACE_DIR}/video/public/video-config.json` includes `short`
- The approved Resolve timeline or approved picture source is available
- `.agents/skills/remix-phase-two/references/vertical-resolve-remotion.md` has
  been read

## Workspace Path Resolution

Before using any filesystem path:

1. Read `.remix-workspace-root.json` from the repository root.
2. Resolve `WORKSPACE_ROOT` from `workspaceRoot`.
3. Resolve `WORKSPACE_DIR` as `<workspaceRoot>/<slug>/`.
4. Use absolute paths below `WORKSPACE_DIR` for commands.
5. Store `meta.json.files.*` paths relative to the workspace root.

## Instructions

### 11.1 — Verify inputs and short configuration

Confirm `video-config.json.short` contains numeric `startTime`, `endTime`, and
`duration`, and that `duration == endTime - startTime` within one video frame.
Resolve the approved picture and audio sources using the normal user input ->
`meta.json` -> workspace scan priority.

### 11.2 — Build the Resolve vertical picture master

1. Duplicate the approved landscape timeline.
2. Set the duplicate to 1080x1920 without changing frame rate.
3. Inventory every scene in `${WORKSPACE_DIR}/resolve-scenes.json` with its id,
   start, end, label, focal point, and whether its reframe is static or keyed.
4. Reframe each shot around its semantic focal point. Faces, eyes, mouths,
   hands, instruments, essential action, and intentional text must remain intact
   throughout the shot. Keyframe moving focal points.
5. Prefer an alternate take over a damaging crop. Use restrained background
   extension or blurred fill only when a clean crop cannot preserve the subject.
6. Keep the duplicate aligned to the full approved remix timeline and export
   `${WORKSPACE_DIR}/${SLUG}-resolve-vertical.mp4`. Remotion owns the later
   selected-segment trim.

Probe the rendered file, not merely the Resolve job. It must contain a video
stream, decode fully, report 1080x1920, match the approved full-remix duration,
and contain no unintended blanking.

### 11.3 — Generate and independently review every Resolve scene

```bash
.agents/skills/remix-phase-two/scripts/generate-scene-contact-sheets.sh \
  "${WORKSPACE_DIR}/${SLUG}-resolve-vertical.mp4" \
  "${WORKSPACE_DIR}/resolve-scenes.json" \
  "${WORKSPACE_DIR}/vertical-scene-review/resolve"
```

Start a separate review sub-agent. Give it the manifest,
`contact-sheet-index.json`, and every contact-sheet page. Require a per-scene
pass/fail decision after inspecting all three samples. The editing agent may not
self-approve this gate.

If any scene fails, fix it in Resolve, re-export, regenerate the affected sheets,
and run a fresh independent review. Save the accepted report at
`${WORKSPACE_DIR}/vertical-scene-review/scene-review.md`.

### 11.4 — Wire the Resolve master into Remotion

Verify `MusicVideoShort.tsx` and `CoverArtVerticalLayout.tsx` match the current
template. Copy the accepted Resolve render into the Remotion public directory:

```bash
cp "${WORKSPACE_DIR}/${SLUG}-resolve-vertical.mp4" \
  "${WORKSPACE_DIR}/video/public/resolve-vertical.mp4"
```

Set `video-config.json.short.videoSrc` to `resolve-vertical.mp4`.

The template must render fixed bands:

- `0..1535`: Resolve video. Use a muted `<Video>` and `objectFit: contain` so
  Remotion never introduces a second crop. A blurred duplicate may fill unused
  panel edges.
- `1536..1727`: current native-script lyric only. Fit against the loaded font,
  retain at least 60px horizontal inset, and cap at two lines.
- `1728..1919`: equalizer and progress.

The selected remix audio is the only audible source. Mute the Resolve video.

### 11.5 — Render the Remotion short

```bash
cd "${WORKSPACE_DIR}/video"
npx remotion render MusicVideoShort out/short.mp4
cp out/short.mp4 "${WORKSPACE_DIR}/${SLUG}-short.mp4"
```

### 11.6 — Validate the final wrapped output

Intersect `resolve-scenes.json` with the selected short window, clip boundary
scenes to that window, subtract the short start time, and write the result to
`resolve-scenes-short.json`. Generate contact sheets for the final Remotion file
with this rebased manifest. Have a separate review sub-agent inspect every
included scene again for:

- no new picture crop or blanking;
- lyric text readable at 25% preview, within two lines, and fully inside its
  10% band;
- equalizer fully inside the bottom 10%;
- no overlap among picture, lyric, and equalizer bands;
- correct first and last frames for the selected segment.

Run a full decode plus dimensions, video-stream, and audio-stream checks. Compare
the video-stream duration, audio-stream duration, container duration, and expected
composition duration; explain or fix any difference greater than one frame. A
successful render command alone is not acceptance.

### 11.7 — Update meta.json

Set:

```json
{
  "files": {
    "resolve_vertical_video": "<slug>/<slug>-resolve-vertical.mp4",
    "vertical_scene_contact_sheet": "<slug>/vertical-scene-review/final/contact-sheet-index.json",
    "vertical_scene_review": "<slug>/vertical-scene-review/scene-review.md",
    "short_video": "<slug>/<slug>-short.mp4"
  },
  "status": {
    "resolve_vertical_generated": true,
    "vertical_scene_review_passed": true,
    "short_video_generated": true
  }
}
```

Do not set any of these status fields until the referenced artifact exists and
its required review has passed.

### 11.8 — Present results

Report the Resolve master, Remotion short, number of scenes reviewed, contact
sheet page count, independent review result, layout split, duration, and the
full-file technical checks.

## Error Handling

| Problem | Fix |
|---|---|
| Subject is clipped in one scene | Reframe or keyframe that scene; do not scale the whole timeline |
| Contact sheet misses a short scene | Fix `resolve-scenes.json`; every scene needs head/middle/tail samples |
| Reviewer cannot read a cell | Regenerate with fewer or larger cells; do not infer a pass |
| Resolve video has audio in Remotion | Keep the embedded video muted; selected remix audio owns sound |
| Video is cropped again by Remotion | Use `objectFit: contain` in the 80% picture band |
| Lyric overflows | Fit using actual font metrics, reduce size, and cap at two lines |
| Equalizer overlaps lyrics | Keep fixed 80/10/10 bands; do not position by eye |
| Black frames | Verify source trim units and run full-file decode |
| Template is stale | Copy current short components and re-run typecheck/tests |
