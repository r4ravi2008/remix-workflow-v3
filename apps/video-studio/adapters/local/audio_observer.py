"""Bounded audio-model diagnostic. Observations never become creative approval."""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import signal
import socket
import time
import urllib.request
import uuid


MODEL = "Qwen/Qwen2-Audio-7B-Instruct"
REVISION = "0a095220c30b7b31434169c3086508ef3ea5bf0a"
SHARED_LEASE = Path("/home/r4ravi2008/projects/remix-workflow-v3/runs/.gpu-inference-lease.json")
QUESTION = "Describe the audible instruments, vocal presence, rhythm and changes in this attached mono excerpt. State uncertainty. The model receives one mono channel, so stereo placement and left/right movement cannot be observed. Do not infer artist identity, lyric words, precise timestamps or events outside the excerpt. Your answer is an observation, not approval of audio quality or a video."


def digest(path):
    result = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def save_new(path, value):
    with path.open("x") as target:
        json.dump(value, target, indent=2, ensure_ascii=False, allow_nan=False)
        target.write("\n")
        target.flush()
        os.fsync(target.fileno())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("request", type=Path)
    args = parser.parse_args()
    if os.environ.get("HERDR_ENV") != "1" or socket.gethostname() != "rkwindows11":
        raise RuntimeError("Run inside the existing Herdr GPU workstation shell")
    request_path = args.request.resolve(strict=True)
    root = request_path.parent
    request = json.loads(request_path.read_text())
    expected = {"schema", "attempt", "source_file", "source_sha256", "source_bytes", "source_rate", "source_channels", "source_sample_frames", "start_sample", "sample_count", "model_snapshot", "output_file"}
    if set(request) != expected or request["schema"] != 1:
        raise ValueError("Unexpected diagnostic request schema")
    uuid.UUID(request["attempt"])
    for key in ["source_rate", "source_channels", "source_sample_frames", "start_sample", "sample_count"]:
        if type(request[key]) is not int:
            raise ValueError("Audio clocks must be integers")
    if not 0 <= request["start_sample"] < request["start_sample"] + request["sample_count"] <= request["source_sample_frames"]:
        raise ValueError("Requested audio range is outside the source")
    if not 1 <= request["sample_count"] / request["source_rate"] <= 30:
        raise ValueError("Observer range must be bounded to 1..30 seconds")
    source = (root / request["source_file"]).resolve(strict=True)
    output = (root / request["output_file"]).resolve()
    if source.parent != root or output.parent != root or output.exists() or source == output:
        raise ValueError("Use fresh output and owned input paths")
    if source.stat().st_size != request["source_bytes"] or digest(source) != request["source_sha256"]:
        raise ValueError("The transferred canonical source differs from its binding")
    snapshot = Path(request["model_snapshot"]).resolve(strict=True)
    if snapshot.name != REVISION or not (snapshot / "config.json").is_file():
        raise ValueError("Use the exact installed model snapshot")
    index = snapshot / "model.safetensors.index.json"
    weights = sorted(set(json.loads(index.read_text())["weight_map"].values()))
    model_files = [snapshot / name for name in weights]
    if not model_files or any(not file.is_file() for file in model_files):
        raise ValueError("Model shards are incomplete")
    with urllib.request.urlopen("http://127.0.0.1:8188/queue", timeout=5) as response:
        queue = json.load(response)
    if queue.get("queue_running") or queue.get("queue_pending"):
        raise RuntimeError("Another ComfyUI job owns the GPU")
    owner = {"service": "video-studio", "purpose": "bounded-audio-observer", "job_id": request["attempt"], "owner_id": str(uuid.uuid4()), "pid": os.getpid(), "reserved_epoch": time.time(), "request_sha256": digest(request_path)}
    save_new(SHARED_LEASE, owner)
    started = time.time()
    receipt = {"schema": 1, "state": "failed", "request": request, "request_sha256": owner["request_sha256"], "runner_sha256": digest(Path(__file__).resolve()), "host": socket.gethostname(), "owner": owner, "model": MODEL, "model_revision": REVISION, "prompt_sha256": hashlib.sha256(QUESTION.encode()).hexdigest(), "audio_model_observed": False, "full_song_heard": False, "full_playback_watched": False, "semantic_findings_verified": False, "creative_accepted": False}
    def deadline(_signum, _frame):
        raise TimeoutError("Bounded model observer exceeded 900 seconds")
    signal.signal(signal.SIGALRM, deadline)
    signal.alarm(900)
    try:
        print("OBSERVER_RESERVED", flush=True)
        import numpy as np
        import soundfile as sf
        import librosa
        import torch
        from transformers import AutoProcessor, BitsAndBytesConfig, Qwen2AudioForConditionalGeneration
        if not torch.cuda.is_available():
            raise RuntimeError("The local CUDA GPU is unavailable")
        free, total = torch.cuda.mem_get_info()
        if free < 10 * 1024 ** 3:
            raise RuntimeError("Insufficient GPU headroom; preserve other workloads")
        receipt["gpu"] = {"name": torch.cuda.get_device_name(0), "free_before": free, "total": total}
        receipt["dependencies"] = {name: importlib.metadata.version(name) for name in ["torch", "transformers", "bitsandbytes", "librosa", "soundfile", "accelerate"]}
        receipt["model_files"] = [{"name": file.name, "bytes": file.stat().st_size, "sha256": digest(file)} for file in [snapshot / "config.json", index, *model_files]]
        with sf.SoundFile(source) as sound:
            if (sound.samplerate, sound.channels, sound.frames) != (request["source_rate"], request["source_channels"], request["source_sample_frames"]):
                raise ValueError("Canonical source layout differs from its measured binding")
            sound.seek(request["start_sample"])
            selected = sound.read(request["sample_count"], dtype="float32", always_2d=True)
        if selected.shape != (request["sample_count"], request["source_channels"]) or not np.isfinite(selected).all():
            raise ValueError("Selected PCM does not cover the exact range")
        samples = librosa.resample(selected.mean(axis=1), orig_sr=request["source_rate"], target_sr=16000, res_type="soxr_hq")
        expected_samples = request["sample_count"] * 16000 // request["source_rate"]
        if len(samples) != expected_samples or not np.isfinite(samples).all():
            raise ValueError("Observer preprocessing lost audio coverage")
        receipt["preprocessing"] = {"source_sample_span": {"start": request["start_sample"], "length": request["sample_count"]}, "source_pcm_sha256": hashlib.sha256(selected.tobytes()).hexdigest(), "channel_operation": "arithmetic mean", "resample": "librosa soxr_hq", "model_sample_rate": 16000, "model_sample_frames": len(samples), "model_pcm_sha256": hashlib.sha256(samples.tobytes()).hexdigest()}
        processor = AutoProcessor.from_pretrained(str(snapshot), local_files_only=True, trust_remote_code=False)
        if processor.feature_extractor.sampling_rate != 16000:
            raise ValueError("Model processor changed sample clock")
        conversation = [{"role": "user", "content": [{"type": "audio", "audio_url": str(source)}, {"type": "text", "text": QUESTION}]}]
        text = processor.apply_chat_template(conversation, add_generation_prompt=True, tokenize=False)
        inputs = processor(text=text, audio=[samples], sampling_rate=16000, return_tensors="pt", padding=True)
        if "input_features" not in inputs or "feature_attention_mask" not in inputs:
            raise ValueError("Text-only model input cannot be recorded as audio observation")
        attended = int(inputs.feature_attention_mask.sum())
        tokens = int((inputs.input_ids == processor.audio_token_id).sum())
        expected_features = len(samples) / processor.feature_extractor.hop_length
        if abs(attended - expected_features) > 1 or tokens <= 0:
            raise ValueError("Actual attended audio features do not cover the source range")
        receipt["model_input"] = {"feature_shape": list(inputs.input_features.shape), "attended_audio_features": attended, "audio_tokens": tokens, "features_sha256": hashlib.sha256(inputs.input_features.numpy().tobytes()).hexdigest(), "input_ids_sha256": hashlib.sha256(inputs.input_ids.numpy().tobytes()).hexdigest()}
        print("OBSERVER_LOADING_MODEL", flush=True)
        quantization = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.bfloat16, llm_int8_skip_modules=["audio_tower", "model.audio_tower", "multi_modal_projector", "model.multi_modal_projector"])
        model = Qwen2AudioForConditionalGeneration.from_pretrained(str(snapshot), local_files_only=True, trust_remote_code=False, device_map={"": 0}, quantization_config=quantization, dtype=torch.bfloat16, attn_implementation="sdpa").eval()
        if any(type(module).__name__ == "Linear4bit" for name, module in model.named_modules() if "audio_tower" in name):
            raise ValueError("Audio encoder precision changed")
        torch.cuda.reset_peak_memory_stats()
        print("OBSERVER_INFERENCE", flush=True)
        with torch.inference_mode():
            result = model.generate(**inputs.to("cuda"), max_new_tokens=160, do_sample=False)
        generated = result[:, inputs.input_ids.shape[1]:]
        response = processor.batch_decode(generated, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
        if not response.strip():
            raise ValueError("Observer returned no observation")
        receipt.update({"state": "observed-unreviewed", "audio_model_observed": True, "raw_observation": response, "generated_tokens": int(generated.shape[1]), "peak_gpu_bytes": torch.cuda.max_memory_allocated()})
    except BaseException as error:
        receipt["error"] = {"type": type(error).__name__, "detail": str(error)}
        raise
    finally:
        signal.alarm(0)
        receipt["elapsed_seconds"] = time.time() - started
        save_new(output, receipt)
        if SHARED_LEASE.is_file() and json.loads(SHARED_LEASE.read_text()) == owner:
            SHARED_LEASE.unlink()
        print("OBSERVER_TERMINAL " + receipt["state"], flush=True)


if __name__ == "__main__":
    main()
