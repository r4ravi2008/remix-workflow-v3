---
name: instagram-lyrics-extractor
description: Use when extracting lyrics from a local video file with Indic-language content, or when needing both plain text lyrics and timestamped JSON from video audio and on-screen text.
---

# Instagram Lyrics Extractor

Extract lyrics from video files using **parallel visual (LLaVA) + audio (Whisper) analysis**. Outputs native Indic script only (Telugu, Hindi, Tamil — never romanized).

Located at `tools/instagram-lyrics-extractor/`. Requires FFmpeg and ~8GB RAM.

## When to Use

- Have a local video file (MP4, MOV) with Indic-language lyrics
- Need both `<slug>-lyrics.txt` and `lyrics-timestamps.json`
- Video has on-screen lyric text AND/OR audible vocals

**Do NOT use when:** source is YouTube (use Step 3 browser search instead), or you already have lyrics text (skip to `align_lyrics.py`).

## Quick Reference

| Item | Detail |
|------|--------|
| **CLI** | `instagram-lyrics-extract <video> [flags]` |
| **Python API** | `from instagram_lyrics_extractor import extract_lyrics` |
| **Key flags** | `--output-dir`, `--language te\|hi\|ta`, `--whisper-model`, `--frame-rate` |
| **Output** | `<slug>-lyrics.txt` + `lyrics-timestamps.json` |
| **Install** | `cd tools/instagram-lyrics-extractor && uv sync` |

Run `instagram-lyrics-extract --help` for all options.

## Usage

### CLI
```bash
cd tools/instagram-lyrics-extractor
instagram-lyrics-extract /path/to/video.mp4 \
  --output-dir workspaces/<slug>/ \
  --language te
```

### Python API
```python
from instagram_lyrics_extractor import extract_lyrics

result = extract_lyrics("video.mp4", output_dir="./output", language="te")
print(result.plain_text)       # Native script lyrics
print(result.confidence)       # 0.0-1.0
print(result.source)           # "visual", "audio", or "both"
```

## Output Format

**`lyrics-timestamps.json`** matches the pipeline format from `align_lyrics.py`:

```json
{
  "audio_duration": 45.2,
  "sections": [{"name": "Verse", "start_time": 0.0, "end_time": 15.0, "lines": [...]}],
  "lyrics": [{"text": "...", "start_time": 0.0, "end_time": 2.5, "section": "Verse", "words": [...]}]
}
```

This JSON is directly consumable by Step 8 (video rendering) without conversion.

## Pipeline Integration

This tool substitutes for Step 3 (Find Lyrics) + Step 6 (Align Lyrics) when the source is a video file. The output `lyrics-timestamps.json` feeds directly into Step 8. Cross-reference: `remix-phase-one` skill.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| FFmpeg not installed | Install FFmpeg: `sudo apt install ffmpeg` |
| Expecting romanized output | Tool always outputs native script — this is by design |
| `large` model on low RAM | Use `--whisper-model base` (default) or `small` |
| Calling `extract_lyrics()` from async code | Use `from instagram_lyrics_extractor import _extract_async` with `await` |
| Wrong output JSON format | Output uses `{audio_duration, sections, lyrics}` wrapper — not a bare array |
