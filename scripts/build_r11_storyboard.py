#!/usr/bin/env python3
"""Create the auditable R11 storyboard, anchor map, and lyric treatment."""

from __future__ import annotations

import json
from pathlib import Path

WORKSPACE = Path(
    "/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/"
    "nuvvantene-istam-deep-house/music-video/rebuild-r10-neon-space"
)


def read(name: str):
    return json.loads((WORKSPACE / name).read_text())


def phase_for(seconds: float) -> tuple[str, str, str]:
    if seconds < 20:
        return ("emergence", "A point wakes inside a quiet star field.", "sparse")
    if seconds < 80:
        return ("ascent", "The Bharatanatyam silhouette opens the first orbit.", "pulse")
    if seconds < 145:
        return ("traversal", "The orbit becomes a depth tunnel around the dancer.", "dense")
    if seconds < 200:
        return ("acceleration", "Every phrase pushes the tunnel farther into space.", "peak")
    return ("return", "The tunnel contracts into the crimson fan and settles.", "release")


def transliterations(cues):
    lines = {
        "L01": ["Nuvvante ne ishtam", "Nuvvu kaadante ne kashtam"],
        "L02": ["Nuvvante ne ishtam", "Nuvvu kaadante ne kashtam"],
        "L03": ["Em cheyamantaavo", "Priyathamaa"],
        "L04": ["Ee nele ningainaa", "Aakaasham nelainaa"],
        "L05": ["Aa rendunu lekunn aa"],
        "L06": ["Nuvvante ne ishtam", "Nuvvu kaadante ne kashtam"],
        "L07": ["Rampam tone vaddu", "Nee roopamto koseyi"],
        "L08": ["Sudigundamlo vaddu", "Nee odilo nanne", "Niluvunaa muncheyi"],
        "L09": ["Nippulutone vaddu", "Kanuchoopulato", "Kaalcheyi"],
        "L10": ["Uritaa dasale vaddu", "Nee vaalu jadatone", "Naa oopiri teeyi"],
        "L11": ["Nuvvante ne ishtam", "Nuvvu kaadante ne kashtam"],
        "L12": ["Paataalaaniki vaddu", "E narakaaniki pampoddu"],
        "L13": ["Nee gundela guhalo nannu", "Tega himsincheyi", "Ante chooseyi"],
        "L14": ["Kaaraagaaram vaddu", "E cherasaalaku pampoddu"],
        "L15": ["Nee kougililone nannu", "Nuvvu bandhincheyi", "Nannu antam cheyi"],
        "L16": ["Vela saarlu ne janmistaa"],
        "L17": ["Vela saarlu ne maranistaa"],
        "L18": ["Okkasaari nuvvu premiste"],
        "L19": ["Chaavu leka ne bratikestaa"],
        "L20": ["Nuvvante ne ishtam", "Nuvvu kaadante ne kashtam"],
        "L21": ["Nuvvante ne ishtam", "Nuvvu kaadante ne kashtam"],
        "L22": ["Em cheyamantaavo", "Priyathamaa"],
    }
    result = []
    for cue in cues:
        result.append(
            {
                "id": cue["id"],
                "start_time": cue["start_time"],
                "end_time": cue["end_time"],
                "source_native_script": cue["display_text"],
                "transliteration": "\n".join(lines[cue["id"]]),
                "language": "Telugu transliterated in Latin script",
                "status": "provisional editorial transliteration; canonical Telugu remains unchanged",
                "style": "thin electric-cyan caps, crimson cursor on phrase entry",
            }
        )
    return result


