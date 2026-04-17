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
        raise FileNotFoundError(f"Video file not found: {video_path}")

    output_dir.mkdir(parents=True, exist_ok=True)

    print("Instagram Lyrics Extractor")
    print(f"  Video: {video_path}")
    print(f"  Output: {output_dir}")
    print()

    # Get video duration
    duration = get_video_duration(video_path)
    print(f"Video duration: {duration:.1f}s")

    # Phase 1: Extract frames and audio in parallel
    print("\nPhase 1: Extracting frames and audio...")
    frames_dir = output_dir / "_frames"

    loop = asyncio.get_running_loop()

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
