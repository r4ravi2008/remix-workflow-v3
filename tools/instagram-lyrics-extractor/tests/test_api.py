"""Tests for public extraction API behavior."""

from pathlib import Path
from unittest.mock import patch

import pytest

from instagram_lyrics_extractor import _extract_async
from instagram_lyrics_extractor.models import VisualFrame, VisualResult


@pytest.mark.asyncio
async def test_extract_async_visual_mode_skips_audio(tmp_path: Path):
    video_path = tmp_path / "video.mp4"
    video_path.write_text("video", encoding="utf-8")

    frame_path = tmp_path / "frame_0000.jpg"
    frame_path.write_text("frame", encoding="utf-8")

    visual_result = VisualResult(
        frames=[
            VisualFrame(
                frame_index=0,
                timestamp=0.0,
                text="తెలుగు పాట",
                confidence=0.9,
            )
        ],
        confidence=0.9,
    )

    with patch(
        "instagram_lyrics_extractor.video_processor.get_video_duration",
        return_value=5.0,
    ), patch(
        "instagram_lyrics_extractor.video_processor.extract_frames",
        return_value=[frame_path],
    ), patch(
        "instagram_lyrics_extractor.video_processor.extract_audio",
    ) as mock_extract_audio, patch(
        "instagram_lyrics_extractor.visual_analyzer.analyze_frames",
        return_value=visual_result,
    ), patch(
        "instagram_lyrics_extractor.audio_transcriber.transcribe_audio",
    ) as mock_transcribe_audio, patch(
        "instagram_lyrics_extractor.formatter.write_outputs",
    ) as mock_write_outputs, patch(
        "instagram_lyrics_extractor.formatter.write_visual_debug_output",
    ) as mock_write_visual_debug_output:
        result = await _extract_async(
            video_path,
            tmp_path / "out",
            language="te",
            mode="visual",
        )

    assert result.source == "visual"
    assert result.plain_text == "తెలుగు పాట\n"
    assert result.language == "te"
    mock_extract_audio.assert_not_called()
    mock_transcribe_audio.assert_not_called()
    mock_write_outputs.assert_called_once()
    mock_write_visual_debug_output.assert_called_once()
