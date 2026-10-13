"""Fixed local audio-perception runner; model observations remain separate from acceptance."""
import argparse
import ast
import gc
import hashlib
import json
import math
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import time
import urllib.request
import uuid

MODEL = 'Qwen/Qwen2-Audio-7B-Instruct'
REVISION = '0a095220c30b7b31434169c3086508ef3ea5bf0a'
PROJECT = Path('/home/r4ravi2008/projects/remix-workflow-v3')
RUN = PROJECT / 'runs/release-kit-service'
LEASE = PROJECT / 'runs/.gpu-inference-lease.json'
CACHE = RUN / 'director/model-cache'
PROMPT = '''Analyze only the attached music excerpt. Describe audible instrumentation,
vocal delivery, mood, rhythm and changes within this excerpt. Do not invent lyric
words, section names, visuals, artist identity or events outside the excerpt.
Do not label the recording a cover or judge its production quality.
State uncertainty when unclear. Return a JSON object with these string fields:
description, instruments, vocals, mood, rhythm, changes, uncertainty. Keep each
field concise. Your observations do not approve a video or certify audio quality.'''
QUESTIONS = [
    'Describe the audible sounds in this short excerpt. Is there singing or spoken speech? Do not guess lyrics, language, timestamps, tempo, recording quality, or artist identity.',
    'Describe changes you can hear within this short excerpt, if any. Qualify uncertain changes. Do not provide timestamps, durations, tempo, section names, or events outside the excerpt.',
]
QUESTIONNAIRE_HASH = hashlib.sha256(json.dumps(QUESTIONS, separators=(',', ':')).encode()).hexdigest()


def windows(duration, length=28.0, overlap=2.0):
    if not math.isfinite(duration) or duration <= 0 or not 0 < length <= 30 or not 0 <= overlap < length:
        raise ValueError('Invalid bounded audio-window contract')
    result = []
    start = 0.0
    while start < duration:
        end = min(start + length, duration)
        result.append({'startSeconds': start, 'endSeconds': end})
        if end == duration:
            break
        start = end - overlap
    return result


def file_receipt(path):
    digest = hashlib.sha256()
    count = 0
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
            count += len(block)
    return {'sha256': digest.hexdigest(), 'bytes': count}


def decoded_audio_duration(path):
    pcm = subprocess.run([
        'ffmpeg', '-v', 'error', '-xerror', '-nostdin',
        '-protocol_whitelist', 'file,pipe', '-format_whitelist',
        'wav,mp3,aac,flac,ogg,mov,matroska,webm,aiff,asf',
        '-i', str(path), '-map', '0:a:0', '-vn', '-ac', '1', '-ar', '16000',
        '-t', '900.25', '-f', 's16le', '-',
    ], check=True, capture_output=True, timeout=120).stdout
    if len(pcm) % 2:
        raise ValueError('Decoded audio contains an incomplete PCM sample')
    duration = len(pcm) / 2 / 16000
    if not 0 < duration <= 900:
        raise ValueError('Decoded audio duration is outside the release contract')
    return duration


def managed():
    if os.environ.get('HERDR_ENV') != '1' or socket.gethostname() != 'rkwindows11':
        raise RuntimeError('Use the verified Herdr-managed GPU workstation pane')


def owned_path(raw):
    path = Path(raw).resolve()
    if not path.is_relative_to(RUN.resolve()):
        raise ValueError('Perception inputs and receipts must stay inside the owned service run')
    return path


def write_new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with path.open('x') as stream:
        os.chmod(path, 0o600)
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


