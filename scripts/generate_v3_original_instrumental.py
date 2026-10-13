#!/usr/bin/env python3
"""Render an original lofi/deep-house instrumental as aligned 48 kHz stems.

This generator intentionally uses no audio, MIDI, melodies, or rhythms from either
Jhol or Pal Pal.  It creates a new 105 BPM arrangement with an F-minor center and
a D-minor breakdown so the native-pitch Jhol breakdown can breathe without a
conflicting chord bed.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt


SR = 48_000
BPM = 105.0
BEAT = 60.0 / BPM
BAR = 4.0 * BEAT
ARRANGEMENT_BARS = 96
TAIL_BARS = 2
TOTAL_BARS = ARRANGEMENT_BARS + TAIL_BARS
TOTAL_SECONDS = TOTAL_BARS * BAR
N = int(round(TOTAL_SECONDS * SR))
RNG = np.random.default_rng(20260806)


def configure_tempo(bpm: float) -> None:
    """Recalculate the timeline while preserving the deterministic arrangement."""
    global BPM, BEAT, BAR, TOTAL_SECONDS, N, RNG
    if not math.isfinite(bpm) or bpm <= 0:
        raise ValueError("bpm must be greater than zero")
    BPM = float(bpm)
    BEAT = 60.0 / BPM
    BAR = 4.0 * BEAT
    TOTAL_SECONDS = TOTAL_BARS * BAR
    N = int(round(TOTAL_SECONDS * SR))
    RNG = np.random.default_rng(20260806)


NOTE_TO_MIDI = {
    "C": 0,
    "Db": 1,
    "D": 2,
    "Eb": 3,
    "E": 4,
    "F": 5,
    "Gb": 6,
    "G": 7,
    "Ab": 8,
    "A": 9,
    "Bb": 10,
    "B": 11,
}


def hz(note: str) -> float:
    if len(note) >= 3 and note[1] in {"b", "#"}:
        name, octave = note[:2], int(note[2:])
    else:
        name, octave = note[0], int(note[1:])
    midi = NOTE_TO_MIDI[name] + 12 * (octave + 1)
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)


CHORDS = {
    "Fm9": ["Ab3", "C4", "Eb4", "G4"],
    "Dbmaj9": ["F3", "Ab3", "C4", "Eb4"],
    "Abmaj7C": ["G3", "Ab3", "C4", "Eb4"],
    "Eb69": ["G3", "Bb3", "C4", "F4"],
    "C7sus": ["F3", "Bb3", "C4", "Eb4"],
    "C7b9": ["E3", "Bb3", "C4", "Db4"],
    "Dm9": ["F3", "A3", "C4", "E4"],
    "Bbmaj9": ["D3", "F3", "A3", "C4"],
    "Cmaj9": ["E3", "G3", "B3", "D4"],
    "A7sus": ["D3", "G3", "A3", "C4"],
}

ROOTS = {
    "Fm9": ("F1", "C2", "Eb2"),
    "Dbmaj9": ("Db2", "Ab1", "C2"),
    "Abmaj7C": ("C2", "Eb2", "Ab1"),
    "Eb69": ("Eb2", "Bb1", "C2"),
    "C7sus": ("C2", "G1", "Bb1"),
    "C7b9": ("C2", "G1", "Db2"),
    "Dm9": ("D2", "A1", "C2"),
    "Bbmaj9": ("Bb1", "F1", "A1"),
    "Cmaj9": ("C2", "G1", "B1"),
    "A7sus": ("A1", "E2", "G2"),
}


def chord_for_bar(bar_zero: int) -> str:
    bar = bar_zero + 1
    if 65 <= bar <= 72:
        return ["Dm9", "Bbmaj9", "Cmaj9", "A7sus"][bar_zero % 4]
    if 41 <= bar <= 48:
        return ["Dbmaj9", "Eb69", "Fm9", "C7sus"][bar_zero % 4]
    if 89 <= bar <= 96:
        return ["Fm9", "Dbmaj9", "Eb69", "Fm9"][bar_zero % 4]
    if 1 <= bar <= 8:
        return ["Fm9", "Dbmaj9", "Eb69", "C7sus"][bar_zero % 4]
    return ["Fm9", "Dbmaj9", "Abmaj7C", "C7sus"][bar_zero % 4]


def active_drums(bar: int) -> bool:
    return 9 <= bar <= 64 or 73 <= bar <= 96


def section_gain(bar: int) -> float:
    if bar <= 8:
        return 0.48
    if 65 <= bar <= 72:
        return 0.44
    if 81 <= bar <= 88:
        return 1.0
    if 89 <= bar <= 96:
        return 0.82
    if 49 <= bar <= 64:
        return 0.9
    return 0.72


def add_mono(buf: np.ndarray, start_s: float, signal: np.ndarray, gain: float = 1.0) -> None:
    start = max(0, int(round(start_s * SR)))
    if start >= len(buf):
        return
    end = min(len(buf), start + len(signal))
    buf[start:end] += signal[: end - start].astype(np.float32) * gain


def stereo_from_mono(mono: np.ndarray, width: float = 0.0, delay_ms: float = 0.0) -> np.ndarray:
    if width <= 0.0:
        return np.column_stack([mono, mono]).astype(np.float32)
    delay = max(1, int(round(delay_ms * SR / 1000.0)))
    right = np.roll(mono, delay)
    right[:delay] = 0.0
    mid = mono * (1.0 - width * 0.15)
    side = (right - mono) * width * 0.35
    return np.column_stack([mid - side, mid + side]).astype(np.float32)


def lowpass(x: np.ndarray, cutoff: float, order: int = 3) -> np.ndarray:
    sos = butter(order, cutoff / (SR / 2.0), btype="low", output="sos")
    return sosfilt(sos, x).astype(np.float32)


def highpass(x: np.ndarray, cutoff: float, order: int = 3) -> np.ndarray:
    sos = butter(order, cutoff / (SR / 2.0), btype="high", output="sos")
    return sosfilt(sos, x).astype(np.float32)


def kick_voice(length_s: float = 0.62) -> np.ndarray:
    n = int(length_s * SR)
    t = np.arange(n, dtype=np.float32) / SR
    f0, f1 = 128.0, 46.0
    phase = 2.0 * np.pi * (f1 * t + (f0 - f1) * 0.018 * (1.0 - np.exp(-t / 0.018)))
    body = np.sin(phase) * np.exp(-t / 0.18)
    sub = np.sin(2.0 * np.pi * 47.0 * t) * np.exp(-t / 0.28) * 0.36
    click = highpass(RNG.normal(0, 1, n).astype(np.float32), 4200) * np.exp(-t / 0.010) * 0.12
    return np.tanh((body + sub + click) * 1.25).astype(np.float32)


def clap_voice(length_s: float = 0.38) -> np.ndarray:
    n = int(length_s * SR)
    t = np.arange(n, dtype=np.float32) / SR
    noise = RNG.normal(0, 1, n).astype(np.float32)
    band = highpass(lowpass(noise, 7200), 850)
    env = np.zeros(n, dtype=np.float32)
    for off, amp in [(0.0, 1.0), (0.018, 0.72), (0.036, 0.48)]:
        idx = int(off * SR)
        env[idx:] += amp * np.exp(-t[: n - idx] / 0.055)
    return np.tanh(band * env * 0.62).astype(np.float32)


def hat_voice(open_hat: bool = False) -> np.ndarray:
    length_s = 0.32 if open_hat else 0.105
    n = int(length_s * SR)
    t = np.arange(n, dtype=np.float32) / SR
    noise = highpass(RNG.normal(0, 1, n).astype(np.float32), 6500)
    decay = 0.12 if open_hat else 0.025
    metallic = np.sin(2 * np.pi * 10_700 * t) + 0.5 * np.sin(2 * np.pi * 12_380 * t)
    return (0.18 * noise + 0.025 * metallic) * np.exp(-t / decay)


def wood_voice() -> np.ndarray:
    n = int(0.16 * SR)
    t = np.arange(n, dtype=np.float32) / SR
    x = np.sin(2 * np.pi * 860 * t) + 0.55 * np.sin(2 * np.pi * 1320 * t)
    return (x * np.exp(-t / 0.038) * 0.30).astype(np.float32)


def bass_voice(note: str, length_s: float = 0.55) -> np.ndarray:
    n = int(length_s * SR)
    t = np.arange(n, dtype=np.float32) / SR
    f = hz(note)
    phase = 2 * np.pi * f * t
    x = np.sin(phase) + 0.18 * np.sin(2 * phase) + 0.06 * np.sin(3 * phase)
    a = np.minimum(1.0, t / 0.012)
    r = np.exp(-np.maximum(0.0, t - 0.12) / 0.24)
    return np.tanh(x * a * r * 0.66).astype(np.float32)


def rhodes_note(note: str, length_s: float, velocity: float) -> np.ndarray:
    n = int(length_s * SR)
    t = np.arange(n, dtype=np.float32) / SR
    f = hz(note)
    trem = 1.0 + 0.018 * np.sin(2 * np.pi * 4.8 * t)
    carrier = np.sin(2 * np.pi * f * t * trem + 1.2 * np.exp(-t / 0.20) * np.sin(2 * np.pi * 2 * f * t))
    bell = np.sin(2 * np.pi * 3 * f * t) * np.exp(-t / 0.46) * 0.20
    env = np.minimum(1.0, t / 0.018) * np.exp(-t / max(0.55, length_s * 0.72))
    return ((carrier * 0.72 + bell) * env * velocity).astype(np.float32)


def pad_note(note: str, length_s: float, velocity: float) -> np.ndarray:
    n = int(length_s * SR)
    t = np.arange(n, dtype=np.float32) / SR
    f = hz(note)
    osc = (
        np.sin(2 * np.pi * f * 0.997 * t)
        + np.sin(2 * np.pi * f * 1.003 * t + 0.7)
        + 0.20 * np.sin(2 * np.pi * 2 * f * t + 0.2)
    ) / 2.2
    attack = np.clip(t / 0.55, 0.0, 1.0)
    release = np.clip((length_s - t) / 0.75, 0.0, 1.0)
    return (osc * attack * release * velocity).astype(np.float32)


def duck_envelope(kick_times: list[float], amount: float, release_s: float) -> np.ndarray:
    env = np.ones(N, dtype=np.float32)
    span = int(release_s * SR)
    curve = 1.0 - amount * np.exp(-np.arange(span, dtype=np.float32) / max(1.0, span / 4.4))
    for start_s in kick_times:
        start = int(start_s * SR)
        if start >= N:
            continue
        end = min(N, start + span)
        env[start:end] = np.minimum(env[start:end], curve[: end - start])
    return env


def render_drums() -> tuple[np.ndarray, list[float]]:
    mono = np.zeros(N, dtype=np.float32)
    kicks: list[float] = []
    kick = kick_voice()
    clap = clap_voice()
    wood = wood_voice()
    for bar in range(1, ARRANGEMENT_BARS + 1):
        bar_start = (bar - 1) * BAR
        if not active_drums(bar):
            if 5 <= bar <= 8 and bar % 2 == 0:
                add_mono(mono, bar_start + 3.5 * BEAT, hat_voice(False), 0.08)
            continue
        energy = section_gain(bar)
        for beat in range(4):
            kt = bar_start + beat * BEAT
            kicks.append(kt)
            add_mono(mono, kt, kick, 0.64 * energy)
        for beat in (1, 3):
            add_mono(mono, bar_start + beat * BEAT, clap, 0.34 * energy)
        for half in (0.5, 1.5, 2.5, 3.5):
            swing = 0.028 if int(half * 2) % 4 == 3 else 0.0
            vel = 0.19 if half in (0.5, 2.5) else 0.15
            add_mono(mono, bar_start + half * BEAT + swing, hat_voice(False), vel * energy)
        if bar >= 49 and bar % 2 == 0:
            add_mono(mono, bar_start + 3.5 * BEAT, hat_voice(True), 0.11 * energy)
        if bar >= 25:
            add_mono(mono, bar_start + 1.75 * BEAT + 0.02, wood, 0.16 * energy)
            add_mono(mono, bar_start + 3.25 * BEAT + 0.04, wood, 0.11 * energy)
        if bar in {24, 40, 48, 64, 80, 88}:
            for i in range(6):
                add_mono(mono, bar_start + (2.5 + i * 0.25) * BEAT, clap, 0.10 + i * 0.025)
    return stereo_from_mono(mono, width=0.10, delay_ms=0.35), kicks


def render_bass(kicks: list[float]) -> np.ndarray:
    mono = np.zeros(N, dtype=np.float32)
    for bar in range(1, ARRANGEMENT_BARS + 1):
        if not active_drums(bar):
            continue
        chord = chord_for_bar(bar - 1)
        roots = ROOTS[chord]
        start = (bar - 1) * BAR
        energy = section_gain(bar)
        for off, note, amp in [(0.55, roots[0], 0.68), (2.55, roots[1], 0.48), (3.52, roots[2], 0.37)]:
            add_mono(mono, start + off * BEAT, bass_voice(note), amp * energy)
    mono = lowpass(mono, 210)
    mono *= duck_envelope(kicks, 0.42, 0.18)
    return stereo_from_mono(mono)


def render_rhodes(kicks: list[float]) -> np.ndarray:
    stereo = np.zeros((N, 2), dtype=np.float32)
    for bar in range(1, ARRANGEMENT_BARS + 1):
        chord = chord_for_bar(bar - 1)
        start = (bar - 1) * BAR
        energy = section_gain(bar)
        strikes = [0.12] if bar <= 8 or 65 <= bar <= 72 else [0.12, 2.25]
        if bar in {16, 24, 32, 40, 48, 56, 64, 80, 88, 96}:
            strikes = [0.12]
        for strike in strikes:
            length = 1.65 * BEAT if strike > 1 else 2.8 * BEAT
            for i, note in enumerate(CHORDS[chord]):
                voice = rhodes_note(note, length, 0.18 * energy / (1.0 + i * 0.08))
                pan = (-0.42 + i * 0.28)
                left = math.sqrt((1.0 - pan) / 2.0)
                right = math.sqrt((1.0 + pan) / 2.0)
                idx = int((start + strike * BEAT) * SR)
                end = min(N, idx + len(voice))
                stereo[idx:end, 0] += voice[: end - idx] * left
                stereo[idx:end, 1] += voice[: end - idx] * right
    stereo[:, 0] = lowpass(stereo[:, 0], 6400)
    stereo[:, 1] = lowpass(stereo[:, 1], 6200)
    duck = duck_envelope(kicks, 0.12, 0.15)
    return stereo * duck[:, None]


def render_pad(kicks: list[float]) -> np.ndarray:
    stereo = np.zeros((N, 2), dtype=np.float32)
    for bar in range(1, ARRANGEMENT_BARS + 1):
        chord = chord_for_bar(bar - 1)
        start = (bar - 1) * BAR
        energy = section_gain(bar)
        for i, note in enumerate(CHORDS[chord]):
            voice = pad_note(note, BAR + 0.45, 0.075 * energy)
            pan = (-0.55 + i * 0.36)
            left = math.sqrt((1.0 - pan) / 2.0)
            right = math.sqrt((1.0 + pan) / 2.0)
            idx = int(start * SR)
            end = min(N, idx + len(voice))
            stereo[idx:end, 0] += voice[: end - idx] * left
            stereo[idx:end, 1] += voice[: end - idx] * right
    stereo[:, 0] = lowpass(stereo[:, 0], 3800)
    stereo[:, 1] = lowpass(stereo[:, 1], 4100)
    duck = duck_envelope(kicks, 0.08, 0.22)
    return stereo * duck[:, None]


def saw_wave(frequency: float, t: np.ndarray, phase: float = 0.0) -> np.ndarray:
    return (2.0 * np.mod(frequency * t + phase, 1.0) - 1.0).astype(np.float32)


def serum_pluck_voice(note: str, length_s: float, velocity: float) -> np.ndarray:
    """Original detuned wavetable-style pluck inspired by modern house synthesis."""
    n = int(length_s * SR)
    t = np.arange(n, dtype=np.float32) / SR
    base = hz(note)
    detunes = (-9.0, -5.0, -2.0, 0.0, 2.0, 5.0, 9.0)
    left = np.zeros(n, dtype=np.float32)
    right = np.zeros(n, dtype=np.float32)
    for index, cents in enumerate(detunes):
        frequency = base * 2.0 ** (cents / 1200.0)
        voice = saw_wave(frequency, t, phase=(index * 0.137) % 1.0)
        left += voice * (1.0 if index <= 3 else 0.62)
        right += voice * (1.0 if index >= 3 else 0.62)
    left /= 5.2
    right /= 5.2
    sub = np.sin(2.0 * np.pi * base * t).astype(np.float32) * 0.16
    attack = np.clip(t / 0.012, 0.0, 1.0)
    decay = np.exp(-np.maximum(0.0, t - 0.025) / max(0.28, 0.42 * BEAT))
    release = np.clip((length_s - t) / max(0.18, 0.55 * BEAT), 0.0, 1.0)
    envelope = attack * decay * release
    stereo = np.column_stack([left + sub, right + sub]) * envelope[:, None] * velocity
    stereo[:, 0] = lowpass(stereo[:, 0], 5200)
    stereo[:, 1] = lowpass(stereo[:, 1], 5600)
    return np.tanh(stereo * 1.18).astype(np.float32)


def render_serum_pluck(kicks: list[float]) -> np.ndarray:
    stereo = np.zeros((N, 2), dtype=np.float32)
    for bar in range(1, ARRANGEMENT_BARS + 1):
        if bar <= 8 or 65 <= bar <= 72:
            continue
        chord = chord_for_bar(bar - 1)
        energy = section_gain(bar)
        starts = [0.5, 2.5] if bar >= 49 else ([1.5] if bar % 2 else [0.5, 2.5])
        for start_beat in starts:
            for note_index, note in enumerate(CHORDS[chord]):
                voice = serum_pluck_voice(note, 1.55 * BEAT, 0.034 * energy / (1.0 + note_index * 0.12))
                idx = int(((bar - 1) * BAR + start_beat * BEAT) * SR)
                end = min(N, idx + len(voice))
                stereo[idx:end] += voice[: end - idx]
    stereo[:, 0] = highpass(stereo[:, 0], 190)
    stereo[:, 1] = highpass(stereo[:, 1], 205)
    return stereo * duck_envelope(kicks, 0.24, 0.20)[:, None]


def serum_air_voice(note: str, length_s: float, velocity: float, pan: float) -> np.ndarray:
    n = int(length_s * SR)
    t = np.arange(n, dtype=np.float32) / SR
    base = hz(note)
    detunes = (-12.0, -4.0, 4.0, 12.0)
    cloud = sum(
        saw_wave(base * 2.0 ** (cents / 1200.0), t, phase=(index + 1) * 0.173)
        for index, cents in enumerate(detunes)
    ) / len(detunes)
    shimmer = np.sin(2 * np.pi * base * 2.0 * t + 0.4) * 0.12
    attack = np.clip(t / max(0.45, 0.55 * BEAT), 0.0, 1.0)
    release = np.clip((length_s - t) / max(0.8, 1.15 * BEAT), 0.0, 1.0)
    motion = 0.86 + 0.14 * np.sin(2 * np.pi * 0.11 * t + pan)
    mono = lowpass((cloud + shimmer).astype(np.float32), 3400) * attack * release * motion * velocity
    left = math.sqrt((1.0 - pan) / 2.0)
    right = math.sqrt((1.0 + pan) / 2.0)
    return np.column_stack([mono * left, mono * right]).astype(np.float32)


def render_serum_air_pad(kicks: list[float]) -> np.ndarray:
    stereo = np.zeros((N, 2), dtype=np.float32)
    for bar in range(1, ARRANGEMENT_BARS + 1):
        chord = chord_for_bar(bar - 1)
        energy = section_gain(bar)
        start_s = (bar - 1) * BAR
        for index, note in enumerate(CHORDS[chord]):
            voice = serum_air_voice(note, BAR + 1.6 * BEAT, 0.026 * energy, -0.58 + index * 0.38)
            start = int(start_s * SR)
            end = min(N, start + len(voice))
            stereo[start:end] += voice[: end - start]
    stereo[:, 0] = highpass(stereo[:, 0], 245)
    stereo[:, 1] = highpass(stereo[:, 1], 260)
    return stereo * duck_envelope(kicks, 0.11, 0.28)[:, None]


def serum_reese_voice(note: str, length_s: float, velocity: float) -> np.ndarray:
    n = int(length_s * SR)
    t = np.arange(n, dtype=np.float32) / SR
    base = hz(note)
    a = saw_wave(base * 2.0 ** (-5.0 / 1200.0), t, 0.13)
    b = saw_wave(base * 2.0 ** (5.0 / 1200.0), t, 0.61)
    sub = np.sin(2.0 * np.pi * base * t).astype(np.float32)
    envelope = np.clip(t / 0.025, 0.0, 1.0) * np.clip((length_s - t) / 0.24, 0.0, 1.0)
    mono = lowpass((0.22 * (a + b) + 0.72 * sub).astype(np.float32), 155)
    return np.column_stack([mono, mono]).astype(np.float32) * envelope[:, None] * velocity


def render_serum_reese(kicks: list[float]) -> np.ndarray:
    stereo = np.zeros((N, 2), dtype=np.float32)
    for bar in list(range(49, 65)) + list(range(81, 97)):
        chord = chord_for_bar(bar - 1)
        root = ROOTS[chord][0]
        for start_beat in (0.45, 2.45):
            voice = serum_reese_voice(root, 1.25 * BEAT, 0.12 * section_gain(bar))
            idx = int(((bar - 1) * BAR + start_beat * BEAT) * SR)
            end = min(N, idx + len(voice))
            stereo[idx:end] += voice[: end - idx]
    return stereo * duck_envelope(kicks, 0.48, 0.22)[:, None]


def render_texture() -> np.ndarray:
    noise_l = RNG.normal(0, 1, N).astype(np.float32)
    noise_r = RNG.normal(0, 1, N).astype(np.float32)
    rain_l = highpass(lowpass(noise_l, 9300), 1500) * 0.0032
    rain_r = highpass(lowpass(noise_r, 9700), 1700) * 0.0030
    vinyl = lowpass(RNG.normal(0, 1, N).astype(np.float32), 6500) * 0.0013
    for _ in range(680):
        idx = int(RNG.uniform(0, N - 900))
        length = int(RNG.uniform(80, 700))
        decay = np.exp(-np.arange(length, dtype=np.float32) / max(18.0, length / 5.0))
        amp = RNG.uniform(0.003, 0.018)
        vinyl[idx : idx + length] += decay * amp * RNG.choice([-1.0, 1.0])
    lfo = 0.78 + 0.22 * np.sin(2 * np.pi * np.arange(N, dtype=np.float32) / SR / 19.0)
    stereo = np.column_stack([rain_l + vinyl * lfo, rain_r + vinyl * np.roll(lfo, SR // 3)]).astype(np.float32)
    fade_in = min(N, int(0.5 * BAR * SR))
    fade_out = min(N, int(2.0 * BAR * SR))
    if fade_in > 1:
        stereo[:fade_in] *= np.sin(np.linspace(0.0, math.pi / 2.0, fade_in, dtype=np.float32))[:, None] ** 2
    if fade_out > 1:
        stereo[-fade_out:] *= np.cos(np.linspace(0.0, math.pi / 2.0, fade_out, dtype=np.float32))[:, None] ** 2
    return stereo


def render_fx() -> np.ndarray:
    stereo = np.zeros((N, 2), dtype=np.float32)
    transitions = [9, 17, 25, 33, 41, 49, 57, 65, 73, 81, 85, 89, 93]
    for bar in transitions:
        end_s = (bar - 1) * BAR
        length = min(BAR, end_s)
        pre_n = int(length * SR)
        release_n = int(0.25 * BAR * SR)
        n = pre_n + release_n
        noise = RNG.normal(0, 1, n).astype(np.float32)
        bright = highpass(noise, 2500)
        rise = np.linspace(0.0, 1.0, pre_n, dtype=np.float32) ** 2.2
        release = np.exp(-np.arange(release_n, dtype=np.float32) / max(1.0, release_n / 4.8))
        env = np.concatenate([rise, release])
        riser = bright * env * 0.017
        start = int((end_s - length) * SR)
        write_end = min(N, start + n)
        stereo[start:write_end, 0] += riser[: write_end - start]
        stereo[start:write_end, 1] += np.roll(riser, 97)[: write_end - start]
        if bar not in {17, 33, 65, 85, 89, 93}:
            drop_n = int(0.85 * SR)
            dt = np.arange(drop_n, dtype=np.float32) / SR
            drop = np.sin(2 * np.pi * (56 - 19 * dt) * dt) * np.exp(-dt / 0.24) * 0.11
            idx = int(end_s * SR)
            end = min(N, idx + drop_n)
            stereo[idx:end, 0] += drop[: end - idx]
            stereo[idx:end, 1] += drop[: end - idx]
    return stereo


def peak_db(x: np.ndarray) -> float:
    return 20.0 * math.log10(max(1e-12, float(np.max(np.abs(x)))))


def write_audio(path: Path, data: np.ndarray) -> dict[str, float | str]:
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(path, data, SR, subtype="PCM_24")
    return {"path": path.name, "peak_dbfs": round(peak_db(data), 3)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--bpm", type=float, default=105.0)
    parser.add_argument("--rich-serum-tones", action="store_true")
    args = parser.parse_args()
    configure_tempo(args.bpm)
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)

    manifest: dict[str, object] = {
        "title": "Jhol x Pal Pal original lofi deep-house instrumental",
        "tempo_bpm": BPM,
        "time_signature": "4/4",
        "arrangement_bars": ARRANGEMENT_BARS,
        "tail_bars": TAIL_BARS,
        "duration_seconds": TOTAL_SECONDS,
        "key_plan": "F minor; bars 65-72 move to D minor for the native-pitch Jhol breakdown",
        "source_policy": "100% synthesized locally; no source-song instrumental, melody, loop, or rhythm used",
        "stems": [],
    }

    mix = np.zeros((N, 2), dtype=np.float32)
    drums, kicks = render_drums()
    stem_specs = [
        ("01-original-drums.wav", drums, 0.90),
        ("02-original-bass.wav", render_bass(kicks), 0.74),
        ("03-original-rhodes.wav", render_rhodes(kicks), 0.82),
        ("04-original-pad.wav", render_pad(kicks), 0.86),
        ("05-original-texture.wav", render_texture(), 1.00),
        ("06-original-fx.wav", render_fx(), 0.90),
    ]
    if args.rich_serum_tones:
        stem_specs.extend(
            [
                ("07-serum-style-pluck.wav", render_serum_pluck(kicks), 4.10),
                ("08-serum-style-air-pad.wav", render_serum_air_pad(kicks), 1.90),
                ("09-serum-style-reese.wav", render_serum_reese(kicks), 1.40),
            ]
        )
    for name, data, gain in stem_specs:
        data = np.tanh(data * 1.08).astype(np.float32) * gain
        manifest["stems"].append(write_audio(out / name, data))
        mix += data

    peak = float(np.max(np.abs(mix)))
    target = 10 ** (-8.0 / 20.0)
    if peak > 0:
        mix *= target / peak
    mix = np.tanh(mix * 1.015).astype(np.float32)
    reference_name = "10-original-instrumental-reference.wav" if args.rich_serum_tones else "07-original-instrumental-reference.wav"
    manifest["instrumental_reference"] = write_audio(out / reference_name, mix)

    sections = [
        (1, 8, "Jhol intro lead", "Fm", "2/10"),
        (9, 16, "Pal Pal hook", "Fm", "4/10"),
        (17, 24, "Jhol setup", "Fm", "4/10"),
        (25, 32, "Pal Pal verse", "Fm", "5/10"),
        (33, 40, "Jhol payoff", "Fm", "5/10"),
        (41, 48, "Pal Pal lift", "Fm", "6/10"),
        (49, 56, "Jhol first drop", "Fm", "7/10"),
        (57, 64, "Pal Pal answer drop", "Fm", "7/10"),
        (65, 72, "Jhol native-key breakdown", "Dm", "3/10"),
        (73, 80, "Pal Pal re-entry", "Fm", "5/10"),
        (81, 84, "Jhol final trade A", "Fm", "8/10"),
        (85, 88, "Pal Pal final trade A", "Fm", "8/10"),
        (89, 92, "Jhol final trade B", "Fm", "6/10"),
        (93, 96, "Pal Pal resolution", "Fm", "4/10"),
    ]
    with (out / "v3-original-instrumental-arrangement-map.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["start_bar", "end_bar", "vocal_lead", "key_center", "energy"])
        writer.writerows(sections)
    (out / "v3-original-instrumental-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
