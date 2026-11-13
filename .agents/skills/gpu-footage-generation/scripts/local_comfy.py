#!/usr/bin/env python3
"""Local ComfyUI still/motion job builder and runner for a workstation GPU (proven on an RTX 4070 Ti 12 GB).

Builds API graphs that follow the installed official templates' structure:
  - FLUX.2 [klein] 4B distilled text-to-image / multi-reference edit (production anchors)
  - LTX-2.5 distilled GGUF image-to-video, or first+last-frame to video (motion)
Model filenames match comfyui_ltx_setup.sh. Validate graphs against the live /object_info before first use.

Run on the execution host with the ComfyUI venv python. Paths given to --ref/--first/--last are relative to
ComfyUI/input. Jobs live under $COMFY_JOBS (default ~/projects/comfyui-ltx/jobs/<project>).
  local_comfy.py --project NAME image --job ID --prompt-file P --ref NAME/x.png ... --width 1360 --height 768 --seed N
  local_comfy.py --project NAME video --job ID --prompt-file P --first NAME/a.png [--last NAME/b.png] --frames 121 --seed N
  local_comfy.py --project NAME wait  --job ID [--timeout 1800]
  local_comfy.py --project NAME check --job ID
Each job directory keeps graph.json, intent.json (input hashes before submission), receipt.json, history.json and
collected originals with SHA-256. Existing job directories are never overwritten: use a new attempt ID.
"""
import argparse, hashlib, json, os, shutil, sys, time, urllib.request, uuid
from pathlib import Path

ROOT = Path(os.environ.get("COMFY_LTX_ROOT", Path.home() / "projects/comfyui-ltx"))
COMFY = ROOT / "ComfyUI"
INPUT = COMFY / "input"
OUTPUT = COMFY / "output"
JOBS = None  # set from --project in main()
URL = os.environ.get("COMFY_URL", "http://127.0.0.1:8188")

LTX_UNET = "ltx-2.5-22b-distilled-UD-Q3_K_XL.gguf"
LTX_CLIP = "gemma4-12b-with-proj-ltx-2.5-comfy-int8-convrot.safetensors"
LTX_VAE = "ltx-2.5-video-vae-conv-bf16.safetensors"
LTX_AVAE = "ltx-2.5-audio-vae-bf16.safetensors"
FLUX_UNET = "flux-2-klein-4b.safetensors"
FLUX_CLIP = "qwen_3_4b.safetensors"
FLUX_VAE = "flux2-vae.safetensors"

LTX_NEG_BASE = ("blurry, out of focus, overexposed, flicker, exposure shift, morphing faces, deformed hands, extra limbs, "
                "text, letters, subtitles, logos, watermark, borders, camera shake, cartoon, sudden cut, jump cut")
