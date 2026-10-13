#!/usr/bin/env python3
"""Create a minimal Telugu temple-mandala overlay for the R12 Resolve pass."""

from __future__ import annotations

import math
import pathlib
import subprocess


WORKSPACE = pathlib.Path(
    "/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/"
    "ai-music/workspaces/nuvvantene-istam-deep-house/music-video/rebuild-r10-neon-space"
)
TMP = WORKSPACE / "analysis" / "r12-telugu-mandala-motif.png"
OUT_DIR = WORKSPACE / "renders" / "r12-overlays"
OUT = OUT_DIR / "r12-telugu-mandala-540p-v4.mp4"
PROBE = WORKSPACE / "analysis" / "r12-telugu-mandala-overlay-probe.json"


def main() -> None:
    TMP.parent.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Use ImageMagick primitives because the workstation's SVG delegate does
    # not reliably preserve thin strokes on transparent canvases.
    draw = ["magick", "-size", "900x900", "xc:none"]
    for r, c in [(110, "#C9A64E"), (180, "#8D7538"), (258, "#8D7538"), (345, "#00D9FF"), (410, "#8D7538")]:
        draw += ["-stroke", c, "-strokewidth", "5", "-fill", "none", "-draw", f"circle 450,450 450,{450-r}"]
    draw += ["-stroke", "#C9A64E", "-strokewidth", "5", "-fill", "none"]
    for points in ["280,720 450,600 620,720", "350,720 450,550 550,720", "410,720 450,500 490,720", "280,738 620,738"]:
        draw += ["-draw", f"polyline {points}"]
    for angle in range(0, 360, 45):
        th = math.radians(angle)
        x = 450 + int(280 * math.sin(th))
        y = 450 - int(280 * math.cos(th))
        draw += ["-draw", f"line 450,450 {x},{y}"]
    draw += ["-stroke", "none", "-fill", "#C9A64E"]
    for x in [380, 420, 460, 500, 540]:
        draw += ["-draw", f"circle {x},698 {x+7},698"]
    draw += ["-fill", "#E51C46"]
    for x, y in [(750, 560), (180, 270), (360, 145)]:
        draw += ["-draw", f"circle {x},{y} {x+9},{y}"]
    draw += ["-fill", "#00D9FF", "-draw", "circle 450,450 457,450", "-define", "png:color-type=6", str(TMP)]
    subprocess.run(draw, check=True)

    # The pulse period is the measured 127.011 BPM beat period (0.4724 s).
    # The ring uses an 80 ms downbeat decay; the mandala twists at each 2.375 s anchor.
    # Screen compositing in Resolve keeps the black field transparent to the film.
    filter_graph = (
        "[0:v]scale=420:420:flags=lanczos,"
        "rotate='0.018*t+0.22*floor(t/2.375)':"
        "ow=rotw(iw):oh=roth(ih):fillcolor=black@0,"
        "format=rgba,"
        "colorchannelmixer=aa=0.32,"
        "eq=brightness='0.02+0.30*exp(-mod(t-0.243871569+0.4724,0.4724)/0.08)':"
        "contrast='1+0.85*exp(-mod(t-0.243871569+0.4724,0.4724)/0.08)':eval=frame[motif];"
        "color=c=black:s=480x270:r=24:d=221.625[bg];"
        "color=c=black@0:s=480x270:r=24:d=221.625,format=rgba,"
        "geq=r='201':g='166':b='78':"
        "a='255*(0.03+0.78*exp(-mod(N/24-0.243871569+0.4724,0.4724)/0.08))*"
        "exp(-abs(hypot(X-W/2,Y-H/2)-125)/3)'[pulse];"
        "[bg][motif]overlay=x='(W-w)/2':y='(H-h)/2':shortest=1[base];"
        "[base][pulse]overlay=shortest=1,"
        "format=yuv420p[out]"
    )
    subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-y",
            "-loop",
            "1",
            "-framerate",
            "24",
            "-i",
            str(TMP),
            "-filter_complex",
            filter_graph,
            "-map",
            "[out]",
            "-frames:v",
            "5319",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "19",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(OUT),
        ],
        check=True,
    )
    subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height,r_frame_rate,nb_frames,duration",
            "-of",
            "json",
            str(OUT),
        ],
        check=True,
        stdout=PROBE.open("w"),
    )
    print(OUT)


if __name__ == "__main__":
    main()
