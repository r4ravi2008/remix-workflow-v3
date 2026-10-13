"""Blind, source-bound local audio controls. No creative acceptance claims."""
import argparse
import gc
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

from audio_observer import SHARED_LEASE, digest, save_new

MODEL = "Qwen/Qwen2.5-Omni-7B"
REVISION = "ae9e1690543ffd5c0221dc27f79834d0294cba00"
QUESTIONS = [
    ("description", "Describe the sounds you hear in this attached mono recording. Include audible instruments, rhythm and changes if music is present. State uncertainty. Do not guess exact BPM, key, duration, timestamps, artist identity or stereo position."),
    ("speech", "Transcribe the clear speech you hear in this attached recording. If no clear speech is audible, say so. Do not add commentary or infer unheard words."),
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("request", type=Path)
    args = parser.parse_args()
    if os.environ.get("HERDR_ENV") != "1" or socket.gethostname() != "rkwindows11":
        raise RuntimeError("Use the existing Herdr workstation shell")
    request_path = args.request.resolve(strict=True)
    root = request_path.parent
    request = json.loads(request_path.read_text())
    if set(request) != {"schema", "attempt", "model_snapshot", "clips", "output_file"} or request["schema"] != 1:
        raise ValueError("Unexpected qualification request schema")
    uuid.UUID(request["attempt"])
    if not 1 <= len(request["clips"]) <= 4:
        raise ValueError("Qualification is bounded to four clips")
    output = (root / request["output_file"]).resolve()
    if output.parent != root or output.exists():
        raise ValueError("Use a fresh owned output")
    snapshot = Path(request["model_snapshot"]).resolve(strict=True)
    if snapshot.name != REVISION:
        raise ValueError("Use the exact installed Omni snapshot")
    sources = []
    for clip in request["clips"]:
        keys = {"id", "file", "sha256", "bytes", "rate", "channels", "frames", "start", "count"}
        if set(clip) != keys or any(type(clip[k]) is not int for k in ["bytes", "rate", "channels", "frames", "start", "count"]):
            raise ValueError("Unexpected source binding")
        if clip["rate"] <= 0 or clip["channels"] not in [1, 2] or not 0 <= clip["start"] < clip["start"] + clip["count"] <= clip["frames"]:
            raise ValueError("Invalid source clock or sample span")
        if not 1 <= clip["count"] / clip["rate"] <= 30:
            raise ValueError("Each observed range must be 1..30 seconds")
        source = (root / clip["file"]).resolve(strict=True)
        if source.parent != root or source == output or source.stat().st_size != clip["bytes"] or digest(source) != clip["sha256"]:
            raise ValueError("Transferred source differs from its binding")
        sources.append(source)
    index = snapshot / "model.safetensors.index.json"
    weights = sorted(set(json.loads(index.read_text())["weight_map"].values()))
    def idle():
        with urllib.request.urlopen("http://127.0.0.1:8188/queue", timeout=5) as response:
            queue = json.load(response)
        if queue.get("queue_running") or queue.get("queue_pending"):
            raise RuntimeError("Another ComfyUI job owns the GPU")
    idle()
    owner = {"service": "video-studio", "purpose": "blind-omni-qualification", "job_id": request["attempt"], "owner_id": str(uuid.uuid4()), "pid": os.getpid(), "reserved_epoch": time.time(), "request_sha256": digest(request_path)}
    save_new(SHARED_LEASE, owner)
    started = time.time()
    receipt = {"schema": 1, "state": "failed", "request": request, "request_sha256": owner["request_sha256"], "runner_sha256": digest(Path(__file__)), "helper_sha256": digest(Path(__file__).with_name("audio_observer.py")), "host": socket.gethostname(), "owner": owner, "model": MODEL, "revision": REVISION, "prompt_sha256": hashlib.sha256(json.dumps(QUESTIONS, separators=(',', ':')).encode()).hexdigest(), "observations": [], "full_song_heard": False, "full_playback_watched": False, "semantic_findings_verified": False, "creative_accepted": False}
    torch = None
    model = None
    def deadline(_signum, _frame):
        raise TimeoutError("Qualification exceeded 900 seconds")
    signal.signal(signal.SIGALRM, deadline)
    signal.alarm(900)
    try:
        idle()
        print("OMNI_RESERVED", flush=True)
        import numpy as np
        import soundfile as sf
        import librosa
        import torch
        from transformers import AutoProcessor, BitsAndBytesConfig, Qwen2_5OmniConfig, Qwen2_5OmniThinkerForConditionalGeneration
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA is unavailable")
        free, total = torch.cuda.mem_get_info()
        if free < 10 * 1024 ** 3:
            raise RuntimeError("Insufficient GPU headroom")
        receipt["gpu"] = {"name": torch.cuda.get_device_name(0), "free_before": free, "total": total}
        receipt["dependencies"] = {name: importlib.metadata.version(name) for name in ["torch", "transformers", "bitsandbytes", "librosa", "soundfile", "accelerate"]}
        receipt["model_files"] = [{"name": p.name, "bytes": p.stat().st_size, "sha256": digest(p)} for p in [snapshot / "config.json", index, *(snapshot / name for name in weights)]]
        processor = AutoProcessor.from_pretrained(str(snapshot), local_files_only=True, trust_remote_code=False)
        if processor.feature_extractor.sampling_rate != 16000:
            raise ValueError("Processor audio clock changed")
        config = Qwen2_5OmniConfig.from_pretrained(str(snapshot), local_files_only=True).thinker_config
        quantization = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.bfloat16, llm_int8_skip_modules=["audio_tower", "visual", "lm_head"])
        print("OMNI_LOADING", flush=True)
        model, loading = Qwen2_5OmniThinkerForConditionalGeneration.from_pretrained(str(snapshot), config=config, local_files_only=True, trust_remote_code=False, device_map={"": 0}, quantization_config=quantization, dtype=torch.bfloat16, attn_implementation="sdpa", output_loading_info=True)
        if loading.get("missing_keys") or loading.get("mismatched_keys") or loading.get("error_msgs") or any(not name.startswith(("talker.", "token2wav.")) for name in loading.get("unexpected_keys", [])):
            raise ValueError("Thinker model weights did not load completely")
        receipt["model_load"] = {"missing_keys": 0, "mismatched_keys": 0, "discarded_generation_keys": len(loading.get("unexpected_keys", []))}
        if any(type(module).__name__ == "Linear4bit" for name, module in model.named_modules() if "audio_tower" in name or "visual" in name):
            raise ValueError("Sensory encoder precision changed")
        if any(p.device.type != "cuda" for p in model.parameters()):
            raise ValueError("Model unexpectedly offloaded outside the GPU")
        audio_token = processor.tokenizer.convert_tokens_to_ids(processor.audio_token)
        if audio_token != model.config.audio_token_index:
            raise ValueError("Processor and model audio tokens differ")
        model.eval()
        eos = processor.tokenizer.eos_token_id
        if eos != model.config.eos_token_id or eos is None:
            raise ValueError("Tokenizer and thinker end-of-response tokens differ")
        receipt["generation"] = {"stored_eos": model.generation_config.eos_token_id, "effective_eos": eos, "effective_pad": processor.tokenizer.pad_token_id, "max_new_tokens": 160}
        torch.cuda.reset_peak_memory_stats()
        for clip, source in zip(request["clips"], sources, strict=True):
            with sf.SoundFile(source) as sound:
                if (sound.samplerate, sound.channels, sound.frames) != (clip["rate"], clip["channels"], clip["frames"]):
                    raise ValueError("Measured source layout changed")
                sound.seek(clip["start"])
                selected = sound.read(clip["count"], dtype="float32", always_2d=True)
            if selected.shape != (clip["count"], clip["channels"]) or not np.isfinite(selected).all():
                raise ValueError("Incomplete or nonfinite source samples")
            mono = selected.mean(axis=1)
            samples = librosa.resample(mono, orig_sr=clip["rate"], target_sr=16000, res_type="soxr_hq")
            if abs(len(samples) - clip["count"] * 16000 / clip["rate"]) > 1 or not np.isfinite(samples).all():
                raise ValueError("Resampling lost coverage")
            for question_id, prompt in QUESTIONS:
                messages = [{"role": "system", "content": [{"type": "text", "text": "You analyze only the attached audio. End your answer after reporting its audible content."}]}, {"role": "user", "content": [{"type": "audio", "audio": str(source)}, {"type": "text", "text": prompt}]}]
                text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                inputs = processor(text=text, audio=[samples], sampling_rate=16000, return_tensors="pt", padding=True)
                attended = int(inputs.feature_attention_mask.sum())
                tokens = int((inputs.input_ids == audio_token).sum())
                if abs(attended - len(samples) / processor.feature_extractor.hop_length) > 1 or tokens <= 0:
                    raise ValueError("Actual audio features do not cover the selected range")
                observed = {"clip": clip["id"], "question": question_id, "source_pcm_sha256": hashlib.sha256(selected.tobytes()).hexdigest(), "model_sample_rate": 16000, "model_sample_frames": len(samples), "model_pcm_sha256": hashlib.sha256(samples.tobytes()).hexdigest(), "feature_shape": list(inputs.input_features.shape), "attended_audio_features": attended, "audio_tokens": tokens, "features_sha256": hashlib.sha256(inputs.input_features.numpy().tobytes()).hexdigest(), "input_ids_sha256": hashlib.sha256(inputs.input_ids.numpy().tobytes()).hexdigest()}
                inputs = {key: value.to("cuda", dtype=torch.bfloat16) if value.is_floating_point() else value.to("cuda") for key, value in inputs.items()}
                print("OMNI_INFERENCE " + clip["id"] + " " + question_id, flush=True)
                with torch.inference_mode():
                    result = model.generate(**inputs, max_new_tokens=160, do_sample=False, eos_token_id=eos, pad_token_id=processor.tokenizer.pad_token_id)
                generated = result[:, inputs["input_ids"].shape[1]:]
                observed["raw_observation"] = processor.batch_decode(generated, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
                observed["generated_tokens"] = int(generated.shape[1])
                observed["ended_with_eos"] = int(generated[0, -1]) == eos
                if not observed["raw_observation"].strip():
                    raise ValueError("Empty observation")
                receipt["observations"].append(observed)
                save_new(root / (clip["id"] + "-" + question_id + "-observation.json"), observed)
                del inputs, result, generated
        if any(source.stat().st_size != clip["bytes"] or digest(source) != clip["sha256"] for source, clip in zip(sources, request["clips"], strict=True)):
            raise ValueError("Sources changed during observation")
        receipt["gpu"]["peak_bytes"] = torch.cuda.max_memory_allocated()
        receipt["state"] = "observed-unreviewed"
    except BaseException as error:
        receipt["error"] = {"type": type(error).__name__, "detail": str(error)}
        raise
    finally:
        signal.alarm(0)
        model = None
        gc.collect()
        if torch is not None and torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
        receipt["elapsed_seconds"] = time.time() - started
        try:
            save_new(output, receipt)
        finally:
            if SHARED_LEASE.is_file() and json.loads(SHARED_LEASE.read_text()) == owner:
                SHARED_LEASE.unlink()
        print("OMNI_TERMINAL " + receipt["state"], flush=True)


if __name__ == "__main__":
    main()
