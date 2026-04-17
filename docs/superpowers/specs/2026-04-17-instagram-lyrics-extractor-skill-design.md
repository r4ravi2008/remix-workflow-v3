# Instagram Lyrics Extractor Skill — Design Spec

**Date:** 2026-04-17
**Type:** Reference skill (tool usage guide)
**Location:** `.agents/skills/instagram-lyrics-extractor/SKILL.md`

## Purpose

Create a reference skill that teaches AI agents how to use the `instagram-lyrics-extractor` tool. The skill should enable agents to:

1. Know when this tool applies (vs. other lyrics-finding methods)
2. Invoke it correctly via CLI or Python API
3. Understand the output format and where files land
4. Integrate output into the broader remix pipeline if needed

## Skill Metadata

- **Name:** `instagram-lyrics-extractor`
- **Description:** `Use when extracting lyrics from Instagram video files using visual and audio analysis, or when needing lyrics in native Indic script from video content.`

## Target Audience

Any agent working in this repository that needs to extract lyrics from a local video file. Primary scenario: standalone extraction. Secondary: as a Step 3 alternative in the remix pipeline.

## Content Sections

### 1. Overview (~30 words)
What the tool does: parallel dual-strategy extraction (visual LLaVA + audio Whisper), outputs plain text + timestamped JSON. Core principle: native Indic script only.

### 2. When to Use (~50 words)
Triggering conditions:
- Have a local video file (MP4, MOV) with Indic-language lyrics
- Need lyrics in native script (Telugu, Hindi, Tamil)
- Need both plain text and timestamped JSON
- Video has on-screen text AND/OR audible lyrics

When NOT to use:
- YouTube source → use existing Step 3 browser-based lyrics search
- Already have lyrics text → skip to alignment

### 3. Quick Reference (table)
Compact table covering:
- CLI command and key flags
- Python API function and params
- Output files produced
- Prerequisites (FFmpeg, ~8GB RAM)

### 4. Usage (~60 words)
One CLI example, one Python API example. Point to `--help` for full flag reference rather than documenting all flags inline.

### 5. Output Format (~40 words)
Brief description of the two output files:
- `<slug>-lyrics.txt` — plain text, one line per lyric
- `lyrics-timestamps.json` — matches pipeline format (audio_duration, sections, lyrics with words)

### 6. Integration (~30 words)
How output plugs into the remix pipeline: the JSON matches the format from `align_lyrics.py`, so it can substitute directly for Step 3 output. Cross-reference `remix-phase-one`.

### 7. Common Mistakes (~50 words)
- FFmpeg not installed → cryptic subprocess error
- Expecting romanized/transliterated output → tool always outputs native script
- Using `large` Whisper model without enough VRAM → use `base` or `small`
- Calling `extract_lyrics()` from async code → use `_extract_async` instead

## Token Budget

Target: under 400 words total. This is a reference skill loaded on demand, not a getting-started skill, but should still be concise.

## Testing Approach (Reference Skill)

Per writing-skills methodology, test with:
1. **Retrieval scenario:** Can an agent find the right CLI command for a given task?
2. **Application scenario:** Can an agent correctly use the Python API?
3. **Gap testing:** Are common use cases covered?

## Success Criteria

- Agent can extract lyrics from a video file using CLI or API after reading the skill
- Agent knows when to use this tool vs. other lyrics-finding methods
- Agent avoids common mistakes (FFmpeg, romanization, model size)
