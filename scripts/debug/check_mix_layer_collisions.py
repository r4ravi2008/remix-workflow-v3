#!/usr/bin/env python3
"""Detect tonal-layer pileups that can mask lead vocals in an arranged mix.

The check works from aligned stems rather than a mastered stereo file.  A frame
is considered a collision when a lead vocal is active while four or more tonal
layers are independently audible, or when both bass layers are audible at once.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import librosa
import numpy as np


TONAL_NAMES = ("bass", "rhodes", "pad", "pluck", "air_pad", "reese")
MID_NAMES = ("rhodes", "pad", "pluck", "air_pad")


def frame_rms(path: Path, sample_rate: int = 4000) -> np.ndarray:
    audio, _ = librosa.load(path, sr=sample_rate, mono=True)
    rms = librosa.feature.rms(y=audio, frame_length=1000, hop_length=400, center=False)[0]
    return 20.0 * np.log10(np.maximum(rms, 1e-9))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--instrumental-dir", type=Path, required=True)
    parser.add_argument("--vocal-bus", type=Path, required=True)
    parser.add_argument("--assert-clean", action="store_true")
    parser.add_argument("--max-vocal-collision-ratio", type=float, default=0.20)
    parser.add_argument("--max-tonal-layers", type=int, default=3)
    args = parser.parse_args()

    candidates = {
        "bass": "02-original-bass.wav",
        "rhodes": "03-original-rhodes.wav",
        "pad": "04-original-pad.wav",
        "pluck": "07-serum-style-pluck.wav",
        "air_pad": "08-serum-style-air-pad.wav",
        "reese": "09-serum-style-reese.wav",
    }
    paths = {name: args.instrumental_dir / filename for name, filename in candidates.items()}
    missing = [str(path) for path in paths.values() if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing aligned stems: " + ", ".join(missing))

    levels = {name: frame_rms(path) for name, path in paths.items()}
    vocal = frame_rms(args.vocal_bus)
    frame_count = min([len(vocal), *(len(value) for value in levels.values())])
    vocal = vocal[:frame_count]
    levels = {name: value[:frame_count] for name, value in levels.items()}

    # The stems were printed near their intended mix gains.  -42 dBFS retains
    # audible sustained parts without counting noise-floor tails as layers.
    audible = {name: value > -42.0 for name, value in levels.items()}
    vocal_active = vocal > -40.0
    tonal_count = sum(audible[name].astype(np.int16) for name in TONAL_NAMES)
    mid_count = sum(audible[name].astype(np.int16) for name in MID_NAMES)
    stacked_bass = audible["bass"] & audible["reese"]
    vocal_pileup = vocal_active & ((tonal_count >= 4) | (mid_count >= 3) | stacked_bass)

    active_vocal_frames = int(vocal_active.sum())
    collision_frames = int(vocal_pileup.sum())
    collision_ratio = collision_frames / active_vocal_frames if active_vocal_frames else 0.0
    histogram = {
        str(count): int((tonal_count == count).sum())
        for count in range(int(tonal_count.max()) + 1)
    }
    layer_pairs = {
        "bass_plus_reese_seconds": round(float(stacked_bass.sum()) * 0.1, 3),
        "rhodes_plus_pluck_seconds": round(
            float((audible["rhodes"] & audible["pluck"]).sum()) * 0.1, 3
        ),
        "pad_plus_air_pad_seconds": round(
            float((audible["pad"] & audible["air_pad"]).sum()) * 0.1, 3
        ),
    }
    failures = []
    if collision_ratio > args.max_vocal_collision_ratio:
        failures.append(
            f"vocal collision ratio {collision_ratio:.3f} exceeds {args.max_vocal_collision_ratio:.3f}"
        )
    if int(tonal_count.max()) > args.max_tonal_layers:
        failures.append(
            f"maximum tonal layer count {int(tonal_count.max())} exceeds {args.max_tonal_layers}"
        )

    result = {
        "frame_hop_seconds": 0.1,
        "audibility_threshold_dbfs": -42.0,
        "vocal_threshold_dbfs": -40.0,
        "active_vocal_seconds": round(active_vocal_frames * 0.1, 3),
        "vocal_collision_seconds": round(collision_frames * 0.1, 3),
        "vocal_collision_ratio": round(collision_ratio, 4),
        "maximum_simultaneous_tonal_layers": int(tonal_count.max()),
        "tonal_layer_histogram_frames": histogram,
        "known_doubled_layer_overlap": layer_pairs,
        "clean_pass": not failures,
        "failures": failures,
    }
    print(json.dumps(result, indent=2))
    if args.assert_clean and failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
