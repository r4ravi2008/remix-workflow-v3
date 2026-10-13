#!/usr/bin/env python3
"""Verify the R12 Resolve delivery and write an auditable record."""

from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re
import subprocess
import tempfile


WORKSPACE = pathlib.Path(
    "/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/"
    "ai-music/workspaces/nuvvantene-istam-deep-house/music-video/rebuild-r10-neon-space"
)
MP4 = WORKSPACE / os.environ.get(
    "R12_MP4", "renders/nuvvantene-r12-telugu-orbital-pulse-full.mp4"
)
MOV = WORKSPACE / os.environ.get(
    "R12_MOV", "renders/nuvvantene-r12-telugu-orbital-pulse-master.mov"
)
CANONICAL = WORKSPACE / "resolve/R05-canonical.wav"
ANCHORS = WORKSPACE / "analysis/r11-anchor-map.json"
RECORD = WORKSPACE / os.environ.get(
    "R12_RECORD", "records/r12-delivery-verification.json"
)


def probe(path: pathlib.Path) -> dict:
    raw = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=codec_name,codec_type,width,height,r_frame_rate,duration,nb_frames,sample_rate,channels,bits_per_sample",
            "-of",
            "json",
            str(path),
        ],
        text=True,
    )
    return json.loads(raw)


def decodes(path: pathlib.Path) -> bool:
    return subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-map", "0:v:0", "-f", "null", "-"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0


def raw_pcm(path: pathlib.Path) -> bytes:
    with tempfile.NamedTemporaryFile(suffix=".s24") as tmp:
        subprocess.run(
            ["ffmpeg", "-v", "error", "-y", "-i", str(path), "-map", "0:a:0", "-f", "s24le", tmp.name],
            check=True,
            stdout=subprocess.DEVNULL,
        )
        return pathlib.Path(tmp.name).read_bytes()


def anchor_signal_stats() -> dict:
    anchor_data = json.loads(ANCHORS.read_text())
    requested = int(anchor_data["anchor_count"])
    with tempfile.TemporaryDirectory() as td:
        out = pathlib.Path(td) / "anchor-%03d.png"
        proc = subprocess.run(
            [
                "ffmpeg",
                "-v",
                "error",
                "-i",
                str(MP4),
                "-vf",
                "select='not(mod(n,57))+eq(n,5318)',signalstats,metadata=print:file=-",
                "-vsync",
                "0",
                str(out),
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        observed = len(list(pathlib.Path(td).glob("anchor-*.png")))
    signal_text = proc.stdout + "\n" + proc.stderr
    yavg = [float(value) for value in re.findall(r"signalstats\.YAVG=([0-9.]+)", signal_text)]
    ymax = [float(value) for value in re.findall(r"signalstats\.YMAX=([0-9.]+)", signal_text)]
    signalstats = {}
    if yavg:
        signalstats["yavg_mean"] = sum(yavg) / len(yavg)
        signalstats["yavg_min"] = min(yavg)
        signalstats["yavg_max"] = max(yavg)
    if ymax:
        signalstats["ymax_mean"] = sum(ymax) / len(ymax)
        signalstats["ymax_min"] = min(ymax)
        signalstats["ymax_max"] = max(ymax)
    return {
        "requested_anchor_count": requested,
        "observed_anchor_count": observed,
        "interval_frames": anchor_data["interval_frames"],
        "interval_seconds": anchor_data["interval_seconds"],
        "audio_sha256": anchor_data["audio_sha256"],
        "signalstats_sample_count": len(yavg),
        "signalstats": signalstats,
    }


def main() -> None:
    mov_probe = probe(MOV)
    mp4_probe = probe(MP4)
    canonical_pcm = raw_pcm(CANONICAL)
    master_pcm = raw_pcm(MOV)
    record = {
        "revision": "R12-telugu-olden-style",
        "timeline": "R12 - TELUGU ORBITAL PULSE FINISH",
        "mov": {"path": str(MOV), "probe": mov_probe, "full_decode_ok": decodes(MOV)},
        "mp4": {"path": str(MP4), "probe": mp4_probe, "full_decode_ok": decodes(MP4)},
        "canonical_audio": {
            "path": str(CANONICAL),
            "pcm24_exact_in_mov": master_pcm == canonical_pcm,
            "sha256": hashlib.sha256(CANONICAL.read_bytes()).hexdigest(),
            "pcm24_sha256": hashlib.sha256(canonical_pcm).hexdigest(),
            "bytes": len(canonical_pcm),
        },
        "visual_anchor_metrics": anchor_signal_stats(),
        "review_state": {
            "measured": True,
            "frame_inspected": True,
            "watched_normal_speed": False,
            "heard_normal_speed": False,
            "creative_accepted": False,
        },
    }
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
