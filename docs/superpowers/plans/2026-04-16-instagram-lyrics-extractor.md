# Instagram Lyrics Extractor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python tool that extracts lyrics from Instagram videos using parallel visual (LLaVA) and audio (Whisper) analysis, outputting both plain text and timestamped JSON matching the existing pipeline format.

**Architecture:** Two concurrent extraction paths (multimodal AI frame analysis + Whisper transcription) run in parallel via asyncio, with a confidence-weighted merger combining results into the project's standard lyrics format. Follows the existing `acapella-extractor` tool structure (UV, CLI + Python API).

**Tech Stack:** Python 3.12+, UV package manager, FFmpeg (frame/audio extraction), OpenAI Whisper (local transcription), Transformers + LLaVA (multimodal frame analysis), Pydantic (models), asyncio (parallelism), pytest (testing).

**Spec:** `docs/superpowers/specs/2026-04-16-instagram-lyrics-extractor-design.md`

---

## File Structure

```
tools/instagram-lyrics-extractor/
├── src/instagram_lyrics_extractor/
│   ├── __init__.py              # Package exports: extract_lyrics
│   ├── cli.py                   # CLI entry point: argparse wrapper
│   ├── models.py                # Pydantic data models for all result types
│   ├── video_processor.py       # FFmpeg frame sampling + audio extraction
│   ├── visual_analyzer.py       # LLaVA multimodal text detection
│   ├── audio_transcriber.py     # Whisper local transcription
│   ├── merger.py                # Confidence-weighted result combination
│   └── formatter.py             # Output: plain text + timestamped JSON
├── tests/
│   ├── conftest.py              # Shared fixtures (temp dirs, sample data)
│   ├── test_models.py           # Data model validation
│   ├── test_video_processor.py  # Frame/audio extraction tests
│   ├── test_merger.py           # Merge algorithm tests
│   ├── test_formatter.py        # Output format tests
│   ├── test_visual_analyzer.py  # LLaVA integration tests
│   ├── test_audio_transcriber.py # Whisper integration tests
│   └── test_cli.py              # CLI integration tests
├── pyproject.toml               # UV project config
└── README.md                    # Usage documentation
```

---

### Task 1: Project Scaffolding + UV Setup

**Files:**
- Create: `tools/instagram-lyrics-extractor/pyproject.toml`
- Create: `tools/instagram-lyrics-extractor/src/instagram_lyrics_extractor/__init__.py`

- [ ] **Step 1: Create `pyproject.toml`**

```toml
[project]
name = "instagram-lyrics-extractor"
version = "0.1.0"
description = "Extract lyrics from Instagram videos using parallel visual (LLaVA) + audio (Whisper) analysis"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "ffmpeg-python>=0.2.0",
    "openai-whisper>=20240930",
    "transformers>=4.45.0",
    "torch>=2.11.0",
    "accelerate>=1.0.0",
    "pillow>=10.0.0",
    "pydantic>=2.0.0",
]

[project.scripts]
instagram-lyrics-extract = "instagram_lyrics_extractor.cli:main"

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24.0",
    "pytest-cov>=5.0",
    "black>=24.0",
    "ruff>=0.3.0",
]
```

- [ ] **Step 2: Create `__init__.py`**

```python
__version__ = "0.1.0"
```

This will be updated in Task 9 to export `extract_lyrics` once it exists.

- [ ] **Step 3: Run `uv sync`**

Run from `tools/instagram-lyrics-extractor`:

```bash
cd tools/instagram-lyrics-extractor && uv sync
```

Expected: Dependencies installed, `.venv/` and `uv.lock` created.

- [ ] **Step 4: Verify Python import works**

```bash
cd tools/instagram-lyrics-extractor && uv run python -c "import instagram_lyrics_extractor; print(instagram_lyrics_extractor.__version__)"
```

Expected: `0.1.0`

- [ ] **Step 5: Commit**

```bash
git add tools/instagram-lyrics-extractor/pyproject.toml tools/instagram-lyrics-extractor/src/instagram_lyrics_extractor/__init__.py tools/instagram-lyrics-extractor/uv.lock
git commit -m "feat: scaffold instagram-lyrics-extractor project with UV"
```

---

### Task 2: Pydantic Data Models

**Files:**
- Create: `tools/instagram-lyrics-extractor/src/instagram_lyrics_extractor/models.py`
- Create: `tools/instagram-lyrics-extractor/tests/conftest.py`
- Create: `tools/instagram-lyrics-extractor/tests/test_models.py`

- [ ] **Step 1: Write the failing test**

Create `tools/instagram-lyrics-extractor/tests/test_models.py`:

```python
"""Tests for Pydantic data models."""

import pytest
from instagram_lyrics_extractor.models import (
    WordTimestamp,
    LineTimestamp,
    VisualFrame,
    VisualResult,
    AudioSegment,
    AudioResult,
    MergedResult,
    LyricsResult,
)


class TestWordTimestamp:
    def test_basic(self):
        w = WordTimestamp(text="hello", start=0.0, end=0.5)
        assert w.text == "hello"
        assert w.start == 0.0
        assert w.end == 0.5

    def test_duration(self):
        w = WordTimestamp(text="word", start=1.0, end=2.5)
        assert w.duration == 1.5

    def test_start_must_be_before_end(self):
        with pytest.raises(ValueError):
            WordTimestamp(text="bad", start=2.0, end=1.0)


class TestLineTimestamp:
    def test_basic(self):
        words = [
            WordTimestamp(text="hello", start=0.0, end=0.5),
            WordTimestamp(text="world", start=0.6, end=1.2),
        ]
        line = LineTimestamp(text="hello world", start=0.0, end=1.2, words=words)
        assert line.text == "hello world"
        assert len(line.words) == 2


class TestVisualFrame:
    def test_basic(self):
        frame = VisualFrame(
            frame_index=0, timestamp=0.0, text="some text", confidence=0.9
        )
        assert frame.frame_index == 0
        assert frame.confidence == 0.9

    def test_no_text(self):
        frame = VisualFrame(frame_index=0, timestamp=0.0, text="", confidence=0.0)
        assert frame.text == ""


class TestVisualResult:
    def test_basic(self):
        frames = [
            VisualFrame(frame_index=0, timestamp=0.0, text="line 1", confidence=0.9),
            VisualFrame(frame_index=1, timestamp=1.0, text="", confidence=0.1),
            VisualFrame(frame_index=2, timestamp=2.0, text="line 2", confidence=0.85),
        ]
        result = VisualResult(frames=frames, confidence=0.87)
        assert len(result.frames) == 3
        assert result.confidence == 0.87


class TestAudioSegment:
    def test_basic(self):
        seg = AudioSegment(text="hello", start=0.0, end=1.0, confidence=0.95)
        assert seg.text == "hello"
        assert seg.confidence == 0.95


class TestAudioResult:
    def test_basic(self):
        segments = [
            AudioSegment(text="hello", start=0.0, end=1.0, confidence=0.9),
        ]
        result = AudioResult(
            segments=segments, language="te", confidence=0.9
        )
        assert result.language == "te"


class TestMergedResult:
    def test_basic(self):
        lines = [
            LineTimestamp(
                text="hello world",
                start=0.0,
                end=1.2,
                words=[
                    WordTimestamp(text="hello", start=0.0, end=0.5),
                    WordTimestamp(text="world", start=0.6, end=1.2),
                ],
            )
        ]
        merged = MergedResult(
            lines=lines,
            confidence=0.9,
            source="both",
            language="te",
        )
        assert merged.source == "both"
        assert len(merged.lines) == 1


class TestLyricsResult:
    def test_basic(self):
        result = LyricsResult(
            plain_text="hello world",
            timestamped_json={"lyrics": []},
            confidence=0.9,
            source="audio",
            language="te",
        )
        assert result.plain_text == "hello world"
        assert result.confidence == 0.9
```

