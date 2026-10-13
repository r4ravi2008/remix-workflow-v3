"""Build a Resolve-compatible FCPXML timeline from a music-video edit map."""

from __future__ import annotations

import argparse
import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path


def frames(value: int, fps: int) -> str:
    return f"{value}/{fps}s"


def video_frame_count(path: Path) -> int:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=nb_frames",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return int(result.stdout.strip())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("edit_map", type=Path)
    parser.add_argument("audio", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    plan = json.loads(args.edit_map.read_text())
    fps = int(plan["timeline"]["frameRate"])
    total_frames = int(plan["timeline"]["totalFrames"])
    items = plan["items"]

    if fps != 24:
        raise ValueError(f"Expected a 24 fps edit map, got {fps}")
    if not args.audio.is_file():
        raise FileNotFoundError(args.audio)

    cursor = 0
    for index, item in enumerate(items, start=1):
        if item["recordStart"] != cursor:
            raise ValueError(f"Item {index} does not begin at frame {cursor}")
        if item["recordEnd"] - item["recordStart"] != item["duration"]:
            raise ValueError(f"Item {index} has an inconsistent duration")
        source = Path(item["path"])
        if not source.is_file():
            raise FileNotFoundError(source)
        available = video_frame_count(source)
        if item["sourceIn"] + item["duration"] > available:
            raise ValueError(
                f"Item {index} requests source frame {item['sourceIn'] + item['duration']} "
                f"from a {available}-frame file"
            )
        cursor = item["recordEnd"]
    if cursor != total_frames:
        raise ValueError(f"Edit ends at frame {cursor}, expected {total_frames}")

    root = ET.Element("fcpxml", version="1.8")
    resources = ET.SubElement(root, "resources")
    ET.SubElement(
        resources,
        "format",
        id="r_timeline",
        name="FFVideoFormat1080p24",
        frameDuration="1/24s",
        width="1920",
        height="1080",
        colorSpace="1-1-1 (Rec. 709)",
    )
    ET.SubElement(
        resources,
        "format",
        id="r_active",
        name="FFVideoFormat1920x804p24",
        frameDuration="1/24s",
        width="1920",
        height="804",
        colorSpace="1-1-1 (Rec. 709)",
    )

    asset_ids: dict[Path, str] = {}
    source_frames: dict[Path, int] = {}
    for item in items:
        source = Path(item["path"])
        if source in asset_ids:
            continue
        asset_id = f"v{len(asset_ids) + 1}"
        count = video_frame_count(source)
        asset_ids[source] = asset_id
        source_frames[source] = count
        ET.SubElement(
            resources,
            "asset",
            id=asset_id,
            name=source.stem,
            src=source.as_uri(),
            start="0s",
            duration=frames(count, fps),
            hasVideo="1",
            format="r_active",
        )

    ET.SubElement(
        resources,
        "asset",
        id="song",
        name=args.audio.stem,
        src=args.audio.as_uri(),
        start="0s",
        duration=frames(total_frames, fps),
        hasAudio="1",
        audioSources="1",
        audioChannels="2",
        audioRate="48000",
    )

    library = ET.SubElement(root, "library")
    event = ET.SubElement(library, "event", name=plan["project"])
    project = ET.SubElement(event, "project", name=plan["timeline"]["name"])
    sequence = ET.SubElement(
        project,
        "sequence",
        format="r_timeline",
        duration=frames(total_frames, fps),
        tcStart=frames(86400, fps),
        tcFormat="NDF",
        audioLayout="stereo",
        audioRate="48k",
    )
    spine = ET.SubElement(sequence, "spine")

    for index, item in enumerate(items, start=1):
        source = Path(item["path"])
        scene = item.get("scene") or item.get("transitionId") or f"E{index:02d}"
        role = item.get("role") or item.get("style") or item["type"]
        clip = ET.SubElement(
            spine,
            "asset-clip",
            ref=asset_ids[source],
            name=f"{scene} | {role}",
            offset=frames(item["recordStart"], fps),
            start=frames(item["sourceIn"], fps),
            duration=frames(item["duration"], fps),
        )
        if index == 1:
            song = ET.SubElement(
                clip,
                "asset-clip",
                ref="song",
                name=args.audio.stem,
                lane="-1",
                offset=frames(item["recordStart"], fps),
                start="0s",
                duration=frames(total_frames, fps),
                audioRole="music",
            )
            for marker in plan["markers"]:
                ET.SubElement(
                    song,
                    "marker",
                    start=frames(marker["frame"], fps),
                    duration="1/24s",
                    value=marker["name"],
                )

    ET.indent(root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(args.output, encoding="utf-8", xml_declaration=True)
    print(
        json.dumps(
            {
                "output": str(args.output),
                "items": len(items),
                "assets": len(asset_ids),
                "markers": len(plan["markers"]),
                "totalFrames": total_frames,
                "fps": fps,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
