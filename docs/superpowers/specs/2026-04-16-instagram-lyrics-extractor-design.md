# Instagram Lyrics Extractor - Design Specification

> **Date:** 2026-04-16  
> **Status:** Approved  
> **Approach:** Parallel Execution (Approach B)

## Overview

A Python tool that extracts lyrics from Instagram videos using a **parallel dual-strategy approach**:
1. **Visual analysis**: Multimodal AI (LLaVA) extracts on-screen text from video frames
2. **Audio transcription**: Local Whisper model transcribes vocals from audio
3. **Smart merging**: Confidence-weighted combination produces final lyrics

Outputs match the existing Indic Song Remixer pipeline format:
- Plain text: `<slug>-lyrics.txt`
- Timestamped JSON: `lyrics-timestamps.json`

## Goals

1. Extract accurate lyrics from Instagram Reels/videos with on-screen lyrics or sung vocals
2. Support Indic languages (Telugu, Hindi, Tamil) in native script
3. Provide both plain text and timestamped outputs
4. Follow existing project tool patterns (UV, CLI + Python API)
5. Handle edge cases gracefully (no lyrics, low quality, partial results)

## Architecture

### High-Level Flow

```
Instagram Video File
         ↓
    ┌────┴────┐
    ↓         ↓
Frame      Audio
Extract    Extract
(1fps)     (16kHz)
    ↓         ↓
LLaVA      Whisper
Analysis   Transcription
    ↓         ↓
Visual     Audio
Results    Results
    └────┬────┘
         ↓
   Confidence-Based
      Merger
         ↓
   ┌─────┴─────┐
   ↓           ↓
lyrics.txt  lyrics-
            timestamps.json
```

### Component Breakdown

| Component | Responsibility | Key Technology |
|-----------|---------------|----------------|
| Video Processor | Frame sampling, audio extraction | FFmpeg |
| Visual Analyzer | Detect and extract on-screen lyrics | LLaVA (multimodal AI) |
| Audio Transcriber | Transcribe vocals to text | Whisper (local) |
| Result Merger | Combine results with confidence weighting | Custom algorithm |
| Output Formatter | Generate plain text and JSON outputs | File I/O |

## Technical Specifications

### Video Processing
- **Frame sampling**: 1 frame per second (configurable)
- **Frame format**: JPEG, 512x512 (for LLaVA efficiency)
- **Audio extraction**: WAV, 16kHz, mono
- **Duration limit**: Default 5 minutes (configurable)

### Visual Analysis (LLaVA)
- **Model**: LLaVA-1.5-7B or LLaVA-NeXT (quantized for efficiency)
- **Prompt**: "Extract all text visible in this frame. Return only the text, nothing else."
- **Batch size**: Process frames in parallel (4-8 concurrent)
- **Output**: Text + confidence score per frame

### Audio Transcription (Whisper)
- **Model**: Whisper base or small (multilingual)
- **Language**: Auto-detect or specify (te, hi, ta)
- **Output format**: Segments with timestamps
- **Segment length**: Variable based on speech patterns

### Merging Algorithm

```python
def merge_results(visual: VisualResult, audio: AudioResult) -> MergedResult:
    # Weight by confidence scores
    visual_weight = visual.confidence
    audio_weight = audio.confidence
    
    # If one method has very low confidence, trust the other
    if visual.confidence < 0.5 and audio.confidence > 0.7:
        return audio
    if audio.confidence < 0.5 and visual.confidence > 0.7:
        return visual
    
    # Otherwise, combine with confidence weighting
    # Deduplicate overlapping segments
    # Sort by timestamp
    # Interleave where both have results
```

## Output Formats

### Plain Text (`<slug>-lyrics.txt`)
```
[Verse 1]
నీ ప్రేమ కోసం నేనుంటా
ఈ బ్రతుకు నీ కోసమే

[Chorus]
ఎదురులేని ప్రేమ నీది
నా గుండెల్లో నీవే ఉంటావు
```

