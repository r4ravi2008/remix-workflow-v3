"""Pinned local Omni thinker; observations never establish creative acceptance."""
import gc
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid

spec = importlib.util.spec_from_file_location('omni_audio_contract', Path(__file__).with_name('audio-perception.py'))
audio = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audio)
MODEL = 'Qwen/Qwen2.5-Omni-7B'
REVISION = 'ae9e1690543ffd5c0221dc27f79834d0294cba00'
CACHE = audio.RUN / 'director/omni-model-cache'
WEIGHTS = {
    'model-00001-of-00005.safetensors': ('5edb02fd7c98803239468375cc9dc1bff492865c2aa086b78f348597021d6cbc', 4985055504),
    'model-00002-of-00005.safetensors': ('7c99b55c6e5bc63fd4b19d4dc23cdc3ddac4b0101bb3c0958cc2b5d05c2bbafe', 4991496800),
    'model-00003-of-00005.safetensors': ('ad00c3ac296300db905934ed213c4077ff49b85d30c0099270c814e2c77ec812', 4991496904),
    'model-00004-of-00005.safetensors': ('152bc7d81441eaba22547d8d96c03d32dd592ce0e0e1d0e449347a4b23a532d3', 4969489824),
    'model-00005-of-00005.safetensors': ('b8b18276481ba8cdf4fe2c98ac4c7a2da6e0d1c8a51850d162a391760cb2b81e', 2425322160),
}


def download(receipt_path):
    audio.managed()
    output = audio.owned_path(receipt_path)
    if output.exists():
        raise ValueError('Preserve the model provisioning receipt.')
    from huggingface_hub import snapshot_download
    started = time.time()
    receipt = {'model': MODEL, 'revision': REVISION, 'status': 'failed',
               'pid': os.getpid(), 'startedAt': started, 'gpuInferenceSubmitted': False}
    try:
        root = Path(snapshot_download(MODEL, revision=REVISION, cache_dir=str(CACHE),
                    allow_patterns=['*.json', '*.txt', '*.safetensors', 'LICENSE', 'README.md'],
                    max_workers=2))
        measured = []
        for name, (checksum, size) in WEIGHTS.items():
            actual = audio.file_receipt(root / name)
            if actual != {'sha256': checksum, 'bytes': size}:
                raise ValueError('Pinned Omni model weights failed full hash verification.')
            measured.append({'name': name, **actual})
        receipt.update({'status': 'downloaded-and-hash-verified', 'weights': measured,
                        'license': audio.file_receipt(root / 'LICENSE'),
                        'config': audio.file_receipt(root / 'config.json'), 'snapshot': str(root)})
    except BaseException as error:
        receipt.update({'errorType': type(error).__name__, 'error': str(error)[:1200]})
        raise
    finally:
        receipt['elapsedSeconds'] = time.time() - started
        audio.write_new(output, receipt)
        print(json.dumps({'status': receipt['status'], 'receiptPath': str(output)}))


