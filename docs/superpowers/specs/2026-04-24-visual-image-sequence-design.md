# Visual Image Sequence Design

## Summary

Replace the current single-cover-art visual path with a composable image sequence pipeline. The pipeline downloads the original YouTube video, extracts a configurable number of evenly spaced source frames, stylizes every selected frame with the same prompt/settings, and feeds a timed `image-sequence.json` manifest into the Remotion video scaffold.

The final video keeps the current cover-art layout structure and beat-reactive behavior. The only visual change is that the static `cover-art.jpg` becomes a timed sequence of stylized source-video frames.

## Goals

- Use frames from the original YouTube video as the source visual material.
- Keep every stage composable and resumable through explicit workspace artifacts.
- Make frame count configurable, defaulting to `20`.
- Apply one shared stylization prompt/settings set to all selected frames for visual consistency.
- Preserve the existing Remotion beat-reactive scale, glow, rings, vignette, lyrics, visualizer, title, and genre behavior.
- Fall back to existing `cover-art.jpg` or placeholder behavior when the image sequence is unavailable.

## Non-Goals

- Beat-energy-based frame selection for v1.
- Per-frame prompt generation or scene-aware prompt variation.
- Replacing lyrics alignment, Suno generation, or short-video selection behavior.
- Removing support for `cover-art.jpg` fallback.

## Pipeline Artifacts

The workspace gains these artifacts:

- `<slug>-original-video.mp4`: original YouTube video downloaded from `meta.json.youtube_url`.
- `source-frames/<slug>-frame-001.jpg` through `source-frames/<slug>-frame-NNN.jpg`: raw source screenshots extracted from the original video.
- `visual-frame-candidates.json`: extraction report containing attempted timestamps, resolved timestamps, and raw frame paths.
- `selected-visual-frames.json`: selected source frames and source timestamps.
- `stylized-frames/<slug>-frame-001.jpg` through `stylized-frames/<slug>-frame-NNN.jpg`: stylized frame outputs.
- `image-sequence.json`: stable render contract consumed by Remotion.

The pipeline can regenerate any artifact without rerunning unrelated remix steps.

## Metadata Changes

Add workspace-level config:

```json
{
  "visual_frame_count": 20
}
```

Add file references:

```json
{
  "files": {
    "original_video": "<slug>/<slug>-original-video.mp4",
    "visual_frame_candidates": "<slug>/visual-frame-candidates.json",
    "selected_visual_frames": "<slug>/selected-visual-frames.json",
    "image_sequence": "<slug>/image-sequence.json"
  }
}
```

Add status flags:

```json
{
  "status": {
    "original_video_downloaded": false,
    "visual_frames_extracted": false,
    "visual_frames_selected": false,
    "visual_frames_stylized": false
  }
}
```

`visual_frame_count` defaults to `20` when absent. A future CLI flag such as `--frame-count=24` may override this for reruns, but `meta.json` remains the workspace source of truth.

## Selection Behavior

Frame selection is deterministic and evenly spaced.

1. Resolve `visual_frame_count` from `meta.json`, defaulting to `20`.
2. Determine original video duration from `<slug>-original-video.mp4`.
3. Generate `visual_frame_count` timestamps evenly spaced across the source video duration using midpoint buckets, so the first and last selected frames avoid the exact video boundaries.
4. Extract a source screenshot at each timestamp, using the nearest decodable frame if the exact timestamp fails.
5. Preserve chronological order in `selected-visual-frames.json`.
6. If fewer frames can be extracted after retries, proceed with available frames and record the shortage in the extraction report.

The final video's musical energy continues to come from existing audio-reactive Remotion behavior, not from scene-change timing.

Example `selected-visual-frames.json`:

```json
{
  "version": 1,
  "source_video": "<slug>/<slug>-original-video.mp4",
  "requested_count": 20,
  "selected_count": 20,
  "frames": [
    {
      "id": "frame-001",
      "source_timestamp": 3.2,
      "source_image_path": "source-frames/<slug>-frame-001.jpg"
    }
  ]
}
```

