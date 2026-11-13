#!/usr/bin/env bash
# Build the local ComfyUI stack for LTX-2.5 motion and FLUX.2 [klein] stills on a NixOS GPU workstation.
# Proven 2026-11-12 on an RTX 4070 Ti 12 GB / 128 GB RAM host. Re-check Nix store paths, tags and hashes before reuse.
# Usage: comfyui_ltx_setup.sh install|nixroots|models|verify|serve   (run in a named Herdr terminal on the host)
# Separate project root; does not touch ~/projects/video-generation.
set -euo pipefail

ROOT="${COMFY_LTX_ROOT:-$HOME/projects/comfyui-ltx}"
COMFY="$ROOT/ComfyUI"
VENV="$ROOT/.venv"
MODELS="$COMFY/models"
LOG="$ROOT/logs"
COMFY_TAG=v0.45.0
GGUF_COMMIT=6ea2651e7df66d7585f6ffee804b20e92fb38b8a
TORCH_INDEX=https://download.pytorch.org/whl/cu130

# Same Nix interpreter/runtime libraries proven by ~/projects/video-generation.
export UV_PYTHON=/nix/store/7xyci35ybc45yr9dz8iajk24pxcqx37x-python3-3.12.14/bin/python3.12
export UV=/nix/store/zvdbpcaqqjmnzs2dpmgsszg3hh229cbp-uv-0.11.21/bin/uv
export UV_CACHE_DIR="$ROOT/cache/uv"
export UV_PYTHON_DOWNLOADS=never
export LD_LIBRARY_PATH=/run/opengl-driver/lib:/nix/store/2ga5nd1m56n5cx2wh8vbf6nrdhqk2f0q-gcc-15.3.0-lib/lib:/nix/store/hl2rmyygyyfzfmhw3ms08xhj07pqglzi-zlib-1.3.2/lib
export PATH="$VENV/bin:/nix/store/wbskc2agldpv2q9sqx7nqi57n201vzqy-ffmpeg-headless-8.1.2-bin/bin:$PATH"
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1
export HF_HUB_CACHE="$ROOT/cache/hf" HF_HUB_DISABLE_TELEMETRY=1
unset PYTHONPATH LD_PRELOAD

