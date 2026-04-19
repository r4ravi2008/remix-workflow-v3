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
2. Run Steps 0-4 in order.
3. Treat Step 5 as optional:
   - run it if the user wants remix generation now
   - skip it if the user only wants preparation artifacts or will supply remix audio later
4. Stop at the checkpoint and summarize exactly what phase two can consume next.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Forcing Step 5 every time | Stop after Step 4 unless remix generation is requested |
| Using transliterated lyrics here | Keep native script canonical in phase one |
| Handing off without `design.json` or Suno files | Verify all Step 4 outputs before stopping |

## Red Flags

- "Phase one is incomplete unless Step 5 ran"
- "I can skip Step 4 outputs because phase two will recover them later"
- "I should transliterate now so alignment is easier later"

If any of these appear, stop and restore the phase-one boundary: native-script preparation first, optional remix generation second, clean checkpoint last.
