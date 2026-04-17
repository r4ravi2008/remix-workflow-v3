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
