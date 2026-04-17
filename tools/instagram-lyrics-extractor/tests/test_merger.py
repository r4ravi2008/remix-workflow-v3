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
