"""Source-bound local Whisper observations; supplied lyrics remain authoritative."""
import importlib.util
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import uuid

SERVICE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('audio_perception', SERVICE / 'audio-perception.py')
audio = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audio)
MODEL = 'Systran/faster-whisper-large-v3'
REVISION = 'edaa852ec7e145841d8ffdb056a99866b5f0a478'
SNAPSHOT = Path('/home/r4ravi2008/.cache/huggingface/hub/models--Systran--faster-whisper-large-v3/snapshots') / REVISION
LANGUAGES = {'Telugu': 'te', 'Hindi': 'hi', 'Tamil': 'ta', 'English': 'en'}


def validate_segments(rows, duration):
    previous = 0
    issues = []
    for row in rows:
        if any(not math.isfinite(row[key]) for key in ['start', 'end', 'avgLogprob', 'noSpeechProbability']):
            raise ValueError('Whisper returned non-finite observations')
        if not 0 <= row['start'] <= row['end'] <= duration + 0.02 or row['start'] < previous - 0.02:
            raise ValueError('Whisper observations exceed or reverse the source range')
        previous = row['end']
        if row['noSpeechProbability'] > 0.6 or row['avgLogprob'] < -1:
            issues.append({'segmentId': row['id'], 'code': 'uncertain-recognition'})
        last_word = row['start']
        for word in row['words']:
            if not all(math.isfinite(word[key]) for key in ['start', 'end', 'probability']):
                raise ValueError('Whisper returned non-finite word evidence')
            if not row['start'] - 0.02 <= word['start'] <= word['end'] <= row['end'] + 0.02 or word['start'] < last_word - 0.02 or not 0 <= word['probability'] <= 1:
                raise ValueError('Word observations differ from their source segment')
            last_word = word['end']
            if word['start'] == word['end'] or word['probability'] < 0.6:
                issues.append({'segmentId': row['id'], 'word': word['text'], 'code': 'uncertain-word-timing'})
    return issues


