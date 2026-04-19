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
    parser.add_argument(
        "--mode",
        default="both",
        choices=["both", "visual"],
        help="Extraction mode: both visual+audio or visual only (default: both)",
    )
    return parser.parse_args(argv)


async def _run_async(args: argparse.Namespace) -> None:
    """Run the extraction pipeline asynchronously."""
    from . import _extract_async
    from .video_processor import get_video_duration

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

    print(f"\nMode: {args.mode}")

    result = await _extract_async(
        video_path,
        output_dir,
        language=args.language,
        frame_rate=args.frame_rate,
        whisper_model=args.whisper_model,
        mode=args.mode,
    )

    print(f"\nDone! Confidence: {result.confidence:.2f} (source: {result.source})")
    print(f"  Plain text: {output_dir / f'{video_path.stem}-lyrics.txt'}")
    print(f"  Timestamps: {output_dir / 'lyrics-timestamps.json'}")
    if args.mode == "visual":
        print(f"  Visual debug: {output_dir / 'visual-frames.json'}")


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