- [ ] **Step 2: Create `conftest.py`**

Create `tools/instagram-lyrics-extractor/tests/conftest.py`:

```python
"""Shared test fixtures."""

import pytest
from pathlib import Path


@pytest.fixture
def tmp_output_dir(tmp_path: Path) -> Path:
    """Temporary output directory for test files."""
    output = tmp_path / "output"
    output.mkdir()
    return output
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
cd tools/instagram-lyrics-extractor && uv run pytest tests/test_models.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'instagram_lyrics_extractor.models'`

- [ ] **Step 4: Implement the models**

Create `tools/instagram-lyrics-extractor/src/instagram_lyrics_extractor/models.py`:

```python
"""Pydantic data models for Instagram lyrics extraction."""

from pydantic import BaseModel, model_validator


class WordTimestamp(BaseModel):
    """A single word with start/end timestamps."""

    text: str
    start: float
    end: float

    @property
    def duration(self) -> float:
        return self.end - self.start

    @model_validator(mode="after")
    def validate_times(self) -> "WordTimestamp":
        if self.start > self.end:
            raise ValueError(
                f"start ({self.start}) must be <= end ({self.end})"
            )
        return self


class LineTimestamp(BaseModel):
    """A lyric line with word-level timestamps."""

    text: str
    start: float
    end: float
    words: list[WordTimestamp] = []
    section: str | None = None


class VisualFrame(BaseModel):
    """Text detected in a single video frame."""

    frame_index: int
    timestamp: float
    text: str
    confidence: float


class VisualResult(BaseModel):
    """Aggregated result from visual text detection."""

    frames: list[VisualFrame]
    confidence: float


class AudioSegment(BaseModel):
    """A transcribed audio segment from Whisper."""

    text: str
    start: float
    end: float
    confidence: float


class AudioResult(BaseModel):
    """Aggregated result from Whisper transcription."""

    segments: list[AudioSegment]
    language: str
    confidence: float


class MergedResult(BaseModel):
    """Combined result from visual + audio analysis."""

    lines: list[LineTimestamp]
    confidence: float
    source: str  # "visual", "audio", or "both"
    language: str


class LyricsResult(BaseModel):
    """Final output of the extraction pipeline."""

    plain_text: str
    timestamped_json: dict
    confidence: float
    source: str
    language: str
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
cd tools/instagram-lyrics-extractor && uv run pytest tests/test_models.py -v
```

Expected: All tests PASS.

- [ ] **Step 6: Commit**

```bash
git add tools/instagram-lyrics-extractor/src/instagram_lyrics_extractor/models.py tools/instagram-lyrics-extractor/tests/conftest.py tools/instagram-lyrics-extractor/tests/test_models.py
git commit -m "feat: add Pydantic data models for lyrics extraction"
```

---

### Task 3: Video Processor (FFmpeg Frame + Audio Extraction)

**Files:**
- Create: `tools/instagram-lyrics-extractor/src/instagram_lyrics_extractor/video_processor.py`
- Create: `tools/instagram-lyrics-extractor/tests/test_video_processor.py`

- [ ] **Step 1: Write the failing test**

Create `tools/instagram-lyrics-extractor/tests/test_video_processor.py`:

```python
"""Tests for video processor (FFmpeg frame + audio extraction)."""

import subprocess
import pytest
from pathlib import Path
from instagram_lyrics_extractor.video_processor import (
    extract_frames,
    extract_audio,
    get_video_duration,
)


def _create_test_video(path: Path, duration: float = 3.0) -> Path:
    """Create a minimal test video with FFmpeg (color bars + sine tone)."""
    video_path = path / "test_video.mp4"
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", f"color=c=blue:s=320x240:d={duration}",
            "-f", "lavfi", "-i", f"sine=frequency=440:duration={duration}",
            "-c:v", "libx264", "-preset", "ultrafast",
            "-c:a", "aac", "-b:a", "64k",
            "-shortest",
            str(video_path),
        ],
        capture_output=True,
        check=True,
    )
    return video_path


class TestGetVideoDuration:
    def test_returns_duration(self, tmp_path: Path):
        video = _create_test_video(tmp_path, duration=3.0)
        dur = get_video_duration(video)
        assert 2.5 <= dur <= 3.5  # allow small tolerance

    def test_nonexistent_file_raises(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            get_video_duration(tmp_path / "nonexistent.mp4")


class TestExtractFrames:
    def test_extracts_correct_number_of_frames(self, tmp_path: Path):
        video = _create_test_video(tmp_path, duration=3.0)
        output_dir = tmp_path / "frames"
        frames = extract_frames(video, output_dir, frame_rate=1)
        # 3-second video at 1fps => 3 or 4 frames (depending on rounding)
        assert 2 <= len(frames) <= 4
        for frame_path in frames:
            assert frame_path.exists()
            assert frame_path.suffix == ".jpg"

    def test_custom_frame_rate(self, tmp_path: Path):
        video = _create_test_video(tmp_path, duration=3.0)
        output_dir = tmp_path / "frames"
        frames = extract_frames(video, output_dir, frame_rate=2)
        # 3s at 2fps => 5-7 frames
        assert 4 <= len(frames) <= 8

    def test_creates_output_dir(self, tmp_path: Path):
        video = _create_test_video(tmp_path, duration=2.0)
        output_dir = tmp_path / "new_dir" / "frames"
        frames = extract_frames(video, output_dir, frame_rate=1)
        assert output_dir.exists()
        assert len(frames) >= 1


class TestExtractAudio:
    def test_extracts_wav(self, tmp_path: Path):
        video = _create_test_video(tmp_path, duration=2.0)
        audio_path = extract_audio(video, tmp_path / "audio.wav")
        assert audio_path.exists()
        assert audio_path.suffix == ".wav"
        assert audio_path.stat().st_size > 0

    def test_16khz_mono(self, tmp_path: Path):
        """Verify extracted audio is 16kHz mono (Whisper requirement)."""
        video = _create_test_video(tmp_path, duration=2.0)
        audio_path = extract_audio(video, tmp_path / "audio.wav")
        # Probe the output
        result = subprocess.run(
            [
                "ffprobe", "-v", "quiet",
                "-show_entries", "stream=sample_rate,channels",
                "-of", "csv=p=0",
                str(audio_path),
            ],
            capture_output=True, text=True, check=True,
        )
        # Output format: "16000,1"
        parts = result.stdout.strip().split(",")
        assert parts[0] == "16000"
        assert parts[1] == "1"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd tools/instagram-lyrics-extractor && uv run pytest tests/test_video_processor.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'instagram_lyrics_extractor.video_processor'`

- [ ] **Step 3: Implement video processor**

Create `tools/instagram-lyrics-extractor/src/instagram_lyrics_extractor/video_processor.py`:

