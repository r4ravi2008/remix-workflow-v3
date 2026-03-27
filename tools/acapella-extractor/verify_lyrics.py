#!/usr/bin/env python3
"""
Terminal karaoke QA preview for lyrics-timestamps.json.

Prints all lyric lines with their timestamps so you can verify alignment
against the audio before committing to a full Remotion render.

Usage:
  uv run python verify_lyrics.py ../../workspaces/bella-bella-lofi/lyrics-timestamps.json

Output example:
  [00:00.000]  (instrumental intro)
  [00:18.020]  బార్సిలోనా బేబీ
  [00:20.900]  మార్స్ నుండి మే బీ
  ...
"""

import json
import sys
from pathlib import Path


def format_timestamp(seconds: float) -> str:
    """Format seconds as MM:SS.mmm"""
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes:02d}:{secs:06.3f}"


def format_ts_short(seconds: float) -> str:
    """Format seconds as MM:SS.mmm for terminal display."""
    return f"[{format_timestamp(seconds)}]"


def print_section_header(name: str) -> None:
    width = 60
    bar = "─" * width
    print(f"\n{bar}")
    print(f"  {name.upper()}")
    print(bar)


def verify(json_path: Path) -> None:
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    audio_duration = data.get("audio_duration", 0)
    sections = data.get("sections", [])
    lyrics = data.get("lyrics", [])

    print(
        f"Audio duration: {format_timestamp(audio_duration)}  ({audio_duration:.3f}s)"
    )
    print(f"Sections: {len(sections)}")
    print(f"Lyric lines: {len(lyrics)}")
    print()

    current_section = None

    # Show intro marker if first line doesn't start at 0
    if lyrics and lyrics[0]["start_time"] > 0.5:
        intro_end = lyrics[0]["start_time"]
        print(f"{format_ts_short(0.0)}  (instrumental intro — {intro_end:.1f}s)")

    for line in lyrics:
        # Print section header when section changes
        section = line.get("section", "")
        if section != current_section:
            print_section_header(section)
            current_section = section

        ts = format_ts_short(line["start_time"])
        end_ts = format_ts_short(line["end_time"])
        duration = line["end_time"] - line["start_time"]
        print(f"  {ts} → {end_ts}  ({duration:.2f}s)  {line['text']}")

        # Optionally show word-level timestamps if present and non-trivial
        words = line.get("words", [])
        if words and len(words) > 1:
            word_parts = []
            for w in words:
                word_parts.append(f"{w['text']}@{w['start_time']:.2f}")
            print(f"    words: {' | '.join(word_parts)}")

    # Show outro marker if last line ends before audio ends
    if lyrics:
        last_end = lyrics[-1]["end_time"]
        if audio_duration - last_end > 2.0:
            print(
                f"\n{format_ts_short(last_end)}  (instrumental outro — {audio_duration - last_end:.1f}s)"
            )
            print(f"{format_ts_short(audio_duration)}  (end)")

    print()
    print("─" * 60)
    print("Validation checklist:")
    print("  [ ] First vocal line appears within ±500ms of actual onset")
    print("  [ ] Chorus lines align within ±1s of their actual position")
    print("  [ ] No lines appear during instrumental sections")
    print(
        f"  [ ] Total drift at end < 3s  (audio ends at {format_timestamp(audio_duration)})"
    )
    print()
    print("If alignment looks correct, proceed to Remotion render.")
    print("If lines are off, re-run align_lyrics.py and check acapella quality.")


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <lyrics-timestamps.json>", file=sys.stderr)
        sys.exit(1)

    json_path = Path(sys.argv[1])
    if not json_path.exists():
        print(f"ERROR: File not found: {json_path}", file=sys.stderr)
        sys.exit(1)

    verify(json_path)


if __name__ == "__main__":
    main()
