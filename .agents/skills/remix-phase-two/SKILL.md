---
name: remix-phase-two
description: Use when remix audio already exists or can be detected in a workspace, and the goal is lyric alignment, optional visual-sequence handling, full video rendering, YouTube metadata, and short-video generation with transliterated sync by default.
---

# Remix Phase Two

## Overview

This skill owns the post-production half of the remix workflow. Native-script lyrics stay canonical, but alignment uses a separate transliterated file by default after Suno metatags are stripped, and phase two runs through both long-form and short-form outputs.

## When to Use

- Remix audio already exists from Step 5, or the user provides it directly
- User wants synced lyrics, video render, YouTube metadata, and optional or default short-form output
- Visual sequence assets or cover art fallback may already exist, be provided, or be skipped

Do not use this when the workspace still needs original download, native-lyrics discovery, or Suno prep. Use `remix-phase-one` instead.

## Quick Reference

| Input resolution order | Default sync text | Optional steps | Phase-two completion |
|---|---|---|---|
| user input -> `meta.json` -> workspace scan | transliterated alignment file | Step 7 visual prep, manual Step 10 selection | Steps 6 -> 11 |

Auto-detect patterns:
- remix audio: selected remix in `meta.json`, then likely `*remix*.mp3`, then likely non-original remix-like MP3s in the workspace
- visual sequence: `meta.json.files.image_sequence`, then `image-sequence.json` plus `stylized-frames/`
- cover art fallback: `meta.json.files.cover_art`, then `*cover-art*`
- lyrics: native lyrics first, then Suno lyrics as fallback input for stripping/transliteration
- short config: `meta.json.shorts_clip_mode`, `meta.json.shorts_duration`, then Step 10 defaults of `auto` and `30`

## Implementation

1. Read `meta.json` first.
2. Resolve remix audio, visual sequence assets, cover art fallback, and lyrics in this order: user-provided, `meta.json`, workspace scan.
3. Keep native lyrics canonical.
4. Before alignment:
   - strip Suno metatags such as `[Verse]`, `[Chorus]`, and similar section markers
   - detect lyric language from the canonical lyrics or workspace metadata
   - create a separate English transliterated alignment file
5. Run Step 6 using the transliterated file by default.
6. Verify alignment quality:
   - check for gaps >30 seconds between consecutive lines
   - if found, review whether the gap represents instrumental sections or alignment errors
7. Use native-script syncing only if the user explicitly requests it.
8. Treat Step 7 visual preparation as composable and optional for rendering:
   - extraction/selection/stylization can start from Step 0 using the original video and `visual_frame_count`
   - `image-sequence.json` manifest generation requires `status.selected_remix` and the selected remix audio after Step 5.5
   - reuse provided or detected `image-sequence.json` plus `stylized-frames/` when available
   - fall back to detected `cover-art.jpg`, then the template placeholder, when visual sequence assets are absent or intentionally skipped
9. Run Steps 8 and 9 and update `meta.json` after each completed step.
10. Continue into short generation by default after Step 9:
   - run Step 10 to select a short clip from the chosen remix and `lyrics-timestamps.json`
   - default to `shorts_clip_mode: auto` unless `meta.json` explicitly requests manual selection
   - if manual mode is enabled, present candidates and pause for the user's choice before Step 11
   - write `shorts-segments.json`, merge short config into `video-config.json`, and persist `status.shorts_clip_selected`
11. Run Step 11 after Step 10 selection completes:
   - verify the existing Remotion project contains the short composition and required vertical layout components
   - render the 9:16 short and copy it to `<slug>-short.mp4`
   - update `meta.json` with `status.short_video_generated` and `files.short_video`

## Common Mistakes

| Mistake | Fix |
|---|---|
| Aligning directly from `suno-lyrics.txt` | Strip metatags and create a transliterated alignment file first |
| Treating Step 7 as always required for rendering | Reuse or skip visual sequence assets; use cover art or placeholder fallback when available |
| Running Step 7 manifest before selected remix exists | Pause manifest creation until `status.selected_remix` and the selected remix audio exist |
| Assuming stylized frames must be JPG | Accept `.jpg`, `.jpeg`, `.png`, or `.webp` in `stylized-frames/` |
| Stopping after Step 9 | Continue through Step 10 clip selection and Step 11 short render unless the user explicitly narrows scope |
| Asking the user to choose a short clip in auto mode | Auto-select the highest-scoring segment unless `shorts_clip_mode` is `manual` |
| Ignoring user-supplied assets | Resolve files in the documented priority order |
| Replacing canonical native lyrics | Keep native lyrics as source of truth and create a separate sync artifact |

## Failure Patterns

| Baseline default | Required correction |
|---|---|
| Align from `suno-lyrics.txt` as-is | Strip Suno metatags first |
| Use native or Suno text directly for sync | Create a separate transliterated alignment file by default |
| Assume cover art must be regenerated | Prefer provided/detected visual sequence assets; cover art remains fallback |
| Treat phase two as complete after metadata | Run the default post-production chain through Steps 10 and 11 |

## Red Flags

- "The repo says native script only, so I should never transliterate"
- "`suno-lyrics.txt` already has the right structure, so I can align it directly"
- "Step 8 mentions cover art, so I can ignore image-sequence assets"
- "Step 7 manifest can run before the selected remix exists"
- "Step 9 is the last deliverable, so short generation is out of scope"
- "Shorts always need user input before continuing"
- "The user did not pass file paths, so I cannot continue"

If any of these appear, stop and re-apply the phase-two rules: native lyrics stay canonical, transliteration is an alignment artifact, metatags are stripped before sync, missing inputs are auto-detected when possible, Step 7 visual sequence prep stays composable with cover-art fallback, and the default autonomous path continues through Steps 10 and 11 unless `meta.json` or the user requires manual short selection.

## Performance Notes

**Video rendering optimization:**
- Default: 30fps
- For songs >5 minutes: consider 24fps (20% fewer frames)
- Use `--concurrency=8` or match CPU cores
- Long songs (>5 min) may take 20-30 minutes to render

**Two-file approach:**
- Native script: `<slug>-lyrics.txt` (canonical, never modified)
- Romanized: `lyrics-timestamps-romanized.json` (alignment artifact, sync source)