```python
"""Video processor: FFmpeg-based frame sampling and audio extraction."""

import subprocess
import json
from pathlib import Path


def get_video_duration(video_path: Path) -> float:
    """Get duration of a video file in seconds.

    Args:
        video_path: Path to video file.

    Returns:
        Duration in seconds.

    Raises:
        FileNotFoundError: If video file does not exist.
    """
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    result = subprocess.run(
        [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            str(video_path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    info = json.loads(result.stdout)
    return float(info["format"]["duration"])


def extract_frames(
    video_path: Path,
    output_dir: Path,
    frame_rate: int = 1,
    size: str = "512x512",
) -> list[Path]:
    """Extract frames from video at the given frame rate.

    Args:
        video_path: Path to input video file.
        output_dir: Directory to save extracted frames.
        frame_rate: Frames per second to extract (default: 1).
        size: Output frame size as WxH (default: 512x512).

    Returns:
        List of paths to extracted JPEG frames, sorted by frame index.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    pattern = str(output_dir / "frame_%04d.jpg")
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-vf", f"fps={frame_rate},scale={size}",
            "-q:v", "2",  # JPEG quality (2 = high)
            pattern,
        ],
        capture_output=True,
        check=True,
    )

    frames = sorted(output_dir.glob("frame_*.jpg"))
    return frames


def extract_audio(
    video_path: Path,
    output_path: Path,
    sample_rate: int = 16000,
) -> Path:
    """Extract audio from video as WAV (16kHz mono, for Whisper).

    Args:
        video_path: Path to input video file.
        output_path: Path for output WAV file.
        sample_rate: Target sample rate (default: 16000 for Whisper).

    Returns:
        Path to extracted WAV file.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-vn",  # No video
            "-acodec", "pcm_s16le",
            "-ar", str(sample_rate),
            "-ac", "1",  # Mono
            str(output_path),
        ],
        capture_output=True,
        check=True,
    )

    return output_path
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd tools/instagram-lyrics-extractor && uv run pytest tests/test_video_processor.py -v
```

Expected: All tests PASS (requires FFmpeg installed on the machine).

- [ ] **Step 5: Commit**

```bash
git add tools/instagram-lyrics-extractor/src/instagram_lyrics_extractor/video_processor.py tools/instagram-lyrics-extractor/tests/test_video_processor.py
git commit -m "feat: add video processor for FFmpeg frame/audio extraction"
```

---

### Task 4: Audio Transcriber (Whisper)

**Files:**
- Create: `tools/instagram-lyrics-extractor/src/instagram_lyrics_extractor/audio_transcriber.py`
- Create: `tools/instagram-lyrics-extractor/tests/test_audio_transcriber.py`

- [ ] **Step 1: Write the failing test**

Create `tools/instagram-lyrics-extractor/tests/test_audio_transcriber.py`:

```python
"""Tests for Whisper audio transcriber."""

import subprocess
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from instagram_lyrics_extractor.audio_transcriber import transcribe_audio
from instagram_lyrics_extractor.models import AudioResult, AudioSegment


def _create_test_wav(path: Path, duration: float = 2.0) -> Path:
    """Create a minimal WAV file with a sine tone (no speech)."""
    wav_path = path / "test_audio.wav"
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", f"sine=frequency=440:duration={duration}",
            "-ar", "16000", "-ac", "1",
            str(wav_path),
        ],
        capture_output=True, check=True,
    )
    return wav_path


class TestTranscribeAudio:
    def test_returns_audio_result(self, tmp_path: Path):
        """Test that transcribe_audio returns an AudioResult with correct structure."""
        wav = _create_test_wav(tmp_path)

        # Mock whisper to avoid model download in tests
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {
            "text": "hello world",
            "language": "te",
            "segments": [
                {
                    "text": "hello world",
                    "start": 0.0,
                    "end": 1.5,
                    "avg_logprob": -0.3,
                    "no_speech_prob": 0.1,
                },
            ],
        }

        with patch("instagram_lyrics_extractor.audio_transcriber.whisper") as mock_whisper:
            mock_whisper.load_model.return_value = mock_model
            result = transcribe_audio(wav, model_size="base")

        assert isinstance(result, AudioResult)
        assert len(result.segments) == 1
        assert result.segments[0].text == "hello world"
        assert result.language == "te"
        assert 0.0 <= result.confidence <= 1.0

    def test_empty_audio_returns_low_confidence(self, tmp_path: Path):
        """Test that audio with no speech returns low confidence."""
        wav = _create_test_wav(tmp_path)

        mock_model = MagicMock()
        mock_model.transcribe.return_value = {
            "text": "",
            "language": "en",
            "segments": [],
        }

        with patch("instagram_lyrics_extractor.audio_transcriber.whisper") as mock_whisper:
            mock_whisper.load_model.return_value = mock_model
            result = transcribe_audio(wav, model_size="base")

        assert isinstance(result, AudioResult)
        assert len(result.segments) == 0
        assert result.confidence == 0.0

    def test_nonexistent_file_raises(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            transcribe_audio(tmp_path / "nonexistent.wav")

    def test_language_override(self, tmp_path: Path):
        """Test that explicit language is passed to Whisper."""
        wav = _create_test_wav(tmp_path)

        mock_model = MagicMock()
        mock_model.transcribe.return_value = {
            "text": "test",
            "language": "te",
            "segments": [
                {"text": "test", "start": 0.0, "end": 1.0,
                 "avg_logprob": -0.2, "no_speech_prob": 0.05},
            ],
        }

        with patch("instagram_lyrics_extractor.audio_transcriber.whisper") as mock_whisper:
            mock_whisper.load_model.return_value = mock_model
            result = transcribe_audio(wav, model_size="base", language="te")

        mock_model.transcribe.assert_called_once()
        call_kwargs = mock_model.transcribe.call_args[1]
        assert call_kwargs["language"] == "te"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd tools/instagram-lyrics-extractor && uv run pytest tests/test_audio_transcriber.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'instagram_lyrics_extractor.audio_transcriber'`

- [ ] **Step 3: Implement audio transcriber**

Create `tools/instagram-lyrics-extractor/src/instagram_lyrics_extractor/audio_transcriber.py`:

