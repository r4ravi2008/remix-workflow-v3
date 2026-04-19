#!/usr/bin/env python3
"""
Acapella Extractor using Mel-Band RoFormer (SOTA)
Extracts vocals from audio files using the current leader in music source separation.
"""

import argparse
import sys
from pathlib import Path
from audio_separator.separator import Separator


def extract_vocals(
    input_path: str,
    output_dir: str,
    model_name: str = "mel_band_roformer_kim_ft_unwa.ckpt",
) -> Path:
    """
    Extract vocals from an audio file using Mel-Band RoFormer.

    Args:
        input_path: Path to input audio file
        output_dir: Directory to save output
        model_name: Model to use (Mel-Band RoFormer Kim FT Unified is SOTA)

    Returns:
        Path to extracted vocals file
    """
    input_file = Path(input_path)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"🎵 Acapella Extractor")
    print(f"   Model: Mel-Band RoFormer (SOTA)")
    print(f"   Input: {input_file}")
    print(f"   Output: {output_path}")
    print()

    # Initialize separator with Mel-Band RoFormer model
    # Use centralized model cache to avoid re-downloading for each workspace
    tool_dir = Path(__file__).parent.parent.parent
    model_cache_dir = tool_dir / "models"
    model_cache_dir.mkdir(parents=True, exist_ok=True)

    print("Loading Mel-Band RoFormer model...")
    print(f"   Model cache: {model_cache_dir}")
    separator = Separator(
        output_dir=str(output_path),
        model_file_dir=str(model_cache_dir),
        output_format="MP3",
        output_bitrate="192k",
        output_single_stem="vocals",  # Only extract vocals
        mdx_params={
            "hop_length": 1024,
            "segment_size": 256,
            "overlap": 0.25,
            "batch_size": 1,
        },
    )

    # Load the model
    separator.load_model(model_name)

    # Separate the audio
    print("Separating vocals... (this may take a few minutes)")
    output_files = separator.separate(str(input_file))

    # The output file will be named something like "input_name_(Vocals).mp3"
    # Let's rename it to "acapella.mp3"
    if output_files:
        original_output = Path(output_files[0])
        if not original_output.is_absolute():
            original_output = output_path / original_output
        acapella_file = output_path / "acapella.mp3"

        # Rename to standard name
        original_output.rename(acapella_file)

        print(f"✓ Acapella extracted successfully!")
        print(f"  Output: {acapella_file}")
        print(f"  Size: {acapella_file.stat().st_size / (1024 * 1024):.2f} MB")

        return acapella_file
    else:
        raise RuntimeError("No output files generated")


def main():
    parser = argparse.ArgumentParser(
        description="Extract acapella (vocals) from audio files using Mel-Band RoFormer (SOTA)"
    )
    parser.add_argument("input", help="Input audio file path")
    parser.add_argument(
        "--output-dir",
        "-o",
        default=".",
        help="Output directory (default: current directory)",
    )
    parser.add_argument(
        "--model",
        default="mel_band_roformer_kim_ft_unwa.ckpt",
        help="Model name (default: Mel-Band RoFormer Kim FT)",
    )

    args = parser.parse_args()

    try:
        extract_vocals(args.input, args.output_dir, args.model)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
