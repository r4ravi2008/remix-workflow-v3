"""Fixed model operations behind the existing managed GPU transport."""
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import uuid

SERVICE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('observation_audio', SERVICE / 'audio-perception.py')
audio = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audio)


def validate_intent(value):
    keys = {'schemaVersion', 'id', 'kind', 'jobId', 'releaseId', 'briefSha256',
            'sourceSha256', 'sourceBytes', 'sourceDuration', 'language', 'lyrics',
            'startSeconds', 'endSeconds'}
    if not isinstance(value, dict) or not keys <= set(value) or set(value) - keys - {'lineIndices', 'alignmentDevice', 'alignmentBackend', 'audioBackend'} or type(value['schemaVersion']) is not int or value['schemaVersion'] != 1 or value['kind'] not in ['audio-window', 'speech', 'lyric-alignment']:
        raise ValueError('Invalid fixed model operation')
    for name in ['id', 'briefSha256', 'sourceSha256']:
        if not isinstance(value[name], str) or not re.fullmatch('[a-f0-9]{64}', value[name]):
            raise ValueError('Frozen model operation hashes are required')
    uuid.UUID(value['jobId'])
    uuid.UUID(value['releaseId'])
    if type(value['sourceBytes']) is not int or not 0 < value['sourceBytes'] <= 512 * 1024 ** 2:
        raise ValueError('Invalid canonical source byte count')
    for key in ['sourceDuration', 'startSeconds', 'endSeconds']:
        if isinstance(value[key], bool) or not isinstance(value[key], (int, float)) or not math.isfinite(value[key]):
            raise ValueError('Finite model operation ranges are required')
    if not 0 <= value['startSeconds'] < value['endSeconds'] <= value['sourceDuration'] <= 900:
        raise ValueError('Model operation range exceeds its canonical source')
    if value['kind'] in ['audio-window', 'lyric-alignment'] and value['endSeconds'] - value['startSeconds'] > 30:
        raise ValueError('Audio model windows cannot exceed 30 seconds')
    if value['kind'] == 'speech' and (value['startSeconds'] != 0 or value['endSeconds'] != value['sourceDuration']):
        raise ValueError('Speech observations must cover the complete source')
    if value['language'] not in ['Telugu', 'Hindi', 'Tamil', 'English'] or not isinstance(value['lyrics'], str) or not 1 <= len(value['lyrics']) <= 30000:
        raise ValueError('Exact native lyrics and their language are required')
    if 'audioBackend' in value and (value['kind'] != 'audio-window' or value['audioBackend'] not in ['qwen2-audio', 'qwen2.5-omni']):
        raise ValueError('Choose a fixed audio backend only for an audio window')
    if value['kind'] == 'lyric-alignment':
        lines = value['lyrics'].splitlines()
        indices = value.get('lineIndices')
        if not isinstance(indices, list) or not 1 <= len(indices) <= 8 or any(type(i) is not int or not 0 <= i < len(lines) or not lines[i].strip() for i in indices) or indices != sorted(set(indices)):
            raise ValueError('Select distinct chronological canonical lyric lines')
        if value.get('alignmentDevice', 'cuda') not in ['cuda', 'cpu']:
            raise ValueError('Alignment device must be the explicitly selected local CPU or CUDA GPU')
        if value.get('alignmentBackend', 'whisper') not in ['whisper', 'indic-conformer-ctc']:
            raise ValueError('Choose a fixed supported lyric alignment backend')
        if value.get('alignmentBackend') == 'indic-conformer-ctc' and (value.get('alignmentDevice') != 'cpu' or value['language'] != 'Telugu'):
            raise ValueError('This CTC backend supports explicitly selected Telugu CPU execution only')
    elif 'lineIndices' in value or 'alignmentDevice' in value or 'alignmentBackend' in value:
        raise ValueError('Canonical line selection applies only to forced alignment')
    return value


