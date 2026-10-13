# AGENTS.md — Indic Song Remixer

This file is the entry point for AI agents working in this repository.
It serves as a **map**, not a manual. Follow the pointers below to find detailed instructions.

## What This Project Does

An AI-orchestrated pipeline that takes a YouTube link + target genre and produces a fully
rendered music video with synced Indic-language lyrics, audio-reactive visuals, and
AI-stylized cover art. The local production pipeline has 12 steps (0–11), each defined in
`prompts/`, followed by an optional private YouTube draft skill.

The standalone `video-director` skill also produces other videos and Shorts. Music
is one category; Telugu news bytes start from a user-supplied item/story and use
verified sources, Telugu scripts and narration rather than the remix pipeline.

## Repository Layout

```
AGENTS.md                  ← You are here (start)
README.md                  ← Project overview and tech stack
prompts/
  README.md                ← Pipeline index — read this to understand the flow
  references/              ← Shared conventions, patterns, and tool guides
  step-0-*.md … step-11-*.md  ← One file per pipeline step
docs/
  intent.md                ← Project intent and design philosophy
  video-visual-system-plan.md
  lyrics-sync-proposal.md
tools/
  acapella-extractor/      ← Mel-Band RoFormer vocal isolation + CTC aligner
  video-generator/         ← Remotion video template system
.agents/skills/
  video-director/         ← Shared direction, production/review; Telugu news bytes
  music-video-director/   ← Music category: song timing, continuity, optional lyrics
  remotion-best-practices/ ← Remotion rules (load via skill tool)
  suno-music-creator/      ← Suno AI workflow (load via skill tool)
  video-generation/        ← AI video generation (load via skill tool)
  upload-remix-to-youtube/ ← Private YouTube draft upload and verification
.remix-workspace-root.example.json ← Example repo-local config for external workspace root
```

## Core Principles

1. **Workspace is state.** Each remix lives in <workspaceRoot>/<slug>/, where workspaceRoot comes from the repo-local .remix-workspace-root.json. The meta.json inside tracks all inputs, outputs, and step completion status. Always read it before acting.

2. **Native script only.** Lyrics are always in Indic script (Telugu, Hindi, Tamil).
Never romanize or transliterate. See `prompts/references/workspace-conventions.md`.

3. **Remix steps are sequential.** Run steps 0→11 in order for the remix pipeline.
Each step's prerequisites list what must exist before it can run. See `prompts/README.md`
for the full pipeline map.

4. **Tools have their own docs.** Before using `acapella-extractor` or `video-generator`,
read their README files in `tools/`. Shared usage patterns are in `prompts/references/`.

5. **Skills are loaded on demand.** The `.agents/skills/` directory contains Remotion best
practices, Suno workflow guides, and video generation patterns. Load them via the skill
tool when working on the relevant step.

## Key Conventions

- **Slug format:** lowercase, hyphenated, derived from song title + genre (see `prompts/references/workspace-conventions.md`)
- **File naming:** `<slug>-<purpose>.<ext>` (e.g., `meesaala-pilla-lofi-acapella.mp3`)
- **meta.json:** Single source of truth per workspace — always update status after each step
- **Browser automation:** Steps 3 and 7 use Chrome DevTools MCP; Step 5 uses Chrome only for Suno, while ACE-Step runs locally (see `prompts/references/chrome-devtools-patterns.md`)
- **Error recovery:** Common errors and fixes are in `prompts/references/error-handling-patterns.md`

## How to Run a Remix

1. Read `prompts/README.md` for the pipeline overview
2. Start at Step 0 — it collects user inputs and creates the workspace
3. Follow each step sequentially; each file has prerequisites, instructions, and verification
4. The user makes one decision at Step 5.5 (choosing between two remix candidates)
5. Steps 6–11 complete autonomously after user selection
6. When the user explicitly requests upload, `upload-remix-to-youtube` configures a private draft and stops for manual publication

## How to Run Other Videos or Shorts

Use `.agents/skills/video-director/SKILL.md` and select category and format separately.
Music uses the `music-video-director` specialization. For Telugu news bytes, the user
supplies a news item/story; follow `video-director/references/news-bytes.md` for source
verification, Telugu scripting, narration, captions, visuals and final review. Read
existing `meta.json` before resuming. New standalone projects live under the configured
workspace root with detailed state in `<slug>/video/`; they do not run the song-remix steps.

## When You're Stuck

For the standalone Rust editor, start at
`apps/release-kit-studio/native-editor/AGENTS.md`.
That entry point maps Poteto workflows, native command ownership, feature progress, and local acceptance checks.
The native specification requires a separate executable path from the historical Python renderer.

- Check `meta.json` status to see what's been completed
- Read the relevant step's error handling section
- Check `prompts/references/error-handling-patterns.md` for cross-cutting issues
- Load the appropriate skill (Remotion, Suno) for domain-specific guidance