# repo|revision|remote path|local subdir|bytes|sha256
MANIFEST=$(cat <<'EOF'
unsloth/LTX-2.5-GGUF|ac3c540c6025903784336e99b2dc179385c4c3b7|distilled/ltx-2.5-22b-distilled-UD-Q3_K_XL.gguf|unet|12000207232|252fef358340eba8d8a0427641b56e1d034ad1f4f8c307a507b7b265a0f8ff22
comfyicu/LTX-2.5|1026e00f808dbd9601911479b22d65b760737dc8|text_encoders/gemma4-12b-with-proj-ltx-2.5-comfy-int8-convrot.safetensors|text_encoders|15372971786|09a89e084de1a149c3de60cfe9dfd3e5161967eb09eea39e806fcdeffdd568de
unsloth/LTX-2.5-GGUF|ac3c540c6025903784336e99b2dc179385c4c3b7|vae/ltx-2.5-video-vae-conv-bf16.safetensors|vae|1452269922|685b06ee3d9b2039647698fc4ea33175112462fc374e2777312c907897dfce8d
unsloth/LTX-2.5-GGUF|ac3c540c6025903784336e99b2dc179385c4c3b7|vae/ltx-2.5-audio-vae-bf16.safetensors|vae|364866540|c52733d37f6a7fb7949c3dc0fb468c6cb2169e4d836983a73babb9f0d54837a5
Comfy-Org/Flux-2-Klein-4B|5b3abca5c0dc1ecd4eaf3340868d09063fc1c965|split_files/diffusion_models/flux-2-klein-4b.safetensors|diffusion_models|7751105712|ec3d4e733a771f61c052fb4856c48b336c55eaf2c65487c2a1faeb9bbda7a343
Comfy-Org/Flux-2-Klein-4B|5b3abca5c0dc1ecd4eaf3340868d09063fc1c965|split_files/text_encoders/qwen_3_4b.safetensors|text_encoders|8044982048|6c671498573ac2f7a5501502ccce8d2b08ea6ca2f661c458e708f36b36edfc5a
Comfy-Org/Flux-2-Klein-4B|5b3abca5c0dc1ecd4eaf3340868d09063fc1c965|split_files/vae/flux2-vae.safetensors|vae|336211292|868fe7b343cc8f3a19dbcfcafbc3d5f888802be3f89bd81b65b3621a066ce8f3
unsloth/Qwen-Image-Edit-2511-GGUF|52838251db242ddd8e8d0118de36c71006d7c397|qwen-image-edit-2511-Q5_K_M.gguf|unet|15395662432|7e5bf7f00b5e219a855641e7a10d5a8b2668423409718e92dfddd6542828f9b6
Comfy-Org/Qwen-Image_ComfyUI|1f12b17be14c89b026c51a91d67c32f84bb047bc|split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors|text_encoders|9384670680|cb5636d852a0ea6a9075ab1bef496c0db7aef13c02350571e388aea959c5c0b4
Comfy-Org/Qwen-Image_ComfyUI|1f12b17be14c89b026c51a91d67c32f84bb047bc|split_files/vae/qwen_image_vae.safetensors|vae|253806246|a70580f0213e67967ee9c95f05bb400e8fb08307e017a924bf3441223e023d1f
lightx2v/Qwen-Image-Edit-2511-Lightning|107d238d68b8387e32843d0b4a2e24ceb0d3ad86|Qwen-Image-Edit-2511-Lightning-8steps-V1.0-bf16.safetensors|loras|849608296|a9e81a58a78f260f67b337a6f615e8fa4cd3bc79847c77b7d61a581b789b1ba8
Comfy-Org/MiniMax-H3|e5eb578a89295337b8ff433a035929ce0279e0b6|diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors|diffusion_models|20970379616|e889202c41dafb67b10d67b97f0d8541508036a6090af23425a5c2615d03c47a
Comfy-Org/MiniMax-H3|e5eb578a89295337b8ff433a035929ce0279e0b6|loras/minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors|loras|1956193000|2339acdf19bfe123f46b971ea35d367a84adb85de43627e1eceafa5a5b2b111e
Comfy-Org/MiniMax-H3|e5eb578a89295337b8ff433a035929ce0279e0b6|text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors|text_encoders|15687142551|35a88d51044231fe332301d7a62aa81e3f2cba62febeb446e2c1e3e0ef76f2c6
Comfy-Org/MiniMax-H3|e5eb578a89295337b8ff433a035929ce0279e0b6|vae/minimax_h3_audio_vae_fp32.safetensors|vae|605254808|8e505d95dd1561d47abd43d4238fd40d9bb1ae9e147ed0a4cba778d76ae4db48
Comfy-Org/MiniMax-H3|e5eb578a89295337b8ff433a035929ce0279e0b6|vae/minimax_h3_video_vae_fp16.safetensors|vae|5207808496|7c1f131492e7eddacaac9069a61b81bdd39de5cc96561e677c5eab1cdce5e522
EOF
)

mkdir -p "$ROOT" "$LOG" "$ROOT/cache"

install() {
  [[ -d "$COMFY/.git" ]] || git clone --depth 1 --branch "$COMFY_TAG" https://github.com/comfyanonymous/ComfyUI.git "$COMFY"
  [[ $(git -C "$COMFY" describe --tags) == "$COMFY_TAG" ]]
  local gg="$COMFY/custom_nodes/ComfyUI-GGUF"
  if [[ ! -d "$gg/.git" ]]; then
    git clone https://github.com/city96/ComfyUI-GGUF.git "$gg"
  fi
  git -C "$gg" checkout -q "$GGUF_COMMIT"
  [[ -x "$VENV/bin/python" ]] || "$UV" venv --python "$UV_PYTHON" "$VENV"
  "$UV" pip install --python "$VENV/bin/python" torch torchvision torchaudio --index-url "$TORCH_INDEX"
  "$UV" pip install --python "$VENV/bin/python" -r "$COMFY/requirements.txt" -r "$gg/requirements.txt" huggingface_hub
  "$VENV/bin/python" - <<'PY'
import torch, json
assert torch.cuda.is_available(), "CUDA unavailable"
a = torch.randn(2048, 2048, device="cuda"); (a @ a).sum().item()
print(json.dumps({"torch": torch.__version__, "cuda": torch.version.cuda, "gpu": torch.cuda.get_device_name(0), "matmul": "ok"}))
PY
}

