#!/usr/bin/env python3
"""Generate a beat-synchronous radial depth pulse for the R12 space film."""
from pathlib import Path
import subprocess

WORKSPACE = Path("/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/nuvvantene-istam-deep-house/music-video/rebuild-r10-neon-space")
OUT = WORKSPACE / "renders" / "r12-overlays" / "r12-beat-depth-pulse-540p-v1.mp4"
PROBE = WORKSPACE / "analysis" / "r12-beat-depth-pulse-probe-v1.json"
FPS = 24
FRAMES = 5319

def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    PROBE.parent.mkdir(parents=True, exist_ok=True)
    # Measured beat grid: 127.011 BPM, 0.4724 s period, 0.243871569 s origin.
    pulse = "exp(-mod(T-0.243871569+0.4724\\,0.4724)/0.06)"
    phase = "mod(T-0.243871569+0.4724\\,0.4724)/0.4724"
    radius = "hypot(X-W/2\\,Y-H/2)"
    ring_near = f"exp(-abs({radius}-(42+470*({phase})))/4)"
    ring_far = f"exp(-abs({radius}-(90+350*({phase})))/6)"
    ray = f"(0.5+0.5*sin(0.04*({radius})-6*({phase})+0.015*X))*({pulse})"
    r = f"2+35*({pulse})*({ring_near})"
    g = f"4+210*({pulse})*({ring_near})+145*({pulse})*({ring_far})+9*({ray})"
    b = f"8+245*({pulse})*({ring_near})+55*({pulse})*({ring_far})+12*({ray})"
    graph = f"geq=r='{r}':g='{g}':b='{b}',format=yuv420p[out]"
    subprocess.run([
        "ffmpeg","-hide_banner","-y",
        "-f","lavfi","-i","color=c=black:s=960x540:r=24:d=221.625",
        "-filter_complex",graph,
        "-map","[out]","-frames:v",str(FRAMES),
        "-c:v","libx264","-preset","veryfast","-crf","18","-pix_fmt","yuv420p",
        "-movflags","+faststart",str(OUT)
    ],check=True)
    subprocess.run([
        "ffprobe","-v","error","-select_streams","v:0",
        "-show_entries","stream=width,height,r_frame_rate,nb_frames,duration",
        "-of","json",str(OUT)
    ],check=True,stdout=PROBE.open("w"))
    print(OUT)

if __name__ == "__main__":
    main()