def validate_features(shape, attended_frames, tokens, samples, hop):
    expected_frames = (samples + hop - 1) // hop
    expected_tokens = (((attended_frames - 1) // 2 + 1) - 2) // 2 + 1
    if (list(shape) != [1, 128, 30000] or
            abs(attended_frames - expected_frames) > 1 or shape[2] < attended_frames or
            tokens != expected_tokens or tokens <= 1):
        raise ValueError('Omni features or audio tokens differ from the actual decoded range.')
    return {'featureShape': list(shape), 'attendedFrames': attended_frames, 'audioTokens': tokens}


def validate_loaded_weights(loading):
    unexpected = loading.get('unexpected_keys', [])
    if (loading.get('missing_keys') or loading.get('mismatched_keys') or loading.get('error_msgs') or
            any(not key.startswith(('talker.', 'token2wav.')) for key in unexpected)):
        raise ValueError('The pinned thinker has missing, mismatched or unrecognized model weights.')
    return {'thinkerOnly': True, 'missingKeys': 0, 'mismatchedKeys': 0,
            'discardedAudioGenerationKeys': len(unexpected)}


def inspect(request_path):
    audio.managed()
    request, source, output = audio.read_request(request_path)
    if request['schemaVersion'] != 2:
        raise ValueError('The Omni observer requires the bounded questionnaire contract.')
    audio.idle_queue()
    owner = {'service': 'release-kit-studio', 'purpose': 'omni-audio-perception',
             'job_id': request['jobId'], 'release_id': request['releaseId'],
             'owner_id': str(uuid.uuid4()), 'pid': os.getpid(), 'reserved_epoch': time.time()}
    audio.write_new(audio.LEASE, owner)
    started = time.time()
    torch = None
    model = None
    receipt = {'schemaVersion': 2, 'status': 'failed', 'request': request,
        'source': {'sha256': request['sourceSha256'], 'bytes': request['sourceBytes']},
        'reviewer': {'kind': 'local-audio-model', 'model': MODEL, 'revision': REVISION,
            'quantization': 'nf4-text-bf16-audio-vision-thinker-only',
            'promptSha256': audio.QUESTIONNAIRE_HASH,
            'runnerSha256': audio.file_receipt(Path(__file__))['sha256']},
        'audioPerceptionComplete': False, 'fullSongHeard': False,
        'semanticFindingsVerified': False, 'pilotApproved': False, 'humanAccepted': False}
    try:
        audio.idle_queue()
        import numpy as np
        import torch
        from transformers import AutoProcessor, BitsAndBytesConfig, Qwen2_5OmniConfig, Qwen2_5OmniThinkerForConditionalGeneration
        if not torch.cuda.is_available():
            raise RuntimeError('The Omni observer requires the verified CUDA GPU.')
        free, total = torch.cuda.mem_get_info()
        if free < 10 * 1024 ** 3:
            raise RuntimeError('Insufficient free GPU memory; preserve other workloads.')
        processor = AutoProcessor.from_pretrained(MODEL, revision=REVISION, cache_dir=str(CACHE),
                    local_files_only=True, trust_remote_code=False)
        if processor.feature_extractor.sampling_rate != 16000:
            raise RuntimeError('Omni processor sample rate differs from its pinned contract.')
        pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(source), '-ss', str(request['startSeconds']),
                '-t', str(request['endSeconds'] - request['startSeconds']), '-ac', '1', '-ar', '16000',
                '-f', 'f32le', '-'], check=True, capture_output=True, timeout=90).stdout
        samples = np.frombuffer(pcm, dtype='<f4').copy()
        if abs(len(samples) - round((request['endSeconds'] - request['startSeconds']) * 16000)) > 1:
            raise ValueError('The decoded audio does not cover the requested range.')
        receipt['decodedAudio'] = {'sampleRate': 16000, 'samples': len(samples), 'sha256': hashlib.sha256(pcm).hexdigest()}
        config = Qwen2_5OmniConfig.from_pretrained(MODEL, revision=REVISION,
                    cache_dir=str(CACHE), local_files_only=True, trust_remote_code=False).thinker_config
        model, loading = Qwen2_5OmniThinkerForConditionalGeneration.from_pretrained(MODEL, revision=REVISION, config=config,
            cache_dir=str(CACHE), local_files_only=True, trust_remote_code=False, device_map={'': 0},
            dtype=torch.bfloat16, attn_implementation='sdpa', output_loading_info=True,
            quantization_config=BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type='nf4',
                bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.bfloat16,
                llm_int8_skip_modules=['audio_tower', 'visual', 'lm_head']))
        receipt['modelLoad'] = validate_loaded_weights(loading)
        from bitsandbytes.nn import Linear4bit
        if any(isinstance(module, Linear4bit) for encoder in [model.audio_tower, model.visual] for module in encoder.modules()):
            raise RuntimeError('Omni sensory encoding was unexpectedly quantized.')
        if any(parameter.device.type != 'cuda' for parameter in model.parameters()):
            raise RuntimeError('Omni model was unexpectedly offloaded outside the GPU.')
        audio_token_id = processor.tokenizer.convert_tokens_to_ids(processor.audio_token)
        if audio_token_id != model.config.audio_token_index:
            raise ValueError('Omni processor and thinker audio token identifiers differ.')
        model.eval()
        torch.cuda.reset_peak_memory_stats()
        responses = []
        for prompt in audio.QUESTIONS:
            messages = [{'role': 'system', 'content': [{'type': 'text', 'text': 'You analyze only the supplied audio.'}]},
                {'role': 'user', 'content': [{'type': 'audio', 'audio': str(source)}, {'type': 'text', 'text': prompt}]}]
            text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            inputs = processor(text=text, audio=[samples], sampling_rate=16000, return_tensors='pt', padding=True)
            attended = int(inputs['feature_attention_mask'].sum().item())
            tokens = int((inputs['input_ids'] == audio_token_id).sum().item())
            features = validate_features(inputs['input_features'].shape, attended, tokens, len(samples), processor.feature_extractor.hop_length)
            features['featureSha256'] = hashlib.sha256(inputs['input_features'].numpy().tobytes()).hexdigest()
            receipt['modelAudioInput'] = features
            inputs = {key: value.to('cuda', dtype=torch.bfloat16) if value.is_floating_point() else value.to('cuda') for key, value in inputs.items()}
            with torch.inference_mode():
                ids = model.generate(**inputs, max_new_tokens=220, do_sample=False)
            raw = processor.batch_decode(ids[:, inputs['input_ids'].shape[1]:], skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
            responses.append(audio.observation_record(prompt, raw))
            del inputs, ids
        receipt['observations'] = responses
        receipt['observationContractPassed'] = all(item['usable'] for item in responses)
        if audio.file_receipt(source) != receipt['source']:
            raise RuntimeError('The canonical source changed during Omni inference.')
        receipt.update({'status': 'observed' if receipt['observationContractPassed'] else 'observed-with-issues', 'audioPerceptionComplete': True,
            'gpu': {'name': torch.cuda.get_device_name(0), 'freeBytesBefore': free,
                    'totalBytes': total, 'peakAllocatedBytes': torch.cuda.max_memory_allocated()}})
    except BaseException as error:
        receipt.update({'errorType': type(error).__name__, 'error': str(error)[:1200]})
        raise
    finally:
        model = None
        gc.collect()
        if torch is not None and torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
        receipt['elapsedSeconds'] = time.time() - started
        receipt['observedAt'] = time.time()
        audio.write_new(output, receipt)
        if audio.LEASE.exists() and json.loads(audio.LEASE.read_text()).get('owner_id') == owner['owner_id']:
            audio.LEASE.unlink()
        print(json.dumps({'status': receipt['status'], 'outputPath': str(output), 'fullSongHeard': False}))


if __name__ == '__main__':
    if len(sys.argv) != 3 or sys.argv[1] not in ['download', 'inspect']:
        raise ValueError('Choose fixed download or inspect with an owned request/receipt path.')
    (download if sys.argv[1] == 'download' else inspect)(sys.argv[2])