def read_request(path):
    request_path = owned_path(path)
    if request_path.stat().st_size > 65536:
        raise ValueError('Perception request exceeds 64 KiB')
    value = json.loads(request_path.read_text())
    required = {'schemaVersion', 'jobId', 'releaseId', 'sourcePath', 'sourceSha256',
                'sourceBytes', 'sourceDuration', 'startSeconds', 'endSeconds', 'outputPath'}
    if not isinstance(value, dict) or set(value) != required or value['schemaVersion'] not in [1, 2]:
        raise ValueError('Invalid perception request fields')
    uuid.UUID(value['jobId'])
    uuid.UUID(value['releaseId'])
    numbers = ['sourceDuration', 'startSeconds', 'endSeconds']
    if any(isinstance(value[key], bool) or not isinstance(value[key], (float, int)) or not math.isfinite(value[key]) for key in numbers):
        raise ValueError('Finite audio ranges are required')
    if not 0 <= value['startSeconds'] < value['endSeconds'] <= value['sourceDuration'] or value['endSeconds'] - value['startSeconds'] > 30:
        raise ValueError('Each actual perception range must cover at most 30 seconds')
    if not isinstance(value['sourceBytes'], int) or isinstance(value['sourceBytes'], bool) or value['sourceBytes'] <= 0:
        raise ValueError('A measured source byte count is required')
    if not isinstance(value['sourceSha256'], str) or len(value['sourceSha256']) != 64 or any(c not in '0123456789abcdef' for c in value['sourceSha256']):
        raise ValueError('A measured source SHA-256 is required')
    source, output = owned_path(value['sourcePath']), owned_path(value['outputPath'])
    if output.exists() or source == output:
        raise ValueError('Preserve existing perception evidence; choose a new receipt path')
    measured = file_receipt(source)
    if measured != {'sha256': value['sourceSha256'], 'bytes': value['sourceBytes']}:
        raise ValueError('Perception source differs from the immutable master')
    actual = decoded_audio_duration(source)
    if abs(actual - value['sourceDuration']) > 0.005:
        raise ValueError('Perception range differs from the measured master duration')
    return value, source, output


def idle_queue():
    with urllib.request.urlopen('http://127.0.0.1:8188/queue', timeout=5) as response:
        queue = json.load(response)
    if queue.get('queue_running') or queue.get('queue_pending'):
        raise RuntimeError('ComfyUI has owned work; preserve it and defer perception')


def parse_findings(raw):
    stripped = raw.strip()
    if stripped.startswith('```'):
        stripped = stripped.split('\n', 1)[1].rsplit('```', 1)[0].strip()
    try:
        value = json.loads(stripped)
    except json.JSONDecodeError:
        if len(stripped) > 16384:
            raise ValueError('Model observation exceeds its normalization limit')
        value = ast.literal_eval(stripped)
    required = {'description', 'instruments', 'vocals', 'mood', 'rhythm', 'changes', 'uncertainty'}
    if isinstance(value, dict) and isinstance(value.get('instruments'), list):
        items = value['instruments']
        if len(items) > 32 or any(not isinstance(item, str) or len(item) > 200 for item in items):
            raise ValueError('Invalid instrument observations')
        value['instruments'] = ', '.join(items)
    if not isinstance(value, dict) or set(value) != required or any(not isinstance(text, str) or len(text) > 3000 for text in value.values()):
        raise ValueError('Audio model output did not match the observation contract')
    return value


