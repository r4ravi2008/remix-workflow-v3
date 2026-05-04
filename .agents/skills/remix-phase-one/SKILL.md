---
name: remix-phase-one
description: Use when starting a new remix from a YouTube URL and genre, and the goal is to prepare the workspace, source audio, lyrics, Suno inputs, and optionally generate remix variations before a later post-production phase.
---

# Remix Phase One

## Overview

This skill owns the preparation half of the remix workflow. It runs the setup and content-prep steps, then stops at a checkpoint that leaves the workspace ready for remix generation or for handoff into phase two.

## When to Use

- User is starting from a YouTube URL and target genre
- Workspace and `meta.json` do not exist yet
- The goal is to prepare lyrics, style, and design assets before alignment/video work

Do not use this when remix audio already exists in the workspace. Use `remix-phase-two` instead.

## Quick Reference

| Range | Default | Optional | Handoff |
|---|---|---|---|
| Steps 0-4 | Required | Step 5 | Prepared workspace |

Required outputs:
- `meta.json`
- original MP3
- original acapella
- native-script lyrics
- Suno lyrics
- Suno style
- `design.json`

If Step 5 runs, also leave behind remix variants and any recorded Suno URLs.

## Implementation

1. Read project prompts and workspace conventions first.
2. Before each step, verify that step's required inputs exist and still match the user's latest instructions. If a required input is missing or ambiguous, ask one focused clarification before executing that step.
3. Run Steps 0-4 in order.
4. Confirm generation inputs before any paid or external generation call:
   - target genre and whether Step 5 remix generation should run now
   - lyric source when native lyrics were not explicitly provided
   - visual style prompt before image or video generation
   - selected generation model when the tool supports configurable models
   - if the user asks to confirm prompts, stop after drafting the prompt/design artifact and wait for approval before continuing
5. Treat Step 5 as optional:
   - run it if the user wants remix generation now
   - skip it if the user only wants preparation artifacts or will supply remix audio later
6. Stop at the checkpoint and summarize exactly what phase two can consume next.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Forcing Step 5 every time | Stop after Step 4 unless remix generation is requested |
| Using transliterated lyrics here | Keep native script canonical in phase one |
| Handing off without `design.json` or Suno files | Verify all Step 4 outputs before stopping |
| Treating URL + genre as every required input | Gate each step and clarify missing generation choices before running it |
| Sending visual prompts straight to generation | Present the prompt and wait for user confirmation first |
| Following step-doc handoff text past the phase boundary | Obey this skill's checkpoint: Step 5 runs only when remix generation was explicitly requested |

## Red Flags

- "Phase one is incomplete unless Step 5 ran"
- "I can skip Step 4 outputs because phase two will recover them later"
- "I should transliterate now so alignment is easier later"
- "The user gave URL + genre, so I can infer the remaining generation choices"
- "I can generate now and adjust the prompt later if needed"
- "The next step file says proceed, so I should keep going without explicit Step 5 approval"

If any of these appear, stop and restore the phase-one boundary: native-script preparation first, optional remix generation second, clean checkpoint last.