```python
"""Audio transcriber using OpenAI Whisper (local model)."""

import math
from pathlib import Path

import whisper

from .models import AudioResult, AudioSegment


def transcribe_audio(
    audio_path: Path,
    model_size: str = "base",
    language: str | None = None,
) -> AudioResult:
    """Transcribe audio to text using Whisper.

    Args:
        audio_path: Path to WAV audio file (16kHz, mono).
        model_size: Whisper model size: "tiny", "base", "small", "medium", "large".
        language: Optional ISO 639-1 language code (e.g., "te", "hi", "ta").
                  If None, Whisper auto-detects.

    Returns:
        AudioResult with transcribed segments and confidence score.

    Raises:
        FileNotFoundError: If audio file does not exist.
    """
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    print(f"Loading Whisper model ({model_size})...")
    model = whisper.load_model(model_size)

    transcribe_kwargs: dict = {
        "fp16": False,  # CPU-safe
    }
    if language is not None:
        transcribe_kwargs["language"] = language

    print(f"Transcribing audio: {audio_path}")
    result = model.transcribe(str(audio_path), **transcribe_kwargs)

    segments = []
    total_logprob = 0.0
    for seg in result.get("segments", []):
        avg_logprob = seg.get("avg_logprob", -1.0)
        no_speech_prob = seg.get("no_speech_prob", 1.0)

        # Convert log probability to confidence (0-1)
        seg_confidence = min(1.0, max(0.0, math.exp(avg_logprob)))

        # Skip segments that are likely silence/noise
        if no_speech_prob > 0.8:
            continue

        segments.append(
            AudioSegment(
                text=seg["text"].strip(),
                start=float(seg["start"]),
                end=float(seg["end"]),
                confidence=round(seg_confidence, 3),
            )
        )
        total_logprob += avg_logprob

    # Overall confidence: average of segment confidences
    if segments:
        overall_confidence = sum(s.confidence for s in segments) / len(segments)
    else:
        overall_confidence = 0.0

    detected_language = result.get("language", language or "unknown")

    print(f"  Transcribed {len(segments)} segments, confidence={overall_confidence:.2f}")

    return AudioResult(
        segments=segments,
        language=detected_language,
        confidence=round(overall_confidence, 3),
    )
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd tools/instagram-lyrics-extractor && uv run pytest tests/test_audio_transcriber.py -v
```

Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/instagram-lyrics-extractor/src/instagram_lyrics_extractor/audio_transcriber.py tools/instagram-lyrics-extractor/tests/test_audio_transcriber.py
git commit -m "feat: add Whisper audio transcriber"
```

---

### Task 5: Visual Analyzer (LLaVA Multimodal)

**Files:**
- Create: `tools/instagram-lyrics-extractor/src/instagram_lyrics_extractor/visual_analyzer.py`
- Create: `tools/instagram-lyrics-extractor/tests/test_visual_analyzer.py`

- [ ] **Step 1: Write the failing test**

Create `tools/instagram-lyrics-extractor/tests/test_visual_analyzer.py`:

```python
"""Tests for LLaVA visual analyzer."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from PIL import Image
from instagram_lyrics_extractor.visual_analyzer import analyze_frames
from instagram_lyrics_extractor.models import VisualResult, VisualFrame


def _create_test_frames(path: Path, count: int = 3) -> list[Path]:
    """Create minimal test JPEG frames."""
    frames = []
    for i in range(count):
        frame_path = path / f"frame_{i:04d}.jpg"
        img = Image.new("RGB", (512, 512), color=(0, 0, 255))
        img.save(frame_path, "JPEG")
        frames.append(frame_path)
    return frames


class TestAnalyzeFrames:
    def test_returns_visual_result(self, tmp_path: Path):
        """Test that analyze_frames returns a VisualResult."""
        frames = _create_test_frames(tmp_path, count=3)

        # Mock the LLaVA model pipeline
        mock_pipe = MagicMock()
        mock_pipe.return_value = [{"generated_text": "frame text here"}]

        with patch(
            "instagram_lyrics_extractor.visual_analyzer._load_pipeline",
            return_value=mock_pipe,
        ):
            result = analyze_frames(frames, frame_rate=1)

        assert isinstance(result, VisualResult)
        assert len(result.frames) == 3

    def test_empty_frames_list(self):
        """Test that empty frame list returns empty result."""
        result = analyze_frames([], frame_rate=1)
        assert isinstance(result, VisualResult)
        assert len(result.frames) == 0
        assert result.confidence == 0.0

    def test_frames_have_timestamps(self, tmp_path: Path):
        """Test that frames are assigned correct timestamps based on frame_rate."""
        frames = _create_test_frames(tmp_path, count=3)

        mock_pipe = MagicMock()
        mock_pipe.return_value = [{"generated_text": "text"}]

        with patch(
            "instagram_lyrics_extractor.visual_analyzer._load_pipeline",
            return_value=mock_pipe,
        ):
            result = analyze_frames(frames, frame_rate=1)

        # At 1fps: frame 0 -> 0.0s, frame 1 -> 1.0s, frame 2 -> 2.0s
        assert result.frames[0].timestamp == 0.0
        assert result.frames[1].timestamp == 1.0
        assert result.frames[2].timestamp == 2.0

    def test_no_text_detected_gives_low_confidence(self, tmp_path: Path):
        """Test that frames with no detected text give low confidence."""
        frames = _create_test_frames(tmp_path, count=2)

        mock_pipe = MagicMock()
        # Simulate LLaVA returning empty / "no text" responses
        mock_pipe.return_value = [{"generated_text": "No text visible in this image."}]

        with patch(
            "instagram_lyrics_extractor.visual_analyzer._load_pipeline",
            return_value=mock_pipe,
        ):
            with patch(
                "instagram_lyrics_extractor.visual_analyzer._is_meaningful_text",
                return_value=False,
            ):
                result = analyze_frames(frames, frame_rate=1)

        for frame in result.frames:
            assert frame.confidence < 0.5
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd tools/instagram-lyrics-extractor && uv run pytest tests/test_visual_analyzer.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'instagram_lyrics_extractor.visual_analyzer'`

- [ ] **Step 3: Implement visual analyzer**

Create `tools/instagram-lyrics-extractor/src/instagram_lyrics_extractor/visual_analyzer.py`:

```python
"""Visual text analyzer using LLaVA multimodal model."""

from pathlib import Path

from PIL import Image

from .models import VisualFrame, VisualResult

# Module-level pipeline cache
_pipeline = None

# Phrases that indicate LLaVA found no meaningful text
_NO_TEXT_PHRASES = [
    "no text",
    "no visible text",
    "i don't see any text",
    "there is no text",
    "cannot identify any text",
    "image does not contain",
]


def _load_pipeline(model_name: str = "llava-hf/llava-1.5-7b-hf"):
    """Load (and cache) the LLaVA pipeline.

    Uses transformers pipeline API for simplicity.
    The model is loaded once and reused across calls.
    """
    global _pipeline
    if _pipeline is not None:
        return _pipeline

    from transformers import pipeline

    print(f"Loading LLaVA model: {model_name}")
    _pipeline = pipeline(
        "image-to-text",
        model=model_name,
        device_map="auto",
    )
    return _pipeline


def _is_meaningful_text(text: str) -> bool:
    """Check if extracted text is meaningful (not a "no text found" response)."""
    text_lower = text.lower().strip()
    if not text_lower:
        return False
    for phrase in _NO_TEXT_PHRASES:
        if phrase in text_lower:
            return False
    return True


def _analyze_single_frame(
    pipe,
    frame_path: Path,
    frame_index: int,
    timestamp: float,
) -> VisualFrame:
    """Analyze a single frame for text content."""
    image = Image.open(frame_path).convert("RGB")

    prompt = (
        "Extract all text visible in this image. "
        "Return only the text content, nothing else. "
        "If there is no text, say 'No text visible'."
    )

    try:
        result = pipe(image, prompt=prompt, generate_kwargs={"max_new_tokens": 200})
        generated = result[0].get("generated_text", "").strip()

        if _is_meaningful_text(generated):
            confidence = 0.9  # High confidence when text is detected
        else:
            generated = ""
            confidence = 0.1  # Low confidence when no text found
    except Exception as e:
        print(f"  Warning: Frame {frame_index} analysis failed: {e}")
        generated = ""
        confidence = 0.0

    return VisualFrame(
        frame_index=frame_index,
        timestamp=timestamp,
        text=generated,
        confidence=confidence,
    )


def analyze_frames(
    frame_paths: list[Path],
    frame_rate: int = 1,
    model_name: str = "llava-hf/llava-1.5-7b-hf",
) -> VisualResult:
    """Analyze video frames for on-screen text using LLaVA.

    Args:
        frame_paths: List of paths to extracted JPEG frames.
        frame_rate: Frames per second (used to compute timestamps).
        model_name: HuggingFace model identifier for LLaVA.

    Returns:
        VisualResult with per-frame text and overall confidence.
    """
    if not frame_paths:
        return VisualResult(frames=[], confidence=0.0)

    pipe = _load_pipeline(model_name)

    frames: list[VisualFrame] = []
    for i, frame_path in enumerate(frame_paths):
        timestamp = float(i) / frame_rate
        print(f"  Analyzing frame {i + 1}/{len(frame_paths)} ({timestamp:.1f}s)...")
        frame = _analyze_single_frame(pipe, frame_path, i, timestamp)
        frames.append(frame)

    # Overall confidence: average of frames that had text, or 0 if none
    text_frames = [f for f in frames if f.text]
    if text_frames:
        overall_confidence = sum(f.confidence for f in text_frames) / len(text_frames)
    else:
        overall_confidence = 0.0

    return VisualResult(
        frames=frames,
        confidence=round(overall_confidence, 3),
    )
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd tools/instagram-lyrics-extractor && uv run pytest tests/test_visual_analyzer.py -v
```

Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/instagram-lyrics-extractor/src/instagram_lyrics_extractor/visual_analyzer.py tools/instagram-lyrics-extractor/tests/test_visual_analyzer.py
git commit -m "feat: add LLaVA visual text analyzer"
```

---

### Task 6: Result Merger (Confidence-Weighted Combination)

**Files:**
- Create: `tools/instagram-lyrics-extractor/src/instagram_lyrics_extractor/merger.py`
- Create: `tools/instagram-lyrics-extractor/tests/test_merger.py`

- [ ] **Step 1: Write the failing test**

Create `tools/instagram-lyrics-extractor/tests/test_merger.py`:

```python
"""Tests for confidence-weighted result merger."""

import pytest
from instagram_lyrics_extractor.merger import merge_results
from instagram_lyrics_extractor.models import (
    VisualResult,
    VisualFrame,
    AudioResult,
    AudioSegment,
    MergedResult,
)


def _make_visual(frames: list[tuple[float, str, float]]) -> VisualResult:
    """Helper: create VisualResult from (timestamp, text, confidence) tuples."""
    visual_frames = [
        VisualFrame(frame_index=i, timestamp=ts, text=text, confidence=conf)
        for i, (ts, text, conf) in enumerate(frames)
    ]
    if visual_frames:
        text_frames = [f for f in visual_frames if f.text]
        overall = sum(f.confidence for f in text_frames) / len(text_frames) if text_frames else 0.0
    else:
        overall = 0.0
    return VisualResult(frames=visual_frames, confidence=round(overall, 3))


def _make_audio(segments: list[tuple[str, float, float, float]], lang: str = "te") -> AudioResult:
    """Helper: create AudioResult from (text, start, end, confidence) tuples."""
    audio_segments = [
        AudioSegment(text=text, start=start, end=end, confidence=conf)
        for text, start, end, conf in segments
    ]
    if audio_segments:
        overall = sum(s.confidence for s in audio_segments) / len(audio_segments)
    else:
        overall = 0.0
    return AudioResult(segments=audio_segments, language=lang, confidence=round(overall, 3))


class TestMergeResults:
    def test_audio_only_when_visual_empty(self):
        """When visual has no text, use audio only."""
        visual = _make_visual([(0.0, "", 0.1), (1.0, "", 0.1)])
        audio = _make_audio([
            ("hello world", 0.0, 1.5, 0.9),
        ])
        result = merge_results(visual, audio)
        assert isinstance(result, MergedResult)
        assert result.source == "audio"
        assert len(result.lines) == 1
        assert result.lines[0].text == "hello world"

    def test_visual_only_when_audio_empty(self):
        """When audio has no segments, use visual only."""
        visual = _make_visual([
            (0.0, "line one", 0.9),
            (1.0, "line two", 0.85),
        ])
        audio = _make_audio([])
        result = merge_results(visual, audio)
        assert result.source == "visual"
        assert len(result.lines) == 2

    def test_both_sources_combined(self):
        """When both have good results, source is 'both'."""
        visual = _make_visual([
            (0.0, "visual line", 0.9),
        ])
        audio = _make_audio([
            ("audio line", 0.0, 2.0, 0.85),
        ])
        result = merge_results(visual, audio)
        assert result.source == "both"
        assert len(result.lines) >= 1

    def test_both_empty_returns_empty(self):
        """When both sources are empty, return empty result."""
        visual = _make_visual([])
        audio = _make_audio([])
        result = merge_results(visual, audio)
        assert len(result.lines) == 0
        assert result.confidence == 0.0

    def test_prefers_higher_confidence_source(self):
        """When one source has much higher confidence, prefer it."""
        visual = _make_visual([
            (0.0, "visual text", 0.95),
        ])
        audio = _make_audio([
            ("audio text", 0.0, 1.0, 0.3),  # Low confidence
        ])
        result = merge_results(visual, audio)
        # Visual should dominate with higher confidence
        assert result.confidence >= 0.7

    def test_language_from_audio(self):
        """Language should come from audio result."""
        visual = _make_visual([(0.0, "text", 0.9)])
        audio = _make_audio([("text", 0.0, 1.0, 0.9)], lang="hi")
        result = merge_results(visual, audio)
        assert result.language == "hi"

    def test_deduplication(self):
        """Identical text from both sources at same time should not duplicate."""
        visual = _make_visual([
            (0.0, "same text", 0.9),
        ])
        audio = _make_audio([
            ("same text", 0.0, 1.0, 0.9),
        ])
        result = merge_results(visual, audio)
        # Should not have "same text" twice
        texts = [line.text for line in result.lines]
        assert texts.count("same text") == 1
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd tools/instagram-lyrics-extractor && uv run pytest tests/test_merger.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'instagram_lyrics_extractor.merger'`

- [ ] **Step 3: Implement merger**

Create `tools/instagram-lyrics-extractor/src/instagram_lyrics_extractor/merger.py`:

```python
"""Confidence-weighted merger for visual + audio results."""

from .models import (
    AudioResult,
    LineTimestamp,
    MergedResult,
    VisualResult,
    WordTimestamp,
)


def _visual_to_lines(visual: VisualResult) -> list[LineTimestamp]:
    """Convert visual frames with text into LineTimestamp entries."""
    lines = []
    for frame in visual.frames:
        if not frame.text:
            continue
        # Each text frame becomes a line; timestamp from frame
        # Estimate end as midpoint to next frame (or +1s if last)
        lines.append(
            LineTimestamp(
                text=frame.text.strip(),
                start=frame.timestamp,
                end=frame.timestamp + 1.0,  # Rough estimate
                words=[],
            )
        )
    return lines


def _audio_to_lines(audio: AudioResult) -> list[LineTimestamp]:
    """Convert audio segments into LineTimestamp entries with word-level data."""
    lines = []
    for seg in audio.segments:
        text = seg.text.strip()
        if not text:
            continue

        # Create word-level timestamps by splitting evenly within segment
        words_raw = text.split()
        duration = seg.end - seg.start
        word_duration = duration / len(words_raw) if words_raw else 0

        words = []
        for i, word_text in enumerate(words_raw):
            w_start = seg.start + i * word_duration
            w_end = w_start + word_duration
            words.append(
                WordTimestamp(
                    text=word_text,
                    start=round(w_start, 3),
                    end=round(w_end, 3),
                )
            )

        lines.append(
            LineTimestamp(
                text=text,
                start=seg.start,
                end=seg.end,
                words=words,
            )
        )
    return lines


def _normalize_text(text: str) -> str:
    """Normalize text for comparison (lowercase, strip whitespace)."""
    return " ".join(text.lower().split())


def _deduplicate_lines(lines: list[LineTimestamp]) -> list[LineTimestamp]:
    """Remove duplicate lines that overlap in time and text."""
    if not lines:
        return []

    # Sort by start time
    sorted_lines = sorted(lines, key=lambda l: l.start)
    deduplicated = [sorted_lines[0]]

    for line in sorted_lines[1:]:
        prev = deduplicated[-1]
        prev_norm = _normalize_text(prev.text)
        curr_norm = _normalize_text(line.text)

        # If same text and overlapping time (within 2s), skip
        if prev_norm == curr_norm and abs(line.start - prev.start) < 2.0:
            # Keep the one with more word data
            if len(line.words) > len(prev.words):
                deduplicated[-1] = line
            continue

        deduplicated.append(line)

    return deduplicated


def merge_results(visual: VisualResult, audio: AudioResult) -> MergedResult:
    """Merge visual and audio results with confidence weighting.

    Strategy:
    - If one source has very low confidence (<0.3) and other is good (>0.5),
      use the good source only.
    - Otherwise, combine both sources, deduplicate, and sort by time.

    Args:
        visual: Result from LLaVA visual text analysis.
        audio: Result from Whisper audio transcription.

    Returns:
        MergedResult with combined lyrics lines.
    """
    visual_lines = _visual_to_lines(visual)
    audio_lines = _audio_to_lines(audio)

    has_visual = len(visual_lines) > 0 and visual.confidence > 0.3
    has_audio = len(audio_lines) > 0 and audio.confidence > 0.3

    # Determine source and select lines
    if has_visual and has_audio:
        source = "both"
        all_lines = visual_lines + audio_lines
        combined = _deduplicate_lines(all_lines)
        # Weighted confidence
        confidence = (
            visual.confidence * 0.4 + audio.confidence * 0.6
        )
    elif has_visual:
        source = "visual"
        combined = visual_lines
        confidence = visual.confidence
    elif has_audio:
        source = "audio"
        combined = audio_lines
        confidence = audio.confidence
    else:
        source = "audio"  # Default
        # Fall back to whatever we have, even low confidence
        if audio_lines:
            combined = audio_lines
            confidence = audio.confidence
        elif visual_lines:
            combined = visual_lines
            confidence = visual.confidence
            source = "visual"
        else:
            combined = []
            confidence = 0.0

    language = audio.language if audio.language else "unknown"

    return MergedResult(
        lines=combined,
        confidence=round(confidence, 3),
        source=source,
        language=language,
    )
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd tools/instagram-lyrics-extractor && uv run pytest tests/test_merger.py -v
```

Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/instagram-lyrics-extractor/src/instagram_lyrics_extractor/merger.py tools/instagram-lyrics-extractor/tests/test_merger.py
git commit -m "feat: add confidence-weighted result merger"
```

---

### Task 7: Output Formatter (Plain Text + Timestamped JSON)

**Files:**
- Create: `tools/instagram-lyrics-extractor/src/instagram_lyrics_extractor/formatter.py`
- Create: `tools/instagram-lyrics-extractor/tests/test_formatter.py`

- [ ] **Step 1: Write the failing test**

Create `tools/instagram-lyrics-extractor/tests/test_formatter.py`:

```python
"""Tests for output formatter (plain text + timestamped JSON)."""

import json
import pytest
from pathlib import Path
from instagram_lyrics_extractor.formatter import format_plain_text, format_timestamped_json, write_outputs
from instagram_lyrics_extractor.models import (
    MergedResult,
    LineTimestamp,
    WordTimestamp,
)


def _make_merged() -> MergedResult:
    """Create a sample MergedResult for testing."""
    return MergedResult(
        lines=[
            LineTimestamp(
                text="first line of lyrics",
                start=0.0,
                end=2.5,
                words=[
                    WordTimestamp(text="first", start=0.0, end=0.5),
                    WordTimestamp(text="line", start=0.5, end=1.0),
                    WordTimestamp(text="of", start=1.0, end=1.3),
                    WordTimestamp(text="lyrics", start=1.3, end=2.5),
                ],
            ),
            LineTimestamp(
                text="second line here",
                start=3.0,
                end=5.0,
                words=[
                    WordTimestamp(text="second", start=3.0, end=3.8),
                    WordTimestamp(text="line", start=3.8, end=4.2),
                    WordTimestamp(text="here", start=4.2, end=5.0),
                ],
            ),
        ],
        confidence=0.9,
        source="both",
        language="te",
    )


class TestFormatPlainText:
    def test_basic(self):
        merged = _make_merged()
        text = format_plain_text(merged)
        assert "first line of lyrics" in text
        assert "second line here" in text

    def test_lines_separated_by_newline(self):
        merged = _make_merged()
        text = format_plain_text(merged)
        lines = [l for l in text.strip().split("\n") if l.strip()]
        assert len(lines) == 2

    def test_empty_result(self):
        merged = MergedResult(lines=[], confidence=0.0, source="audio", language="te")
        text = format_plain_text(merged)
        assert text.strip() == ""


class TestFormatTimestampedJson:
    def test_has_required_keys(self):
        merged = _make_merged()
        data = format_timestamped_json(merged, audio_duration=10.0)
        assert "audio_duration" in data
        assert "lyrics" in data
        assert "sections" in data
        assert data["audio_duration"] == 10.0

    def test_lyrics_structure(self):
        merged = _make_merged()
        data = format_timestamped_json(merged, audio_duration=10.0)
        lyrics = data["lyrics"]
        assert len(lyrics) == 2
        first = lyrics[0]
        assert "text" in first
        assert "start_time" in first
        assert "end_time" in first
        assert "words" in first
        assert first["text"] == "first line of lyrics"

    def test_word_timestamps_present(self):
        merged = _make_merged()
        data = format_timestamped_json(merged, audio_duration=10.0)
        words = data["lyrics"][0]["words"]
        assert len(words) == 4
        assert words[0]["text"] == "first"
        assert words[0]["start_time"] == 0.0

    def test_empty_result(self):
        merged = MergedResult(lines=[], confidence=0.0, source="audio", language="te")
        data = format_timestamped_json(merged, audio_duration=5.0)
        assert data["lyrics"] == []
        assert data["audio_duration"] == 5.0


class TestWriteOutputs:
    def test_writes_both_files(self, tmp_path: Path):
        merged = _make_merged()
        text_path = tmp_path / "lyrics.txt"
        json_path = tmp_path / "lyrics-timestamps.json"
        write_outputs(merged, text_path, json_path, audio_duration=10.0)

        assert text_path.exists()
        assert json_path.exists()

        # Verify text content
        text_content = text_path.read_text(encoding="utf-8")
        assert "first line of lyrics" in text_content

        # Verify JSON content
        json_content = json.loads(json_path.read_text(encoding="utf-8"))
        assert len(json_content["lyrics"]) == 2

    def test_creates_parent_dirs(self, tmp_path: Path):
        merged = _make_merged()
        text_path = tmp_path / "sub" / "dir" / "lyrics.txt"
        json_path = tmp_path / "sub" / "dir" / "lyrics-timestamps.json"
        write_outputs(merged, text_path, json_path, audio_duration=10.0)
        assert text_path.exists()
        assert json_path.exists()

    def test_json_ensure_ascii_false(self, tmp_path: Path):
        """Ensure Indic characters are not escaped in JSON output."""
        merged = MergedResult(
            lines=[
                LineTimestamp(text="తెలుగు పాట", start=0.0, end=2.0, words=[]),
            ],
            confidence=0.9,
            source="audio",
            language="te",
        )
        json_path = tmp_path / "lyrics-timestamps.json"
        text_path = tmp_path / "lyrics.txt"
        write_outputs(merged, text_path, json_path, audio_duration=5.0)

        raw = json_path.read_text(encoding="utf-8")
        assert "తెలుగు" in raw  # Not escaped as \uXXXX
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd tools/instagram-lyrics-extractor && uv run pytest tests/test_formatter.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'instagram_lyrics_extractor.formatter'`

- [ ] **Step 3: Implement formatter**

Create `tools/instagram-lyrics-extractor/src/instagram_lyrics_extractor/formatter.py`:

```python
"""Output formatter: plain text + timestamped JSON.

