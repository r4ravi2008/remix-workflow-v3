# Instagram Lyrics Extractor

Extract lyrics from Instagram videos using parallel **visual (LLaVA)** + **audio (Whisper)** analysis.

This tool is part of the [Indic Song Remixer](../../README.md) project. It provides an alternative to Step 3 (Find Lyrics) when the source is an Instagram video rather than a YouTube link.

## Features

- **Dual extraction**: Visual on-screen text detection + audio transcription, run in parallel
- **Confidence merging**: Results from both methods are combined using confidence-weighted scoring
- **Indic language support**: Telugu, Hindi, Tamil in native script (never romanized)
- **Pipeline-compatible output**: Produces `lyrics.txt` + `lyrics-timestamps.json` matching the existing format

## Prerequisites

- Python 3.12+
- [UV](https://github.com/astral-sh/uv) package manager
- FFmpeg (frame/audio extraction)
- ~8GB RAM (for LLaVA model)

## Installation

```bash
cd tools/instagram-lyrics-extractor
uv sync
```

First run will download the LLaVA (~4GB) and Whisper (~140MB for base) models.

## Usage

### Command Line

```bash
# Basic usage
instagram-lyrics-extract video.mp4 --output-dir ./output

# With options
instagram-lyrics-extract video.mp4 \
  --output-dir ./output \
  --language te \
  --frame-rate 2 \
  --whisper-model small
```

### Python API

```python
from instagram_lyrics_extractor import extract_lyrics

result = extract_lyrics(
    video_path="video.mp4",
    output_dir="./output",
    language="te",
    frame_rate=1,
    whisper_model="base",
)

print(result.plain_text)
print(result.confidence)
print(result.source)  # "visual", "audio", or "both"
```

## Output

The tool produces two files:

### `<video-name>-lyrics.txt`
Plain text lyrics, one line per lyric line.

### `lyrics-timestamps.json`
Timestamped JSON matching the pipeline format:

```json
{
  "audio_duration": 45.2,
  "sections": [
    {"name": "Verse", "start_time": 0.0, "end_time": 15.0, "lines": ["..."]}
  ],
  "lyrics": [
    {
      "text": "lyric line",
      "start_time": 0.0,
      "end_time": 2.5,
      "section": "Verse",
      "words": [
        {"text": "lyric", "start_time": 0.0, "end_time": 1.2},
        {"text": "line", "start_time": 1.2, "end_time": 2.5}
      ]
    }
  ]
}
```

## How It Works

```
Instagram Video File
         |
    +----+----+
    |         |
 Frame     Audio
 Extract   Extract
 (1fps)    (16kHz)
    |         |
 LLaVA     Whisper
 Analysis  Transcription
    |         |
    +----+----+
         |
   Confidence-Based
      Merger
         |
   +-----+-----+
   |           |
lyrics.txt  lyrics-
            timestamps.json
```

## Integration with Indic Song Remixer

This tool can supplement Step 3 (Find Lyrics) when the source is an Instagram video:

```python
if source_type == "instagram":
    from instagram_lyrics_extractor import extract_lyrics
    result = extract_lyrics(video_path)
else:
    # Existing browser-based lyrics search
    ...
```

## Testing

```bash
cd tools/instagram-lyrics-extractor
uv run pytest tests/ -v
```

## Project Structure

```
tools/instagram-lyrics-extractor/
├── src/instagram_lyrics_extractor/
│   ├── __init__.py          # Public API: extract_lyrics
│   ├── cli.py               # CLI entry point
│   ├── models.py            # Pydantic data models
│   ├── video_processor.py   # FFmpeg frame/audio extraction
│   ├── visual_analyzer.py   # LLaVA text detection
│   ├── audio_transcriber.py # Whisper transcription
│   ├── merger.py            # Confidence-weighted combination
│   └── formatter.py         # Output formatting
├── tests/
│   ├── conftest.py
│   ├── test_models.py
│   ├── test_video_processor.py
│   ├── test_audio_transcriber.py
│   ├── test_visual_analyzer.py
│   ├── test_merger.py
│   ├── test_formatter.py
│   └── test_cli.py
├── pyproject.toml
└── README.md
```

## License

MIT