LTX_NEG = LTX_NEG_BASE + ", talking, singing, open mouth, lip movement"
LTX_NEG_SINGING = LTX_NEG_BASE + ", closed mouth while singing, lip sync drift, mumbling, chewing, extra mouths, distorted teeth"


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def api(route, payload=None):
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(URL + route, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def flux_graph(prompt, refs, width, height, seed, prefix, steps=4, init=None, denoise=1.0, mask=None):
    """init: input-relative image used as the starting latent (img2img); denoise < 1 keeps its structure (faces, pose).
    mask: input-relative grayscale image, white = regenerate, black = keep the init pixels (protect characters)."""
    g = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": FLUX_UNET, "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": FLUX_CLIP, "type": "flux2", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": FLUX_VAE}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["2", 0]}},
        "5": {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["4", 0]}},
    }
    pos, neg = ["4", 0], ["5", 0]
    for i, ref in enumerate(refs):
        b = 100 + i * 10
        g[str(b)] = {"class_type": "LoadImage", "inputs": {"image": ref}}
        g[str(b + 1)] = {"class_type": "ImageScaleToTotalPixels",
                         "inputs": {"image": [str(b), 0], "upscale_method": "lanczos", "megapixels": 1.0, "resolution_steps": 1}}
        g[str(b + 2)] = {"class_type": "VAEEncode", "inputs": {"pixels": [str(b + 1), 0], "vae": ["3", 0]}}
        g[str(b + 3)] = {"class_type": "ReferenceLatent", "inputs": {"conditioning": pos, "latent": [str(b + 2), 0]}}
        g[str(b + 4)] = {"class_type": "ReferenceLatent", "inputs": {"conditioning": neg, "latent": [str(b + 2), 0]}}
        pos, neg = [str(b + 3), 0], [str(b + 4), 0]
    g.update({
        "10": {"class_type": "EmptyFlux2LatentImage", "inputs": {"width": width, "height": height, "batch_size": 1}},
        "11": {"class_type": "Flux2Scheduler", "inputs": {"steps": steps, "width": width, "height": height}},
        "12": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}},
        "13": {"class_type": "RandomNoise", "inputs": {"noise_seed": seed}},
        "14": {"class_type": "CFGGuider", "inputs": {"model": ["1", 0], "positive": pos, "negative": neg, "cfg": 1.0}},
        "15": {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["13", 0], "guider": ["14", 0], "sampler": ["12", 0],
                                                                  "sigmas": ["11", 0], "latent_image": ["10", 0]}},
        "16": {"class_type": "VAEDecode", "inputs": {"samples": ["15", 0], "vae": ["3", 0]}},
        "17": {"class_type": "SaveImage", "inputs": {"images": ["16", 0], "filename_prefix": prefix}},
    })
    if init is not None:
        g.update({
            "90": {"class_type": "LoadImage", "inputs": {"image": init}},
            "91": {"class_type": "ImageScale", "inputs": {"image": ["90", 0], "upscale_method": "lanczos", "width": width, "height": height, "crop": "center"}},
            "92": {"class_type": "VAEEncode", "inputs": {"pixels": ["91", 0], "vae": ["3", 0]}},
            "93": {"class_type": "SplitSigmasDenoise", "inputs": {"sigmas": ["11", 0], "denoise": denoise}},
        })
        g["15"]["inputs"]["latent_image"] = ["92", 0]
        g["15"]["inputs"]["sigmas"] = ["93", 1]
        if mask is not None:
            g["94"] = {"class_type": "LoadImageMask", "inputs": {"image": mask, "channel": "red"}}
            g["95"] = {"class_type": "SetLatentNoiseMask", "inputs": {"samples": ["92", 0], "mask": ["94", 0]}}
            g["15"]["inputs"]["latent_image"] = ["95", 0]
    return g, "17"


QEDIT_UNET = "qwen-image-edit-2511-Q5_K_M.gguf"
QEDIT_CLIP = "qwen_2.5_vl_7b_fp8_scaled.safetensors"
QEDIT_VAE = "qwen_image_vae.safetensors"
QEDIT_LORA = "Qwen-Image-Edit-2511-Lightning-8steps-V1.0-bf16.safetensors"


def qedit_graph(prompt, images, seed, prefix, steps=8):
    """Qwen-Image-Edit-2511 (official 2511 template structure, Lightning 8-step LoRA). images: 1-3 input-relative refs;
    image 1 sets the output size (FluxKontextImageScale) and is the edit subject."""
    g = {
        "1": {"class_type": "UnetLoaderGGUF", "inputs": {"unet_name": QEDIT_UNET}},
        "2": {"class_type": "ModelSamplingAuraFlow", "inputs": {"model": ["1", 0], "shift": 3.1}},
        "3": {"class_type": "CFGNorm", "inputs": {"model": ["2", 0], "strength": 1.0}},
        "4": {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["3", 0], "lora_name": QEDIT_LORA, "strength_model": 1.0}},
        "5": {"class_type": "CLIPLoader", "inputs": {"clip_name": QEDIT_CLIP, "type": "qwen_image", "device": "default"}},
        "6": {"class_type": "VAELoader", "inputs": {"vae_name": QEDIT_VAE}},
    }
    enc_imgs = {}
    for i, im in enumerate(images[:3]):
        n = str(10 + i)
        g[n] = {"class_type": "LoadImage", "inputs": {"image": im}}
        enc_imgs[f"image{i + 1}"] = [n, 0]
    g["20"] = {"class_type": "FluxKontextImageScale", "inputs": {"image": ["10", 0]}}
    enc_imgs["image1"] = ["20", 0]
    for nid, text in (("21", prompt), ("22", "")):
        g[nid] = {"class_type": "TextEncodeQwenImageEditPlus", "inputs": {"clip": ["5", 0], "vae": ["6", 0], "prompt": text, **enc_imgs}}
    g["23"] = {"class_type": "FluxKontextMultiReferenceLatentMethod", "inputs": {"conditioning": ["21", 0], "reference_latents_method": "index_timestep_zero"}}
    g["24"] = {"class_type": "FluxKontextMultiReferenceLatentMethod", "inputs": {"conditioning": ["22", 0], "reference_latents_method": "index_timestep_zero"}}
    g["25"] = {"class_type": "VAEEncode", "inputs": {"pixels": ["20", 0], "vae": ["6", 0]}}
    g["26"] = {"class_type": "KSampler", "inputs": {"model": ["4", 0], "positive": ["23", 0], "negative": ["24", 0], "latent_image": ["25", 0],
                                                     "seed": seed, "steps": steps, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0}}
    g["27"] = {"class_type": "VAEDecode", "inputs": {"samples": ["26", 0], "vae": ["6", 0]}}
    g["28"] = {"class_type": "SaveImage", "inputs": {"images": ["27", 0], "filename_prefix": prefix}}
    return g, "28"


