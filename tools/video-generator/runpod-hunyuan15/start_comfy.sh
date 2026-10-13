#!/usr/bin/env bash
set -euo pipefail

ROOT=/workspace/urvashi-hunyuan15
COMFY="$ROOT/ComfyUI"
PYTHON=/workspace/runpod-slim/ComfyUI/.venv-cu128/bin/python

test -f "$ROOT/READY"
pkill -f "$COMFY/main.py" 2>/dev/null || true
nohup "$PYTHON" "$COMFY/main.py" --listen 127.0.0.1 --port 8189 \
  >"$ROOT/comfy.log" 2>&1 &
echo $! >"$ROOT/comfy.pid"

for _ in $(seq 1 120); do
  if curl --fail --silent http://127.0.0.1:8189/system_stats >/dev/null; then
    echo ready
    exit 0
  fi
  sleep 2
done

tail -n 100 "$ROOT/comfy.log"
exit 1
