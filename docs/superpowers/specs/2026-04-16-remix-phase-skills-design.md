# Remix Phase Skills Design

## Goal

Add three reusable skills for the remix pipeline:

1. `remix-phase-one` for Steps 0-4, with Step 5 optional
2. `remix-phase-two` for Steps 6-9, with Step 7 optional
3. `remix-full-pipeline` as a thin orchestrator that invokes the two phase skills with a checkpoint between them

## Confirmed Rules

- Native-script lyrics remain the source of truth
- Phase two creates a separate transliterated alignment file for sync
- Phase two strips Suno metatags before alignment
- Video sync uses the transliterated alignment output by default
- Native-script syncing happens only if the user explicitly asks for it
- Phase two supports both:
  - standard path: remix output already present from Step 5
  - recovery path: user provides remix audio, cover art, and/or lyrics
- If assets are not provided, phase two auto-detects likely remix audio, cover art, and lyrics files from the workspace

## RED-Phase Findings

Baseline testing without the new skills showed these unwanted defaults:

1. Phase two defaults to aligning directly from `suno-lyrics.txt`
2. Phase two does not introduce transliteration by default
3. Phase two does not explicitly strip Suno metatags before alignment
4. Step 7 is treated as effectively required because Step 8 docs expect cover art
5. Full orchestration tends to make phase one too rigid by folding remix selection into the first phase instead of stopping at a checkpoint

## Skill Boundaries

### remix-phase-one

- Starts from user inputs and workspace preparation
- Runs Steps 0-4
- Runs Step 5 only when remix generation is requested and feasible
- Stops at a handoff checkpoint with prepared workspace artifacts

### remix-phase-two

- Starts when remix assets already exist, are supplied, or can be detected
- Runs Steps 6-9
- Makes Step 7 optional
- Resolves assets in this order: user-provided, `meta.json`, workspace scan

### remix-full-pipeline

- Does not restate step details
- Delegates to `remix-phase-one`
- Pauses at the phase checkpoint
- Delegates to `remix-phase-two`

## Completion Criteria

- Three skills exist under `.agents/skills/`
- The phase two skill encodes transliteration, metatag stripping, asset autodetection, and optional cover art
- The full orchestrator delegates instead of duplicating the phase instructions