H3_UNET = "minimax_h3_fl2va_pruned_int8_convrot.safetensors"
H3_LORA = "minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors"
H3_CLIP = "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors"
H3_VAE = "minimax_h3_video_vae_fp16.safetensors"


def h3_graph(prompt, first, last, width, height, frames, seed, prefix, steps=8):
    """MiniMax H3 first(/last)-frame to video, reproducing the graph recorded on the RTX 4070 Ti (panja/Urvashi).
    Generated audio is not saved; the canonical song owns sound. length snaps to the model's 17k+5 grid (124 = ~5 s)."""
    g = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": H3_UNET, "weight_dtype": "default"}},
        "2": {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["1", 0], "lora_name": H3_LORA, "strength_model": 1.0}},
        "3": {"class_type": "CLIPLoader", "inputs": {"clip_name": H3_CLIP, "type": "minimax", "device": "default"}},
        "4": {"class_type": "VAELoader", "inputs": {"vae_name": H3_VAE}},
        "6": {"class_type": "LoadImage", "inputs": {"image": first}},
        "8": {"class_type": "MiniMaxH3ImageToVideo", "inputs": {"clip": ["3", 0], "vae": ["4", 0], "prompt": prompt, "width": width,
                                                                 "height": height, "length": frames, "first_frame": ["6", 0]}},
        "9": {"class_type": "RandomNoise", "inputs": {"noise_seed": seed}},
        "10": {"class_type": "BasicGuider", "inputs": {"model": ["2", 0], "conditioning": ["8", 0]}},
        "11": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "res_multistep"}},
        "12": {"class_type": "BasicScheduler", "inputs": {"model": ["2", 0], "scheduler": "simple", "steps": steps, "denoise": 1.0}},
        "13": {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["9", 0], "guider": ["10", 0], "sampler": ["11", 0],
                                                                  "sigmas": ["12", 0], "latent_image": ["8", 1]}},
        "14": {"class_type": "VAEDecode", "inputs": {"samples": ["13", 0], "vae": ["4", 0]}},
        "16": {"class_type": "CreateVideo", "inputs": {"images": ["14", 0], "fps": 24}},
        "17": {"class_type": "SaveVideo", "inputs": {"video": ["16", 0], "filename_prefix": prefix, "format": "mp4", "codec": "h264"}},
    }
    if last is not None:
        g["7"] = {"class_type": "LoadImage", "inputs": {"image": last}}
        g["8"]["inputs"]["last_frame"] = ["7", 0]
    return g, "17"


