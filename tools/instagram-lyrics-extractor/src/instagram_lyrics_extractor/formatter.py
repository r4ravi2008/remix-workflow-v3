"""Output formatter: plain text + timestamped JSON.

Output JSON format matches the existing pipeline's lyrics-timestamps.json
produced by tools/acapella-extractor/align_lyrics.py:

{
  "audio_duration": 180.5,
  "sections": [...],
  "lyrics": [
    {
      "text": "line text",
      "start_time": 0.0,
      "end_time": 2.5,
      "section": "Verse 1",
      "words": [{"text": "word", "start_time": 0.0, "end_time": 0.5}, ...]
    }
  ]
}
"""

import json
from pathlib import Path

from .models import MergedResult


def format_plain_text(merged: MergedResult) -> str:
    """Convert merged result to plain text lyrics."""
    if not merged.lines:
        return ""
    return "\n".join(line.text for line in merged.lines) + "\n"


def format_timestamped_json(merged: MergedResult, audio_duration: float) -> dict:
    """Convert merged result to timestamped JSON matching pipeline format."""
    lyrics = []
    for line in merged.lines:
        words_out = [
            {
                "text": w.text,
                "start_time": round(w.start, 3),
                "end_time": round(w.end, 3),
            }
            for w in line.words
        ]

        lyrics.append(
            {
                "text": line.text,
                "start_time": round(line.start, 3),
                "end_time": round(line.end, 3),
                "section": line.section or "Verse",
                "words": words_out,
            }
        )

    # Build sections summary
    sections = []
    if lyrics:
        current_section = lyrics[0]["section"]
        section_start = lyrics[0]["start_time"]
        section_lines: list[dict] = []

        for lyric in lyrics:
            if lyric["section"] != current_section:
                sections.append(
                    {
                        "name": current_section,
                        "start_time": section_start,
                        "end_time": section_lines[-1]["end_time"],
                        "lines": [l["text"] for l in section_lines],
                    }
                )
                current_section = lyric["section"]
                section_start = lyric["start_time"]
                section_lines = []
            section_lines.append(lyric)

        if section_lines:
            sections.append(
                {
                    "name": current_section,
                    "start_time": section_start,
                    "end_time": section_lines[-1]["end_time"],
                    "lines": [l["text"] for l in section_lines],
                }
            )

    return {
        "audio_duration": round(audio_duration, 3),
        "sections": sections,
        "lyrics": lyrics,
    }


def write_outputs(
    merged: MergedResult,
    text_path: Path,
    json_path: Path,
    audio_duration: float,
) -> None:
    """Write both plain text and timestamped JSON output files."""
    text_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)

    text_content = format_plain_text(merged)
    text_path.write_text(text_content, encoding="utf-8")
    print(f"  Wrote plain text: {text_path}")

    json_data = format_timestamped_json(merged, audio_duration)
    json_path.write_text(
        json.dumps(json_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"  Wrote timestamps: {json_path}")
