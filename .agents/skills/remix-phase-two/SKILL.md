---
name: remix-phase-two
description: Use when remix audio already exists or can be detected in a workspace, and the goal is lyric alignment, optional cover-art handling, video rendering, and YouTube metadata generation with transliterated sync by default.
---

# Remix Phase Two

## Overview

This skill owns the post-production half of the remix workflow. Native-script lyrics stay canonical, but alignment uses a separate transliterated file by default after Suno metatags are stripped.

## When to Use

- Remix audio already exists from Step 5, or the user provides it directly
- User wants synced lyrics, video render, and YouTube metadata
- Cover art may already exist, be provided, or be skipped

Do not use this when the workspace still needs original download, native-lyrics discovery, or Suno prep. Use `remix-phase-one` instead.

## Quick Reference

| Input resolution order | Default sync text | Optional step |
|---|---|---|
| user input -> `meta.json` -> workspace scan | transliterated alignment file | Step 7 |

Auto-detect patterns:
- remix audio: selected remix in `meta.json`, then likely `*remix*.mp3`, then likely non-original remix-like MP3s in the workspace
- cover art: `meta.json.files.cover_art`, then `*cover-art*`
- lyrics: native lyrics first, then Suno lyrics as fallback input for stripping/transliteration

## Implementation

1. Read `meta.json` first.
2. Resolve remix audio, cover art, and lyrics in this order: user-provided, `meta.json`, workspace scan.
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
8. Treat Step 7 as optional:
   - reuse provided or detected cover art when available
   - fetch cover art only if needed
   - continue if cover art is intentionally skipped and the video path supports it
9. Run Steps 8 and 9 and update `meta.json` after each completed step.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Aligning directly from `suno-lyrics.txt` | Strip metatags and create a transliterated alignment file first |
| Treating Step 7 as always required | Reuse or skip cover art when the workflow allows it |
| Ignoring user-supplied assets | Resolve files in the documented priority order |
| Replacing canonical native lyrics | Keep native lyrics as source of truth and create a separate sync artifact |

## Failure Patterns

| Baseline default | Required correction |
|---|---|
| Align from `suno-lyrics.txt` as-is | Strip Suno metatags first |
| Use native or Suno text directly for sync | Create a separate transliterated alignment file by default |
| Assume cover art must be regenerated | Reuse provided or detected cover art and keep Step 7 optional |

## Red Flags

- "The repo says native script only, so I should never transliterate"
- "`suno-lyrics.txt` already has the right structure, so I can align it directly"
- "Step 8 mentions cover art, so Step 7 must always run"
- "The user did not pass file paths, so I cannot continue"

If any of these appear, stop and re-apply the phase-two rules: native lyrics stay canonical, transliteration is an alignment artifact, metatags are stripped before sync, missing inputs are auto-detected when possible, and Step 7 stays optional.

## Performance Notes

**Video rendering optimization:**
- Default: 30fps
- For songs >5 minutes: consider 24fps (20% fewer frames)
- Use `--concurrency=8` or match CPU cores
- Long songs (>5 min) may take 20-30 minutes to render

**Two-file approach:**
- Native script: `<slug>-lyrics.txt` (canonical, never modified)
- Romanized: `lyrics-timestamps-romanized.json` (alignment artifact, sync source)
