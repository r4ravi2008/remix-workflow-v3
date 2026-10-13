#!/usr/bin/env python3
"""Diagnose whether arranged vocal stems and an FL render play forward or reversed.

The test is non-destructive.  It derives low-rate multiband energy fingerprints
with ffmpeg, then compares each arranged vocal event with the exact source
excerpt in four placements/directions:

* declared position, forward audio
* declared position, reversed audio
* time-mirrored position, forward audio
* time-mirrored position, reversed audio

A complete reversal of a full-length stem produces the last signature.  The FL
render is also compared with the original instrumental reference in both time
directions.  Only temporary in-memory ffmpeg output is used.
"""

from __future__ import annotations

import argparse
import array
import json
import math
import statistics
import subprocess
import sys
from pathlib import Path


BANDS = {
    "low": (45, 220),
    "mid": (220, 2200),
    "high": (2200, 10500),
}
ENVELOPE_RATE = 100


def ffmpeg_fingerprint(
    path: Path,
    start: float,
    duration: float,
    *,
    tempo: float = 1.0,
    pitch: float = 1.0,
    source_processing: bool = False,
) -> list[float]:
    """Return a flattened, normalized multiband energy fingerprint."""
    if duration <= 0:
        return []
    all_bands: list[list[float]] = []
    for lo, hi in BANDS.values():
        filters = [
            f"atrim=start={start:.6f}:duration={duration:.6f}",
            "asetpts=PTS-STARTPTS",
        ]
        if source_processing and (abs(tempo - 1.0) > 1e-6 or abs(pitch - 1.0) > 1e-6):
            filters.append(
                "rubberband="
                f"tempo={tempo:.9f}:pitch={pitch:.9f}:"
                "transients=smooth:detector=soft:phase=laminar:window=long:"
                "formant=preserved:pitchq=quality:channels=together"
            )
        if source_processing:
            filters.extend(["highpass=f=85", "lowpass=f=15500"])
        filters.extend(
            [
                "pan=mono|c0=0.5*c0+0.5*c1",
                f"highpass=f={lo}",
                f"lowpass=f={hi}",
                "aeval=abs(val(0))",
                "lowpass=f=12",
                f"aresample={ENVELOPE_RATE}",
            ]
        )
        cmd = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(path),
            "-af",
            ",".join(filters),
            "-ac",
            "1",
            "-f",
            "f32le",
            "pipe:1",
        ]
        raw = subprocess.run(cmd, check=True, capture_output=True).stdout
        values = array.array("f")
        values.frombytes(raw)
        band = [float(v) for v in values]
        if band:
            scale = math.sqrt(sum(v * v for v in band) / len(band)) or 1.0
            band = [v / scale for v in band]
        all_bands.append(band)

    n = min((len(x) for x in all_bands), default=0)
    # Interleave frequency bands at each time step so a lag remains a time lag.
    return [all_bands[b][i] for i in range(n) for b in range(len(all_bands))]


def corr_at_lag(a: list[float], b: list[float], lag_frames: int) -> float:
    stride = len(BANDS)
    lag = lag_frames * stride
    if lag >= 0:
        aa, bb = a[lag:], b[: len(a) - lag]
    else:
        aa, bb = a[: len(a) + lag], b[-lag:]
    n = min(len(aa), len(bb))
    if n < 30:
        return -1.0
    aa, bb = aa[:n], bb[:n]
    ma = sum(aa) / n
    mb = sum(bb) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(aa, bb))
    da = math.sqrt(sum((x - ma) ** 2 for x in aa))
    db = math.sqrt(sum((y - mb) ** 2 for y in bb))
    return num / (da * db) if da and db else -1.0


def reverse_time(fingerprint: list[float]) -> list[float]:
    stride = len(BANDS)
    frames = [fingerprint[i : i + stride] for i in range(0, len(fingerprint), stride)]
    return [v for frame in reversed(frames) for v in frame]