def ltx_graph(prompt, first, last, width, height, frames, seed, prefix, guide_strength=0.7, audio=None, audio_start=0.0,
              negative=None):
    """audio: input-relative file; its [audio_start, audio_start + frames/24) window is encoded and held fixed
    (noise mask 0) so the generated picture follows it, e.g. a lead-vocal stem for lip sync."""
    g = {
        "1": {"class_type": "UnetLoaderGGUF", "inputs": {"unet_name": LTX_UNET}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": LTX_CLIP, "type": "ltxv", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": LTX_VAE}},
        "4": {"class_type": "VAELoader", "inputs": {"vae_name": LTX_AVAE}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["2", 0]}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": negative or (LTX_NEG_SINGING if audio else LTX_NEG), "clip": ["2", 0]}},
        "7": {"class_type": "LTXVConditioning", "inputs": {"positive": ["5", 0], "negative": ["6", 0], "frame_rate": 24}},
        "8": {"class_type": "EmptyLTXVLatentVideo", "inputs": {"width": width, "height": height, "length": frames, "batch_size": 1}},
        "20": {"class_type": "LoadImage", "inputs": {"image": first}},
        "21": {"class_type": "ImageScale", "inputs": {"image": ["20", 0], "upscale_method": "lanczos", "width": width,
                                                       "height": height, "crop": "center"}},
        "22": {"class_type": "LTXVPreprocess", "inputs": {"image": ["21", 0], "img_compression": 18}},
        "23": {"class_type": "LTXVAddGuide", "inputs": {"positive": ["7", 0], "negative": ["7", 1], "vae": ["3", 0],
                                                         "latent": ["8", 0], "image": ["22", 0], "frame_idx": 0,
                                                         "strength": 1.0 if last is None else guide_strength}},
    }
    tip = "23"
    if last is not None:
        g.update({
            "30": {"class_type": "LoadImage", "inputs": {"image": last}},
            "31": {"class_type": "ImageScale", "inputs": {"image": ["30", 0], "upscale_method": "lanczos", "width": width,
                                                           "height": height, "crop": "center"}},
            "32": {"class_type": "LTXVPreprocess", "inputs": {"image": ["31", 0], "img_compression": 18}},
            "33": {"class_type": "LTXVAddGuide", "inputs": {"positive": ["23", 0], "negative": ["23", 1], "vae": ["3", 0],
                                                             "latent": ["23", 2], "image": ["32", 0], "frame_idx": -1,
                                                             "strength": guide_strength}},
        })
        tip = "33"
    if audio is None:
        g["40"] = {"class_type": "LTXVEmptyLatentAudio", "inputs": {"audio_vae": ["4", 0], "frames_number": frames,
                                                                     "frame_rate": 24, "batch_size": 1}}
        audio_latent = ["40", 0]
    else:
        g.update({
            "60": {"class_type": "LoadAudio", "inputs": {"audio": audio}},
            "61": {"class_type": "TrimAudioDuration", "inputs": {"audio": ["60", 0], "start_index": round(audio_start, 4),
                                                                  "duration": round(frames / 24, 4)}},
            "62": {"class_type": "LTXVAudioVAEEncode", "inputs": {"audio": ["61", 0], "audio_vae": ["4", 0]}},
            "63": {"class_type": "SolidMask", "inputs": {"value": 0.0, "width": 1024, "height": 1024}},
            "64": {"class_type": "SetLatentNoiseMask", "inputs": {"samples": ["62", 0], "mask": ["63", 0]}},
        })
        audio_latent = ["64", 0]
    g.update({
        "41": {"class_type": "LTXVConcatAVLatent", "inputs": {"video_latent": [tip, 2], "audio_latent": audio_latent}},
        "42": {"class_type": "RandomNoise", "inputs": {"noise_seed": seed}},
        "43": {"class_type": "SamplerEulerAncestral", "inputs": {"eta": 0.0, "s_noise": 1.0}},
        "44": {"class_type": "ManualSigmas", "inputs": {"sigmas": "1.0, 0.99375, 0.9875, 0.98125, 0.975, 0.909375, 0.725, 0.421875, 0.0"}},
        "45": {"class_type": "LTXVDualCFGGuider", "inputs": {"model": ["1", 0], "positive": [tip, 0], "negative": [tip, 1],
                                                              "video_cfg": 1.0, "audio_cfg": 1.0}},
        "46": {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["42", 0], "guider": ["45", 0], "sampler": ["43", 0],
                                                                  "sigmas": ["44", 0], "latent_image": ["41", 0]}},
        "47": {"class_type": "LTXVSeparateAVLatent", "inputs": {"av_latent": ["46", 1]}},
        "48": {"class_type": "LTXVCropGuides", "inputs": {"positive": [tip, 0], "negative": [tip, 1], "latent": ["47", 0]}},
        "49": {"class_type": "VAEDecodeTiled", "inputs": {"samples": ["48", 2], "vae": ["3", 0], "tile_size": 512,
                                                           "overlap": 64, "temporal_size": 64, "temporal_overlap": 16}},
        "50": {"class_type": "CreateVideo", "inputs": {"images": ["49", 0], "fps": 24}},
        "51": {"class_type": "SaveVideo", "inputs": {"video": ["50", 0], "filename_prefix": prefix, "format": "mp4", "codec": "h264"}},
    })
    return g, "51"


