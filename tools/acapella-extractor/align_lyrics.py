#!/usr/bin/env python3
"""
Lyrics aligner using ctc-forced-aligner (MMS/Wav2Vec2 CTC, ONNX runtime).

Pipeline:
  remix-v1-acapella.mp3 + suno-lyrics.txt → lyrics-timestamps.json

Usage:
  uv run python align_lyrics.py \
    --audio ../../workspaces/<slug>/remix-v1-acapella.mp3 \
    --lyrics ../../workspaces/<slug>/suno-lyrics.txt \
    --output ../../workspaces/<slug>/lyrics-timestamps.json \
    --language tel
"""

import argparse
import json
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Lyrics parser
# ---------------------------------------------------------------------------


def parse_suno_lyrics(lyrics_path: Path) -> tuple[list[dict], list[str]]:
    """
    Parse a suno-lyrics.txt file.

    Returns:
        sections: list of {"name": str, "lines": [str]}
        all_lines: flat list of lyric lines (no section headers, no stage directions)
    """
    sections = []
    current_section = None
    current_lines = []

    with open(lyrics_path, encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()

            # Skip style tag at top (first line with square brackets containing commas)
            if re.match(r"^\[.*,.*\]$", line):
                continue

            # Section header: [Verse 1], [Chorus], [Bridge], etc.
            section_match = re.match(r"^\[(.+)\]$", line)
            if section_match:
                if current_section is not None:
                    sections.append({"name": current_section, "lines": current_lines})
                current_section = section_match.group(1)
                current_lines = []
                continue

            # Skip stage directions: lines wrapped in ( )
            if re.match(r"^\(.*\)$", line):
                continue

            # Skip blank lines
            if not line:
                continue

            # Actual lyric line
            if current_section is not None:
                current_lines.append(line)

    # Flush last section
    if current_section is not None and current_lines:
        sections.append({"name": current_section, "lines": current_lines})

    all_lines = [line for section in sections for line in section["lines"]]
    return sections, all_lines


# ---------------------------------------------------------------------------
# CTC forced aligner (ONNX path)
# ---------------------------------------------------------------------------


def run_ctc_alignment(
    audio_path: Path,
    all_lines: list[str],
    language: str,
) -> list[dict]:
    """
    Run ctc-forced-aligner using the ONNX runtime path.

    Returns list of {"text": str, "start": float, "end": float}
    """
    try:
        import ctc_forced_aligner as cfa
    except ImportError:
        print("ERROR: ctc-forced-aligner not installed.", file=sys.stderr)
        print("Run: uv add ctc-forced-aligner", file=sys.stderr)
        sys.exit(1)

    import numpy as np

    # --- Load and resample audio ---
    print(f"Loading audio: {audio_path}")
    audio_waveform = cfa.load_audio(str(audio_path), ret_type="np")
    # load_audio returns a 1D float32 numpy array at 16 kHz

    # --- Ensure ONNX model is downloaded ---
    import os

    model_cache_dir = Path(__file__).parent / "models"
    model_cache_dir.mkdir(parents=True, exist_ok=True)
    model_path = model_cache_dir / "ctc_forced_aligner.onnx"
    print("Ensuring ONNX alignment model is available...")
    cfa.ensure_onnx_model(str(model_path), cfa.MODEL_URL)

    # --- Create ONNX inference session ---
    import onnxruntime as ort

    session_options = ort.SessionOptions()
    session_options.log_severity_level = 3  # suppress verbose logs
    session = ort.InferenceSession(str(model_path), sess_options=session_options)

    # --- Generate CTC emissions ---
    print("Generating CTC emissions (ONNX)...")
    emissions, stride = cfa.generate_emissions(
        session,
        audio_waveform,
        window_length=30,
        context_length=2,
        batch_size=4,
    )
    print(f"  Emissions shape: {emissions.shape}, stride: {stride}ms")

    # --- Preprocess text ---
    transcript = "\n".join(all_lines)
    print(f"Preprocessing text (language={language}, romanize=True)...")
    tokens_starred, text_starred = cfa.preprocess_text(
        transcript,
        romanize=True,  # required for non-Latin scripts
        language=language,
        split_size="word",
        star_frequency="segment",
    )

    # --- Get tokenizer ---
    tokenizer = cfa.Tokenizer()

    # --- Run alignment ---
    print("Running forced alignment...")
    segments, scores, blank_token = cfa.get_alignments(
        emissions,
        tokens_starred,
        tokenizer,
    )

    spans = cfa.get_spans(tokens_starred, segments, blank_token)

    word_timestamps = cfa.postprocess_results(text_starred, spans, stride, scores)

    # Normalise to {"text", "start", "end"} dicts
    results = []
    for item in word_timestamps:
        results.append(
            {
                "text": item["text"],
                "start": float(item["start"]),
                "end": float(item["end"]),
            }
        )

    return results


# ---------------------------------------------------------------------------
# Group words → lines → sections
# ---------------------------------------------------------------------------


def group_words_to_lines(
    word_segments: list[dict],
    sections: list[dict],
    all_lines: list[str],
) -> list[dict]:
    """
    Re-associate flat word timestamps back to original lyric lines.

    Strategy: greedily consume words per line by matching word count.
    Line start = first word start; line end = last word end.
    """
    lyrics_output = []
    word_idx = 0

    # Build a flat list of (section_name, line_text) pairs
    line_section_pairs = []
    for section in sections:
        for line in section["lines"]:
            line_section_pairs.append((section["name"], line))

    for section_name, line_text in line_section_pairs:
        line_words = line_text.split()
        n_words = len(line_words)

        consumed = word_segments[word_idx : word_idx + n_words]
        word_idx += n_words

        if not consumed:
            last_time = word_segments[-1]["end"] if word_segments else 0.0
            lyrics_output.append(
                {
                    "text": line_text,
                    "start_time": last_time,
                    "end_time": last_time + 2.0,
                    "section": section_name,
                    "words": [],
                }
            )
            continue

        start_time = consumed[0]["start"]
        end_time = consumed[-1]["end"]

        words_out = [
            {
                "text": w["text"],
                "start_time": round(w["start"], 3),
                "end_time": round(w["end"], 3),
            }
            for w in consumed
        ]

        lyrics_output.append(
            {
                "text": line_text,
                "start_time": round(start_time, 3),
                "end_time": round(end_time, 3),
                "section": section_name,
                "words": words_out,
            }
        )

    return lyrics_output


def build_sections_summary(
    sections: list[dict],
    lyrics_output: list[dict],
) -> list[dict]:
    """Build section-level time boundaries from the line-level timestamps."""
    sections_out = []
    for section in sections:
        section_lines = [l for l in lyrics_output if l["section"] == section["name"]]
        if not section_lines:
            continue
        sections_out.append(
            {
                "name": section["name"],
                "start_time": section_lines[0]["start_time"],
                "end_time": section_lines[-1]["end_time"],
                "lines": [l["text"] for l in section_lines],
            }
        )
    return sections_out


# ---------------------------------------------------------------------------
# Audio duration helper
# ---------------------------------------------------------------------------


def get_audio_duration(audio_path: Path) -> float:
    """Return duration of audio file in seconds."""
    try:
        import torchaudio

        info = torchaudio.info(str(audio_path))
        return info.num_frames / info.sample_rate
    except Exception:
        import subprocess

        result = subprocess.run(
            [
                "ffprobe",
                "-i",
                str(audio_path),
                "-show_entries",
                "format=duration",
                "-v",
                "quiet",
                "-of",
                "csv=p=0",
            ],
            capture_output=True,
            text=True,
        )
        return float(result.stdout.strip())


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Align Telugu (or other) lyrics to audio using ctc-forced-aligner"
    )
    parser.add_argument("--audio", required=True, help="Path to acapella audio file")
    parser.add_argument("--lyrics", required=True, help="Path to suno-lyrics.txt")
    parser.add_argument(
        "--output", required=True, help="Path for lyrics-timestamps.json"
    )
    parser.add_argument(
        "--language",
        default="tel",
        help="ISO 639-3 language code (default: tel for Telugu)",
    )
    args = parser.parse_args()

    audio_path = Path(args.audio)
    lyrics_path = Path(args.lyrics)
    output_path = Path(args.output)

    if not audio_path.exists():
        print(f"ERROR: Audio file not found: {audio_path}", file=sys.stderr)
        sys.exit(1)
    if not lyrics_path.exists():
        print(f"ERROR: Lyrics file not found: {lyrics_path}", file=sys.stderr)
        sys.exit(1)

    # 1. Parse lyrics
    print(f"Parsing lyrics: {lyrics_path}")
    sections, all_lines = parse_suno_lyrics(lyrics_path)
    print(f"  {len(sections)} sections, {len(all_lines)} lyric lines")
    total_words = sum(len(l.split()) for l in all_lines)
    print(f"  {total_words} total words to align")

    # 2. Get audio duration
    print("Measuring audio duration...")
    audio_duration = get_audio_duration(audio_path)
    print(f"  Duration: {audio_duration:.3f}s")

    # 3. Run CTC alignment
    word_segments = run_ctc_alignment(audio_path, all_lines, args.language)
    print(f"  Aligned {len(word_segments)} word segments")

    # 4. Group back to lines
    print("Grouping words into lines...")
    lyrics_output = group_words_to_lines(word_segments, sections, all_lines)

    # 5. Build section summaries
    sections_output = build_sections_summary(sections, lyrics_output)

    # 6. Assemble output JSON
    result = {
        "audio_duration": round(audio_duration, 3),
        "sections": sections_output,
        "lyrics": lyrics_output,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\nWrote {output_path}")
    print(f"  {len(lyrics_output)} lyric lines")
    if lyrics_output:
        print(
            f"  First line: [{lyrics_output[0]['start_time']:.3f}s] {lyrics_output[0]['text']}"
        )
    if len(lyrics_output) > 1:
        print(
            f"  Last line:  [{lyrics_output[-1]['start_time']:.3f}s] {lyrics_output[-1]['text']}"
        )
    print("\nDone. Run verify_lyrics.py to QA the alignment before rendering.")


if __name__ == "__main__":
    main()
