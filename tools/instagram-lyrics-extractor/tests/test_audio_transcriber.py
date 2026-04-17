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