def best_corr(a: list[float], b: list[float], max_lag_seconds: float = 0.20) -> float:
    limit = int(round(max_lag_seconds * ENVELOPE_RATE))
    return max(corr_at_lag(a, b, lag) for lag in range(-limit, limit + 1))


def stem_diagnosis(manifest: dict, stem: Path, source_name: str) -> dict:
    total = float(manifest["duration_seconds"])
    source_path = Path(manifest["source_paths"][source_name])
    rows = []
    for event in manifest["events"]:
        if event["source"] != source_name:
            continue
        source_duration = float(event["source_end"]) - float(event["source_start"])
        processed_duration = float(event["processed_duration_seconds"])
        source_fp = ffmpeg_fingerprint(
            source_path,
            float(event["source_start"]),
            source_duration,
            tempo=float(event["tempo"]),
            pitch=float(event["pitch"]),
            source_processing=True,
        )
        declared_start = float(event["destination_start_seconds"])
        mirrored_start = total - float(event["destination_end_seconds"])
        declared_fp = ffmpeg_fingerprint(stem, declared_start, processed_duration)
        mirrored_fp = ffmpeg_fingerprint(stem, mirrored_start, processed_duration)
        rows.append(
            {
                "phrase_id": event["phrase_id"],
                "declared_forward": round(best_corr(declared_fp, source_fp), 4),
                "declared_reversed": round(best_corr(declared_fp, reverse_time(source_fp)), 4),
                "mirrored_forward": round(best_corr(mirrored_fp, source_fp), 4),
                "mirrored_reversed": round(best_corr(mirrored_fp, reverse_time(source_fp)), 4),
            }
        )
    hypotheses = ["declared_forward", "declared_reversed", "mirrored_forward", "mirrored_reversed"]
    medians = {h: round(statistics.median(row[h] for row in rows), 4) for h in hypotheses}
    winner = max(medians, key=medians.get)
    return {"stem": str(stem), "event_count": len(rows), "median_correlations": medians, "winner": winner, "events": rows}


def timeline_diagnosis(render: Path, reference: Path, duration: float, label: str) -> dict:
    render_fp = ffmpeg_fingerprint(render, 0.0, duration)
    reference_fp = ffmpeg_fingerprint(reference, 0.0, duration)
    scores = {
        f"forward_{label}_timeline": round(best_corr(render_fp, reference_fp, 1.0), 4),
        f"reversed_{label}_timeline": round(best_corr(render_fp, reverse_time(reference_fp), 1.0), 4),
    }
    return {
        "render": str(render),
        "reference": str(reference),
        "correlations": scores,
        "winner": max(scores, key=scores.get),
    }


