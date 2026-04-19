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

## 3. Step 7 Is Documented as Required But Should Be Optional

**What happened:** Step 8 docs say cover art is required, creating confusion about Step 7 being optional.

**Fix:** `remix-phase-two` skill explicitly marks Step 7 optional with fallback path.

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
- Treating Step 7 as required
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
- Phase two: Steps 6-9, optionally 7

## 8. Native Script Preservation vs Transliteration Sync

**What happened:** Initial confusion about whether to transliterate at all.

**Resolution:** Two separate files:
- `<slug>-lyrics.txt` = native script (canonical, preserved)
- `<slug>-lyrics-romanized.txt` or `lyrics-timestamps-romanized.json` = alignment artifact

## Checklist for Future Runs

Before starting phase two:
- [ ] Confirm lyric language detected
- [ ] Strip Suno metatags from alignment source
- [ ] Create transliterated alignment file
- [ ] Verify alignment has no >30s gaps
- [ ] Confirm cover art exists or Step 7 skip is intentional
- [ ] Update `meta.json` with `lyrics_timestamps` path

Before rendering video:
- [ ] Check `video-config.json` has correct duration
- [ ] Confirm `lyrics-timestamps.json` is romanized version
- [ ] Verify cover art is in `video/public/cover-art.jpg`
- [ ] Consider preview render for long songs (>5 min)
