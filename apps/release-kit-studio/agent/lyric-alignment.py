"""Fixed Whisper forced alignment of selected, exact canonical lyric lines."""
import importlib.util
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import unicodedata
import uuid

SERVICE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('alignment_audio', SERVICE / 'audio-perception.py')
audio = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audio)
MODEL = 'Systran/faster-whisper-large-v3'
REVISION = 'edaa852ec7e145841d8ffdb056a99866b5f0a478'
SNAPSHOT = Path('/home/r4ravi2008/.cache/huggingface/hub/models--Systran--faster-whisper-large-v3/snapshots') / REVISION
LANGUAGES = {'Telugu': 'te', 'Hindi': 'hi', 'Tamil': 'ta', 'English': 'en'}


def validate_request(value):
    keys = {'schemaVersion', 'jobId', 'releaseId', 'briefSha256', 'sourcePath', 'sourceSha256',
            'sourceBytes', 'sourceDuration', 'language', 'lyrics', 'startSeconds', 'endSeconds',
            'lineIndices', 'device', 'outputPath'}
    if not isinstance(value, dict) or set(value) != keys or type(value['schemaVersion']) is not int or value['schemaVersion'] != 1 or value['language'] not in LANGUAGES:
        raise ValueError('Invalid forced lyric alignment request')
    uuid.UUID(value['jobId'])
    uuid.UUID(value['releaseId'])
    if value['device'] not in ['cuda', 'cpu']:
        raise ValueError('Choose an explicit local alignment device')
    for key in ['briefSha256', 'sourceSha256']:
        if not isinstance(value[key], str) or len(value[key]) != 64 or any(c not in '0123456789abcdef' for c in value[key]):
            raise ValueError('Frozen source and brief hashes are required')
    if type(value['sourceBytes']) is not int or not 0 < value['sourceBytes'] <= 512 * 1024 ** 2:
        raise ValueError('A bounded measured source byte count is required')
    for key in ['startSeconds', 'endSeconds', 'sourceDuration']:
        if isinstance(value[key], bool) or not isinstance(value[key], (int, float)) or not math.isfinite(value[key]):
            raise ValueError('Finite alignment source ranges are required')
    if not 0 <= value['startSeconds'] < value['endSeconds'] <= value['sourceDuration'] <= 900 or value['endSeconds'] - value['startSeconds'] > 30:
        raise ValueError('Forced alignment must cover an actual range of at most 30 seconds')
    if not isinstance(value['lyrics'], str) or not 1 <= len(value['lyrics']) <= 30000:
        raise ValueError('Exact canonical lyric text is required')
    lines = value['lyrics'].splitlines()
    indices = value['lineIndices']
    if not isinstance(indices, list) or not 1 <= len(indices) <= 8 or any(type(i) is not int or not 0 <= i < len(lines) or not lines[i].strip() for i in indices) or indices != sorted(set(indices)):
        raise ValueError('Select up to eight distinct chronological canonical lines')
    return ' '.join(lines[i] for i in indices)


def group_words(rows, text, duration):
    groups = []
    previous = 0.
    for row in rows:
        if not isinstance(row['text'], str) or any(not math.isfinite(row[key]) for key in ['startSeconds', 'endSeconds', 'probability']):
            raise ValueError('Alignment contains non-finite or invalid word evidence')
        if not 0 <= row['startSeconds'] <= row['endSeconds'] <= duration + .04 or row['startSeconds'] < previous - .02 or not 0 <= row['probability'] <= 1:
            raise ValueError('Alignment exceeds or reverses the actual decoded range')
        previous = row['endSeconds']
        if not groups or row['text'][:1].isspace():
            groups.append([])
        groups[-1].append(row)
    joined = ''.join(row['text'] for row in rows)
    if joined.split() != text.split():
        raise ValueError('Alignment token decoding changed the supplied canonical words')
    words, issues = [], []
    for index, group in enumerate(groups):
        spelling = ''.join(row['text'] for row in group).strip()
        if not spelling:
            continue
        lexical = [row for row in group if any(unicodedata.category(c)[0] in 'LMN' for c in row['text'])]
        if not lexical:
            lexical = group
        start, end = lexical[0]['startSeconds'], lexical[-1]['endSeconds']
        probability = min(row['probability'] for row in lexical)
        codes = []
        # Whisper DTW can attach pre-roll to its first token. Probability does
        # not establish a word onset at the crop edge.
        if index == 0 and start <= .02:
            codes.append('crop-boundary-onset-unresolved')
        if start == end:
            codes.append('zero-length-word-alignment')
        if probability < .6:
            codes.append('uncertain-canonical-word')
        if codes:
            issues.append({'wordIndex': index, 'text': spelling, 'issues': codes})
        words.append({'wordIndex': index, 'text': spelling, 'startSeconds': start,
                      'endSeconds': end, 'probability': probability, 'issues': codes, 'verified': False})
    if [row['text'] for row in words] != text.split():
        raise ValueError('Canonical word grouping changed the supplied text')
    return words, issues


