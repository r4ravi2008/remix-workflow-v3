#!/usr/bin/env python3
"""Prepare extracted acapella audio for remix generation."""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import librosa
import numpy as np


class PrepareError(RuntimeError):
    pass


NOTES = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
MAJOR_PROFILE = np.array(
    [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
)
MINOR_PROFILE = np.array(
    [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
)


@dataclass(frozen=True)
class AudioAnalysis:
    detected_bpm: float
    key_candidates: list[dict[str, float | str]]

    @property
    def detected_key(self) -> str | None:
        if not self.key_candidates:
            return None
        return str(self.key_candidates[0]["key"])


@dataclass(frozen=True)
class PrepResult:
    output_audio: Path
    report_path: Path
    report: dict


def require_file(path: Path) -> Path:
    if not path.exists():
        raise PrepareError(f"Missing required file: {path}")
    return path


def workspace_relative(path: Path, workspace_dir: Path) -> str:
    relative = path.resolve().relative_to(workspace_dir.resolve())
    return f"{workspace_dir.name}/{relative.as_posix()}"


def pitch_ratio_from_semitones(semitones: float) -> float:
    return 2 ** (semitones / 12)


def normalize_profile(profile: np.ndarray) -> np.ndarray:
    return profile / (np.linalg.norm(profile) + 1e-12)


def detect_key_candidates(
    chroma: np.ndarray, limit: int = 8
) -> list[dict[str, float | str]]:
    chroma_mean = normalize_profile(chroma.mean(axis=1))
    major = normalize_profile(MAJOR_PROFILE)
    minor = normalize_profile(MINOR_PROFILE)

    candidates: list[tuple[float, str]] = []
    for index, note in enumerate(NOTES):
        candidates.append(
            (float(np.dot(chroma_mean, np.roll(major, index))), f"{note} major")
        )
        candidates.append(
            (float(np.dot(chroma_mean, np.roll(minor, index))), f"{note} minor")
        )

    return [
        {"key": key, "confidence": round(score, 6)}
        for score, key in sorted(candidates, reverse=True)[:limit]
    ]


def analyze_audio(audio_path: Path, *, sample_rate: int = 22050) -> AudioAnalysis:
    y, sr = librosa.load(audio_path, sr=sample_rate, mono=True)
    if y.size == 0:
        raise PrepareError(f"Audio file has no samples: {audio_path}")

    onset_envelope = librosa.onset.onset_strength(y=y, sr=sr)
    tempo = librosa.feature.tempo(onset_envelope=onset_envelope, sr=sr)
    detected_bpm = float(np.asarray(tempo).reshape(-1)[0])
    if not math.isfinite(detected_bpm) or detected_bpm <= 0:
        raise PrepareError(f"Could not detect a valid BPM for {audio_path}")

    harmonic = librosa.effects.harmonic(y)
    chroma = librosa.feature.chroma_cqt(y=harmonic, sr=sr, bins_per_octave=36)

    return AudioAnalysis(
        detected_bpm=round(detected_bpm, 3),
        key_candidates=detect_key_candidates(chroma),
    )


def build_rubberband_filter(tempo_ratio: float, pitch_ratio: float) -> str:
    return (
        f"rubberband=tempo={tempo_ratio:.8f}:pitch={pitch_ratio:.8f}:"
        "formant=preserved:pitchq=quality"
    )


def run_ffmpeg_prepare(
    *,
    input_audio: Path,
    output_audio: Path,
    tempo_ratio: float,
    pitch_ratio: float,
    runner=subprocess.run,
) -> list[str]:
    output_audio.parent.mkdir(parents=True, exist_ok=True)
    if abs(tempo_ratio - 1.0) < 0.0001 and abs(pitch_ratio - 1.0) < 0.0001:
        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(input_audio),
            "-codec:a",
            "libmp3lame",
            "-b:a",
            "192k",
            str(output_audio),
        ]
    else:
        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(input_audio),
            "-af",
            build_rubberband_filter(tempo_ratio, pitch_ratio),
            "-codec:a",
            "libmp3lame",
            "-b:a",
            "192k",
            str(output_audio),
        ]

    try:
        runner(command, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError) as error:
        raise PrepareError(f"ffmpeg failed while preparing {input_audio}") from error

    return command