Output JSON format matches the existing pipeline's lyrics-timestamps.json
produced by tools/acapella-extractor/align_lyrics.py:

{
  "audio_duration": 180.5,
  "sections": [...],
  "lyrics": [
    {
      "text": "line text",
      "start_time": 0.0,
      "end_time": 2.5,
      "section": "Verse 1",
      "words": [{"text": "word", "start_time": 0.0, "end_time": 0.5}, ...]
    }
  ]
}
"""

import json
from pathlib import Path

from .models import MergedResult


def format_plain_text(merged: MergedResult) -> str:
    """Convert merged result to plain text lyrics.

    Args:
        merged: Combined result from visual + audio analysis.

    Returns:
        Plain text string with one lyric line per line.
    """
    if not merged.lines:
        return ""

    return "\n".join(line.text for line in merged.lines) + "\n"


def format_timestamped_json(merged: MergedResult, audio_duration: float) -> dict:
    """Convert merged result to timestamped JSON matching pipeline format.

    The output format matches the lyrics-timestamps.json produced by
    tools/acapella-extractor/align_lyrics.py so the video generator
    can consume it directly.

    Args:
        merged: Combined result from visual + audio analysis.
        audio_duration: Total audio duration in seconds.

    Returns:
        Dictionary ready to be serialized as JSON.
    """
    lyrics = []
    for line in merged.lines:
        words_out = [
            {
                "text": w.text,
                "start_time": round(w.start, 3),
                "end_time": round(w.end, 3),
            }
            for w in line.words
        ]

        lyrics.append(
            {
                "text": line.text,
                "start_time": round(line.start, 3),
                "end_time": round(line.end, 3),
                "section": line.section or "Verse",
                "words": words_out,
            }
        )

    # Build sections summary (group consecutive lines with same section)
    sections = []
    if lyrics:
        current_section = lyrics[0]["section"]
        section_start = lyrics[0]["start_time"]
        section_lines = []

        for lyric in lyrics:
            if lyric["section"] != current_section:
                sections.append(
                    {
                        "name": current_section,
                        "start_time": section_start,
                        "end_time": section_lines[-1]["end_time"],
                        "lines": [l["text"] for l in section_lines],
                    }
                )
                current_section = lyric["section"]
                section_start = lyric["start_time"]
                section_lines = []
            section_lines.append(lyric)

        # Flush last section
        if section_lines:
            sections.append(
                {
                    "name": current_section,
                    "start_time": section_start,
                    "end_time": section_lines[-1]["end_time"],
                    "lines": [l["text"] for l in section_lines],
                }
            )

    return {
        "audio_duration": round(audio_duration, 3),
        "sections": sections,
        "lyrics": lyrics,
    }


def write_outputs(
    merged: MergedResult,
    text_path: Path,
    json_path: Path,
    audio_duration: float,
) -> None:
    """Write both plain text and timestamped JSON output files.

    Args:
        merged: Combined result from visual + audio analysis.
        text_path: Path for plain text lyrics file.
        json_path: Path for timestamped JSON file.
        audio_duration: Total audio duration in seconds.
    """
    text_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)

    # Write plain text
    text_content = format_plain_text(merged)
    text_path.write_text(text_content, encoding="utf-8")
    print(f"  Wrote plain text: {text_path}")

    # Write timestamped JSON
    json_data = format_timestamped_json(merged, audio_duration)
    json_path.write_text(
        json.dumps(json_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"  Wrote timestamps: {json_path}")
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd tools/instagram-lyrics-extractor && uv run pytest tests/test_formatter.py -v
```

Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/instagram-lyrics-extractor/src/instagram_lyrics_extractor/formatter.py tools/instagram-lyrics-extractor/tests/test_formatter.py
git commit -m "feat: add output formatter for plain text + timestamped JSON"
```

---

### Task 8: CLI Entry Point

**Files:**
- Create: `tools/instagram-lyrics-extractor/src/instagram_lyrics_extractor/cli.py`
- Create: `tools/instagram-lyrics-extractor/tests/test_cli.py`

- [ ] **Step 1: Write the failing test**

Create `tools/instagram-lyrics-extractor/tests/test_cli.py`:

```python
"""Tests for CLI entry point."""

import pytest
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock
from instagram_lyrics_extractor.cli import parse_args


class TestParseArgs:
    def test_required_video_arg(self):
        args = parse_args(["video.mp4"])
        assert args.video == "video.mp4"

    def test_default_output_dir(self):
        args = parse_args(["video.mp4"])
        assert args.output_dir == "."

    def test_custom_output_dir(self):
        args = parse_args(["video.mp4", "--output-dir", "/tmp/out"])
        assert args.output_dir == "/tmp/out"

    def test_language_flag(self):
        args = parse_args(["video.mp4", "--language", "te"])
        assert args.language == "te"

    def test_default_language_is_none(self):
        args = parse_args(["video.mp4"])
        assert args.language is None

    def test_frame_rate_flag(self):
        args = parse_args(["video.mp4", "--frame-rate", "2"])
        assert args.frame_rate == 2

    def test_default_frame_rate(self):
        args = parse_args(["video.mp4"])
        assert args.frame_rate == 1

    def test_whisper_model_flag(self):
        args = parse_args(["video.mp4", "--whisper-model", "small"])
        assert args.whisper_model == "small"

    def test_default_whisper_model(self):
        args = parse_args(["video.mp4"])
        assert args.whisper_model == "base"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd tools/instagram-lyrics-extractor && uv run pytest tests/test_cli.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'instagram_lyrics_extractor.cli'`

- [ ] **Step 3: Implement CLI**

Create `tools/instagram-lyrics-extractor/src/instagram_lyrics_extractor/cli.py`:

```python
"""CLI entry point for Instagram lyrics extractor."""

import argparse
import asyncio
import sys
from pathlib import Path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        argv: Argument list (defaults to sys.argv[1:]).

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Extract lyrics from Instagram videos using parallel "
            "visual (LLaVA) + audio (Whisper) analysis."
        )
    )
    parser.add_argument(
        "video",
        help="Path to Instagram video file (MP4, MOV, etc.)",
    )
    parser.add_argument(
        "--output-dir", "-o",
        default=".",
        help="Output directory for lyrics files (default: current directory)",
    )
    parser.add_argument(
        "--language", "-l",
        default=None,
        help="ISO 639-1 language code, e.g. 'te' (Telugu), 'hi' (Hindi), 'ta' (Tamil). Auto-detects if omitted.",
    )
    parser.add_argument(
        "--frame-rate",
        type=int,
        default=1,
        help="Frames per second to sample for visual analysis (default: 1)",
    )
    parser.add_argument(
        "--whisper-model",
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size (default: base)",
    )
    return parser.parse_args(argv)


async def _run_async(args: argparse.Namespace) -> None:
    """Run the extraction pipeline asynchronously."""
    from .video_processor import extract_frames, extract_audio, get_video_duration
    from .visual_analyzer import analyze_frames
    from .audio_transcriber import transcribe_audio
    from .merger import merge_results
    from .formatter import write_outputs

    video_path = Path(args.video)
    output_dir = Path(args.output_dir)

    if not video_path.exists():
        print(f"Error: Video file not found: {video_path}", file=sys.stderr)
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Instagram Lyrics Extractor")
    print(f"  Video: {video_path}")
    print(f"  Output: {output_dir}")
    print()

    # Get video duration
    duration = get_video_duration(video_path)
    print(f"Video duration: {duration:.1f}s")

    # Phase 1: Extract frames and audio in parallel
    print("\nPhase 1: Extracting frames and audio...")
    frames_dir = output_dir / "_frames"

    loop = asyncio.get_event_loop()

    frames_future = loop.run_in_executor(
        None, extract_frames, video_path, frames_dir, args.frame_rate
    )
    audio_path = output_dir / "_audio.wav"
    audio_future = loop.run_in_executor(
        None, extract_audio, video_path, audio_path
    )

    frame_paths, _ = await asyncio.gather(frames_future, audio_future)
    print(f"  Extracted {len(frame_paths)} frames + audio")

    # Phase 2: Visual + Audio analysis in parallel
    print("\nPhase 2: Running parallel analysis...")

    visual_future = loop.run_in_executor(
        None, analyze_frames, frame_paths, args.frame_rate
    )
    audio_result_future = loop.run_in_executor(
        None, transcribe_audio, audio_path, args.whisper_model, args.language
    )

    visual_result, audio_result = await asyncio.gather(
        visual_future, audio_result_future
    )

    print(f"  Visual: {visual_result.confidence:.2f} confidence, "
          f"{sum(1 for f in visual_result.frames if f.text)} frames with text")
    print(f"  Audio: {audio_result.confidence:.2f} confidence, "
          f"{len(audio_result.segments)} segments")

    # Phase 3: Merge results
    print("\nPhase 3: Merging results...")
    merged = merge_results(visual_result, audio_result)
    print(f"  Source: {merged.source}, {len(merged.lines)} lines, "
          f"confidence={merged.confidence:.2f}")

    # Phase 4: Write outputs
    print("\nPhase 4: Writing output files...")
    slug = video_path.stem
    text_path = output_dir / f"{slug}-lyrics.txt"
    json_path = output_dir / "lyrics-timestamps.json"
    write_outputs(merged, text_path, json_path, audio_duration=duration)

    print(f"\nDone! Confidence: {merged.confidence:.2f} (source: {merged.source})")
    print(f"  Plain text: {text_path}")
    print(f"  Timestamps: {json_path}")


def main(argv: list[str] | None = None) -> None:
    """Main CLI entry point."""
    args = parse_args(argv)

    try:
        asyncio.run(_run_async(args))
    except KeyboardInterrupt:
        print("\nAborted.", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd tools/instagram-lyrics-extractor && uv run pytest tests/test_cli.py -v
```

Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/instagram-lyrics-extractor/src/instagram_lyrics_extractor/cli.py tools/instagram-lyrics-extractor/tests/test_cli.py
git commit -m "feat: add CLI entry point with async parallel pipeline"
```

---

### Task 9: Package Exports + Integration Test

**Files:**
- Modify: `tools/instagram-lyrics-extractor/src/instagram_lyrics_extractor/__init__.py`

- [ ] **Step 1: Update `__init__.py` to export public API**

Update `tools/instagram-lyrics-extractor/src/instagram_lyrics_extractor/__init__.py`:

```python
"""Instagram Lyrics Extractor - Extract lyrics from Instagram videos.