def submit(job, graph, out_node, inputs, meta):
    d = JOBS / job
    if d.exists():
        sys.exit(f"job {job} exists; use a new attempt id")
    d.mkdir(parents=True)
    intent = {"job": job, "created": time.time(), "output_node": out_node, "meta": meta,
              "inputs": {p: sha(INPUT / p) for p in inputs},
              "graph_sha256": hashlib.sha256(json.dumps(graph, sort_keys=True).encode()).hexdigest()}
    (d / "graph.json").write_text(json.dumps(graph, indent=1))
    (d / "intent.json").write_text(json.dumps(intent, indent=1))
    client_id = str(uuid.uuid4())
    r = api("/prompt", {"prompt": graph, "client_id": client_id})
    receipt = {"prompt_id": r.get("prompt_id"), "number": r.get("number"), "node_errors": r.get("node_errors"),
               "client_id": client_id, "submitted": time.time()}
    (d / "receipt.json").write_text(json.dumps(receipt, indent=1))
    print(json.dumps({"job": job, **receipt}))


def outputs_of(hist, node):
    out = hist.get("outputs", {}).get(node, {})
    for key in ("images", "videos", "gifs", "video"):
        for item in out.get(key, []) or []:
            if isinstance(item, dict) and "filename" in item:
                yield item


