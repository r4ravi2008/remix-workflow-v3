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