### Timestamped JSON (`lyrics-timestamps.json`)
```json
{
  "version": "1.0",
  "source": "instagram",
  "language": "te",
  "confidence": 0.91,
  "segments": [
    {
      "type": "verse",
      "index": 1,
      "start": 0.0,
      "end": 8.5,
      "lines": [
        {
          "text": "నీ ప్రేమ కోసం నేనుంటా",
          "start": 0.0,
          "end": 4.2,
          "words": [
            {"text": "నీ", "start": 0.0, "end": 0.5},
            {"text": "ప్రేమ", "start": 0.5, "end": 1.8},
            {"text": "కోసం", "start": 1.8, "end": 3.0},
            {"text": "నేనుంటా", "start": 3.0, "end": 4.2}
          ]
        }
      ]
    }
  ]
}
```

## File Structure

```
tools/instagram-lyrics-extractor/
├── src/instagram_lyrics_extractor/
│   ├── __init__.py              # Package exports
│   ├── cli.py                   # Command-line interface
│   ├── video_processor.py       # Frame/audio extraction
│   ├── visual_analyzer.py       # LLaVA text detection
│   ├── audio_transcriber.py     # Whisper transcription
│   ├── merger.py                # Result combination
│   ├── formatter.py             # Output formatting
│   └── models.py                # Pydantic data models
├── tests/
│   ├── test_video_processor.py
│   ├── test_visual_analyzer.py
│   ├── test_audio_transcriber.py
│   ├── test_merger.py
│   └── test_formatter.py
├── pyproject.toml               # UV project config
├── README.md                    # Usage documentation
└── uv.lock                      # Dependency lock
```

## Dependencies

### Core
- `ffmpeg-python` - Video/audio processing
- `openai-whisper` - Local transcription
- `llava` or `transformers` - Multimodal AI
- `torch` - PyTorch backend for models
- `pydantic` - Data validation
- `asyncio` - Parallel execution

### Development
- `pytest` - Testing framework
- `pytest-asyncio` - Async test support
- `pytest-cov` - Coverage reporting

## Error Handling

| Scenario | Behavior |
|----------|----------|
| No visual text detected | Use audio-only results |
| Low audio quality | Use visual-only results |
| Both methods fail | Raise `ExtractionError` with diagnostics |
| Partial results | Return available data with confidence flags |
| Invalid video format | Raise `ValueError` with supported formats |
| Model download fails | Retry with exponential backoff |

## API Design

### CLI
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
from pathlib import Path

result = extract_lyrics(
    video_path=Path("video.mp4"),
    output_dir=Path("./output"),
    language="te",  # Optional: auto-detect if not specified
    frame_rate=1,   # Frames per second to sample
    whisper_model="base"  # Model size
)

# Result object
print(result.plain_text)  # str
print(result.timestamped_json)  # dict
print(result.confidence)  # float (0-1)
```

## Performance Considerations

- **Parallel execution**: Visual and audio analysis run concurrently
- **Model caching**: LLaVA and Whisper models loaded once, reused
- **Frame sampling**: Configurable to balance speed vs accuracy
- **Batch processing**: Frames processed in parallel batches
- **Memory limits**: Stream video processing for large files

## Testing Strategy

1. **Unit tests**: Each component tested in isolation
2. **Integration tests**: Full pipeline with sample videos
3. **Language tests**: Verify Indic script output (Telugu, Hindi, Tamil)
4. **Edge cases**: Empty videos, no audio, no text, low quality
5. **Performance tests**: Timeout limits, memory usage

## Integration with Indic Song Remixer

This tool can replace or supplement Step 3 (Find Lyrics) in the pipeline:

```python
# Current: Step 3 finds lyrics via browser automation
# New option: Extract from Instagram video directly

if source_type == "instagram":
    from instagram_lyrics_extractor import extract_lyrics
    result = extract_lyrics(video_path)
    lyrics_text = result.plain_text
    timestamps = result.timestamped_json
else:
    # Existing browser-based lyrics search
    ...
```

## Success Criteria

1. ✅ Extracts lyrics from Instagram videos with >90% accuracy
2. ✅ Outputs native Indic script (no romanization)
3. ✅ Produces both plain text and timestamped JSON
4. ✅ Completes in <2 minutes for 3-minute videos
5. ✅ CLI and Python API both functional
6. ✅ All tests pass (>90% coverage)
7. ✅ Documentation complete (README + inline)

## Future Enhancements (Not in Scope)

- Real-time Instagram URL download
- Support for other video platforms (TikTok, YouTube Shorts)
- GPU acceleration for faster processing
- Automatic language detection
- Lyric translation to English
- Batch processing multiple videos