models() {
  df -BG --output=avail "$ROOT" | tail -1
  while IFS='|' read -r repo rev path sub bytes sha; do
    local dest="$MODELS/$sub/$(basename "$path")"
    mkdir -p "$MODELS/$sub"
    if [[ -f "$dest" ]] && [[ $(stat -c %s "$dest") == "$bytes" ]]; then echo "present: $dest"; continue; fi
    echo "downloading $repo@$rev $path"
    "$VENV/bin/hf" download "$repo" "$path" --revision "$rev" --local-dir "$ROOT/cache/dl/$repo"
    mv "$ROOT/cache/dl/$repo/$path" "$dest"
  done <<< "$MANIFEST"
  verify
}

verify() {
  local ok=1
  while IFS='|' read -r repo rev path sub bytes sha; do
    local dest="$MODELS/$sub/$(basename "$path")"
    local got; got=$(sha256sum "$dest" | cut -d' ' -f1)
    if [[ $(stat -c %s "$dest") == "$bytes" && "$got" == "$sha" ]]; then echo "OK   $sub/$(basename "$path")"; else echo "FAIL $dest $got"; ok=0; fi
  done <<< "$MANIFEST"
  [[ $ok == 1 ]]
}

nixroots() {
  # NixOS only: Triton needs a C compiler and runnable ptxas/cuobjdump/nvdisasm. Pin them as project GC roots.
  local nix=(nix --extra-experimental-features "nix-command flakes")
  mkdir -p "$ROOT/nix-roots/bin"
  "${nix[@]}" build nixpkgs#gcc --out-link "$ROOT/nix-roots/gcc"
  "${nix[@]}" build nixpkgs#glibc.out --out-link "$ROOT/nix-roots/glibc"
  local g="$ROOT/nix-roots/glibc"
  local tb="$VENV/lib/python3.12/site-packages/triton/backends/nvidia/bin"
  for t in ptxas cuobjdump nvdisasm; do
    printf '#!/bin/sh\nexec %s/lib/ld-linux-x86-64.so.2 --library-path %s/lib:%s %s/%s "$@"\n' "$g" "$g" "$LD_LIBRARY_PATH" "$tb" "$t" > "$ROOT/nix-roots/bin/$t"
    chmod +x "$ROOT/nix-roots/bin/$t"
  done
  "$ROOT/nix-roots/bin/ptxas" --version | tail -1
}

serve() {
  # NixOS: Triton cannot find libcuda via /sbin/ldconfig and needs a C compiler for its driver stub.
  export TRITON_LIBCUDA_PATH=/run/opengl-driver/lib
  export CC="$ROOT/nix-roots/gcc/bin/gcc"
  export PATH="$ROOT/nix-roots/gcc/bin:$PATH"
  # Triton's bundled CUDA tools are generic-linux binaries; nix-roots/bin wraps them with the pinned Nix glibc loader.
  export TRITON_PTXAS_PATH="$ROOT/nix-roots/bin/ptxas"
  export TRITON_CUOBJDUMP_PATH="$ROOT/nix-roots/bin/cuobjdump"
  export TRITON_NVDISASM_PATH="$ROOT/nix-roots/bin/nvdisasm"
  cd "$COMFY"
  exec "$VENV/bin/python" main.py --lowvram --cache-none --reserve-vram 2 --disable-pinned-memory --listen 127.0.0.1 --port 8188 2>&1 | tee -a "$LOG/comfyui.log"
}

case "${1:-}" in
  install) install 2>&1 | tee "$LOG/install.log" ;;
  nixroots) nixroots 2>&1 | tee "$LOG/nixroots.log" ;;
  models) models 2>&1 | tee "$LOG/models.log" ;;
  verify) verify ;;
  serve) serve ;;
  *) echo "Usage: $0 install|nixroots|models|verify|serve" >&2; exit 2 ;;
esac