Uses parallel visual (LLaVA) + audio (Whisper) analysis to extract lyrics
from Instagram videos, outputting both plain text and timestamped JSON.
"""

from .cli import main as _main
from .models import LyricsResult

__version__ = "0.1.0"
__all__ = ["extract_lyrics", "LyricsResult"]


async def _extract_async(
    video_path,
    output_dir,
    language=None,
    frame_rate=1,
    whisper_model="base",
):
    """Internal async implementation."""
    from pathlib import Path
    from .video_processor import extract_frames, extract_audio, get_video_duration
    from .visual_analyzer import analyze_frames
    from .audio_transcriber import transcribe_audio
    from .merger import merge_results
    from .formatter import format_plain_text, format_timestamped_json, write_outputs

    import asyncio

    video_path = Path(video_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    duration = get_video_duration(video_path)

    # Extract frames + audio in parallel
    loop = asyncio.get_event_loop()
    frames_dir = output_dir / "_frames"
    audio_path = output_dir / "_audio.wav"

    frame_paths, _ = await asyncio.gather(
        loop.run_in_executor(None, extract_frames, video_path, frames_dir, frame_rate),
        loop.run_in_executor(None, extract_audio, video_path, audio_path),
    )

    # Analyze in parallel
    visual_result, audio_result = await asyncio.gather(
        loop.run_in_executor(None, analyze_frames, frame_paths, frame_rate),
        loop.run_in_executor(None, transcribe_audio, audio_path, whisper_model, language),
    )

    # Merge
    merged = merge_results(visual_result, audio_result)

    # Format outputs
    slug = video_path.stem
    text_path = output_dir / f"{slug}-lyrics.txt"
    json_path = output_dir / "lyrics-timestamps.json"
    write_outputs(merged, text_path, json_path, audio_duration=duration)

    return LyricsResult(
        plain_text=format_plain_text(merged),
        timestamped_json=format_timestamped_json(merged, duration),
        confidence=merged.confidence,
        source=merged.source,
        language=merged.language,
    )


def extract_lyrics(
    video_path,
    output_dir=".",
    language=None,
    frame_rate=1,
    whisper_model="base",
) -> LyricsResult:
    """Extract lyrics from an Instagram video file.

    Runs parallel visual (LLaVA) + audio (Whisper) analysis,
    merges results, and writes output files.

    Args:
        video_path: Path to Instagram video file.
        output_dir: Directory for output files (default: current dir).
        language: ISO 639-1 language code (e.g., "te", "hi", "ta").
                  Auto-detects if None.
        frame_rate: Frames per second for visual analysis (default: 1).
        whisper_model: Whisper model size (default: "base").

    Returns:
        LyricsResult with plain text, timestamped JSON, and confidence.
    """
    import asyncio

    return asyncio.run(
        _extract_async(video_path, output_dir, language, frame_rate, whisper_model)
    )
```

- [ ] **Step 2: Verify import works**

```bash
cd tools/instagram-lyrics-extractor && uv run python -c "from instagram_lyrics_extractor import extract_lyrics, LyricsResult; print('OK')"
```

Expected: `OK`

- [ ] **Step 3: Run full test suite**

```bash
cd tools/instagram-lyrics-extractor && uv run pytest tests/ -v --tb=short
```

Expected: All tests PASS.

- [ ] **Step 4: Commit**

```bash
git add tools/instagram-lyrics-extractor/src/instagram_lyrics_extractor/__init__.py
git commit -m "feat: export public API (extract_lyrics) from package"
```

---

### Task 10: README Documentation

**Files:**
- Create: `tools/instagram-lyrics-extractor/README.md`

- [ ] **Step 1: Write README**

Create `tools/instagram-lyrics-extractor/README.md`:

````markdown
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
````

- [ ] **Step 2: Commit**

```bash
git add tools/instagram-lyrics-extractor/README.md
git commit -m "docs: add README for instagram-lyrics-extractor"
```

---

### Task 11: Final Integration — Run Full Test Suite

- [ ] **Step 1: Run the complete test suite**

```bash
cd tools/instagram-lyrics-extractor && uv run pytest tests/ -v --tb=short
```

Expected: All tests PASS.

- [ ] **Step 2: Verify CLI help works**

```bash
cd tools/instagram-lyrics-extractor && uv run instagram-lyrics-extract --help
```

Expected: Help text with all options displayed.

- [ ] **Step 3: Verify Python import works end-to-end**

```bash
cd tools/instagram-lyrics-extractor && uv run python -c "
from instagram_lyrics_extractor import extract_lyrics, LyricsResult
from instagram_lyrics_extractor.models import WordTimestamp, LineTimestamp, VisualResult, AudioResult, MergedResult
from instagram_lyrics_extractor.video_processor import extract_frames, extract_audio, get_video_duration
from instagram_lyrics_extractor.visual_analyzer import analyze_frames
from instagram_lyrics_extractor.audio_transcriber import transcribe_audio
from instagram_lyrics_extractor.merger import merge_results
from instagram_lyrics_extractor.formatter import format_plain_text, format_timestamped_json, write_outputs
print('All imports OK')
"
```

Expected: `All imports OK`

- [ ] **Step 4: Final commit (if any remaining changes)**

```bash
git status
# If any unstaged changes:
git add -A tools/instagram-lyrics-extractor/
git commit -m "chore: finalize instagram-lyrics-extractor tool"
```