def validate_features(shape, attended_frames, audio_tokens, expected_samples, hop_length):
    expected_frames = math.ceil(expected_samples / hop_length)
    expected_tokens = (((attended_frames - 1) // 2 + 1) - 2) // 2 + 1
    if len(shape) != 3 or shape[0] != 1 or shape[1] != 128 or shape[2] != 3000 or abs(attended_frames - expected_frames) > 1 or audio_tokens != expected_tokens or audio_tokens <= 1:
        raise ValueError('Model input does not attend the actual decoded audio range')
    return {'featureShape': list(shape), 'attendedFrames': attended_frames, 'audioTokens': audio_tokens}


def validate_observation(raw):
    import re
    if not isinstance(raw, str) or not 1 <= len(raw.strip()) <= 6000:
        raise ValueError('Model observation is empty or exceeds its limit')
    if re.search(r'\d', raw):
        raise ValueError('Unmeasured model timing or tempo cannot enter audio observations')
    return raw.strip()


def observation_record(prompt, raw):
    try:
        text = validate_observation(raw)
        return {'question': prompt, 'response': text, 'usable': True,
                'issues': [], 'semanticVerified': False}
    except ValueError as error:
        return {'question': prompt, 'response': raw, 'usable': False,
                'issues': [str(error)], 'semanticVerified': False}


def inspect(request_path):
    managed()
    request, source, output = read_request(request_path)
    idle_queue()
    owner = {'service': 'release-kit-studio', 'purpose': 'audio-perception',
             'job_id': request['jobId'], 'release_id': request['releaseId'],
             'owner_id': str(uuid.uuid4()), 'pid': os.getpid(), 'reserved_epoch': time.time()}
    write_new(LEASE, owner)
    started = time.time()
    torch = None
    model = None
    modern = request['schemaVersion'] == 2
    prompts = QUESTIONS if modern else [PROMPT]
    prompt_hash = QUESTIONNAIRE_HASH if modern else hashlib.sha256(PROMPT.encode()).hexdigest()
    receipt = {'schemaVersion': request['schemaVersion'], 'status': 'failed', 'request': request,
               'source': {'sha256': request['sourceSha256'], 'bytes': request['sourceBytes']},
               'reviewer': {'kind': 'local-audio-model', 'model': MODEL, 'revision': REVISION,
                            'quantization': 'nf4-text-bf16-audio' if modern else 'bitsandbytes-nf4', 'promptSha256': prompt_hash,
                            'runnerSha256': file_receipt(Path(__file__))['sha256']},
               'audioPerceptionComplete': False, 'fullSongHeard': False,
               'semanticFindingsVerified': False, 'pilotApproved': False, 'humanAccepted': False}
    try:
        idle_queue()
        import numpy as np
        import torch
        from transformers import AutoProcessor, BitsAndBytesConfig, Qwen2AudioForConditionalGeneration
        if not torch.cuda.is_available():
            raise RuntimeError('The owned audio model requires the verified CUDA GPU')
        free, total = torch.cuda.mem_get_info()
        if free < (10 if modern else 8) * 1024 ** 3:
            raise RuntimeError('Insufficient free GPU memory; preserve other workloads')
        processor = AutoProcessor.from_pretrained(MODEL, revision=REVISION, cache_dir=str(CACHE), local_files_only=True, trust_remote_code=False)
        if processor.feature_extractor.sampling_rate != 16000 or processor.feature_extractor.chunk_length != 30:
            raise RuntimeError('The pinned model processor differs from the verified 30-second contract')
        pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(source), '-ss', str(request['startSeconds']),
                              '-t', str(request['endSeconds'] - request['startSeconds']), '-ac', '1', '-ar', '16000',
                              '-f', 'f32le', '-'], check=True, capture_output=True, timeout=90).stdout
        samples = np.frombuffer(pcm, dtype='<f4').copy()
        expected = round((request['endSeconds'] - request['startSeconds']) * 16000)
        if abs(len(samples) - expected) > 1 or not np.isfinite(samples).all():
            raise RuntimeError('Decoded perception input does not cover its exact source range')
        receipt['decodedAudio'] = {'sampleRate': 16000, 'samples': len(samples), 'sha256': hashlib.sha256(pcm).hexdigest()}
        torch.cuda.reset_peak_memory_stats()
        quantization = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type='nf4',
                                          bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.bfloat16,
                                          llm_int8_skip_modules=['audio_tower', 'model.audio_tower', 'multi_modal_projector', 'model.multi_modal_projector'] if modern else [])
        conversation = [{'role': 'user', 'content': [{'type': 'audio', 'audio_url': str(source)}, {'type': 'text', 'text': prompts[0]}]}]
        text = processor.apply_chat_template(conversation, add_generation_prompt=True, tokenize=False)
        inputs = processor(text=text, audio=[samples], return_tensors='pt', padding=True)
        if 'input_features' not in inputs or 'feature_attention_mask' not in inputs:
            raise ValueError('Processor omitted audio features; text-only guesses cannot count as perception')
        attended = int(inputs.feature_attention_mask.sum().item())
        tokens = int((inputs.input_ids == processor.audio_token_id).sum().item())
        receipt['modelAudioInput'] = {**validate_features(inputs.input_features.shape, attended, tokens, len(samples), processor.feature_extractor.hop_length),
                    'featureSha256': hashlib.sha256(inputs.input_features.numpy().tobytes()).hexdigest()}
        model = Qwen2AudioForConditionalGeneration.from_pretrained(MODEL, revision=REVISION, cache_dir=str(CACHE),
                  local_files_only=True, trust_remote_code=False, device_map={'': 0},
                  quantization_config=quantization, dtype=torch.bfloat16, attn_implementation='sdpa').eval()
        if modern and any(type(module).__name__ == 'Linear4bit' for name, module in model.named_modules() if 'audio_tower' in name):
            raise ValueError('The qualified audio encoder must retain full precision')
        responses = []
        receipt['rawResponses'] = []
        for prompt in prompts:
            conversation[0]['content'][1]['text'] = prompt
            text = processor.apply_chat_template(conversation, add_generation_prompt=True, tokenize=False)
            inputs = processor(text=text, audio=[samples], return_tensors='pt', padding=True).to('cuda')
            validate_features(inputs.input_features.shape, int(inputs.feature_attention_mask.sum().item()), int((inputs.input_ids == processor.audio_token_id).sum().item()), len(samples), processor.feature_extractor.hop_length)
            with torch.inference_mode():
                generated = model.generate(**inputs, max_new_tokens=200 if modern else 512, do_sample=False)
            raw = processor.batch_decode(generated[:, inputs.input_ids.shape[1]:], skip_special_tokens=True,
                                         clean_up_tokenization_spaces=False)[0]
            receipt['rawResponse'] = raw
            receipt['rawResponses'].append({'question': prompt, 'response': raw})
            responses.append(observation_record(prompt, raw) if modern else {'question': prompt, 'response': raw, 'semanticVerified': False})
        receipt['gpu'] = {'name': torch.cuda.get_device_name(0), 'totalBytes': total,
                          'freeBytesBefore': free, 'peakAllocatedBytes': torch.cuda.max_memory_allocated()}
        if modern:
            receipt['observations'] = responses
            receipt['observationContractPassed'] = all(row['usable'] for row in responses)
        else:
            receipt['findings'] = parse_findings(raw)
        if file_receipt(source) != receipt['source']:
            raise RuntimeError('Perception source changed during inference')
        receipt.update({'status': 'observed-with-issues' if modern and not receipt['observationContractPassed'] else 'observed', 'audioPerceptionComplete': True})
    except BaseException as error:
        receipt['errorType'] = type(error).__name__
        receipt['error'] = str(error)[:1200]
        raise
    finally:
        model = None
        gc.collect()
        if torch is not None and torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
        receipt['elapsedSeconds'] = time.time() - started
        receipt['observedAt'] = time.time()
        write_new(output, receipt)
        if LEASE.exists() and json.loads(LEASE.read_text()).get('owner_id') == owner['owner_id']:
            LEASE.unlink()
        print(json.dumps({'status': receipt['status'], 'outputPath': str(output),
                          'audioPerceptionComplete': receipt['audioPerceptionComplete'],
                          'fullSongHeard': False, 'pilotApproved': False, 'humanAccepted': False}))


