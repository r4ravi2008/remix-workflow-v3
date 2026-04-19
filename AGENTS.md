# AGENTS.md — Indic Song Remixer

This file is the entry point for AI agents working in this repository.
It serves as a **map**, not a manual. Follow the pointers below to find detailed instructions.

## What This Project Does

An AI-orchestrated pipeline that takes a YouTube link + target genre and produces a fully
rendered music video with synced Indic-language lyrics, audio-reactive visuals, and
AI-stylized cover art. The pipeline has 10 steps (0–9), each defined in `prompts/`.

## Repository Layout

```
AGENTS.md                  ← You are here (start)
README.md                  ← Project overview and tech stack
prompts/
  README.md                ← Pipeline index — read this to understand the flow
  references/              ← Shared conventions, patterns, and tool guides
  step-0-*.md … step-9-*.md  ← One file per pipeline step
docs/
  intent.md                ← Project intent and design philosophy
  video-visual-system-plan.md
  lyrics-sync-proposal.md
tools/
  acapella-extractor/      ← Mel-Band RoFormer vocal isolation + CTC aligner
  video-generator/         ← Remotion video template system
.agents/skills/
  remotion-best-practices/ ← Remotion rules (load via skill tool)
  suno-music-creator/      ← Suno AI workflow (load via skill tool)
  video-generation/        ← AI video generation (load via skill tool)
.remix-workspace-root.example.json ← Example repo-local config for external workspace root
```

## Core Principles

1. **Workspace is state.** Each remix lives in <workspaceRoot>/<slug>/, where workspaceRoot comes from the repo-local .remix-workspace-root.json. The meta.json inside tracks all inputs, outputs, and step completion status. Always read it before acting.

2. **Native script only.** Lyrics are always in Indic script (Telugu, Hindi, Tamil).
Never romanize or transliterate. See `prompts/references/workspace-conventions.md`.

3. **Steps are sequential.** Run steps 0→9 in order. Each step's prerequisites list what
must exist before it can run. See `prompts/README.md` for the full pipeline map.

4. **Tools have their own docs.** Before using `acapella-extractor` or `video-generator`,
read their README files in `tools/`. Shared usage patterns are in `prompts/references/`.

5. **Skills are loaded on demand.** The `.agents/skills/` directory contains Remotion best
practices, Suno workflow guides, and video generation patterns. Load them via the skill
tool when working on the relevant step.

## Key Conventions

- **Slug format:** lowercase, hyphenated, derived from song title + genre (see `prompts/references/workspace-conventions.md`)
- **File naming:** `<slug>-<purpose>.<ext>` (e.g., `meesaala-pilla-lofi-acapella.mp3`)
- **meta.json:** Single source of truth per workspace — always update status after each step
- **Browser automation:** Steps 3, 5, 7 use Chrome DevTools MCP (see `prompts/references/chrome-devtools-patterns.md`)
- **Error recovery:** Common errors and fixes are in `prompts/references/error-handling-patterns.md`

## How to Run a Remix

1. Read `prompts/README.md` for the pipeline overview
2. Start at Step 0 — it collects user inputs and creates the workspace
3. Follow each step sequentially; each file has prerequisites, instructions, and verification
4. The user makes one decision at Step 5.5 (choosing between 2 Suno variations)
5. Steps 6–9 complete autonomously after user selection

## When You're Stuck

- Check `meta.json` status to see what's been completed
- Read the relevant step's error handling section
- Check `prompts/references/error-handling-patterns.md` for cross-cutting issues
- Load the appropriate skill (Remotion, Suno) for domain-specific guidance
