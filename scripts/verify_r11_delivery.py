#!/usr/bin/env python3
"""Technical verification for the R11 Resolve delivery."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

P = Path(
    "/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/"
    "nuvvantene-istam-deep-house/music-video/rebuild-r10-neon-space"
)
MOV = P / "renders/nuvvantene-r11-orbital-pulse-master.mov"
MP4 = P / "renders/nuvvantene-r11-orbital-pulse-full.mp4"
CANONICAL = P / "resolve/R05-canonical.wav"


def run(*args: str, capture=True):
    return subprocess.run(args, check=True, text=True, capture_output=capture)


def probe(path: Path) -> dict:
    return json.loads(
        run(
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=codec_name,codec_type,width,height,r_frame_rate,nb_frames,duration,sample_rate,channels,bits_per_sample",
            "-of",
            "json",
            str(path),
        ).stdout
    )


def decode_ok(path: Path) -> bool:
    result = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-map", "0:v:0", "-f", "null", "-"],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0 and not result.stderr.strip()


def pcm_exact() -> bool:
    r11 = P / "analysis/r11-verify-audio.s24"
    r05 = P / "analysis/r05-verify-audio.s24"
    run("ffmpeg", "-y", "-v", "error", "-i", str(MOV), "-map", "0:a:0", "-f", "s24le", str(r11))
    run("ffmpeg", "-y", "-v", "error", "-i", str(CANONICAL), "-map", "0:a:0", "-f", "s24le", str(r05))
    return r11.read_bytes() == r05.read_bytes()


def anchor_metrics() -> dict:
    log = P / "analysis/r11-anchor-signalstats.log"
    with log.open("w") as handle:
        subprocess.run(
            [
                "ffmpeg",
                "-v",
                "error",
                "-i",
                str(MOV),
                "-vf",
                "select='not(mod(n,57))+eq(n,5318)',signalstats,metadata=print:file=-",
                "-frames:v",
                "95",
                "-f",
                "null",
                "-",
            ],
            stdout=handle,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
    text = log.read_text()
    rows = []
    current = {}
    for line in text.splitlines():
        if "lavfi.signalstats.YAVG" in line:
            if current:
                rows.append(current)
            current = {"yavg": float(line.rsplit("=", 1)[1])}
        elif "lavfi.signalstats.YMAX" in line:
            current["ymax"] = float(line.rsplit("=", 1)[1])
        elif "lavfi.signalstats.UAVG" in line:
            current["uavg"] = float(line.rsplit("=", 1)[1])
        elif "lavfi.signalstats.VAVG" in line:
            current["vavg"] = float(line.rsplit("=", 1)[1])
    if current:
        rows.append(current)
    for row in rows:
        row.setdefault("ymax", 0.0)
        row.setdefault("uavg", 0.0)
        row.setdefault("vavg", 0.0)
    y = [r["yavg"] for r in rows]
    ymax = [r["ymax"] for r in rows]
    return {
        "requested_anchor_count": 95,
        "observed_anchor_count": len(rows),
        "yavg_min": min(y) if y else None,
        "yavg_max": max(y) if y else None,
        "yavg_mean": sum(y) / len(y) if y else None,
        "ymax_max": max(ymax) if ymax else None,
        "sample_rows": rows[:5] + rows[-5:],
    }


def main():
    mov = probe(MOV)
    mp4 = probe(MP4)
    record = {
        "revision": "R11-orbital-pulse",
        "timeline": "R11 - ORBITAL PULSE - FINAL",
        "mov": {"path": str(MOV), "probe": mov, "full_decode_ok": decode_ok(MOV)},
        "mp4": {"path": str(MP4), "probe": mp4, "full_decode_ok": decode_ok(MP4)},
        "canonical_audio": {
            "path": str(CANONICAL),
            "pcm24_exact_in_mov": pcm_exact(),
            "sha256": "9769452de248e4c05029f678fe3eac2d0ae0134161e7636356af641379e9396c",
        },
        "visual_anchor_metrics": anchor_metrics(),
        "review_state": {
            "measured": True,
            "frame_inspected": True,
            "watched_normal_speed": False,
            "heard_normal_speed": False,
            "creative_accepted": False,
        },
    }
    out = P / "records/r11-delivery-verification.json"
    out.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