def inspect_song(request_path):
    managed()
    request = json.loads(owned_path(request_path).read_text())
    fields = {'schemaVersion', 'jobId', 'releaseId', 'sourcePath', 'sourceSha256',
              'sourceBytes', 'sourceDuration', 'outputDirectory'}
    if not isinstance(request, dict) or set(request) != fields or type(request['schemaVersion']) is not int or request['schemaVersion'] not in [1, 2]:
        raise ValueError('Invalid complete-song perception request')
    if not isinstance(request['sourceDuration'], (int, float)) or isinstance(request['sourceDuration'], bool) or not math.isfinite(request['sourceDuration']) or not 0 < request['sourceDuration'] <= 900:
        raise ValueError('A complete-song request must bind at most 900 seconds')
    root = owned_path(request['outputDirectory'])
    final = root / 'song-receipt.json'
    if final.exists():
        raise ValueError('Preserve the complete song receipt; select a new observation attempt')
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    base = {key: value for key, value in request.items() if key != 'outputDirectory'}
    receipts = []
    modern = request['schemaVersion'] == 2
    prompt_hash = QUESTIONNAIRE_HASH if modern else hashlib.sha256(PROMPT.encode()).hexdigest()
    runner_hash = file_receipt(Path(__file__))['sha256']
    for index, window in enumerate(windows(request['sourceDuration'])):
        output = root / f'window-{index:02d}.json'
        planned = {**base, **window, 'outputPath': str(output)}
        input_path = root / f'window-{index:02d}-request.json'
        if not input_path.exists():
            write_new(input_path, planned)
        elif json.loads(input_path.read_text()) != planned:
            raise ValueError('Preserved perception request differs from this song attempt')
        if not output.exists():
            subprocess.run([sys.executable, str(Path(__file__).resolve()), 'inspect', str(input_path)],
                           check=True, timeout=360)
        receipt = json.loads(output.read_text())
        if receipt['status'] not in (['observed', 'observed-with-issues'] if modern else ['observed']) or receipt['request'] != planned or receipt['reviewer']['revision'] != REVISION or receipt['reviewer']['promptSha256'] != prompt_hash or receipt['reviewer'].get('runnerSha256') != runner_hash or receipt['audioPerceptionComplete'] is not True or 'modelAudioInput' not in receipt:
            raise ValueError('A missing, failed or changed window prevents complete-song coverage')
        receipts.append({'startSeconds': window['startSeconds'], 'endSeconds': window['endSeconds'],
                         'receiptPath': str(output), **file_receipt(output),
                         'observations' if modern else 'findings': receipt['observations'] if modern else receipt['findings']})
    if file_receipt(owned_path(request['sourcePath'])) != {'sha256': request['sourceSha256'], 'bytes': request['sourceBytes']}:
        raise ValueError('Master changed before complete-song observation was saved')
    write_new(final, {'schemaVersion': request['schemaVersion'], 'status': 'model-observed-complete-song', 'request': request,
                     'model': MODEL, 'revision': REVISION, 'promptSha256': prompt_hash,
                     'runnerSha256': runner_hash,
                     'windows': receipts, 'modelAudioCoverageComplete': True,
                     'observationContractPassed': all(row.get('usable', False) for window in receipts for row in window.get('observations', [])) if modern else True,
                     'semanticFindingsVerified': False,
                     'lyricTimingVerified': False, 'fullSongHeard': False,
                     'pilotApproved': False, 'humanAccepted': False, 'observedAt': time.time()})
    print(json.dumps({'status': 'model-observed-complete-song', 'outputPath': str(final), 'windows': len(receipts),
                      'modelAudioCoverageComplete': True, 'fullSongHeard': False, 'pilotApproved': False}))


