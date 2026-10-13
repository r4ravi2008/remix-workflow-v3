#!/usr/bin/env python3
"""Add the prepared transliterated lyrics as an ITT caption lane to the
existing Last Tide conform FCPXML, without re-encoding any picture.

The resulting FCPXML is imported into Resolve as a new timeline; native
Resolve transitions are then applied to that imported timeline by the Lua
pass, keeping caption import and transition creation independently auditable.
"""

from __future__ import annotations

import argparse
import re
import xml.etree.ElementTree as ET
from fractions import Fraction
from pathlib import Path


TIME_RE = re.compile(r"(\d+):(\d+):(\d+),(\d+)")


def srt_time(value: str) -> Fraction:
    match = TIME_RE.fullmatch(value.strip())
    if not match:
        raise ValueError(f"bad SRT time: {value!r}")
    hh, mm, ss, ms = (int(part) for part in match.groups())
    return Fraction(hh * 3600 + mm * 60 + ss, 1) + Fraction(ms, 1000)


def parse_srt(path: Path) -> list[tuple[Fraction, Fraction, str]]:
    blocks = re.split(r"\n\s*\n", path.read_text(encoding="utf-8").strip())
    entries: list[tuple[Fraction, Fraction, str]] = []
    for block in blocks:
        lines = [line.rstrip() for line in block.splitlines() if line.strip()]
        if len(lines) < 3:
            continue
        start_raw, end_raw = [part.strip() for part in lines[1].split("-->", 1)]
        text = " ".join(line.strip() for line in lines[2:])
        start = srt_time(start_raw)
        end = srt_time(end_raw)
        if end <= start:
            raise ValueError(f"non-positive caption: {block!r}")
        entries.append((start, end - start, text))
    return entries


def fcpx_time(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}s"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--srt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    tree = ET.parse(args.input)
    root = tree.getroot()
    spine = root.find(".//spine")
    if spine is None:
        raise SystemExit("FCPXML has no spine")

    # Caption offsets are timeline-relative and therefore can be appended to
    # the spine after the picture/audio story. Resolve reads the lane/offset
    # attributes and creates a native subtitle track on import.
    captions = parse_srt(args.srt)
    for index, (offset, duration, text) in enumerate(captions, start=1):
        caption = ET.Element(
            "caption",
            {
                "name": f"LYRIC {index:02d}",
                "lane": "1",
                "offset": fcpx_time(offset),
                "duration": fcpx_time(duration),
                "role": "ITT Subtitles?captionFormat=ITT.en",
            },
        )
        text_node = ET.SubElement(caption, "text", {"placement": "bottom", "alignment": "center"})
        text_node.text = text
        spine.append(caption)

    root.set("version", "1.8")
    ET.indent(tree, space="  ")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    tree.write(args.output, encoding="utf-8", xml_declaration=True)
    print(f"wrote {args.output} captions={len(captions)}")


if __name__ == "__main__":
    main()