## Stylization Behavior

Stylization reads `selected-visual-frames.json` and applies the same prompt/settings to every selected frame.

- Input: selected source frame images.
- Output: `stylized-frames/<slug>-frame-NNN.jpg`.
- Prompt: one shared style prompt for the entire sequence.
- Consistency: no per-frame prompt variation in v1.

If stylization fails for individual frames, keep successful outputs and report failed frame IDs. Rendering may proceed with the successful subset.

## Render Manifest

`image-sequence.json` is the contract between visual preparation and Remotion.

```json
{
  "version": 1,
  "source": {
    "video": "<slug>/<slug>-original-video.mp4",
    "selection": "evenly-spaced",
    "requested_count": 20
  },
  "frames": [
    {
      "id": "frame-001",
      "image_path": "stylized-frames/<slug>-frame-001.jpg",
      "source_timestamp": 3.2,
      "start_time": 0,
      "end_time": 12.4,
      "transition": "crossfade"
    }
  ]
}
```

The manifest distributes the stylized frames evenly across the final remix audio duration. `start_time` and `end_time` are render times in seconds, not source-video timestamps.

## Remotion Rendering Behavior

The Remotion template keeps the current cover-art layout as the base.

1. `design.layout.variant` can remain `"cover-art"`.
2. `MusicVideo` or `CoverArtLayout` checks for `image-sequence.json` in `public/`.
3. If the manifest exists and has valid frames, the active frame replaces `cover-art.jpg` in the main inset image and blurred background image.
4. If the manifest is missing, malformed, empty, or references missing files, fall back to `cover-art.jpg`.
5. If both sequence and cover art are missing, keep the existing placeholder.

The existing beat-reactive behavior must remain unchanged:

- Bass-driven `artScale` continues to scale the active image.
- Glow, vignette, rings, title glow, badge pulse, lyrics, progress bar, and frequency bars continue to behave as they do today.
- Scene changes use subtle crossfade. Ken Burns movement is optional and should be skipped in v1 if it conflicts with beat-reactive scale.

## Step Integration

The clean integration is to replace the current Step 7 cover-art fetch with a composable Step 7 visual-sequence preparation phase, while preserving Step 8 as the renderer.

- Step 7 downloads `<slug>-original-video.mp4` from `meta.json.youtube_url`.
- Frame extraction/selection is an independent command or script.
- Stylization is an independent command or step that reads selected frames and writes `image-sequence.json`.
- Step 8 copies `image-sequence.json` and `stylized-frames/` into `video/public/` before rendering.
- Existing `cover-art.jpg` support remains a fallback path, not the primary Step 7 output.

This keeps each operation composable and avoids forcing users to rerun lyrics, Suno, alignment, or rendering when only visual assets changed.

## Error Handling

- If original video download fails, leave visual-sequence statuses false and allow the existing cover-art flow.
- If exact frame extraction fails at a timestamp, retry with the nearest decodable frame.
- If fewer than the requested frame count is available, continue with available frames and record the shortage.
- If stylization fails for some frames, keep successful frames and record failed IDs.
- If `image-sequence.json` is invalid at render time, Remotion falls back to `cover-art.jpg`.
- If both sequence and cover art are unavailable, the existing placeholder remains the final fallback.

## Testing And Verification

- Unit-test even timestamp generation for different durations and frame counts.
- Unit-test low-candidate behavior and shortage reporting.
- Unit-test manifest validation and fallback behavior.
- Unit-test any scaffolder support for copying `image-sequence.json` and `stylized-frames/`.
- Render-smoke-test `MusicVideo` with a small fixture manifest and placeholder images.
- Verify docs updates in workspace conventions and Step 8 so new files and statuses are discoverable.

## Open Implementation Notes

- Prefer FFmpeg for extracting exact source screenshots from the original video.
- Keep `image-sequence.json` path values relative to `video/public/` once copied into the Remotion project.
- Keep `meta.json.files.*` values root-relative, following existing workspace conventions.
- Avoid changing the short-video composition in v1 unless the same sequence manifest naturally works there.