def audit_song(receipt_path, source_path):
    """Independently re-decode every source range; never rewrite model evidence."""
    path, source = Path(receipt_path).resolve(), Path(source_path).resolve()
    if path.stat().st_size > 2 * 1024 ** 2:
        raise ValueError('Song evidence exceeds its bounded size')
    saved = json.loads(path.read_text())
    request = saved['request']
    measured = file_receipt(source)
    actual = float(json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                   'format=duration', '-of', 'json', str(source)], check=True,
                   capture_output=True, text=True, timeout=60).stdout)['format']['duration'])
    if saved.get('schemaVersion') != 2 or saved.get('model') != MODEL or saved.get('revision') != REVISION or saved.get('promptSha256') != QUESTIONNAIRE_HASH or saved.get('modelAudioCoverageComplete') is not True:
        raise ValueError('The complete-song evidence does not bind the pinned questionnaire')
    if measured != {'sha256': request['sourceSha256'], 'bytes': request['sourceBytes']} or not 0 < actual <= 900 or abs(actual - request['sourceDuration']) > 0.005:
        raise ValueError('Audit source differs from the processed canonical master')
    uuid.UUID(request['jobId'])
    uuid.UUID(request['releaseId'])
    planned = windows(request['sourceDuration'])
    if len(planned) != len(saved['windows']):
        raise ValueError('Complete-song evidence has missing or repeated windows')
    findings = []
    for index, (window, record) in enumerate(zip(planned, saved['windows'])):
        if any(record[key] != value for key, value in window.items()):
            raise ValueError('Window evidence leaves a gap or changes its ordered range')
        window_path = path.parent / f'window-{index:02d}.json'
        if window_path.stat().st_size > 2 * 1024 ** 2 or file_receipt(window_path) != {'sha256': record['sha256'], 'bytes': record['bytes']}:
            raise ValueError('Preserved window evidence differs from its recorded checksum')
        row = json.loads(window_path.read_text())
        binding = row['request']
        if row.get('schemaVersion') != 2 or row.get('status') not in ['observed', 'observed-with-issues'] or row.get('audioPerceptionComplete') is not True or row.get('source') != measured:
            raise ValueError('A failed or incomplete window prevents processing coverage')
        for key in ['jobId', 'releaseId', 'sourceSha256', 'sourceBytes', 'sourceDuration']:
            if binding.get(key) != request[key]:
                raise ValueError('Window belongs to a different canonical song or release')
        reviewer = row['reviewer']
        if reviewer.get('model') != MODEL or reviewer.get('revision') != REVISION or reviewer.get('promptSha256') != QUESTIONNAIRE_HASH or reviewer.get('runnerSha256') != saved['runnerSha256'] or reviewer.get('quantization') != 'nf4-text-bf16-audio':
            raise ValueError('Window model or executed runner changed')
        if any(binding.get(key) != value for key, value in window.items()) or any(row.get(key) is not False for key in ['semanticFindingsVerified', 'fullSongHeard', 'pilotApproved', 'humanAccepted']):
            raise ValueError('Processing evidence cannot assert unverified creative acceptance')
        pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(source), '-ss', str(window['startSeconds']),
                              '-t', str(window['endSeconds'] - window['startSeconds']), '-ac', '1', '-ar', '16000',
                              '-f', 'f32le', '-'], check=True, capture_output=True, timeout=90).stdout
        samples = len(pcm) // 4
        expected = round((window['endSeconds'] - window['startSeconds']) * 16000)
        if len(pcm) % 4 or abs(samples - expected) > 1 or row['decodedAudio'] != {'sampleRate': 16000, 'samples': samples, 'sha256': hashlib.sha256(pcm).hexdigest()}:
            raise ValueError('Model input checksum does not cover the actual canonical range')
        features = row['modelAudioInput']
        validate_features(features['featureShape'], features['attendedFrames'], features['audioTokens'], samples, 160)
        if len(row['observations']) != len(QUESTIONS) or row['observations'] != record['observations']:
            raise ValueError('Window observation payload changed')
        for question_index, (prompt, observation) in enumerate(zip(QUESTIONS, row['observations'])):
            if observation.get('question') != prompt or observation.get('semanticVerified') is not False:
                raise ValueError('Raw observations cannot become verified interpretation')
            assessed = observation_record(prompt, observation['response'])
            findings.append({'windowIndex': index, 'questionIndex': question_index,
                             'contractPassed': assessed['usable'], 'issues': assessed['issues']})
    if file_receipt(source) != measured:
        raise ValueError('The master changed during independent observation audit')
    return {'schemaVersion': 1, 'status': 'processing-verified-interpretation-unverified',
            'jobId': request['jobId'], 'releaseId': request['releaseId'], 'source': measured,
            'durationSeconds': actual, 'songReceipt': file_receipt(path),
            'auditorSha256': file_receipt(Path(__file__))['sha256'],
            'processingCoverageVerified': True, 'windowCount': len(planned),
            'observationContractPassed': all(row['contractPassed'] for row in findings),
            'invalidObservationCount': sum(not row['contractPassed'] for row in findings),
            'findings': findings, 'semanticFindingsVerified': False,
            'lyricTimingVerified': False, 'fullSongHeard': False,
            'pilotApproved': False, 'humanAccepted': False, 'observedAt': time.time()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['windows', 'download', 'inspect', 'inspect-song', 'audit-song'])
    parser.add_argument('input', nargs='?')
    parser.add_argument('source', nargs='?')
    args = parser.parse_args()
    if args.action == 'windows':
        print(json.dumps({'windows': windows(float(args.input)), 'fullSongHeard': False}))
    elif args.action == 'audit-song':
        if not args.input or not args.source:
            raise ValueError('Pass the complete song receipt and canonical source for offline audit')
        print(json.dumps(audit_song(args.input, args.source), ensure_ascii=False, indent=2))
    elif args.action == 'download':
        managed()
        from huggingface_hub import snapshot_download
        path = snapshot_download(MODEL, revision=REVISION, cache_dir=str(CACHE),
                                 allow_patterns=['*.json', '*.safetensors', '*.txt', '*.model', '*.jinja', 'LICENSE', 'README.md'], max_workers=2)
        print(json.dumps({'model': MODEL, 'revision': REVISION, 'snapshotPath': path, 'inferenceSubmitted': False}))
    else:
        def terminate(signum, frame):
            raise SystemExit(f'Perception interrupted by signal {signum}')
        signal.signal(signal.SIGTERM, terminate)
        if args.action == 'inspect-song':
            inspect_song(args.input)
        else:
            inspect(args.input)


if __name__ == '__main__':
    main()
