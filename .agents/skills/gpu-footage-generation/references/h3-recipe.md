# Historical H3 recipe and runnable handoff

Use this recipe only when H3 is the selected model and the live server supports the recorded nodes. This is extracted from Urvashi's successful saved pilot graph, not a claim that it is the newest or best available model. The source is task `01a0c2ed-a2ed-75a2-87c3-6ec62fc9482d`, workspace-relative `music-video/motion-production-v5/pilot-save-repair-workflow.json` and `pilot-save-repair-result.json`. The result recorded a decoded 1536×640, 124-frame, 24 fps output. Creative acceptance remains separate.

The retained graph is [h3-i2v-api.json](../assets/h3-i2v-api.json), with the song-specific prompt, image and output prefix replaced by neutral sample values. [prepare_h3_job.py](../scripts/prepare_h3_job.py) parameterizes it without submitting a job or modifying source images.

Historical runtime from the repository's `setup_pinned_h3_runtime.sh`: ComfyUI commit `e638023d54497dbe0579565e5de4bb7076899592`, Torch 2.10.0 / torchvision 0.25.0 / torchaudio 2.10.0 from the CUDA 13.0 wheel index. Verify driver/GPU compatibility before reproducing it. Do not reinstall this over another working environment.

Historical model filenames:

| Directory | Filename | Repository recorded by the cache script |
|---|---|---|
| diffusion_models | `minimax_h3_fl2va_pruned_int8_convrot.safetensors` | `Comfy-Org/MiniMax-H3` |
| text_encoders | `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` | `Comfy-Org/MiniMax-H3` |
| vae | `minimax_h3_video_vae_fp16.safetensors` | `Comfy-Org/MiniMax-H3` |
| vae | `minimax_h3_audio_vae_fp32.safetensors` | `Comfy-Org/MiniMax-H3` |
| loras | `minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors` | `lightx2v/Minimax-h3-Turbo` |

Resolve those repositories live, freeze repository revisions and publisher file hashes, and verify the cache. Do not fabricate missing hashes or download whatever a matching filename happens to point to. The graph uses `MiniMaxH3ImageToVideo`, `res_multistep`, eight `simple` scheduler steps, `CreateVideo` with `codec: none`, then `SaveVideo` using its recorded `format.codec` H.264 settings. The save schema was the source of a real pilot failure; check it against `/object_info` before use. This graph also generates audio; mute it in a canonical-song edit. Native generation dimensions are not a 1080p/2K quality claim after upscale.

## Prepare one job

Create an accepted, barless model-input image with the correct recorded crop/scale before these commands. Its dimensions must match the planned conditioning geometry. The input snapshot and bindings use paths relative to the actual ComfyUI input root. For custom image-loading nodes, explicitly bind every conditioning file; the submission helper additionally checks the standard `LoadImage`/`LoadImageMask` classes.

```sh
python3 <skill-dir>/scripts/prepare_h3_job.py \
  --anchor run-01/shot-01.png --prompt-file <run>/shot-01-visual.txt \
  --width 1536 --height 640 --frames 124 --fps 24 --seed 1001 \
  --job shot-01-r1 --directory <run>/prepared/shot-01-r1

python3 <skill-dir>/scripts/asset_snapshot.py create \
  --root <ComfyUI>/input --output <run>/inputs.json run-01/shot-01.png
```

These dimensions and length reproduce the recorded profile, not every song's required canvas. Derive them from the chosen model/brief and verify the live frame-count lattice. For first/last-frame chains, use a separately verified graph supporting both anchors; do not infer that this single-anchor graph implements a bridge.

## Submit, observe and collect

Complete the RunPod/Herdr and budget preflight first. On the execution host, or through a verified forwarded API, run:

```sh
python3 <skill-dir>/scripts/comfy_job.py --url <server-url> --ledger <run>/jobs --job shot-01-r1 submit \
  --workflow <run>/prepared/shot-01-r1/workflow.json \
  --bindings <run>/prepared/shot-01-r1/bindings.json \
  --inputs <run>/inputs.json --input-root <ComfyUI>/input \
  --deadline <shutdown-unix-seconds> --reserve-seconds <measured-job-save-transfer-seconds>

python3 <skill-dir>/scripts/comfy_job.py --url <server-url> --ledger <run>/jobs --job shot-01-r1 status
python3 <skill-dir>/scripts/comfy_job.py --url <server-url> --ledger <run>/jobs --job shot-01-r1 reconcile
python3 <skill-dir>/scripts/comfy_job.py --url <server-url> --ledger <run>/jobs --job shot-01-r1 collect \
  --output-root <ComfyUI>/output --archive <run>/originals --output-node 17
```

Use `reconcile` only after an uncertain submission; an existing receipt routes to status. Poll in bounded observation calls, preserving the same job. Copy the archived original and job directory back to the editor's machine, verify the result hash there, and review the footage before starting the next batch. The helper's deadline does not stop RunPod; carry out and verify the separate compute-shutdown step.