def main():
    audio.managed()
    path = audio.owned_path(sys.argv[1])
    if path.stat().st_size > 65536:
        raise ValueError('Alignment input exceeds 64 KiB')
    request = json.loads(path.read_text())
    text = validate_request(request)
    source, output = audio.owned_path(request['sourcePath']), audio.owned_path(request['outputPath'])
    expected = {'sha256': request['sourceSha256'], 'bytes': request['sourceBytes']}
    if output.exists() or source == output:
        raise ValueError('Preserve existing alignment evidence; select a new receipt')
    if audio.file_receipt(source) != expected:
        raise ValueError('Alignment source differs from the frozen master')
    actual = audio.decoded_audio_duration(source)
    if abs(actual - request['sourceDuration']) > .005:
        raise ValueError('Alignment source duration differs from its measured binding')
    gpu = request['device'] == 'cuda'
    if gpu:
        audio.idle_queue()
    lease = audio.LEASE if gpu else SERVICE / 'director/.cpu-alignment-lease.json'
    owner = {'service': 'release-kit-studio', 'purpose': 'lyric-alignment', 'job_id': request['jobId'],
             'owner_id': str(uuid.uuid4()), 'pid': os.getpid(), 'reserved_epoch': time.time()}
    audio.write_new(lease, owner)
    started = time.time()
    receipt = {'schemaVersion': 1, 'status': 'failed', 'request': request, 'source': expected,
               'model': MODEL, 'revision': REVISION, 'runnerSha256': audio.file_receipt(Path(__file__))['sha256'],
               'canonicalText': text, 'alignmentComplete': False, 'alignmentContractPassed': False,
               'runtime': {'device': request['device'], 'computeType': 'int8_float16' if gpu else 'int8_float32', 'cpuThreads': 4},
               'lyricTimingVerified': False, 'canonicalLyricsChanged': False,
               'fullSongHeard': False, 'pilotApproved': False, 'humanAccepted': False}
    try:
        if gpu:
            audio.idle_queue()
            free = int(subprocess.run(['/usr/lib/wsl/lib/nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'], check=True, capture_output=True, text=True, timeout=15).stdout.strip())
            if free < 4096:
                raise RuntimeError('Insufficient GPU memory; preserve other workloads')
        import numpy as np
        from faster_whisper import WhisperModel
        from faster_whisper.audio import pad_or_trim
        from faster_whisper.tokenizer import Tokenizer
        receipt['weights'] = audio.file_receipt(SNAPSHOT / 'model.bin')
        pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(source), '-ss', str(request['startSeconds']),
                              '-t', str(request['endSeconds'] - request['startSeconds']), '-ac', '1', '-ar', '16000',
                              '-f', 'f32le', '-'], check=True, capture_output=True, timeout=90).stdout
        samples = np.frombuffer(pcm, dtype='<f4').copy()
        if abs(len(samples) - round((request['endSeconds'] - request['startSeconds']) * 16000)) > 1 or not np.isfinite(samples).all():
            raise ValueError('Alignment input does not cover its exact source range')
        receipt['decodedAudio'] = {'sampleRate': 16000, 'samples': len(samples), 'sha256': __import__('hashlib').sha256(pcm).hexdigest()}
        model = WhisperModel(str(SNAPSHOT), device=request['device'], compute_type=receipt['runtime']['computeType'], cpu_threads=4, local_files_only=True)
        tokenizer = Tokenizer(model.hf_tokenizer, model.model.is_multilingual, task='transcribe', language=LANGUAGES[request['language']])
        tokens = tokenizer.encode(' ' + text)
        if len(tokens) + len(tokenizer.sot_sequence) + 1 > 448:
            raise ValueError('Canonical text exceeds the pinned decoder token window')
        features = pad_or_trim(model.feature_extractor(samples), 3000)
        frames = math.ceil(len(samples) / 160)
        if list(features.shape) != [128, 3000] or not 0 < frames <= 3000:
            raise ValueError('Forced alignment features differ from the bounded real audio')
        receipt['modelAudioInput'] = {'featureShape': list(features.shape), 'attendedFrames': frames,
                                      'textTokens': len(tokens), 'featureSha256': __import__('hashlib').sha256(features.tobytes()).hexdigest()}
        aligned = model.find_alignment(tokenizer, [tokens], model.encode(features), frames)[0]
        rows = [{'text': row['word'], 'startSeconds': float(row['start']), 'endSeconds': float(row['end']),
                 'probability': float(row['probability']), 'tokens': row['tokens']} for row in aligned]
        receipt['rawAlignments'] = rows
        words, issues = group_words(rows, text, len(samples) / 16000)
        receipt['words'] = [{**row, 'startSeconds': row['startSeconds'] + request['startSeconds'],
                             'endSeconds': row['endSeconds'] + request['startSeconds']} for row in words]
        receipt['issues'] = issues
        if audio.file_receipt(source) != expected:
            raise ValueError('The canonical master changed during forced alignment')
        receipt.update({'status': 'aligned-unverified', 'alignmentComplete': True, 'alignmentContractPassed': not issues})
    except BaseException as error:
        receipt.update({'errorType': type(error).__name__, 'error': str(error)[:1200]})
        raise
    finally:
        receipt['elapsedSeconds'] = time.time() - started
        receipt['observedAt'] = time.time()
        audio.write_new(output, receipt)
        if lease.exists() and json.loads(lease.read_text()).get('owner_id') == owner['owner_id']:
            lease.unlink()
        print(json.dumps({'status': receipt['status'], 'outputPath': str(output), 'alignmentComplete': receipt['alignmentComplete'], 'lyricTimingVerified': False}))


if __name__ == '__main__':
    audio.managed()
    if os.environ.get('RELEASE_KIT_ALIGNMENT_LOADER') != '1':
        libraries = audio.PROJECT / 'tools/ltx-video-generator/comfyui/.venv/lib/python3.12/site-packages/nvidia'
        paths = [str(libraries / name / 'lib') for name in ['cublas', 'cudnn']]
        if not all(Path(path).is_dir() for path in paths):
            raise RuntimeError('Verified CUDA libraries are unavailable')
        environment = {**os.environ, 'LD_LIBRARY_PATH': ':'.join(paths + [os.environ.get('LD_LIBRARY_PATH', '')]), 'RELEASE_KIT_ALIGNMENT_LOADER': '1'}
        os.execve(sys.executable, [sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]], environment)
    signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit(f'Alignment interrupted by signal {signum}'))
    main()
