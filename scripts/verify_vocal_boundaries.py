#!/usr/bin/env python3
"""Verify vocal edit boundaries, recurrence, and cross-source overlap."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import soundfile as sf


def db(value: float) -> float:
    return 20.0 * math.log10(max(1e-12, value))


def rms_frames(audio: np.ndarray, frame: int) -> np.ndarray:
    mono = np.mean(audio, axis=1) if audio.ndim == 2 else audio
    usable = len(mono) - len(mono) % frame
    if usable <= 0:
        return np.zeros(0, dtype=np.float32)
    blocks = mono[:usable].reshape(-1, frame)
    return np.sqrt(np.mean(blocks * blocks, axis=1) + 1e-12)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("vocal_dir", type=Path)
    parser.add_argument("--max-endpoint-jump", type=float, default=0.004)
    parser.add_argument("--max-dual-overlap", type=float, default=0.08)
    args = parser.parse_args()

    manifest = json.loads((args.vocal_dir / "vocal-arrangement-manifest.json").read_text())
    outputs = manifest["outputs"]
    stems = {}
    sample_rate = None
    for source in ("jhol", "pal_pal"):
        audio, sr = sf.read(args.vocal_dir / outputs[source], dtype="float32", always_2d=True)
        sample_rate = sample_rate or sr
        if sr != sample_rate:
            raise RuntimeError("vocal stems have mismatched sample rates")
        stems[source] = audio

    boundary_rows = []
    failures = []
    radius = max(2, int(0.010 * sample_rate))
    for event in manifest["events"]:
        audio = stems[event["source"]]
        for edge in ("start", "end"):
            seconds = float(event[f"destination_{edge}_seconds"])
            index = min(len(audio) - 2, max(1, int(round(seconds * sample_rate))))
            lo = max(1, index - radius)
            hi = min(len(audio) - 1, index + radius)
            local_jump = float(np.max(np.abs(np.diff(audio[lo:hi], axis=0)))) if hi - lo > 1 else 0.0
            row = {
                "phrase_id": event["phrase_id"],
                "source": event["source"],
                "edge": edge,
                "seconds": round(seconds, 6),
                "max_sample_jump": round(local_jump, 7),
                "passes": local_jump <= args.max_endpoint_jump,
            }
            if not row["passes"]:
                failures.append(f"{event['phrase_id']} {edge} jump {local_jump:.6f}")
            boundary_rows.append(row)

    frame = int(0.050 * sample_rate)
    jhol_rms = rms_frames(stems["jhol"], frame)
    pal_rms = rms_frames(stems["pal_pal"], frame)
    jhol_active = jhol_rms >= 10 ** (-45.0 / 20.0)
    pal_active = pal_rms >= 10 ** (-45.0 / 20.0)
    union = np.count_nonzero(jhol_active | pal_active)
    overlap = np.count_nonzero(jhol_active & pal_active)
    overlap_ratio = overlap / union if union else 0.0
    if overlap_ratio > args.max_dual_overlap:
        failures.append(f"dual vocal overlap ratio {overlap_ratio:.4f}")

    result = {
        "tempo_bpm": manifest["tempo_bpm"],
        "duration_seconds": manifest["duration_seconds"],
        "event_count": len(manifest["events"]),
        "boundary_policy": manifest.get("boundary_policy"),
        "maximum_endpoint_sample_jump": round(max(row["max_sample_jump"] for row in boundary_rows), 7),
        "dual_vocal_overlap_ratio": round(overlap_ratio, 6),
        "active_seconds": {
            "jhol": round(float(np.count_nonzero(jhol_active)) * 0.05, 3),
            "pal_pal": round(float(np.count_nonzero(pal_active)) * 0.05, 3),
        },
        "boundary_pass": not failures,
        "failures": failures,
        "boundaries": boundary_rows,
    }
    print(json.dumps(result, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
