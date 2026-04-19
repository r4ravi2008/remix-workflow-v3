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
    max_dimension: int = 512,
) -> list[Path]:
    """Extract frames from video at the given frame rate.

    Args:
        video_path: Path to input video file.
        output_dir: Directory to save extracted frames.
        frame_rate: Frames per second to extract (default: 1).
        max_dimension: Max width/height while preserving aspect ratio.

    Returns:
        List of paths to extracted JPEG frames, sorted by frame index.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    pattern = str(output_dir / "frame_%04d.jpg")
    scale_filter = (
        f"fps={frame_rate},"
        f"scale='if(gt(iw,ih),{max_dimension},-2)':'if(gt(iw,ih),-2,{max_dimension})'"
    )
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-vf", scale_filter,
            "-q:v", "2",
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
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", str(sample_rate),
            "-ac", "1",
            str(output_path),
        ],
        capture_output=True,
        check=True,
    )

    return output_path
