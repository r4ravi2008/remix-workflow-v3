# Pilla Acapella Cleanup Design

## Goal

Create a one-off, reversible cleanup workflow for the original vocal stem from `Pilla Ayithey Keka Undhi`, which currently sounds overly roomy or hall-like. The workflow should produce cleaned vocal outputs for listening review without replacing existing workspace files.

## Target Input

- Workspace: `workspaces/pilla-ayithey-keka-undhi-deep-house-trap/`
- Input: `pilla-ayithey-keka-undhi-deep-house-trap-acapella.mp3`
- Source role: original extracted acapella, not the Suno remix acapella

## Outputs

Generate three candidate files next to the source stem:

- `pilla-ayithey-keka-undhi-deep-house-trap-acapella-cleaned-light.mp3`
- `pilla-ayithey-keka-undhi-deep-house-trap-acapella-cleaned-medium.mp3`
- `pilla-ayithey-keka-undhi-deep-house-trap-acapella-cleaned-strong.mp3`

Also write a small manifest:

- `vocal-cleanup-settings.json`

The manifest records input path, output paths, filter chain, command parameters, and timestamp so the best result can be reproduced or promoted into a toolbox feature later.

## Workflow

1. Convert the MP3 input to a temporary WAV working file.
2. Apply a cleanup chain using FFmpeg and available Python audio tooling.
3. Export three MP3 candidates at 192 kbps.
4. Preserve all existing files and avoid mutating `meta.json` until a cleaned candidate is explicitly selected for pipeline use.

## Cleanup Chain

Each preset uses the same stages with different strengths:

- High-pass filtering to remove low room rumble.
- Presence-focused EQ to keep vocal intelligibility.
- Gentle low-pass filtering to reduce brittle separation artifacts.
- Expansion/noise-gate behavior to reduce reverb tails between sung phrases.
- Loudness normalization to keep outputs easy to compare.

The initial implementation should prefer deterministic local processing over cloud or UI tools. If the installed Python stack does not provide a reliable dereverb model, avoid adding heavy dependencies during the one-off pass and use FFmpeg-based cleanup first.

## Feature Path

If one of the candidates is useful, the workflow can later become a reusable acapella toolbox command:

```bash
python -m acapella_extractor.clean input.mp3 -o output.mp3 --preset light|medium|strong
```

The future feature should live under `tools/acapella-extractor/src/acapella_extractor/clean.py`. Tests should validate CLI parsing, command construction, output naming, and manifest writing. Audio quality should be evaluated manually with A/B listening rather than unit tests.

## Verification

- Confirm all three cleaned MP3 files exist and have the same approximate duration as the input.
- Confirm the input file remains unchanged.
- Confirm `vocal-cleanup-settings.json` records exact commands/settings.
- Listen to the three candidates and pick the least roomy version that does not introduce obvious pumping, muffling, or watery artifacts.

## Non-Goals

- Do not replace the existing acapella automatically.
- Do not regenerate the remix or video.
- Do not add a reusable toolbox feature until the one-off workflow proves useful on this stem.