def update_meta(
    meta_path: Path, *, workspace_dir: Path, slug: str, report: dict
) -> None:
    with meta_path.open("r", encoding="utf-8") as file:
        meta = json.load(file)

    meta.setdefault("files", {})
    meta["files"]["acapella_prepped"] = f"{slug}/{slug}-acapella-prepped.mp3"
    meta["files"]["acapella_prep_report"] = f"{slug}/{slug}-acapella-prep.json"
    meta.setdefault("status", {})
    meta["status"]["acapella_prepped"] = True
    meta["audio_analysis"] = {
        "detected_bpm": report["detected_bpm"],
        "target_bpm": report["target_bpm"],
        "detected_key": report["detected_key"],
        "pitch_semitones": report["pitch_semitones"],
    }

    meta_path.write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def prepare_acapella(
    workspace_dir: Path,
    slug: str,
    *,
    target_bpm: float | None = None,
    pitch_semitones: float = 0.0,
    update_metadata: bool = True,
    runner=subprocess.run,
) -> PrepResult:
    workspace_dir = workspace_dir.resolve()
    meta_path = require_file(workspace_dir / "meta.json")
    original_audio = require_file(workspace_dir / f"{slug}-original.mp3")
    acapella_audio = require_file(workspace_dir / f"{slug}-acapella.mp3")
    output_audio = workspace_dir / f"{slug}-acapella-prepped.mp3"
    report_path = workspace_dir / f"{slug}-acapella-prep.json"

    analysis = analyze_audio(original_audio)
    effective_target_bpm = round(float(target_bpm or analysis.detected_bpm), 3)
    if not math.isfinite(effective_target_bpm) or effective_target_bpm <= 0:
        raise PrepareError("--target-bpm must be greater than 0")
    if not math.isfinite(pitch_semitones):
        raise PrepareError("--pitch-semitones must be finite")
    tempo_ratio = effective_target_bpm / analysis.detected_bpm
    pitch_ratio = pitch_ratio_from_semitones(pitch_semitones)

    command = run_ffmpeg_prepare(
        input_audio=acapella_audio,
        output_audio=output_audio,
        tempo_ratio=tempo_ratio,
        pitch_ratio=pitch_ratio,
        runner=runner,
    )

    report = {
        "input_original": workspace_relative(original_audio, workspace_dir),
        "input_acapella": workspace_relative(acapella_audio, workspace_dir),
        "output_acapella": workspace_relative(output_audio, workspace_dir),
        "detected_bpm": analysis.detected_bpm,
        "target_bpm": effective_target_bpm,
        "tempo_ratio": round(tempo_ratio, 8),
        "detected_key": analysis.detected_key,
        "key_candidates": analysis.key_candidates,
        "pitch_semitones": pitch_semitones,
        "pitch_ratio": round(pitch_ratio, 8),
        "ffmpeg_command": command,
        "created_at": datetime.now(UTC).isoformat(),
    }
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    if update_metadata:
        update_meta(meta_path, workspace_dir=workspace_dir, slug=slug, report=report)

    return PrepResult(output_audio=output_audio, report_path=report_path, report=report)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prepare extracted acapella for remix generation"
    )
    parser.add_argument("--workspace-dir", required=True, type=Path)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--target-bpm", type=float, default=None)
    parser.add_argument("--pitch-semitones", type=float, default=0.0)
    parser.add_argument("--no-update-meta", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = prepare_acapella(
            args.workspace_dir,
            args.slug,
            target_bpm=args.target_bpm,
            pitch_semitones=args.pitch_semitones,
            update_metadata=not args.no_update_meta,
        )
        print(f"Acapella prepared: {result.output_audio}")
        print(f"Report: {result.report_path}")
        return 0
    except PrepareError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
