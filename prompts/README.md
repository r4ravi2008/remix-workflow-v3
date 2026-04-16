# Prompts Index — Indic Song Remixer Pipeline

This directory contains the execution guides for each step of the Indic Song Remixer pipeline.
Each step file is self-contained and can be executed by an AI agent.

## Pipeline Overview

The pipeline transforms a YouTube link + target genre into a fully rendered music video:

```
YouTube URL + Genre → [Pipeline Steps 0-9] → Music Video with Synced Lyrics + Cover Art
```

## Steps

| Step | File | Purpose | Key Outputs | Prerequisites |
|------|------|---------|-------------|---------------|
| 0 | `step-0-prepare-workspace.md` | Collect inputs, create workspace, write meta.json | `workspaces/<slug>/`, `meta.json` | None |
| 1 | `step-1-download-mp3.md` | Download YouTube audio as MP3 | `<slug>-original.mp3` | Step 0 |
| 2 | `step-2-extract-acapella.md` | Extract vocals using Mel-Band RoFormer | `<slug>-acapella.mp3` | Step 1 |
| 3 | `step-3-find-lyrics.md` | Find native-script lyrics via browser automation | `<slug>-lyrics.txt` | Step 0 |
| 4 | `step-4-generate-suno-lyrics.md` | Convert to Suno meta-tag format | `<slug>-suno-lyrics.txt`, `<slug>-suno-style.txt`, `design.json` | Steps 0, 3 |
| 5 | `step-5-upload-to-suno.md` | Upload to Suno.ai, generate 2 variations | `<slug>-remix-v1.mp3`, `<slug>-remix-v2.mp3` | Steps 2, 4 |
| 5.5 | *User Decision* | User selects v1 or v2 | Selected remix file | Step 5 |
| 6 | `step-6-extract-acapella-and-align.md` | Extract remix acapella + CTC forced alignment | `lyrics-timestamps.json` | Steps 5, 5.5 |
| 7 | `step-7-fetch-cover-art.md` | Fetch original cover art + AI stylization | `<slug>-cover-art.jpg` | Step 0 |
| 8 | `step-8-generate-video.md` | Generate music video with Remotion | `<slug>-video.mp4` | Steps 6, 7 |
| 9 | `step-9-generate-youtube-metadata.md` | Generate title, description, tags, thumbnail text | `youtube-metadata.json` | Step 8 |
| 10 | `step-10-select-short-clip.md` | Analyze audio + lyrics, select best clip segment | `shorts-segments.json` | Step 9 |
| 11 | `step-11-generate-short-video.md` | Render 9:16 vertical short in existing Remotion project | `<slug>-short.mp4` | Step 10 |

## Shared References

Common patterns and conventions are extracted into the `references/` directory:

| Reference | Used By | Purpose |
|-----------|---------|---------|
| `workspace-conventions.md` | All steps | Slug format, meta.json schema, file naming |
| `chrome-devtools-patterns.md` | Steps 3, 5, 7 | Browser automation patterns |
| `acapella-extractor-usage.md` | Steps 2, 6 | Tool setup and execution |
| `suno-format-guide.md` | Steps 4, 5 | Meta-tag format and style conventions |
| `error-handling-patterns.md` | All steps | Common errors and recovery procedures |

## Quick Start

1. **Start at Step 0**: Run `step-0-prepare-workspace.md` to collect user inputs
2. **Follow sequentially**: Each step updates `meta.json` with status
3. **Check meta.json**: Always read the workspace's `meta.json` before acting
4. **Handle Step 5.5**: Pause for user selection between v1 and v2
5. **Complete Steps 6-11**: Autonomous after user selection

## Key Conventions

- **Sequential execution**: Steps must run 0→1→2→3→4→5→6→7→8→9→10→11
- **Workspace state**: `workspaces/<slug>/meta.json` is the single source of truth
- **Native script only**: Never romanize or transliterate Indic lyrics
- **Browser automation**: Steps 3, 5, 7 use Chrome DevTools MCP
- **User checkpoint**: Only Step 5.5 requires human input
