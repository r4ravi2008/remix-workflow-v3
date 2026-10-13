# Design: Acapella Pitch/BPM Variations for Copyright Avoidance

## Goal
Render multiple pitch-shifted and tempo-shifted versions of the extracted acapella so the user can try different inputs in Step 5 (Suno upload / ACE-Step generation) to reduce copyright-flag risk.

## Context
- Workspace: `nuvvantene-istam-deep-house`
- Detected original BPM: 103.359
- Detected key: C minor
- Existing tool: `tools/acapella-extractor/src/acapella_extractor/prepare.py` supports `--target-bpm` and `--pitch-semitones`.

## Variants
| Variant | Target BPM | Pitch Semitones | Purpose |
|---------|-----------|-----------------|---------|
| b95-p-2 | 95 | -2 | Slower, lower, moodier |
| b103-p0 | 103.359 | 0 | Canonical prepped acapella (already exists) |
| b110-p2 | 110 | +2 | Brighter, club-ready lift |
| b120-p3 | 120 | +3 | Energetic, more distinct from original |

## Output Files
For each variant:
- `<slug>-acapella-prepped-b<bpm>-p<sign><semitones>.mp3`
- `<slug>-acapella-prepped-b<bpm>-p<sign><semitones>.json`

The existing `<slug>-acapella-prepped.mp3` and `<slug>-acapella-prep.json` remain the canonical files.

## Meta.json Update
Add an `acapella_variants` array under the top-level object, each entry containing:
- `variant_id`: e.g. `b95-p-2`
- `target_bpm`
- `pitch_semitones`
- `mp3`: workspace-root-relative path
- `report`: workspace-root-relative path

## Implementation Notes
- Run `prepare.py` once per variant with explicit `--target-bpm` and `--pitch-semitones`.
- Verify each output file is readable and non-zero.
- No changes to lyrics, Suno style, or design.json.