def main():
    screenplay = read("screenplay.json")
    beat_map = read("analysis/beat-map.json")
    lyrics = read("lyrics.json")
    shots = []
    for index, shot in enumerate(screenplay["shots"], start=1):
        start_seconds = shot["start"] / screenplay["fps"]
        phase, story, reactivity = phase_for(start_seconds)
        shots.append(
            {
                "id": shot["id"],
                "sequence": index,
                "start_frame": shot["start"],
                "end_frame": shot["end"],
                "start_seconds": round(start_seconds, 6),
                "end_seconds": round(shot["end"] / screenplay["fps"], 6),
                "phase": phase,
                "story_beat": story,
                "original_action": shot["action"],
                "anchor": shot.get("anchor"),
                "space_direction": "camera travels forward through cyan orbit depth; crimson fan remains the identity anchor",
                "reactivity": reactivity,
                "beat_strategy": "phrase or bar accent; no one-effect-per-beat cutting",
                "transition": [
                    "orbit trace",
                    "depth dissolve",
                    "radial stretch",
                    "crimson point handoff",
                ][(index - 1) % 4],
                "lyric_mode": "transliterated English where a canonical cue overlaps; otherwise no lyric card",
                "palette": ["#050914", "#00D9FF", "#E51C46"],
                "status": "planned for R11 Resolve replacement pass",
            }
        )

    anchors = []
    interval = 57  # 2.375 seconds at 24 fps, inside the requested 2–3 second window.
    total_frames = screenplay["canonical_frames"]
    for frame in list(range(0, total_frames, interval)) + [total_frames - 1]:
        beat = min(beat_map["beats"], key=lambda b: abs(b["frame"] - frame))
        shot = next(s for s in shots if s["start_frame"] <= frame < s["end_frame"])
        anchors.append(
            {
                "frame": frame,
                "seconds": round(frame / screenplay["fps"], 6),
                "shot_id": shot["id"],
                "phase": shot["phase"],
                "nearest_measured_pulse_frame": beat["frame"],
                "pulse_offset_frames": frame - beat["frame"],
                "visual_check": "figure silhouette, orbit depth, lyric legibility, and transition continuity",
                "review_status": "planned; verify from rendered frame evidence",
            }
        )

    translit = transliterations(lyrics["cues"])
    (WORKSPACE / "analysis/r11-anchor-map.json").write_text(
        json.dumps(
            {
                "revision": "R11-orbital-pulse",
                "fps": screenplay["fps"],
                "interval_frames": interval,
                "interval_seconds": interval / screenplay["fps"],
                "anchor_count": len(anchors),
                "audio_sha256": beat_map["audio_sha256"],
                "anchors": anchors,
            },
            indent=2,
        )
        + "\n"
    )
    (WORKSPACE / "analysis/r11-storyboard.json").write_text(
        json.dumps(
            {
                "revision": "R11-orbital-pulse",
                "title": "ORBITAL PULSE",
                "logline": "An Indian-inspired Bharatanatyam silhouette crosses a sparse star void, turns an orbit into a tunnel, and returns with the crimson fan intact.",
                "visual_rules": [
                    "black and deep-space navy carry the void",
                    "electric cyan draws geometry and lyric text",
                    "crimson marks the dancer and every emotional arrival",
                    "background shader motion reacts in phrases and bars",
                    "the silhouette and lyric layer stay readable during peaks",
                ],
                "chapters": [
                    {"id": "C1", "range": [0, 20], "name": "emergence", "purpose": "establish the dancer as a signal"},
                    {"id": "C2", "range": [20, 80], "name": "ascent", "purpose": "open the first orbit with the first lyric phrases"},
                    {"id": "C3", "range": [80, 145], "name": "traversal", "purpose": "turn the orbit into spatial travel"},
                    {"id": "C4", "range": [145, 200], "name": "acceleration", "purpose": "increase density and pulse without hiding the costume"},
                    {"id": "C5", "range": [200, 221.625], "name": "return", "purpose": "collapse the tunnel into the crimson fan"},
                ],
                "transition_palette": [
                    "orbit trace handoff",
                    "depth dissolve through navy",
                    "radial stretch on phrase arrivals",
                    "crimson point wipe",
                    "measured hard cut at section changes",
                ],
                "shots": shots,
                "anchor_policy": "every 57 frames, with the final frame added explicitly",
                "status": "storyboard and anchor map generated before final R11 render",
            },
            indent=2,
        )
        + "\n"
    )
    (WORKSPACE / "analysis/lyrics-transliteration-r11.json").write_text(
        json.dumps(
            {
                "revision": "R11-orbital-pulse",
                "source": "lyrics.json",
                "canonical_audio_sha256": beat_map["audio_sha256"],
                "note": "This is a display treatment. It does not replace the native Telugu source.",
                "cues": translit,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n"
    )
    (WORKSPACE / "R11-STORYBOARD.md").write_text(
        "# ORBITAL PULSE — R11 storyboard\n\n"
        "A minimal space film for the R05 canonical master. The dancer keeps the Indian-inspired Bharatanatyam silhouette, stitched sari fan, waist belt, ankle bells, and low bun.\n\n"
        "The story moves through five chapters: emergence, ascent, traversal, acceleration, and return. A measured 127.011 BPM grid drives phrase-level shader pulses. The anchor map checks the story every 57 frames (2.375 seconds).\n\n"
        "The lyric layer uses a provisional Latin transliteration for readability. The native Telugu cue file remains canonical and unchanged.\n\n"
        f"Shots: {len(shots)}\nAnchors: {len(anchors)}\nAudio SHA-256: {beat_map['audio_sha256']}\n"
    )


if __name__ == "__main__":
    main()
