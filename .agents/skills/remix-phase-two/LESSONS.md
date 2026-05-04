# Remix Workflow Lessons Learned

Operational mistakes and practical fixes discovered while running the full remix pipeline.

## 1. Transliteration Should Be Default, Not Manual

**What happened:** User had to explicitly ask for transliteration after we'd already aligned with Telugu lyrics.

**Fix:** Phase two now defaults to transliterated sync (see `remix-phase-two` skill).

## 2. Alignment Quality Gaps Aren't Automatically Flagged

**What happened:** Verify output showed a 107-second gap for one line (3:47 to 5:34) but wasn't treated as a failure.

**Pattern to watch for:**
```
[03:47.300] → [05:34.380]  (107.08s)  Angatlo Poolanni...
```

**Fix:** Add gap threshold check (>30s between lines should trigger review).

## 3. Step 7 Visual Prep Is Composable, Not A Render Blocker

**What happened:** Step 8 historically centered cover art, and later visual-sequence prep added a manifest step that requires selected remix audio. This can confuse agents into either blocking rendering on Step 7 or running manifest generation too early.

**Fix:** `remix-phase-two` skill marks Step 7 as visual-sequence-first and composable: extraction can start from Step 0, manifest waits for selected remix audio, rendering can fall back to `cover-art.jpg` or placeholder.

## 4. Auto-Detection Must Be Documented

**What happened:** When user provided custom file paths, I asked instead of auto-detecting.

**Fix:** Phase two skill now documents auto-detection priority: user input → meta.json → workspace scan.

## 5. Video Rendering Is Slow Without Concurrency Tweaks

**What happened:** 10,034 frames took significant time with default settings.

**Observed:** ~7-9 minutes estimated initially
**Reality:** ~20-30 minutes actual

**Potential improvements:**
- Reduce FPS if quality allows (24fps vs 30fps = 20% fewer frames)
- Use `concurrency` flag: `npx remotion render --concurrency=8`
- Consider splitting long songs or using preview mode first

## 6. Baseline Agents Violate Pipeline Rules Without Skills

**What happened:** Testing showed agents default to:
- Aligning directly from `suno-lyrics.txt`
- Skipping transliteration
- Treating Step 7 as required for rendering
- Running visual-sequence manifest before selected remix audio exists
- Not auto-detecting files

**Fix:** Three skills now enforce correct defaults (remix-phase-one, remix-phase-two, remix-full-pipeline).

## 7. Phase Boundaries Must Be Explicit

**What happened:** Multiple clarifications needed about:
- What constitutes phase one vs phase two
- Whether Step 5 is in phase one or separate
- Whether checkpoint is part of phase one or between phases

**Fix:** Skills now explicitly define boundaries:
- Phase one: Steps 0-4, optionally 5
- Checkpoint: After phase one, before phase two
- Phase two: Steps 6-11, with Step 7 visual prep composable and Step 10/11 short output default

## 8. Native Script Preservation vs Transliteration Sync

**What happened:** Initial confusion about whether to transliterate at all.

**Resolution:** Two separate files:
- `<slug>-lyrics.txt` = native script (canonical, preserved)
- `<slug>-lyrics-romanized.txt` or `lyrics-timestamps-romanized.json` = alignment artifact

## 9. Latest User Instruction Overrides Earlier Step Skips

**What happened:** User said to skip Step 7, then later clarified that frames should be stylized. Treating the earlier skip as permanent caused the visual sequence to be under-handled.

**Fix:** Reconcile each new user correction against earlier session state. If the user re-opens a previously skipped step, resume from existing artifacts instead of defending the stale skip.

**State rule:** Record the resolved decision in `meta.json` or a workspace note so the retired instruction does not keep influencing later steps.

## 10. Lossless User Audio Stays Canonical

**What happened:** A user-provided WAV was converted to MP3 for pipeline compatibility. That derived MP3 risked becoming the selected remix by accident.

**Fix:** Store the explicitly confirmed WAV/FLAC as `files.selected_remix`. MP3 copies are compatibility artifacts only, and every duration probe, alignment path, render asset, and metadata field must be checked for audio consistency.

## 11. Copied Visual Assets Do Not Prove They Render

**What happened:** `image-sequence.json` and `stylized-frames/` were copied into Remotion, but the active design used `center-stage`, which ignores the sequence. The video rendered without the intended frames.

**Fix:** Pre-render review must include the active Remotion layout. For the current template, sequence visuals require `cover-art` or another sequence-aware layout. Render a still/preview to verify frames are visible before a full render.

**Verification rule:** A successful still render is not enough. Inspect the still/preview and confirm it contains the intended frame imagery.

## 12. Deleted Frames May Be User Curation

**What happened:** Missing source frames were title cards intentionally deleted by the user. Regenerating them fought the user's curation.

**Fix:** Ask whether missing curated assets should be excluded or regenerated if intent is unclear. When the user says continue without them, remove those frames from `selected-visual-frames.json` and regenerate `image-sequence.json` with the remaining frames.

## Checklist for Future Runs

Before starting phase two:
- [ ] Confirm lyric language detected
- [ ] Strip Suno metatags from alignment source
- [ ] Create transliterated alignment file
- [ ] Verify alignment has no >30s gaps
- [ ] Confirm `image-sequence.json` + `stylized-frames/` exist, or cover art/placeholder fallback is intentional
- [ ] Update `meta.json` with `lyrics_timestamps` path

Before rendering video:
- [ ] Check `video-config.json` has correct duration
- [ ] Confirm `lyrics-timestamps.json` is romanized version
- [ ] Verify `image-sequence.json` and `stylized-frames/` are in `video/public/` when using sequence visuals
- [ ] Verify active `design.json` layout renders visual sequence assets (`cover-art` in the current template)
- [ ] Verify the selected Remotion composition and props reference the intended audio and lyrics assets
- [ ] Render a still/preview and inspect it to confirm the intended frame sequence appears
- [ ] Confirm user-confirmed WAV/FLAC remains canonical if MP3 compatibility copies exist
- [ ] Exclude user-deleted title cards/bad frames from `selected-visual-frames.json` and `image-sequence.json`
- [ ] Verify `cover-art.jpg` is in `video/public/cover-art.jpg` only when using cover-art fallback
- [ ] Consider preview render for long songs (>5 min)
