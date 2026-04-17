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
