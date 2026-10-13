#!/usr/bin/env python3
"""Verify that both songs recur audibly across the rendered v3 timeline."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import soundfile as sf


BPM = 105.0
BAR = 4.0 * 60.0 / BPM
FRAME_SECONDS = 0.100
ACTIVITY_DBFS = -45.0


SECTIONS = [
    ("jhol_intro", 1, 8, "jhol"),
    ("pal_hook", 9, 16, "pal_pal"),
    ("jhol_setup", 17, 24, "jhol"),
    ("pal_verse", 25, 32, "pal_pal"),
    ("jhol_payoff", 33, 40, "jhol"),
    ("pal_lift", 41, 48, "pal_pal"),
    ("jhol_drop", 49, 56, "jhol"),
    ("pal_answer_drop", 57, 64, "pal_pal"),
    ("jhol_breakdown", 65, 72, "jhol"),
    ("pal_reentry", 73, 80, "pal_pal"),
    ("jhol_trade_a", 81, 84, "jhol"),
    ("pal_trade_a", 85, 88, "pal_pal"),
    ("jhol_trade_b", 89, 92, "jhol"),
    ("pal_resolution", 93, 96, "pal_pal"),
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def load(path: Path) -> tuple[np.ndarray, int]:
    x, sr = sf.read(path, dtype="float32", always_2d=True)
    return np.mean(x, axis=1), sr


def frame_rms(x: np.ndarray, sr: int) -> np.ndarray:
    size = max(1, int(round(FRAME_SECONDS * sr)))
    usable = len(x) - len(x) % size
    if usable <= 0:
        return np.zeros(0, dtype=np.float32)
    frames = x[:usable].reshape(-1, size)
    return np.sqrt(np.mean(np.square(frames), axis=1) + 1e-12)


def db(value: float) -> float:
    return 20.0 * math.log10(max(1e-12, value))


def cosine_projection(render: np.ndarray, stem: np.ndarray) -> float:
    if len(render) != len(stem):
        n = min(len(render), len(stem))
        render, stem = render[:n], stem[:n]
    stem_energy = float(np.dot(stem, stem))
    if stem_energy < 1e-12:
        return 0.0
    return float(np.dot(render, stem) / stem_energy)


def envelope_correlation(render_vocals: np.ndarray, source_stem: np.ndarray, sr: int) -> float:
    a = frame_rms(render_vocals, sr)
    b = frame_rms(source_stem, sr)
    best = 0.0
    for shift in range(-4, 5):
        aa = a[max(0, shift) : len(a) + min(0, shift)]
        bb = b[max(0, -shift) : len(b) - max(0, shift)]
        if len(aa) < 5 or float(np.std(aa)) < 1e-9 or float(np.std(bb)) < 1e-9:
            continue
        best = max(best, float(np.corrcoef(aa, bb)[0, 1]))
    return best


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--render", type=Path, required=True)
    parser.add_argument("--jhol-stem", type=Path, required=True)
    parser.add_argument("--pal-stem", type=Path, required=True)
    parser.add_argument("--instrumental", type=Path, required=True)
    parser.add_argument("--render-vocals", type=Path)
    parser.add_argument("--fl-project", type=Path)
    parser.add_argument("--live-playback-pass", action="store_true")
    parser.add_argument("--vocal-manifest", type=Path, required=True)
    parser.add_argument("--jhol-source", type=Path, required=True)
    parser.add_argument("--pal-source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    paths = {
        "render": args.render.resolve(),
        "jhol_stem": args.jhol_stem.resolve(),
        "pal_stem": args.pal_stem.resolve(),
        "instrumental": args.instrumental.resolve(),
        "vocal_manifest": args.vocal_manifest.resolve(),
        "jhol_source": args.jhol_source.resolve(),
        "pal_source": args.pal_source.resolve(),
    }
    if args.render_vocals:
        paths["render_vocals"] = args.render_vocals.resolve()
    if args.fl_project:
        paths["fl_project"] = args.fl_project.resolve()
    arrays = {}
    sample_rates = {}
    for key in ("render", "jhol_stem", "pal_stem", "instrumental"):
        arrays[key], sample_rates[key] = load(paths[key])
    if "render_vocals" in paths:
        arrays["render_vocals"], sample_rates["render_vocals"] = load(paths["render_vocals"])
    if len(set(sample_rates.values())) != 1:
        raise RuntimeError(f"sample-rate mismatch: {sample_rates}")
    sr = sample_rates["render"]
    threshold = 10 ** (ACTIVITY_DBFS / 20.0)

    section_results = []
    jhol_detected = []
    pal_detected = []
    dual_active_total = 0
    active_total = 0
    for section_id, start_bar, end_bar, expected in SECTIONS:
        start = int(round((start_bar - 1) * BAR * sr))
        end = int(round(end_bar * BAR * sr))
        j = arrays["jhol_stem"][start:end]
        p = arrays["pal_stem"][start:end]
        r = arrays["render"][start:end]
        jr = frame_rms(j, sr)
        pr = frame_rms(p, sr)
        j_active = jr > threshold
        p_active = pr > threshold
        both = j_active & p_active
        any_active = j_active | p_active
        j_seconds = float(np.sum(j_active) * FRAME_SECONDS)
        p_seconds = float(np.sum(p_active) * FRAME_SECONDS)
        dual_seconds = float(np.sum(both) * FRAME_SECONDS)
        dual_active_total += int(np.sum(both))
        active_total += int(np.sum(any_active))
        if j_seconds >= 2.5:
            jhol_detected.append(section_id)
        if p_seconds >= 2.5:
            pal_detected.append(section_id)
        expected_seconds = j_seconds if expected == "jhol" else p_seconds
        wrong_seconds = p_seconds if expected == "jhol" else j_seconds
        stem = j if expected == "jhol" else p
        projection = cosine_projection(r, stem)
        render_vocal_rms_dbfs = None
        render_vocal_envelope_correlation = None
        if "render_vocals" in arrays:
            rv = arrays["render_vocals"][start:end]
            render_vocal_rms_dbfs = db(float(np.sqrt(np.mean(np.square(rv)) + 1e-12)))
            render_vocal_envelope_correlation = envelope_correlation(rv, stem, sr)
            render_presence_pass = render_vocal_rms_dbfs >= -45.0
        else:
            render_presence_pass = projection >= 0.45
        section_pass = expected_seconds >= 2.5 and wrong_seconds <= 0.25 and dual_seconds <= 0.10 and render_presence_pass
        section_results.append(
            {
                "section_id": section_id,
                "bars": [start_bar, end_bar],
                "expected_lead": expected,
                "seconds": [round(start / sr, 6), round(end / sr, 6)],
                "jhol_active_seconds": round(j_seconds, 3),
                "pal_pal_active_seconds": round(p_seconds, 3),
                "dual_active_seconds": round(dual_seconds, 3),
                "jhol_rms_dbfs": round(db(float(np.sqrt(np.mean(np.square(j)) + 1e-12))), 3),
                "pal_pal_rms_dbfs": round(db(float(np.sqrt(np.mean(np.square(p)) + 1e-12))), 3),
                "render_projection_on_expected_stem": round(projection, 4),
                "separated_render_vocal_rms_dbfs": None if render_vocal_rms_dbfs is None else round(render_vocal_rms_dbfs, 3),
                "separated_render_vocal_envelope_correlation": None
                if render_vocal_envelope_correlation is None
                else round(render_vocal_envelope_correlation, 4),
                "passes": section_pass,
            }
        )

    manifest = json.loads(paths["vocal_manifest"].read_text(encoding="utf-8"))
    jhol_event_count = sum(1 for event in manifest["events"] if event["source"] == "jhol")
    pal_event_count = sum(1 for event in manifest["events"] if event["source"] == "pal_pal")
    recurrence = {
        "jhol": {
            "event_count": jhol_event_count,
            "detected_sections": jhol_detected,
            "nonadjacent_section_count": len(jhol_detected),
            "minimum_required": 3,
            "passes": len(jhol_detected) >= 7 and jhol_event_count >= 10,
        },
        "pal_pal": {
            "event_count": pal_event_count,
            "detected_sections": pal_detected,
            "nonadjacent_section_count": len(pal_detected),
            "minimum_required": 4,
            "passes": len(pal_detected) >= 7 and pal_event_count >= 7,
        },
    }
    recurrence["both_sources_recur_across_timeline"] = bool(recurrence["jhol"]["passes"] and recurrence["pal_pal"]["passes"])
    all_sections = all(section["passes"] for section in section_results)
    dual_ratio = dual_active_total / max(1, active_total)
    final_pass = bool(recurrence["both_sources_recur_across_timeline"] and all_sections and dual_ratio < 0.01)

    receipt = {
        "schema": "fl-studio-mashup-render-verification/v3",
        "candidate_id": "v3-balanced-original-instrumental",
        "tempo_bpm": BPM,
        "time_signature": "4/4",
        "verification_boundary": "rendered waveform plus aligned source-derived vocal stems; FL live playback is tracked separately",
        "method": {
            "frame_seconds": FRAME_SECONDS,
            "activity_threshold_dbfs": ACTIVITY_DBFS,
            "minimum_expected_vocal_seconds_per_section": 2.5,
            "maximum_wrong_source_seconds_per_section": 0.25,
            "minimum_render_projection_on_expected_stem": 0.45,
            "minimum_separated_render_vocal_rms_dbfs": -45.0,
        },
        "files": {key: {"path": str(path), "sha256": sha256(path)} for key, path in paths.items()},
        "sample_rates": sample_rates,
        "duration_seconds": round(len(arrays["render"]) / sr, 6),
        "sections": section_results,
        "recurrence": recurrence,
        "dual_intelligible_lead_overlap_ratio": round(dual_ratio, 6),
        "rendered_audio_pass": final_pass,
        "live_fl_playback_pass": bool(args.live_playback_pass),
        "verified_complete": bool(final_pass and args.live_playback_pass),
        "failure_reasons": ([] if final_pass else ["rendered_audio_recurrence_or_section_gate_failed"])
        + ([] if args.live_playback_pass else ["live_fl_playback_pending"]),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "rendered_audio_pass": final_pass,
                "jhol_sections": len(jhol_detected),
                "pal_pal_sections": len(pal_detected),
                "dual_overlap_ratio": round(dual_ratio, 6),
                "failed_sections": [s["section_id"] for s in section_results if not s["passes"]],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
