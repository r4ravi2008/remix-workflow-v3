#!/usr/bin/env bash
set -euo pipefail
root=/workspace/ComfyUI-H3
apt-get update -qq
apt-get install -y -qq aria2 ffmpeg
if [[ ! -d "$root/.git" ]]; then
  git clone --depth 1 https://github.com/comfyanonymous/ComfyUI.git "$root"
fi
python -m venv --system-site-packages /workspace/urvashi-h3/venv
/workspace/urvashi-h3/venv/bin/python -m pip install -r "$root/requirements.txt"
bash /workspace/urvashi-h3/download_h3.sh
/workspace/urvashi-h3/venv/bin/python "$root/main.py" --listen 127.0.0.1 --port 8189 --disable-auto-launch
