#!/usr/bin/env python3
"""Build aligned, recurring Jhol and Pal Pal vocal stems for the v3 mashup.

The arrangement follows the reference mashup's sustained thought-unit handoffs:
eight-bar lead blocks through the body, then four-bar trades in the final drop.
It never layers two intelligible lead phrases at the same time.
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import tempfile
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np
import soundfile as sf


SR = 48_000
BPM = 105.0
BEAT = 60.0 / BPM
BAR = 4.0 * BEAT
TOTAL_BARS = 98
TOTAL_SECONDS = TOTAL_BARS * BAR
N = int(round(TOTAL_SECONDS * SR))
JHOL_TEMPO = 78.0
PAL_TEMPO = 103.359
JHOL_TO_GRID = BPM / JHOL_TEMPO
PAL_TO_GRID = BPM / PAL_TEMPO
PITCH_PLUS_3 = 2.0 ** (3.0 / 12.0)
FADE_IN_SECONDS = 0.080
FADE_OUT_SECONDS = 0.550


@dataclass(frozen=True)
class Phrase:
    phrase_id: str
    source: str
    source_start: float
    source_end: float
    destination_bar: int
    offset_seconds: float
    tempo: float
    pitch: float
    key_role: str
    thought_role: str

    @property
    def destination_seconds(self) -> float:
        return (self.destination_bar - 1) * BAR + self.offset_seconds


PHRASES = [
    # Jhol is established immediately with two complete lead ideas, not a one-beat teaser.
    Phrase("jhol_intro_hook", "jhol", 89.980, 101.360, 1, 0.350, JHOL_TO_GRID, PITCH_PLUS_3, "Fm", "opening hook"),
    Phrase("jhol_intro_lift", "jhol", 109.640, 115.780, 1, 11.300, JHOL_TO_GRID, PITCH_PLUS_3, "Fm", "opening lift"),
    Phrase("pal_hook_a", "pal_pal", 17.480, 35.820, 9, 0.120, PAL_TO_GRID, 1.0, "Fm", "first hook"),
    Phrase("jhol_setup_a", "jhol", 35.680, 47.320, 17, 0.350, JHOL_TO_GRID, PITCH_PLUS_3, "Fm", "verse setup"),
    Phrase("jhol_answer_a", "jhol", 48.040, 54.880, 17, 11.500, JHOL_TO_GRID, PITCH_PLUS_3, "Fm", "emotional answer"),
    Phrase("pal_verse_a", "pal_pal", 35.680, 53.420, 25, 0.120, PAL_TO_GRID, 1.0, "Fm", "verse response"),
    Phrase("jhol_payoff_a", "jhol", 58.820, 65.300, 33, 0.300, JHOL_TO_GRID, PITCH_PLUS_3, "Fm", "payoff"),
    Phrase("jhol_prehook_a", "jhol", 64.960, 74.680, 33, 6.304, JHOL_TO_GRID, PITCH_PLUS_3, "Fm", "pre-hook lift"),
    Phrase("jhol_title_tag_a", "jhol", 89.980, 94.360, 33, 14.954, JHOL_TO_GRID, PITCH_PLUS_3, "Fm", "title tag"),
    Phrase("pal_verse_b", "pal_pal", 53.260, 70.620, 41, 0.120, PAL_TO_GRID, 1.0, "Fm", "second verse response"),
    Phrase("jhol_primary_hook_a", "jhol", 74.300, 89.160, 49, 0.250, JHOL_TO_GRID, PITCH_PLUS_3, "Fm", "primary hook setup"),
    Phrase("jhol_primary_hook_b", "jhol", 94.300, 101.360, 49, 13.507, JHOL_TO_GRID, PITCH_PLUS_3, "Fm", "primary hook payoff"),
    Phrase("pal_lift_a", "pal_pal", 70.580, 88.620, 57, 0.120, PAL_TO_GRID, 1.0, "Fm", "answer drop"),
    # Native-pitch/free-feel Jhol over an original D-minor breakdown.
    Phrase("jhol_native_breakdown", "jhol", 207.440, 224.720, 65, 0.550, 1.0, 1.0, "Dm", "intimate breakdown"),
    Phrase("pal_reentry", "pal_pal", 91.140, 109.640, 73, 0.040, PAL_TO_GRID, 1.0, "Fm", "post-breakdown re-entry"),
    # The final sixteen bars use four-bar thought-unit trades.
    Phrase("jhol_final_trade_a", "jhol", 231.380, 243.520, 81, 0.050, JHOL_TO_GRID, PITCH_PLUS_3, "Fm", "final trade A"),
    Phrase("pal_final_trade_a", "pal_pal", 17.480, 22.020, 85, 0.150, PAL_TO_GRID, 1.0, "Fm", "final trade A"),
    Phrase("jhol_final_trade_b", "jhol", 166.500, 178.550, 89, 0.100, JHOL_TO_GRID, PITCH_PLUS_3, "Fm", "final trade B"),
    Phrase("pal_final_trade_b", "pal_pal", 28.000, 35.820, 93, 0.200, PAL_TO_GRID, 1.0, "Fm", "final resolution"),
]

PHRASE_FADES = {
    "jhol_intro_hook": (0.120, 0.220),
    "jhol_intro_lift": (0.140, 0.230),
    "pal_hook_a": (0.140, 0.180),
    "jhol_setup_a": (0.120, 0.220),
    "jhol_answer_a": (0.140, 0.230),
    "pal_verse_a": (0.140, 0.160),
    "jhol_payoff_a": (0.130, 0.200),
    "jhol_prehook_a": (0.120, 0.220),
    "jhol_title_tag_a": (0.120, 0.220),
    "pal_verse_b": (0.140, 0.180),
    "jhol_primary_hook_a": (0.130, 0.220),
    "jhol_primary_hook_b": (0.130, 0.230),
    "pal_lift_a": (0.150, 0.200),
    "jhol_native_breakdown": (0.160, 0.260),
    "pal_reentry": (0.150, 0.180),
    "jhol_final_trade_a": (0.120, 0.220),
    "pal_final_trade_a": (0.140, 0.220),
    "jhol_final_trade_b": (0.130, 0.240),
    "pal_final_trade_b": (0.140, 0.220),
}


def configure_tempo(bpm: float) -> None:
    """Re-grid the arrangement without altering the source phrase order."""
    global BPM, BEAT, BAR, TOTAL_SECONDS, N, JHOL_TO_GRID, PAL_TO_GRID, PHRASES
    if not math.isfinite(bpm) or bpm <= 0:
        raise ValueError("bpm must be greater than zero")
    BPM = float(bpm)
    BEAT = 60.0 / BPM
    BAR = 4.0 * BEAT
    TOTAL_SECONDS = TOTAL_BARS * BAR
    N = int(round(TOTAL_SECONDS * SR))
    JHOL_TO_GRID = BPM / JHOL_TEMPO
    PAL_TO_GRID = BPM / PAL_TEMPO
    PHRASES = [
        Phrase(
            phrase_id=phrase.phrase_id,
            source=phrase.source,
            source_start=phrase.source_start,
            source_end=phrase.source_end,
            destination_bar=phrase.destination_bar,
            offset_seconds=phrase.offset_seconds,
            tempo=(
                1.0
                if phrase.phrase_id == "jhol_native_breakdown"
                else JHOL_TO_GRID
                if phrase.source == "jhol"
                else PAL_TO_GRID
            ),
            pitch=(
                1.0
                if phrase.phrase_id == "jhol_native_breakdown" or phrase.source == "pal_pal"
                else PITCH_PLUS_3
            ),
            key_role=phrase.key_role,
            thought_role=phrase.thought_role,
        )
        for phrase in PHRASES
    ]


def run_ffmpeg(source: Path, phrase: Phrase, output: Path) -> None:
    filters = [
        f"atrim=start={phrase.source_start:.6f}:end={phrase.source_end:.6f}",
        "asetpts=PTS-STARTPTS",
    ]
    if abs(phrase.tempo - 1.0) > 1e-6 or abs(phrase.pitch - 1.0) > 1e-6:
        filters.append(
            "rubberband="
            f"tempo={phrase.tempo:.9f}:pitch={phrase.pitch:.9f}:"
            "transients=smooth:detector=soft:phase=laminar:window=long:"
            "formant=preserved:pitchq=quality:channels=together"
        )
    filters.extend(["highpass=f=85", "lowpass=f=15500", "aresample=48000"])
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        str(source),
        "-af",
        ",".join(filters),
        "-ar",
        str(SR),
        "-ac",
        "2",
        "-c:a",
        "pcm_s24le",
        str(output),
    ]
    subprocess.run(cmd, check=True)


def active_rms(x: np.ndarray) -> float:
    mono = np.mean(x, axis=1) if x.ndim == 2 else x
    frame = max(1, int(0.050 * SR))
    usable = len(mono) - (len(mono) % frame)
    if usable <= 0:
        return float(np.sqrt(np.mean(np.square(mono)) + 1e-12))
    framed = mono[:usable].reshape(-1, frame)
    rms = np.sqrt(np.mean(np.square(framed), axis=1) + 1e-12)
    threshold = max(10 ** (-48.0 / 20.0), float(np.percentile(rms, 35)) * 1.8)
    active = rms[rms >= threshold]
    return float(np.median(active)) if len(active) else float(np.median(rms))


def prepare_audio(x: np.ndarray, source: str, phrase_id: str) -> np.ndarray:
    if x.ndim == 1:
        x = np.column_stack([x, x])
    target_db = -22.3 if source == "jhol" else -22.8
    rms = max(1e-9, active_rms(x))
    x = x * ((10 ** (target_db / 20.0)) / rms)
    peak = float(np.max(np.abs(x)))
    ceiling = 10 ** (-4.0 / 20.0)
    if peak > ceiling:
        x *= ceiling / peak
    fade_in_seconds, fade_out_seconds = PHRASE_FADES.get(
        phrase_id, (FADE_IN_SECONDS, FADE_OUT_SECONDS)
    )
    fade_in_n = min(len(x) // 2, int(fade_in_seconds * SR))
    fade_out_n = min(len(x) // 2, int(fade_out_seconds * SR))
    if fade_in_n > 1:
        fade_in = np.sin(np.linspace(0.0, math.pi / 2.0, fade_in_n, dtype=np.float32)) ** 2
        x[:fade_in_n] *= fade_in[:, None]
    if fade_out_n > 1:
        fade_out = np.cos(np.linspace(0.0, math.pi / 2.0, fade_out_n, dtype=np.float32)) ** 2
        x[-fade_out_n:] *= fade_out[:, None]
    return x.astype(np.float32)


def add_at(stem: np.ndarray, audio: np.ndarray, start_s: float) -> tuple[float, float]:
    start = int(round(start_s * SR))
    end = min(N, start + len(audio))
    if start < 0 or start >= N:
        raise ValueError(f"invalid destination time {start_s}")
    stem[start:end] += audio[: end - start]
    return start / SR, end / SR


def vocal_fx_bus(dry: np.ndarray) -> np.ndarray:
    wet = np.zeros_like(dry)
    # 91-BPM-friendly 1/16, 1/8 and dotted-1/8 delay taps; values follow BPM dynamically.
    for delay_s, gain, swap in [
        (BEAT / 4.0, 0.090, True),
        (BEAT / 2.0, 0.068, False),
        (BEAT * 0.75, 0.050, True),
        (BEAT * 1.5, 0.026, False),
    ]:
        d = int(delay_s * SR)
        src = dry[:-d]
        if swap:
            src = src[:, ::-1]
        wet[d:] += src * gain
    # A sparse plate-style tail keeps phrase endings alive across vocal handoffs.
    for delay_s, gain, swap in [
        (0.028, 0.055, False),
        (0.083, 0.038, True),
        (0.149, 0.030, False),
        (0.263, 0.022, True),
        (0.431, 0.016, False),
        (0.719, 0.011, True),
        (1.103, 0.007, False),
        (1.603, 0.004, True),
    ]:
        d = int(delay_s * SR)
        src = dry[:-d]
        if swap:
            src = src[:, ::-1]
        wet[d:] += src * gain
    return wet


def peak_db(x: np.ndarray) -> float:
    return 20.0 * math.log10(max(1e-12, float(np.max(np.abs(x)))))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--jhol", type=Path, required=True)
    parser.add_argument("--pal-pal", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--bpm", type=float, default=105.0)
    parser.add_argument("--prefix", default="v3")
    args = parser.parse_args()
    configure_tempo(args.bpm)
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)

    stems = {
        "jhol": np.zeros((N, 2), dtype=np.float32),
        "pal_pal": np.zeros((N, 2), dtype=np.float32),
    }
    events = []
    sources = {"jhol": args.jhol.resolve(), "pal_pal": args.pal_pal.resolve()}

    with tempfile.TemporaryDirectory(prefix="v3-vocal-phrases.") as temp:
        temp_dir = Path(temp)
        for phrase in PHRASES:
            rendered = temp_dir / f"{phrase.phrase_id}.wav"
            run_ffmpeg(sources[phrase.source], phrase, rendered)
            audio, sr = sf.read(rendered, dtype="float32", always_2d=True)
            if sr != SR:
                raise RuntimeError(f"unexpected sample rate {sr} for {rendered}")
            audio = prepare_audio(audio, phrase.source, phrase.phrase_id)
            start, end = add_at(stems[phrase.source], audio, phrase.destination_seconds)
            event = asdict(phrase)
            event.update(
                {
                    "destination_start_seconds": round(start, 6),
                    "destination_end_seconds": round(end, 6),
                    "processed_duration_seconds": round(end - start, 6),
                    "processed_peak_dbfs": round(peak_db(audio), 3),
                }
            )
            events.append(event)

    for source, stem in stems.items():
        stem = np.tanh(stem * 1.015).astype(np.float32)
        stems[source] = stem
        sf.write(out / f"{args.prefix}-{source.replace('_', '-')}-recurring-vocals.wav", stem, SR, subtype="PCM_24")

    dry_bus = stems["jhol"] + stems["pal_pal"]
    fx_bus = vocal_fx_bus(dry_bus)
    sf.write(out / f"{args.prefix}-vocal-fx-return.wav", fx_bus, SR, subtype="PCM_24")
    sf.write(out / f"{args.prefix}-vocal-bus-reference.wav", dry_bus + fx_bus, SR, subtype="PCM_24")

    manifest = {
        "tempo_bpm": BPM,
        "time_signature": "4/4",
        "duration_seconds": TOTAL_SECONDS,
        "arrangement_policy": "complete thought-unit handoffs; eight-bar blocks then four-bar final trades; no dual intelligible lead",
        "boundary_policy": {
            "fade_in_ms": round(FADE_IN_SECONDS * 1000),
            "fade_out_ms": round(FADE_OUT_SECONDS * 1000),
            "per_phrase_fades": True,
            "fx_tails_cross_handoffs": True,
        },
        "transforms": {
            "jhol_grid_sections": {
                "native_bpm": JHOL_TEMPO,
                "target_bpm": BPM,
                "tempo_factor": JHOL_TO_GRID,
                "pitch_semitones": 3,
                "formants": "preserved",
            },
            "jhol_breakdown": {"tempo_factor": 1.0, "pitch_semitones": 0, "key_center": "D minor"},
            "pal_pal": {"native_bpm": PAL_TEMPO, "target_bpm": BPM, "tempo_factor": PAL_TO_GRID},
        },
        "source_paths": {key: str(value) for key, value in sources.items()},
        "events": events,
        "outputs": {
            "jhol": f"{args.prefix}-jhol-recurring-vocals.wav",
            "pal_pal": f"{args.prefix}-pal-pal-recurring-vocals.wav",
            "fx_return": f"{args.prefix}-vocal-fx-return.wav",
            "vocal_bus_reference": f"{args.prefix}-vocal-bus-reference.wav",
        },
        "peaks_dbfs": {key: round(peak_db(value), 3) for key, value in stems.items()},
    }
    (out / "vocal-arrangement-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"events": len(events), "peaks_dbfs": manifest["peaks_dbfs"], "duration_seconds": TOTAL_SECONDS}, indent=2))


if __name__ == "__main__":
    main()
