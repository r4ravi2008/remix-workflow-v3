#!/usr/bin/env python3
"""Measure beat-period visual response in the R12 film and temple overlay."""

from __future__ import annotations

import json
import math
import pathlib
import re
import subprocess
import tempfile


WORKSPACE = pathlib.Path(
    "/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/"
    "ai-music/workspaces/nuvvantene-istam-deep-house/music-video/rebuild-r10-neon-space"
)
FILM = WORKSPACE / "renders/nuvvantene-r12-telugu-orbital-pulse-full-v6.mp4"
OVERLAY = WORKSPACE / "renders/r12-overlays/r12-telugu-mandala-540p-v4.mp4"
RECORD = WORKSPACE / "records/r12-reactivity-v6.json"

BPM = 127.01100762066172
FPS = 24.0
BEAT_PERIOD = 60.0 / BPM
BEAT_ORIGIN = 0.243871569


def yavg_series(path: pathlib.Path) -> list[float]:
    process = subprocess.run(
        [
            "ffmpeg",
            "-v",
            "info",
            "-i",
            str(path),
            "-vf",
            "signalstats,metadata=print:file=-",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    output = process.stdout + "\n" + process.stderr
    values = [
        float(value)
        for value in re.findall(r"signalstats\.YAVG=([0-9.]+)", output)
    ]
    if not values:
        raise RuntimeError(f"No signalstats YAVG values found for {path}")
    return values


def correlation(xs: list[float], ys: list[float]) -> float:
    count = min(len(xs), len(ys))
    xs = xs[:count]
    ys = ys[:count]
    xmean = sum(xs) / count
    ymean = sum(ys) / count
    numerator = sum((x - xmean) * (y - ymean) for x, y in zip(xs, ys))
    xenergy = sum((x - xmean) ** 2 for x in xs)
    yenergy = sum((y - ymean) ** 2 for y in ys)
    if xenergy == 0 or yenergy == 0:
        return 0.0
    return numerator / math.sqrt(xenergy * yenergy)


def metrics(values: list[float]) -> dict:
    pulse = []
    downbeat_pulse = []
    cosine = []
    for frame_index in range(len(values)):
        time = frame_index / FPS
        phase = 2.0 * math.pi * (time - BEAT_ORIGIN) / BEAT_PERIOD
        c = math.cos(phase)
        cosine.append(c)
        pulse.append(max(0.0, c) ** 4)
        phase_seconds = (time - BEAT_ORIGIN + BEAT_PERIOD) % BEAT_PERIOD
        downbeat_pulse.append(math.exp(-phase_seconds / 0.08))
    return {
        "frames_measured": len(values),
        "duration_seconds": len(values) / FPS,
        "yavg_mean": sum(values) / len(values),
        "yavg_min": min(values),
        "yavg_max": max(values),
        "beat_cosine_correlation": correlation(values, cosine),
        "beat_pulse_correlation": correlation(values, pulse),
        "downbeat_pulse_correlation": correlation(values, downbeat_pulse),
    }


def main() -> None:
    film_values = yavg_series(FILM)
    overlay_values = yavg_series(OVERLAY)
    record = {
        "revision": "R12-telugu-olden-style-v6",
        "canonical_audio_sha256": "9769452de248e4c05029f678fe3eac2d0ae0134161e7636356af641379e9396c",
        "beat_grid": {
            "bpm": BPM,
            "period_seconds": BEAT_PERIOD,
            "origin_seconds": BEAT_ORIGIN,
            "fps": FPS,
        },
        "measurement": {
            "film": {"path": str(FILM), **metrics(film_values)},
            "temple_overlay_v4": {"path": str(OVERLAY), **metrics(overlay_values)},
        },
        "beat_depth_overlay": {"path": str(WORKSPACE / "renders/r12-overlays/r12-beat-depth-pulse-540p-v1.mp4"), **metrics(yavg_series(WORKSPACE / "renders/r12-overlays/r12-beat-depth-pulse-540p-v1.mp4"))},
        "construction_evidence": {
            "overlay_expression": "brightness=0.02+0.30*exp(-mod(t-0.243871569+0.4724,0.4724)/0.08); contrast=1+0.85*exp(-mod(t-0.243871569+0.4724,0.4724)/0.08); antique-gold ring alpha=0.03+0.78*downbeat_pulse",
            "resolve_composite": "Screen",
            "resolve_opacity": 42.0,
            "beat_depth_resolve_track": "V10",
            "beat_depth_resolve_opacity": 34.0,
            "anchor_count": 95,
            "anchor_interval_seconds": 2.375,
        },
        "review_state": {
            "measured": True,
            "frame_inspected": True,
            "watched_normal_speed": False,
            "heard_normal_speed": False,
            "creative_accepted": False,
        },
    }
    RECORD.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