def run(request):
    audio.managed()
    if set(request) != {'intent', 'stagedSource'}:
        raise ValueError('Invalid staged model operation')
    intent = validate_intent(request['intent'])
    staged = audio.owned_path(request['stagedSource'])
    if staged.parent != SERVICE / 'requests' or not re.fullmatch(r'[a-f0-9-]{36}\.audio', staged.name):
        raise ValueError('Audio staging must use this exact transport request')
    expected = {'sha256': intent['sourceSha256'], 'bytes': intent['sourceBytes']}
    if audio.file_receipt(staged) != expected:
        raise ValueError('Staged audio differs from the frozen source')
    directory = SERVICE / 'director/operations' / intent['id']
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    source = SERVICE / 'director/inputs' / (intent['sourceSha256'] + '.audio')
    source.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    try:
        os.link(staged, source)
        source.chmod(0o400)
    except FileExistsError:
        pass
    if audio.file_receipt(source) != expected:
        raise ValueError('Preserved audio snapshot changed; do not replace it')
    staged.unlink()
    scripts = ['audio-perception.py'] + (['speech-evidence.py'] if intent['kind'] == 'speech' else ['lyric-alignment.py'] if intent['kind'] == 'lyric-alignment' else [])
    if intent.get('audioBackend') == 'qwen2.5-omni':
        scripts.append('omni-perception.py')
    if intent.get('alignmentBackend') == 'indic-conformer-ctc':
        scripts.append('ctc-alignment.py')
    bound = {'intent': intent, 'runnerHashes': {name: audio.file_receipt(SERVICE / name)['sha256'] for name in scripts}}
    saved = directory / 'intent.json'
    if saved.exists():
        if json.loads(saved.read_text()) != bound:
            raise ValueError('This observation belongs to different inputs or runner bytes')
    else:
        audio.write_new(saved, bound)
    output = directory / 'receipt.json'
    submitted = False
    if not output.exists():
        marker = directory / 'inference-intent.json'
        if marker.exists():
            raise RuntimeError('Inference outcome is uncertain; reconcile its receipt before any new operation')
        common = {key: intent[key] for key in ['jobId', 'releaseId', 'sourceSha256', 'sourceBytes', 'sourceDuration']}
        operation = {**common, 'sourcePath': str(source), 'outputPath': str(output)}
        if intent['kind'] in ['speech', 'lyric-alignment']:
            operation.update({'schemaVersion': 1, **{key: intent[key] for key in ['briefSha256', 'language', 'lyrics']}})
            interpreter = SERVICE / 'director/asr-venv/bin/python'
            runner = 'speech-evidence.py' if intent['kind'] == 'speech' else 'lyric-alignment.py'
            if intent.get('alignmentBackend') == 'indic-conformer-ctc':
                runner = 'ctc-alignment.py'
            if intent['kind'] == 'lyric-alignment':
                operation.update({key: intent[key] for key in ['startSeconds', 'endSeconds', 'lineIndices']})
                operation['device'] = intent.get('alignmentDevice', 'cuda')
            args = [str(interpreter), str(SERVICE / runner)]
        else:
            operation.update({'schemaVersion': 2, **{key: intent[key] for key in ['startSeconds', 'endSeconds']}})
            interpreter = SERVICE / 'director/venv/bin/python'
            runner = 'omni-perception.py' if intent.get('audioBackend') == 'qwen2.5-omni' else 'audio-perception.py'
            args = [str(interpreter), str(SERVICE / runner), 'inspect']
        if not interpreter.is_file():
            raise RuntimeError('The isolated model environment is unavailable')
        cpu = intent['kind'] == 'lyric-alignment' and intent.get('alignmentDevice') == 'cpu'
        if not cpu:
            audio.idle_queue()
        if not cpu and audio.LEASE.exists():
            raise RuntimeError('The shared GPU lease is occupied; preserve its owner')
        if cpu and (SERVICE / 'director/.cpu-alignment-lease.json').exists():
            raise RuntimeError('The CPU alignment lease is occupied; preserve its owner')
        operation_path = directory / 'request.json'
        if operation_path.exists():
            if json.loads(operation_path.read_text()) != operation:
                raise ValueError('The preserved native model request changed')
        else:
            audio.write_new(operation_path, operation)
        audio.write_new(marker, {'pid': os.getpid(), 'startedAt': time.time(), 'intent': intent})
        submitted = True
        with (directory / 'inference.log').open('x') as log:
            subprocess.run([*args, str(operation_path)], stdout=log, stderr=subprocess.STDOUT, timeout=330)
        if not output.exists():
            raise RuntimeError('Model process has no terminal receipt; preserve the inference fence')
    if output.stat().st_size > 2 * 1024 ** 2:
        raise ValueError('Model evidence exceeds the bounded receipt size')
    receipt = json.loads(output.read_text())
    if receipt.get('source') != expected or receipt.get('request', {}).get('jobId') != intent['jobId'] or receipt.get('request', {}).get('releaseId') != intent['releaseId']:
        raise ValueError('Model evidence differs from its immutable operation')
    if audio.file_receipt(source) != expected:
        raise ValueError('The source changed while model evidence was collected')
    return {'intent': intent, 'receipt': {'path': str(output), **audio.file_receipt(output)}, 'inferenceSubmitted': submitted}