def main():
    audio.managed()
    path = audio.owned_path(sys.argv[1])
    if path.stat().st_size > 65536:
        raise ValueError('Speech request exceeds 64 KiB')
    request = json.loads(path.read_text())
    keys = {'schemaVersion', 'jobId', 'releaseId', 'briefSha256', 'sourcePath', 'sourceSha256', 'sourceBytes', 'sourceDuration', 'language', 'lyrics', 'outputPath'}
    if not isinstance(request, dict) or set(request) != keys or request['schemaVersion'] != 1 or request['language'] not in LANGUAGES:
        raise ValueError('Invalid source-bound speech request')
    uuid.UUID(request['jobId'])
    uuid.UUID(request['releaseId'])
    for key in ['briefSha256', 'sourceSha256']:
        if not isinstance(request[key], str) or len(request[key]) != 64 or any(c not in '0123456789abcdef' for c in request[key]):
            raise ValueError('Measured source and frozen brief hashes are required')
    if not isinstance(request['lyrics'], str) or not 1 <= len(request['lyrics']) <= 30000:
        raise ValueError('Exact supplied lyrics are required')
    if isinstance(request['sourceDuration'], bool) or not isinstance(request['sourceDuration'], (int, float)) or not math.isfinite(request['sourceDuration']) or not 0 < request['sourceDuration'] <= 900:
        raise ValueError('A finite source duration up to 900 seconds is required')
    source = audio.owned_path(request['sourcePath'])
    output = audio.owned_path(request['outputPath'])
    if output.exists() or output == source:
        raise ValueError('Preserve existing speech evidence; select a new receipt')
    measured = audio.file_receipt(source)
    if measured != {'sha256': request['sourceSha256'], 'bytes': request['sourceBytes']}:
        raise ValueError('Speech source differs from the frozen master')
    actual = audio.decoded_audio_duration(source)
    if abs(actual - request['sourceDuration']) > 0.005:
        raise ValueError('Speech source duration differs from its requested range')
    audio.idle_queue()
    owner = {'service': 'release-kit-studio', 'purpose': 'speech-evidence', 'job_id': request['jobId'], 'owner_id': str(uuid.uuid4()), 'pid': os.getpid(), 'reserved_epoch': time.time()}
    audio.write_new(audio.LEASE, owner)
    receipt = {'schemaVersion': 1, 'status': 'failed', 'request': request, 'source': measured,
               'model': MODEL, 'revision': REVISION, 'runnerSha256': audio.file_receipt(Path(__file__))['sha256'],
               'recognitionComplete': False, 'lyricTimingVerified': False, 'canonicalLyricsChanged': False,
               'fullSongHeard': False, 'pilotApproved': False, 'humanAccepted': False}
    started = time.time()
    try:
        audio.idle_queue()
        free_mib = int(subprocess.run(['/usr/lib/wsl/lib/nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'], check=True, capture_output=True, text=True, timeout=15).stdout.strip())
        if free_mib < 4096:
            raise RuntimeError('Fewer than 4 GiB are free; preserve other GPU workloads')
        import numpy as np
        from faster_whisper import WhisperModel
        weights = SNAPSHOT / 'model.bin'
        if not weights.is_file():
            raise ValueError('The pinned local Whisper snapshot is incomplete')
        receipt['weights'] = audio.file_receipt(weights)
        pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(source), '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'], check=True, capture_output=True, timeout=90).stdout
        samples = np.frombuffer(pcm, dtype='<f4').copy()
        if abs(len(samples) - round(actual * 16000)) > 1 or not np.isfinite(samples).all():
            raise ValueError('Whisper input does not cover the complete canonical source')
        receipt['decodedAudio'] = {'sampleRate': 16000, 'samples': len(samples), 'sha256': __import__('hashlib').sha256(pcm).hexdigest()}
        model = WhisperModel(str(SNAPSHOT), device='cuda', compute_type='int8_float16', local_files_only=True)
        stream, info = model.transcribe(samples, language=LANGUAGES[request['language']], task='transcribe', beam_size=5,
                    word_timestamps=True, vad_filter=False, condition_on_previous_text=False, temperature=0)
        rows = []
        for segment in stream:
            rows.append({'id': segment.id, 'start': segment.start, 'end': segment.end, 'text': segment.text,
                         'avgLogprob': segment.avg_logprob, 'noSpeechProbability': segment.no_speech_prob,
                         'words': [{'text': word.word, 'start': word.start, 'end': word.end, 'probability': word.probability} for word in segment.words or []]})
        receipt['segments'] = rows
        receipt['issues'] = validate_segments(rows, actual)
        if abs(info.duration - actual) > 0.001 or audio.file_receipt(source) != measured:
            raise ValueError('Complete recognition does not bind the unchanged master duration')
        receipt.update({'status': 'recognized-unverified', 'recognitionComplete': True,
                        'recognizedLanguage': info.language, 'durationProcessed': info.duration})
    except BaseException as error:
        receipt['errorType'] = type(error).__name__
        receipt['error'] = str(error)[:1000]
        raise
    finally:
        receipt['elapsedSeconds'] = time.time() - started
        receipt['observedAt'] = time.time()
        audio.write_new(output, receipt)
        if audio.LEASE.exists() and json.loads(audio.LEASE.read_text()).get('owner_id') == owner['owner_id']:
            audio.LEASE.unlink()
        print(json.dumps({'status': receipt['status'], 'outputPath': str(output), 'recognitionComplete': receipt['recognitionComplete'], 'lyricTimingVerified': False}))


if __name__ == '__main__':
    audio.managed()
    if os.environ.get('RELEASE_KIT_SPEECH_LOADER') != '1':
        libraries = audio.PROJECT / 'tools/ltx-video-generator/comfyui/.venv/lib/python3.12/site-packages/nvidia'
        paths = [str(libraries / name / 'lib') for name in ['cublas', 'cudnn']]
        if not all(Path(path).is_dir() for path in paths):
            raise RuntimeError('Verified CUDA 12/cuDNN libraries are unavailable')
        environment = {**os.environ, 'LD_LIBRARY_PATH': ':'.join(paths + [os.environ.get('LD_LIBRARY_PATH', '')]), 'RELEASE_KIT_SPEECH_LOADER': '1'}
        os.execve(sys.executable, [sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]], environment)
    signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit(f'Speech evidence interrupted by signal {signum}'))
    main()