def first_existing(*paths: Path) -> Path:
    """Return the first existing path, with the candidates in the error."""
    for path in paths:
        if path.exists():
            return path
    joined = ", ".join(str(path) for path in paths)
    raise FileNotFoundError(f"None of the expected files exist: {joined}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path(
            "/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/"
            "jhol-pal-pal-lofi-deep-house/v3-balanced-original-instrumental"
        ),
    )
    parser.add_argument(
        "--render",
        type=Path,
        default=None,
        help="FL Studio render to inspect (defaults to the original faulty v3 render)",
    )
    parser.add_argument(
        "--assert-forward",
        action="store_true",
        help="Exit non-zero unless both vocal timelines and the instrumental are forward",
    )
    parser.add_argument(
        "--include-details",
        action="store_true",
        help="Also inspect source stems, offline preview, and the existing separated-vocal analysis",
    )
    parser.add_argument(
        "--vocal-only",
        action="store_true",
        help="Treat --render as an extracted vocal render and skip the instrumental timeline test",
    )
    parser.add_argument(
        "--vocal-reference",
        type=Path,
        default=None,
        help="Exact arranged vocal-bus reference for a whole-timeline direction check",
    )
    args = parser.parse_args()
    workspace = args.workspace
    vocal_dir = workspace / "vocal-stems"
    manifest_path = first_existing(
        vocal_dir / "vocal-arrangement-manifest.json",
        vocal_dir / "v3-vocal-arrangement-manifest.json",
    )
    manifest = json.loads(manifest_path.read_text())
    render = args.render or workspace / "renders" / "jhol-pal-pal-v3-balanced-fl-mix-224s.wav"
    direct_jhol = stem_diagnosis(manifest, render, "jhol")
    direct_pal = stem_diagnosis(manifest, render, "pal_pal")
    instrumental = None
    if not args.vocal_only:
        instrumental_reference = first_existing(
            workspace / "instrumental-stems" / "10-original-instrumental-reference.wav",
            workspace / "instrumental-stems" / "07-original-instrumental-reference.wav",
        )
        instrumental = timeline_diagnosis(
            render,
            instrumental_reference,
            float(manifest["duration_seconds"]),
            "instrumental",
        )
    result = {
        "method": "multiband energy fingerprint correlation; higher is a closer time-direction match",
        "render": str(render),
        "direct_render_jhol_events": direct_jhol,
        "direct_render_pal_pal_events": direct_pal,
    }
    vocal_timeline = None
    if args.vocal_reference is not None:
        vocal_timeline = timeline_diagnosis(
            render,
            args.vocal_reference,
            float(manifest["duration_seconds"]),
            "vocal",
        )
        result["render_vs_vocal_reference"] = vocal_timeline
    if instrumental is not None:
        result["fl_render_vs_instrumental"] = instrumental
    extracted_vocals = (
        workspace
        / "analysis"
        / "fl-render-vocals"
        / "jhol-pal-pal-v3-balanced-fl-mix-224s_(vocals)_mel_band_roformer_kim_ft_unwa.wav"
    )
    if args.include_details:
        result["jhol_stem"] = stem_diagnosis(
            manifest, vocal_dir / "v3-jhol-recurring-vocals.wav", "jhol"
        )
        result["pal_pal_stem"] = stem_diagnosis(
            manifest, vocal_dir / "v3-pal-pal-recurring-vocals.wav", "pal_pal"
        )
        result["fl_render_vs_offline_preview"] = timeline_diagnosis(
            render,
            workspace / "renders" / "jhol-pal-pal-v3-balanced-offline-preview.wav",
            float(manifest["duration_seconds"]),
            "mix",
        )
    if (
        args.include_details
        and extracted_vocals.exists()
        and render.name == "jhol-pal-pal-v3-balanced-fl-mix-224s.wav"
    ):
        result["extracted_render_vocals"] = timeline_diagnosis(
            extracted_vocals,
            vocal_dir / "v3-vocal-bus-reference.wav",
            float(manifest["duration_seconds"]),
            "vocals",
        )
        result["extracted_render_jhol_events"] = stem_diagnosis(manifest, extracted_vocals, "jhol")
        result["extracted_render_pal_pal_events"] = stem_diagnosis(manifest, extracted_vocals, "pal_pal")

    failures = []
    if instrumental is not None and instrumental["winner"] != "forward_instrumental_timeline":
        failures.append("instrumental timeline is reversed")
    if vocal_timeline is not None:
        scores = vocal_timeline["correlations"]
        forward = scores["forward_vocal_timeline"]
        reversed_score = scores["reversed_vocal_timeline"]
        if vocal_timeline["winner"] != "forward_vocal_timeline" or forward < 0.15 or forward - reversed_score < 0.05:
            failures.append(
                "whole vocal timeline did not clear the forward confidence gate "
                f"(forward={forward}, reversed={reversed_score})"
            )
    else:
        if direct_jhol["winner"] != "declared_forward":
            failures.append(f"Jhol render direction is {direct_jhol['winner']}")
        if direct_pal["winner"] != "declared_forward":
            failures.append(f"Pal Pal render direction is {direct_pal['winner']}")
    result["forward_pass"] = not failures
    result["failures"] = failures
    print(json.dumps(result, indent=2))
    if args.assert_forward and failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
