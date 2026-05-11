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
- ACE-Step context: `meta.json.files.ace_step_generation`, then `<slug>-ace-step-generation.json`; inspect `effective_request` when generation settings matter
- visual sequence: `meta.json.files.image_sequence`, then `image-sequence.json` plus `stylized-frames/`
- cover art fallback: `meta.json.files.cover_art`, then `*cover-art*`
- lyrics: native lyrics first, then Suno lyrics as fallback input for stripping/transliteration
- short config: `meta.json.shorts_clip_mode`, `meta.json.shorts_duration`, then Step 10 defaults of `auto` and `30`

## Implementation

1. Read `meta.json` first.
2. Before each step, verify that step's required inputs exist, are readable, and still match the user's latest instructions. If user-provided files or newer obvious workspace candidates disagree with `meta.json`, pause long enough to reconcile them, prefer the latest explicit user intent, update state after verification, and do not render stale assets. Newer user corrections override earlier instructions from the same session; record the resolved decision in `meta.json` or a workspace note so the stale instruction is visibly retired.
3. Resolve remix audio, visual sequence assets, cover art fallback, and lyrics in this order: user-provided, `meta.json`, workspace scan.
4. If ACE-Step generated candidates exist but `meta.json.status.selected_remix` is missing, stop and ask the user to choose `v1` or `v2` before alignment or rendering.
5. Canonicalize audio ownership before alignment or rendering:
   - if the user explicitly provides or later confirms a WAV/FLAC as the correct remix, keep that lossless file as canonical in `meta.json.files.selected_remix`
   - create MP3 copies only as compatibility artifacts for tools that require MP3, and label them as derived assets
   - ensure alignment audio, render audio, duration probes, `video-config.json`, and metadata all point to the intended canonical or declared derivative; never let WAV and MP3 coexist ambiguously
6. Validate assets semantically, not just by filename or dimensions:
   - confirm selected remix audio is the intended final mix when multiple remix-like MP3/WAV files exist, especially if a newer explicit user-provided file appears after the stored selection
   - inspect visual sequence frames for internal letterboxing, black padding, watermarks, captions, or unwanted prompt text before rendering
   - if the user intentionally deleted bad/title-card frames, exclude those frames from `selected-visual-frames.json` and `image-sequence.json`; do not regenerate them unless explicitly asked
   - verify the active Remotion layout consumes the detected `image-sequence.json` and `stylized-frames/`; `cover-art` layout renders the visual sequence, while layouts such as `center-stage` may ignore it
   - verify Telugu-capable fonts are installed or bundled before headless render when native-script lyrics are displayed
7. Run a pre-render manifest review before Step 8/9/11 renders: selected audio path, lyrics/timestamps path, visual manifest, copied public assets, active Remotion layout, selected Remotion composition, composition props such as `audioSrc`/`lyricsDataSrc`, font dependency/imports, and whether any source asset changed after the previous output timestamp.
8. Render a cheap still or short preview after wiring visual assets and before committing to a full long render. Inspect the preview content and verify the expected frame imagery is visible, not merely that the still command succeeded or files were copied to `public/`.
9. Keep native lyrics canonical.
10. Before alignment:
   - strip Suno metatags such as `[Verse]`, `[Chorus]`, and similar section markers
   - detect lyric language from the canonical lyrics or workspace metadata
   - create a separate English transliterated alignment file
11. Run Step 6 using the transliterated file by default.
12. Verify alignment quality:
   - check for gaps >30 seconds between consecutive lines
   - if found, review whether the gap represents instrumental sections or alignment errors
13. Use native-script syncing only if the user explicitly requests it.
14. Treat Step 7 visual preparation as composable and optional for rendering:
   - extraction/selection/stylization can start from Step 0 using the original video and `visual_frame_count`
   - `image-sequence.json` manifest generation requires `status.selected_remix` and the selected remix audio after Step 5.5
   - reuse provided or detected `image-sequence.json` plus `stylized-frames/` when available
   - if the user first skips visual prep but later asks for stylized frames, resume Step 7 from the latest instruction rather than treating the earlier skip as permanent
   - fall back to detected `cover-art.jpg`, then the template placeholder, when visual sequence assets are absent or intentionally skipped