def check(job, block=False, timeout=1800):
    d = JOBS / job
    receipt = json.loads((d / "receipt.json").read_text())
    intent = json.loads((d / "intent.json").read_text())
    pid = receipt["prompt_id"]
    t0 = time.time()
    while True:
        h = api(f"/history/{pid}").get(pid)
        if h and h.get("status", {}).get("completed") is not None or (h and h.get("outputs")):
            break
        if not block or time.time() - t0 > timeout:
            q = api("/queue")
            running = any(x[1] == pid for x in q.get("queue_running", []))
            print(json.dumps({"job": job, "state": "running" if running else "pending", "elapsed": round(time.time() - receipt["submitted"])}))
            return
        time.sleep(5)
    (d / "history.json").write_text(json.dumps(h, indent=1))
    status = h.get("status", {})
    items = list(outputs_of(h, intent["output_node"]))
    collected = []
    for it in items:
        src = OUTPUT / it.get("subfolder", "") / it["filename"]
        dst = d / it["filename"]
        shutil.copy2(src, dst)
        collected.append({"file": str(dst), "sha256": sha(dst), "bytes": dst.stat().st_size})
    msgs = status.get("messages", [])
    t = [m[1].get("timestamp") for m in msgs if isinstance(m, list) and len(m) > 1 and isinstance(m[1], dict)]
    res = {"job": job, "status": status.get("status_str"), "collected": collected,
           "exec_seconds": round((max(t) - min(t)) / 1000, 1) if len(t) >= 2 else None}
    (d / "collection.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res))


def main():
    global JOBS
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True, help="Project/run label; also the output subfolder prefix")
    sp = ap.add_subparsers(dest="cmd", required=True)
    a = sp.add_parser("image"); a.add_argument("--job", required=True); a.add_argument("--prompt-file", type=Path, required=True)
    a.add_argument("--ref", action="append", default=[]); a.add_argument("--width", type=int, default=1344)
    a.add_argument("--height", type=int, default=768); a.add_argument("--seed", type=int, default=1); a.add_argument("--steps", type=int, default=4)
    a.add_argument("--init", help="input-relative start image (img2img)"); a.add_argument("--denoise", type=float, default=1.0)
    a.add_argument("--mask", help="input-relative mask with --init: white regenerates, black keeps")
    v = sp.add_parser("video"); v.add_argument("--job", required=True); v.add_argument("--prompt-file", type=Path, required=True)
    v.add_argument("--first", required=True); v.add_argument("--last"); v.add_argument("--width", type=int, default=1024)
    v.add_argument("--height", type=int, default=576); v.add_argument("--frames", type=int, default=121)
    v.add_argument("--seed", type=int, default=1); v.add_argument("--strength", type=float, default=0.7)
    v.add_argument("--audio", help="input-relative audio held fixed as conditioning (lip sync); picture frame k = audio-start + k/24 s")
    v.add_argument("--audio-start", type=float, default=0.0)
    h = sp.add_parser("h3"); h.add_argument("--job", required=True); h.add_argument("--prompt-file", type=Path, required=True)
    h.add_argument("--first", required=True); h.add_argument("--last"); h.add_argument("--width", type=int, default=1536)
    h.add_argument("--height", type=int, default=640); h.add_argument("--frames", type=int, default=124); h.add_argument("--seed", type=int, default=1)
    q = sp.add_parser("qedit"); q.add_argument("--job", required=True); q.add_argument("--prompt-file", type=Path, required=True)
    q.add_argument("--image", action="append", required=True); q.add_argument("--seed", type=int, default=1); q.add_argument("--steps", type=int, default=8)
    for name in ("wait", "check"):
        w = sp.add_parser(name); w.add_argument("--job", required=True); w.add_argument("--timeout", type=int, default=1800)
    args = ap.parse_args()
    JOBS = Path(os.environ.get("COMFY_JOBS", ROOT / "jobs" / args.project))
    if args.cmd == "image":
        prompt = args.prompt_file.read_text().strip()
        g, node = flux_graph(prompt, args.ref, args.width, args.height, args.seed, f"{args.project}/{args.job}", args.steps,
                             args.init, args.denoise, args.mask)
        submit(args.job, g, node, args.ref + ([args.init] if args.init else []) + ([args.mask] if args.mask else []),
               {"kind": "flux2-klein-4b", "prompt": prompt, "refs": args.ref, "w": args.width, "h": args.height, "seed": args.seed,
                "steps": args.steps, "init": args.init, "denoise": args.denoise, "mask": args.mask})
    elif args.cmd == "video":
        prompt = args.prompt_file.read_text().strip()
        assert (args.frames - 1) % 8 == 0, "LTX length must be 8n+1"
        g, node = ltx_graph(prompt, args.first, args.last, args.width, args.height, args.frames, args.seed, f"{args.project}/{args.job}",
                            args.strength, args.audio, args.audio_start)
        ins = [args.first] + ([args.last] if args.last else []) + ([args.audio] if args.audio else [])
        submit(args.job, g, node, ins, {"kind": "ltx-2.5-distilled-gguf", "prompt": prompt, "first": args.first, "last": args.last,
                                        "w": args.width, "h": args.height, "frames": args.frames, "seed": args.seed,
                                        "guide_strength": args.strength, "audio": args.audio, "audio_start": args.audio_start})
    elif args.cmd == "h3":
        prompt = args.prompt_file.read_text().strip()
        g, node = h3_graph(prompt, args.first, args.last, args.width, args.height, args.frames, args.seed, f"{args.project}/{args.job}")
        submit(args.job, g, node, [args.first] + ([args.last] if args.last else []),
               {"kind": "minimax-h3-int8+turbo8", "prompt": prompt, "first": args.first, "last": args.last, "w": args.width,
                "h": args.height, "frames": args.frames, "seed": args.seed})
    elif args.cmd == "qedit":
        prompt = args.prompt_file.read_text().strip()
        g, node = qedit_graph(prompt, args.image, args.seed, f"{args.project}/{args.job}", args.steps)
        submit(args.job, g, node, args.image, {"kind": "qwen-image-edit-2511-Q5_K_M+lightning8", "prompt": prompt, "images": args.image,
                                               "seed": args.seed, "steps": args.steps})
    elif args.cmd == "wait":
        check(args.job, True, args.timeout)
    elif args.cmd == "check":
        check(args.job, False)


if __name__ == "__main__":
    main()
