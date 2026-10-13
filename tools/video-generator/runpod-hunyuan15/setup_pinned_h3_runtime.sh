#!/usr/bin/env bash
set -euo pipefail
# Reproduce the reviewed runtime without advancing the ComfyUI revision.
runtime_root=/workspace/urvashi-h3
comfy_root=/workspace/ComfyUI-H3
mkdir -p "$runtime_root/anchors-v5"
apt-get update -qq
apt-get install -y -qq ffmpeg git python3-venv
if [[ ! -d "$comfy_root/.git" ]]; then
  git clone --filter=blob:none https://github.com/comfyanonymous/ComfyUI.git "$comfy_root"
fi
git -C "$comfy_root" checkout --detach e638023d54497dbe0579565e5de4bb7076899592
python3 -m venv "$runtime_root/venv"
"$runtime_root/venv/bin/python" -m pip install --no-cache-dir torch==2.10.0 torchvision==0.25.0 torchaudio==2.10.0 --index-url https://download.pytorch.org/whl/cu130
"$runtime_root/venv/bin/python" -m pip install --no-cache-dir -r "$comfy_root/requirements.txt"
"$runtime_root/venv/bin/python" -c 'import torch; print(torch.__version__, torch.version.cuda, torch.cuda.get_device_name())'
