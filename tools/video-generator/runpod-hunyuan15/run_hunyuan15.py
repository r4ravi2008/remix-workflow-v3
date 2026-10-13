#!/usr/bin/env python3
"""Run full-quality HunyuanVideo-1.5 I2V plus its learned 1080p SR stage."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


COMFY_ROOT = Path("/workspace/urvashi-hunyuan15/ComfyUI")
SERVER = "http://127.0.0.1:8189"


def request_json(path: str, body: dict | None = None) -> dict:
    data = None if body is None else json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        SERVER + path,
        data=data,
        headers={"Content-Type": "application/json"},
        method="GET" if body is None else "POST",
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.load(response)


def build_prompt(args: argparse.Namespace, uploaded_name: str) -> dict:
    ref = lambda node, slot=0: [str(node), slot]
    prompt = {
        "81": {
            "class_type": "CLIPVisionLoader",
            "inputs": {"clip_name": "sigclip_vision_patch14_384.safetensors"},
        },
        "11": {
            "class_type": "DualCLIPLoader",
            "inputs": {
                "clip_name1": "qwen_2.5_vl_7b.safetensors",
                "clip_name2": "byt5_small_glyphxl_fp16.safetensors",
                "type": "hunyuan_video_15",
                "device": "default",
            },
        },
        "108": {
            "class_type": "LatentUpscaleModelLoader",
            "inputs": {"model_name": "hunyuanvideo15_latent_upsampler_1080p.safetensors"},
        },
        "111": {
            "class_type": "UNETLoader",
            "inputs": {
                "unet_name": "hunyuanvideo1.5_1080p_sr_distilled_fp16.safetensors",
                "weight_dtype": "default",
            },
        },
        "79": {
            "class_type": "CLIPVisionEncode",
            "inputs": {"clip_vision": ref(81), "image": ref(80), "crop": "center"},
        },
        "93": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": args.negative_prompt, "clip": ref(11)},
        },
        "10": {
            "class_type": "VAELoader",
            "inputs": {"vae_name": "hunyuanvideo15_vae_fp16.safetensors"},
        },
        "78": {
            "class_type": "HunyuanVideo15ImageToVideo",
            "inputs": {
                "positive": ref(44),
                "negative": ref(93),
                "vae": ref(10),
                "width": args.width,
                "height": args.height,
                "length": args.frames,
                "batch_size": 1,
                "start_image": ref(80),
                "clip_vision_output": ref(79),
            },
        },
        "12": {
            "class_type": "UNETLoader",
            "inputs": {
                "unet_name": "hunyuanvideo1.5_720p_i2v_fp16.safetensors",
                "weight_dtype": "default",
            },
        },
        "44": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": args.prompt, "clip": ref(11)},
        },
        "80": {"class_type": "LoadImage", "inputs": {"image": uploaded_name}},
        "126": {
            "class_type": "BasicScheduler",
            "inputs": {"model": ref(130), "scheduler": "simple", "steps": args.steps, "denoise": 1.0},
        },
        "127": {"class_type": "RandomNoise", "inputs": {"noise_seed": args.seed}},
        "128": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}},
        "129": {
            "class_type": "CFGGuider",
            "inputs": {"model": ref(130), "positive": ref(78, 0), "negative": ref(78, 1), "cfg": 6.0},
        },
        "130": {"class_type": "ModelSamplingSD3", "inputs": {"model": ref(12), "shift": 7.0}},
        "125": {
            "class_type": "SamplerCustomAdvanced",
            "inputs": {
                "noise": ref(127),
                "guider": ref(129),
                "sampler": ref(128),
                "sigmas": ref(126),
                "latent_image": ref(78, 2),
            },
        },
        "131": {"class_type": "RandomNoise", "inputs": {"noise_seed": args.seed + 1}},
        "132": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}},
        "133": {"class_type": "ModelSamplingSD3", "inputs": {"model": ref(111), "shift": 2.0}},
        "134": {
            "class_type": "BasicScheduler",
            "inputs": {"model": ref(111), "scheduler": "simple", "steps": 8, "denoise": 1.0},
        },
        "135": {"class_type": "SplitSigmas", "inputs": {"sigmas": ref(134), "step": 4}},
        "137": {"class_type": "DisableNoise", "inputs": {}},
        "138": {
            "class_type": "SamplerCustomAdvanced",
            "inputs": {
                "noise": ref(131),
                "guider": ref(141),
                "sampler": ref(132),
                "sigmas": ref(135, 0),
                "latent_image": ref(113, 2),
            },
        },
        "139": {
            "class_type": "SamplerCustomAdvanced",
            "inputs": {
                "noise": ref(137),
                "guider": ref(140),
                "sampler": ref(132),
                "sigmas": ref(135, 1),
                "latent_image": ref(138),
            },
        },
        "140": {
            "class_type": "CFGGuider",
            "inputs": {"model": ref(111), "positive": ref(44), "negative": ref(93), "cfg": 1.0},
        },
        "141": {
            "class_type": "CFGGuider",
            "inputs": {"model": ref(133), "positive": ref(113, 0), "negative": ref(113, 1), "cfg": 1.0},
        },
        "109": {
            "class_type": "HunyuanVideo15LatentUpscaleWithModel",
            "inputs": {
                "model": ref(108),
                "samples": ref(125),
                "upscale_method": "bilinear",
                "width": args.sr_width,
                "height": args.sr_height,
                "crop": "disabled",
            },
        },
        "113": {
            "class_type": "HunyuanVideo15SuperResolution",
            "inputs": {
                "positive": ref(44),
                "negative": ref(93),
                "latent": ref(109),
                "vae": ref(10),
                "start_image": ref(80),
                "clip_vision_output": ref(79),
                "noise_augmentation": 0.7,
            },
        },
        "117": {"class_type": "VAEDecode", "inputs": {"samples": ref(139), "vae": ref(10)}},
        "114": {"class_type": "CreateVideo", "inputs": {"images": ref(117), "fps": 24.0}},
        "118": {
            "class_type": "SaveVideo",
            "inputs": {
                "video": ref(114),
                "filename_prefix": args.output_prefix,
                "format": {"format": "mp4", "codec": {"codec": "h264", "encoding": {"encoding": "re-encode", "crf": args.crf}}},
            },
        },
    }
    if args.stage == "base":
        for node in (108, 109, 111, 113, 131, 132, 133, 134, 135, 137, 138, 139, 140, 141):
            del prompt[str(node)]
        prompt["117"]["inputs"]["samples"] = ref(125)
    elif args.stage == "sr":
        if not args.latent:
            raise ValueError("SR-only requires --latent from the same anchor and base generation")
        for node in (12, 78, 125, 126, 127, 128, 129, 130):
            del prompt[str(node)]
        prompt["150"] = {"class_type": "LoadLatent", "inputs": {"latent": args.latent}}
        prompt["109"]["inputs"]["samples"] = ref(150)
    if args.save_latent and args.stage != "sr":
        prompt["151"] = {"class_type": "SaveLatent", "inputs": {"samples": ref(125), "filename_prefix": args.output_prefix + "-base"}}
    if args.tiled_vae:
        samples = prompt["117"]["inputs"]["samples"]
        prompt["117"] = {"class_type": "VAEDecodeTiled", "inputs": {"samples": samples, "vae": ref(10), "tile_size": 512, "overlap": 64, "temporal_size": 4096, "temporal_overlap": 8}}
    return prompt


def wait_for_completion(prompt_id: str, poll_seconds: int, max_seconds: int) -> dict:
    started = time.monotonic()
    while True:
        history = request_json(f"/history/{prompt_id}")
        if prompt_id in history:
            record = history[prompt_id]
            status = record.get("status", {})
            if status.get("status_str") == "error" or any(m[0] in ("execution_error", "execution_interrupted") for m in status.get("messages", [])):
                raise RuntimeError(json.dumps(record, indent=2))
            if status.get("completed"):
                if status.get("status_str") != "success":
                    raise RuntimeError(json.dumps(record, indent=2))
                print(json.dumps({"event": "completed", "elapsed_seconds": round(time.monotonic() - started, 1)}))
                return record
        if time.monotonic() - started >= max_seconds:
            request_json("/interrupt", {})
            raise TimeoutError(f"Job {prompt_id} exceeded {max_seconds}s; interrupted GPU execution")
        queue = request_json("/queue")
        print(
            json.dumps(
                {
                    "event": "waiting",
                    "elapsed_seconds": round(time.monotonic() - started, 1),
                    "queue_running": len(queue.get("queue_running", [])),
                    "queue_pending": len(queue.get("queue_pending", [])),
                }
            ),
            flush=True,
        )
        time.sleep(poll_seconds)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--negative-prompt", default="cartoon, anime, illustration, plastic skin, waxy face, over-smoothed skin, warped hands, extra fingers, deformed anatomy, duplicated people, identity drift, flicker, frame jitter, low resolution, blur, text, subtitles, watermark")
    parser.add_argument("--output-prefix", required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--steps", type=int, default=50)
    parser.add_argument("--frames", type=int, default=121)
    parser.add_argument("--stage", choices=("base", "sr", "full"), default="full")
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument("--sr-width", type=int, default=1920)
    parser.add_argument("--sr-height", type=int, default=1088)
    parser.add_argument("--tiled-vae", action="store_true")
    parser.add_argument("--save-latent", action="store_true")
    parser.add_argument("--latent")
    parser.add_argument("--crf", type=int, default=16)
    parser.add_argument("--max-seconds", type=int, default=1800)
    parser.add_argument("--record", type=Path)
    parser.add_argument("--expected-sha256")
    parser.add_argument("--poll-seconds", type=int, default=20)
    parser.add_argument("--validate-only", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.input.is_file():
        raise FileNotFoundError(args.input)
    digest = hashlib.sha256(args.input.read_bytes()).hexdigest()
    if args.expected_sha256 and digest != args.expected_sha256:
        raise ValueError("Anchor input changed after acceptance; refusing paid generation")
    if any(d % 16 for d in (args.width, args.height, args.sr_width, args.sr_height)):
        raise ValueError("All generation dimensions must be divisible by 16")
    if args.frames < 1 or (args.frames - 1) % 4:
        raise ValueError("Hunyuan frame count must be 4n+1")
    if args.validate_only:
        print(json.dumps(build_prompt(args, args.input.name), indent=2))
        return 0

    destination = COMFY_ROOT / "input" / args.input.name
    if args.input.resolve() != destination.resolve():
        shutil.copy2(args.input, destination)

    prompt = build_prompt(args, destination.name)
    started = time.time()
    try:
        result = request_json("/prompt", {"prompt": prompt, "client_id": "urvashi-hunyuan15"})
    except urllib.error.HTTPError as error:
        print(error.read().decode("utf-8", errors="replace"), file=sys.stderr)
        raise
    if result.get("node_errors"):
        raise RuntimeError(json.dumps(result, indent=2))
    prompt_id = result["prompt_id"]
    journal = {"prompt_id": prompt_id, "started_at_unix": started, "input": str(args.input), "input_sha256": digest, "stage": args.stage, "prompt": prompt, "status": "queued"}
    if args.record:
        args.record.parent.mkdir(parents=True, exist_ok=True)
        args.record.write_text(json.dumps(journal, indent=2))
    print(json.dumps({"event": "queued", "prompt_id": prompt_id}), flush=True)
    record = wait_for_completion(prompt_id, args.poll_seconds, args.max_seconds)
    journal.update(status="generated-unreviewed", elapsed_seconds=time.time()-started, history=record)
    if args.record:
        args.record.write_text(json.dumps(journal, indent=2))
    print(json.dumps(record.get("outputs", {}), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
