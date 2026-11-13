# Local LTX-2.5 motion and FLUX.2 [klein] stills on a 12 GB GPU

Use this recipe when the selected provider is the local workstation GPU. It was proven on 2026-11-12 (Nuvvantene R15) on an RTX 4070 Ti 12 GB under NixOS. It is a working baseline, not a claim that these are the newest or best models. Verify the live node schema, model hashes and free disk before reuse.

## Stack

[comfyui_ltx_setup.sh](../scripts/comfyui_ltx_setup.sh) owns installation: `install` (pinned ComfyUI tag, ComfyUI-GGUF commit, Torch from the CUDA wheel index, CUDA matmul smoke test), `nixroots` (NixOS only), `models` (pinned repo revision + byte count + SHA-256 per file), `verify`, `serve`. All repositories below are ungated; no Hugging Face login is required.

| Role | File | Source | Size |
|---|---|---|---|
| Motion DiT | `ltx-2.5-22b-distilled-UD-Q3_K_XL.gguf` | `unsloth/LTX-2.5-GGUF` | 12.0 GB |
| Motion text encoder | `gemma4-12b-with-proj-ltx-2.5-comfy-int8-convrot.safetensors` | `comfyicu/LTX-2.5` | 15.4 GB |
| Video / audio VAE | `ltx-2.5-video-vae-conv-bf16`, `ltx-2.5-audio-vae-bf16` | `unsloth/LTX-2.5-GGUF` | 1.8 GB |
| Still model | `flux-2-klein-4b.safetensors` + `qwen_3_4b.safetensors` + `flux2-vae.safetensors` | `Comfy-Org/Flux-2-Klein-4B` (Apache-2.0) | 16.1 GB |

The earlier Nuvvantene/cyberpunk local runs used differently named LTX-2.5 Q3_K_M and Gemma w4a8 files whose hashes match no published file; treat those records as historical. UD-Q3_K_XL is the closest published quant with better measured fidelity than Q3_K_M.

## NixOS runtime fixes

Pip wheels assume a generic Linux. On NixOS:

- Use a pinned Nix Python and set `LD_LIBRARY_PATH` to `/run/opengl-driver/lib` plus Nix `gcc-lib` and `zlib`.
- Triton fails inside text encoding with `/sbin/ldconfig` missing: set `TRITON_LIBCUDA_PATH=/run/opengl-driver/lib`.
- Triton then needs a C compiler (`CC`) and runnable `ptxas`/`cuobjdump`/`nvdisasm`. Its bundled binaries are generic-Linux ELF files, and NixOS refuses them unless nix-ld is enabled. `nixroots` pins gcc and glibc as project GC roots and writes loader wrappers; `serve` exports `TRITON_PTXAS_PATH`, `TRITON_CUOBJDUMP_PATH`, `TRITON_NVDISASM_PATH`.
- Do not rebuild the system or enable nix-ld for this; project-scoped roots are reversible.

## Graphs and runner

[local_comfy.py](../scripts/local_comfy.py) builds API graphs following the installed `image_flux2_klein_image_edit_4b_distilled` and `video_ltx2_5_flf2v` templates, submits them, waits and collects originals with intent/receipt/history records and hashes:

- `image`: FLUX.2 klein 4 steps, CFG 1, any number of `--ref` images chained as `ReferenceLatent` on positive and zero-out negative conditioning. Use reference crops for identity and the accepted start still as a reference for an end still with matching framing.
- `video`: LTX-2.5 distilled, 8 manual sigmas, `LTXVAddGuide` at frame 0 (strength 1.0 for single-image I2V) or at frames 0 and −1 (default 0.7) for first/last-frame. Length must be `8n+1`. Generated audio is discarded by the edit; the canonical song owns sound.

- `video --audio <file> --audio-start <s>`: lip sync. Following the installed `video_ltx2_3_ia2v` template, the audio window `[s, s + frames/24)` is encoded with the LTX audio VAE and held fixed (`SetLatentNoiseMask` with a zero `SolidMask`), so the picture is generated to it. Use an isolated lead-vocal stem whose sample alignment to the canonical master you have verified (FFT cross-correlation within one frame). Start the window a few frames before the edit slot (pre-roll) and use that same offset as the source in-point, so picture frame k equals song time `s + k/24`. The negative prompt then permits mouth movement. In two-person shots, say explicitly that only the singer's lips move; LTX otherwise animates both mouths. The output carries no audio stream, so prove sync by muxing each clip with the song at its window and watching it with sound.

Validate a new graph against `/object_info` before the first submission. ComfyUI's cached `LoadImage` option list omits subfolders; that alone is not an error.

## Measured performance (4070 Ti 12 GB, 128 GB RAM)

| Job | Setting | Time |
|---|---|---|
| FLUX.2 klein still | 1360×768, 4 steps, 0–4 references | 4–11 s after first load |
| LTX-2.5 I2V / FLF | 1024×576, 97 or 121 frames | 80–105 s total, ~7.3 s/step, ~10.2 GB VRAM with partial offload |

A full three-to-four-minute film of about 55 shots is roughly 1.5–2 GPU hours of motion plus minutes of stills. Run one hardest-shot pilot, inspect it, then queue a section batch; ComfyUI runs one prompt at a time.

## What first/last-frame can and cannot do

FLF interpolation produces a real on-screen transformation only when start and end share framing and geometry (same camera, object position, scale): a saw blade becoming a silk ring in the same place, or an overhead whirlpool becoming saree folds. When the two stills have different compositions (embers vs eye close-up, rope vs a woman's back), LTX hides the gap with a hard jump or a ghosted double exposure inside the clip. Detect it with early-frame grids, not five-frame strips. Repair by generating each state as its own I2V clip and making a deliberate editorial cut at a meaningful audio event, or by regenerating the end still with the start still as a framing reference.