15. Run Steps 8 and 9 and update `meta.json` after each completed step.
16. Continue into short generation by default after Step 9:
   - run Step 10 to select a short clip from the chosen remix and `lyrics-timestamps.json`
   - default to `shorts_clip_mode: auto` unless `meta.json` explicitly requests manual selection
   - if manual mode is enabled, present candidates and pause for the user's choice before Step 11
   - write `shorts-segments.json`, merge short config into `video-config.json`, and persist `status.shorts_clip_selected`
17. Run Step 11 after Step 10 selection completes:
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
| Trusting stale `meta.json` over new user files | Reconcile explicit user-provided inputs first, then update `meta.json` |
| Treating an earlier "skip Step 7" as permanent after user asks for stylized frames | Apply the latest user instruction; resume visual prep from available artifacts |
| Converting user-provided WAV to MP3 and then forgetting the WAV | Store the WAV as canonical and mark MP3 as a derived compatibility artifact |
| Accepting square frame dimensions as sufficient | Inspect frames for internal padding, borders, captions, or watermarks before rendering |
| Regenerating deleted title-card frames | Treat user deletion as curation; remove those frames from selection and sequence manifests |
| Reusing an old Remotion scaffold after template changes | Verify the scaffold contains current dependencies, font imports, and visual-sequence support |
| Checking copied frame files but not active layout | Confirm the Remotion layout actually consumes image-sequence assets; switch to `cover-art` or another sequence-aware layout if needed |
| Treating a successful still render as visual verification | Inspect the still/preview content and confirm expected frame imagery appears |
| Updating behavior but not state after a user correction | Record superseded instructions and resolved decisions in workspace state |
| Rendering over outputs after inputs changed | Compare output timestamps to selected audio, timestamps, visual assets, and template files; regenerate stale outputs |
| Starting phase two from ACE-Step candidates without selection | Ask for `v1` or `v2`, then persist `status.selected_remix` before Step 6 |

## Failure Patterns

| Baseline default | Required correction |
|---|---|
| Align from `suno-lyrics.txt` as-is | Strip Suno metatags first |
| Use native or Suno text directly for sync | Create a separate transliterated alignment file by default |
| Assume cover art must be regenerated | Prefer provided/detected visual sequence assets; cover art remains fallback |
| Treat phase two as complete after metadata | Run the default post-production chain through Steps 10 and 11 |
| Dimension-check frames only | Check actual image content for letterboxing and unwanted text |
| Render from whatever `meta.json` selects | Reconfirm when the workspace contains newer explicit remix audio |
| Manifest exists but visuals are absent | Check active Remotion layout and render a still/preview before full render |
| Missing source frames are automatically extraction failures | Check whether the user intentionally removed bad/title-card frames and update manifests accordingly |
| Assume a successful render means fonts are correct | Verify bundled/system Telugu font availability and inspect preview/output when fonts changed |

## Red Flags

- "The repo says native script only, so I should never transliterate"
- "`suno-lyrics.txt` already has the right structure, so I can align it directly"
- "Step 8 mentions cover art, so I can ignore image-sequence assets"
- "Step 7 manifest can run before the selected remix exists"
- "Step 9 is the last deliverable, so short generation is out of scope"
- "Shorts always need user input before continuing"
- "The user did not pass file paths, so I cannot continue"
- "`meta.json` is authoritative even though the user added a newer final mix"
- "The user said skip Step 7 earlier, so I should ignore their later request to stylize frames"
- "The MP3 copy exists, so the original user-provided WAV no longer matters"
- "The image sequence is copied, so it must be visible in the render"
- "The still command succeeded, so the visual sequence must be visible"
- "Missing frame files should be regenerated, even if the user deleted title cards"
- "1024x1024 means the frames are safe for cover-art rendering"
- "`center-stage` looks better, so it is fine even when the user asked for video frames"
- "The video rendered once, so font/template changes do not need re-verification"
- "A newer `final-v1.mp3` is only a workspace scan result, so stale `meta.json` still wins"
- "Both ACE-Step candidates exist, so I can pick one automatically"

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
