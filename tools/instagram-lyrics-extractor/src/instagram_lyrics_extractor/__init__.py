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
    mode="both",
):
    """Internal async implementation."""
    from pathlib import Path
    from .audio_transcriber import transcribe_audio
    from .formatter import (
        format_plain_text,
        format_timestamped_json,
        write_outputs,
        write_visual_debug_output,
    )
    from .merger import merge_results
    from .models import AudioResult
    from .video_processor import extract_audio, extract_frames, get_video_duration
    from .visual_analyzer import analyze_frames

    import asyncio

    video_path = Path(video_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    duration = get_video_duration(video_path)

    # Extract frames and optionally audio.
    loop = asyncio.get_running_loop()
    frames_dir = output_dir / "_frames"
    audio_path = output_dir / "_audio.wav"

    if mode == "visual":
        frame_paths = await loop.run_in_executor(
            None, extract_frames, video_path, frames_dir, frame_rate
        )
        visual_result = await loop.run_in_executor(
            None, analyze_frames, frame_paths, frame_rate
        )
        audio_result = AudioResult(
            segments=[],
            language=language or "unknown",
            confidence=0.0,
        )
    else:
        frame_paths, _ = await asyncio.gather(
            loop.run_in_executor(None, extract_frames, video_path, frames_dir, frame_rate),
            loop.run_in_executor(None, extract_audio, video_path, audio_path),
        )
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
    if mode == "visual":
        write_visual_debug_output(visual_result, output_dir / "visual-frames.json")

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
    mode="both",
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
        _extract_async(
            video_path,
            output_dir,
            language,
            frame_rate,
            whisper_model,
            mode,
        )
    )
