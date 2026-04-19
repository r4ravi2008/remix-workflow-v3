"""Tests for video processor (FFmpeg frame + audio extraction)."""

import subprocess
from pathlib import Path

import pytest
from PIL import Image
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

    def test_preserves_aspect_ratio(self, tmp_path: Path):
        video_path = tmp_path / "portrait.mp4"
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-f", "lavfi", "-i", "color=c=blue:s=180x320:d=1",
                "-c:v", "libx264", "-preset", "ultrafast",
                str(video_path),
            ],
            capture_output=True,
            check=True,
        )

        frames = extract_frames(video_path, tmp_path / "frames", frame_rate=1)
        image = Image.open(frames[0])

        assert image.width != image.height
        ratio = image.width / image.height
        assert 0.5 <= ratio <= 0.65


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
