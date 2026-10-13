#!/bin/zsh
set -euo pipefail

workspace='/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/nuvvantene-istam-deep-house/music-video/rebuild-r10-neon-space'
out="$workspace/renders/r11-overlays/r11-orbital-space-field-540p-v2.mp4"
mkdir -p "${out:h}"

# The field is a deterministic polar tunnel. T is the video clock, and the
# pulse term repeats on the measured 127.011 BPM period. Black remains black
# so Resolve can use Screen composite without hiding the protected figure.
filter="nullsrc=s=480x270:r=24:d=221.625,format=rgb24,geq=r='255*(0.02+0.70*if(lt(abs(sin(atan2(Y-135,X-240)*10+hypot(X-240,Y-135)*0.065-T*2)),0.07),0.35+0.65*pow(max(0,cos(2*PI*T/0.4724)),4),0)+0.55*if(lt(abs(sin(hypot(X-240,Y-135)*0.11-T*1.5)),0.05),0.25+0.75*pow(max(0,cos(2*PI*T/0.4724)),4),0)+0.9*if(lt(abs(sin(hypot(X-240,Y-135)*0.21+T*2.2)),0.035),0.25+0.75*pow(max(0,cos(2*PI*T/0.4724)),4),0))':g='255*(0.08+0.85*if(lt(abs(sin(atan2(Y-135,X-240)*10+hypot(X-240,Y-135)*0.065-T*2)),0.07),0.45+0.55*pow(max(0,cos(2*PI*T/0.4724)),4),0)+0.3*if(lt(abs(sin(hypot(X-240,Y-135)*0.11-T*1.5)),0.05),0.25+0.75*pow(max(0,cos(2*PI*T/0.4724)),4),0))':b='255*(0.12+1.0*if(lt(abs(sin(atan2(Y-135,X-240)*10+hypot(X-240,Y-135)*0.065-T*2)),0.07),0.55+0.45*pow(max(0,cos(2*PI*T/0.4724)),4),0)+0.18*if(lt(abs(sin(hypot(X-240,Y-135)*0.11-T*1.5)),0.05),0.25+0.75*pow(max(0,cos(2*PI*T/0.4724)),4),0))'"

ffmpeg -hide_banner -y -f lavfi -i "$filter" \
  -frames:v 5319 -c:v libx264 -preset ultrafast -crf 21 -pix_fmt yuv420p \
  -movflags +faststart "$out"

ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,nb_frames,duration \
  -of json "$out" > "$workspace/analysis/r11-space-overlay-probe.json"
echo "$out"
