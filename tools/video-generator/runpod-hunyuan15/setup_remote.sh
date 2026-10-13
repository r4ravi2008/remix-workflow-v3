#!/usr/bin/env bash
set -euo pipefail

ROOT=/workspace/urvashi-hunyuan15
COMFY="$ROOT/ComfyUI"
PYTHON=/workspace/runpod-slim/ComfyUI/.venv-cu128/bin/python
PIP=/workspace/runpod-slim/ComfyUI/.venv-cu128/bin/pip
LOG="$ROOT/setup.log"
STAGE=${1:-full}

mkdir -p "$ROOT"
exec > >(tee -a "$LOG") 2>&1

pkill -f '/workspace/runpod-slim/ComfyUI/main.py' 2>/dev/null || true

if [[ ! -d "$COMFY/.git" ]]; then
  git clone --depth 1 https://github.com/comfyanonymous/ComfyUI.git "$COMFY"
fi

"$PIP" install -r "$COMFY/requirements.txt"
if ! command -v aria2c >/dev/null; then
  apt-get update -qq
  apt-get install -y -qq aria2
fi

mkdir -p \
  "$COMFY/models/clip_vision" \
  "$COMFY/models/diffusion_models" \
  "$COMFY/models/latent_upscale_models" \
  "$COMFY/models/text_encoders" \
  "$COMFY/models/vae" \
  "$COMFY/input" \
  "$COMFY/output"

BASE=https://huggingface.co/Comfy-Org/HunyuanVideo_1.5_repackaged/resolve/main/split_files

download() {
  local source_url=$1
  local destination=$2
  local expected_bytes=$3
  local actual_bytes=0
  if [[ -f "$destination" ]]; then
    actual_bytes=$(stat -c %s "$destination")
  fi
  if [[ "$actual_bytes" == "$expected_bytes" && ! -f "$destination.aria2" ]]; then
    echo "present $destination ($actual_bytes bytes)"
    return
  fi
  aria2c --continue=true --allow-overwrite=true --auto-file-renaming=false --console-log-level=warn \
    --file-allocation=none --max-connection-per-server=16 --min-split-size=1M \
    --split=16 --dir="$(dirname "$destination")" --out="$(basename "$destination")" \
    "$source_url"
  actual_bytes=$(stat -c %s "$destination")
  [[ "$actual_bytes" == "$expected_bytes" ]]
}

download "$BASE/diffusion_models/hunyuanvideo1.5_720p_i2v_fp16.safetensors" \
  "$COMFY/models/diffusion_models/hunyuanvideo1.5_720p_i2v_fp16.safetensors" 16653368128
download "$BASE/text_encoders/qwen_2.5_vl_7b.safetensors" \
  "$COMFY/models/text_encoders/qwen_2.5_vl_7b.safetensors" 16584415576
download "$BASE/text_encoders/byt5_small_glyphxl_fp16.safetensors" \
  "$COMFY/models/text_encoders/byt5_small_glyphxl_fp16.safetensors" 438643184
download "$BASE/clip_vision/sigclip_vision_patch14_384.safetensors" \
  "$COMFY/models/clip_vision/sigclip_vision_patch14_384.safetensors" 856505640
download "$BASE/vae/hunyuanvideo15_vae_fp16.safetensors" \
  "$COMFY/models/vae/hunyuanvideo15_vae_fp16.safetensors" 2521292758
if [[ "$STAGE" != base ]]; then
  download "$BASE/diffusion_models/hunyuanvideo1.5_1080p_sr_distilled_fp16.safetensors" \
    "$COMFY/models/diffusion_models/hunyuanvideo1.5_1080p_sr_distilled_fp16.safetensors" 16662949080
  download "$BASE/latent_upscale_models/hunyuanvideo15_latent_upsampler_1080p.safetensors" \
    "$COMFY/models/latent_upscale_models/hunyuanvideo15_latent_upsampler_1080p.safetensors" 201404760
fi

"$PYTHON" - <<'PY'
import torch
print("torch", torch.__version__, "cuda", torch.version.cuda, "gpu", torch.cuda.get_device_name())
PY

touch "$ROOT/READY"
echo ready
