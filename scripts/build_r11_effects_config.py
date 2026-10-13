#!/usr/bin/env python3
import json
from pathlib import Path

P = Path(
    "/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/"
    "nuvvantene-istam-deep-house/music-video/rebuild-r10-neon-space"
)

config = {
    "schema_version": 1,
    "revision": "R11-orbital-pulse",
    "direction": "Minimal abstract space travel around an Indian-inspired Bharatanatyam silhouette.",
    "canonical_audio": {
        "path": "audio-remaster/renders/nuvvantene-istam-neon-remaster-r05-24bit.wav",
        "sha256": "9769452de248e4c05029f678fe3eac2d0ae0134161e7636356af641379e9396c",
        "bpm": 127.01100762066172,
        "fps": 24,
    },
    "framing": {
        "canvas": [1920, 1080],
        "timeline_frames": 5319,
        "intentional_character": "Indian-inspired silhouette in Bharatanatyam-style stitched sari, pleated fan, waist belt, ankle bells, and low bun",
        "camera_language": "forward depth travel, orbit expansion, radial stretch, and controlled return",
    },
    "palette": {
        "void": "#050914",
        "navy": "#071B33",
        "cyan": "#00D9FF",
        "crimson": "#E51C46",
        "rule": "crimson remains the emotional anchor; cyan carries geometry and transliterated lyrics",
    },
    "resolve_fusion": {
        "owner": "DaVinci Resolve Fusion",
        "nodes": ["FastNoise", "Glow", "Merge"],
        "composite": "Screen",
        "purpose": "animated depth field behind the protected figure and lyric layers",
        "reactivity": "FastNoise seethe, contrast, and screen blend are keyed at measured phrase and bar accents",
        "protected_layers": ["Bharatanatyam silhouette", "crimson fan", "transliterated lyrics"],
        "3d_language": "depth is authored through scale, seethe, glow falloff, orbit geometry, and forward field movement; no unsupported 3D node is allowed into the final render",
    },
    "beat_reactivity": {
        "grid_source": "analysis/beat-map.json",
        "grid_bpm": 127.01100762066172,
        "hierarchy": ["section", "phrase", "bar", "accent"],
        "quiet_alpha": 0.045,
        "phrase_alpha": 0.11,
        "peak_alpha": 0.18,
        "note": "The background moves with the song while the character remains readable.",
    },
    "transitions": [
        {"name": "orbit trace handoff", "usage": "character enters or exits a shot through the shared cyan orbit"},
        {"name": "depth dissolve", "usage": "navy field carries the viewer between shot families"},
        {"name": "radial stretch", "usage": "phrase arrival and acceleration"},
        {"name": "crimson point wipe", "usage": "emotional lyric entry and return"},
        {"name": "measured hard cut", "usage": "chapter change only"},
    ],
    "review": {
        "anchor_interval_frames": 57,
        "anchor_interval_seconds": 2.375,
        "requirements": ["frame-inspect all anchor pages", "decode full MOV and MP4", "verify canonical audio in PCM MOV", "normal-speed watch and hear before creative acceptance"],
        "current_status": "planned; the final WATCHED and HEARD gates remain open until playback review",
    },
}
(P / "analysis/r11-effects-config.json").write_text(json.dumps(config, indent=2) + "\n")
print(json.dumps({"path": str(P / 'analysis/r11-effects-config.json'), "revision": config['revision']}))
