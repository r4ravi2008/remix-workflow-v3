"""Verify an exact ending preview from the existing full-length synthetic native film."""
from contextlib import closing
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import threading
import time
import uuid


APP = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('long_preview_http', APP / 'agent/check-editor.py')
http = importlib.util.module_from_spec(spec)
spec.loader.exec_module(http)
SOURCE = APP / 'docs/editor/long-kit-runtime-receipt.json'
SOURCE_HASH = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
source = json.loads(SOURCE.read_text())
assert source['passed'] and source['sourceAudioIsSynthetic'] and not source['cloudVerified']
original = next(item for item in source['nativeReceipt']['outputs'] if item['id'] == 'film')
assert original['frames'] == 5753 and source['sourceAudioDuration'] == 239.68
ROOT = APP / '.local' / ('editor-preview-long-' + str(uuid.uuid4()))
ROOT.mkdir(mode=0o700)
DATABASE = next((APP / '.alchemy/local/d1/cloudflare-runtime-D1DatabaseObject').glob('*.sqlite'))
FILES = ['editor/preview.ts', 'editor/render-object.ts', 'editor/render-coordinator.ts', 'editor/api.ts', 'editor/catalog.ts',
         'editor/capacity.ts', 'editor/engine/engine.py', 'editor/engine/server.py',
         'editor/engine/preview.py', 'editor/engine/Dockerfile', 'agent/editor-cli.ts',
         'agent/editor-request.ts', 'agent/check-editor-preview-long.py']
HASHES = {name: hashlib.sha256((APP / name).read_bytes()).hexdigest() for name in FILES}
samples, sampling_errors = [], []


def sql(query, values=()):
    with closing(sqlite3.connect(f'file:{DATABASE}?mode=ro', uri=True)) as connection:
        connection.row_factory = sqlite3.Row
        return [dict(row) for row in connection.execute(query, values)]


def sample():
    names = subprocess.check_output(['docker', 'ps', '--format', '{{.Names}}'], text=True).splitlines()
    native = sum(name.startswith('workerd-release-kit-editor-preview-RenderObject-') and not name.endswith('-proxy') for name in names)
    capacity = sql('SELECT job_id,purpose FROM editor_capacity')
    assert native <= 1 and len(capacity) <= 1
    result = {'at': time.time(), 'nativeContainers': native, 'capacity': capacity}
    samples.append(result)
    return result


def holds():
    config = json.loads((APP / '.local/local-worker.json').read_text())
    result, _ = http.request(http.STUDIO, '/api/worker/holds', token=config['token'])
    return sorted((job['id'], job['attempt'], job['state']) for job in result['jobs'])


def hash_file(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''): digest.update(block)
    return digest.hexdigest()


def cli(token, *args):
    started = time.monotonic()
    result = subprocess.run(['bun', 'agent/editor-cli.ts', *map(str, args)], cwd=APP,
                            env={**os.environ, 'EDITOR_URL': http.EDITOR, 'EDITOR_TOKEN': token},
                            text=True, capture_output=True, timeout=650)
    if result.returncode: raise AssertionError('Editor CLI failed: ' + result.stderr[-2000:])
    return json.loads(result.stdout), time.monotonic() - started


def ffmpeg(*args):
    return subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-nostdin', *args],
                          capture_output=True, check=True, timeout=180).stdout


def main():
    job_id = source['editorJobId']
    job = sql('SELECT tenant_id,release_id,state,receipt_json FROM editor_jobs WHERE id=?', (job_id,))[0]
    assert job['state'] == 'ready'
    before = sql('SELECT id,state,receipt_json FROM editor_jobs WHERE release_id=? ORDER BY id', (job['release_id'],))
    before_holds = holds()
    first = sample(); assert first['nativeContainers'] == 0 and not first['capacity']
    token = receipt = None
    stop = threading.Event()
    def sampling():
        while not stop.wait(.5):
            try: sample()
            except Exception as error: sampling_errors.append(str(error)); return
    thread = threading.Thread(target=sampling, daemon=True)
    try:
        credential, _ = http.request(http.EDITOR, '/v1/operator/tokens', 'POST', {'tenantId': job['tenant_id']}, token=http.OPERATOR, expected=201)
        token = credential['token']
        original_path = ROOT / 'original-film.mp4'
        _, download_seconds = cli(token, 'download', job_id, 'film', original_path)
        assert original_path.stat().st_size == original['bytes'] and hash_file(original_path) == original['sha256']
        request = {'jobId': job_id, 'outputId': 'film', 'startFrame': 5513, 'frames': 240,
                   'sampleFrames': [5513, 5629, 5751, 5752]}
        request_path = ROOT / 'request.json'; request_path.write_text(json.dumps(request)); request_path.chmod(0o600)
        thread.start()
        proof, generation_seconds = cli(token, 'preview', request_path, ROOT / 'ending')
        bundle = json.loads((ROOT / 'ending/receipt.json').read_text())
        assert proof['filesVerified'] == 5
        assert bundle['source']['sha256'] == original['sha256'] and bundle['source']['bytes'] == original['bytes']
        assert bundle['startFrame'] == 5513 and bundle['frames'] == 240 and bundle['sampleFrames'] == request['sampleFrames']
        movie = bundle['files'][0]
        assert (movie['width'], movie['height'], movie['frames'], movie['fps']) == (960, 540, 240, 24)
        assert movie['audioComparison']['passed'] and min(movie['audioComparison']['channelCosine']) >= .99
        assert abs(movie['audioComparison']['sourceStartSeconds'] - 5513 / 24) < .000001
        assert abs(movie['audioComparison']['sourceDurationSeconds'] - (239.68 - 5513 / 24)) < .000001
        for file in bundle['files']:
            path = ROOT / 'ending' / file['name']
            assert path.stat().st_size == file['bytes'] and hash_file(path) == file['sha256']
            ffmpeg('-i', str(path), '-f', 'null', '-')
        print(json.dumps({'phase': 'ending-generated-and-decoded', 'seconds': generation_seconds,
                          'reused': proof['reused'], 'frames': movie['frames']}), flush=True)
        assert sample()['nativeContainers'] == 0 and not samples[-1]['capacity']
        cache_start = len(samples)
        replay, replay_seconds = cli(token, 'preview', request_path, ROOT / 'replay')
        assert replay['reused'] and json.loads((ROOT / 'replay/receipt.json').read_text()) == bundle
        assert all(row['nativeContainers'] == 0 and not row['capacity'] for row in samples[cache_start:])
        checks = []
        for file in bundle['files'][1:]:
            frame = file['sourceFrame']
            reference = ffmpeg('-ss', f'{frame / 24 - .00001:.9f}', '-i', str(original_path),
                               '-frames:v', '1', '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-')
            image = ffmpeg('-i', str(ROOT / 'ending' / file['name']), '-frames:v', '1',
                           '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-')
            assert len(reference) == len(image) == 1920 * 1080 * 3
            error = sum(abs(a - b) for a, b in zip(reference, image)) / len(reference)
            assert error < 3, f'Ending source frame {frame} differs: {error}'
            checks.append({'sourceFrame': frame, 'meanAbsoluteRgbError': error, 'threshold': 3})
        assert all(bundle[key] is False for key in ['semanticReviewed', 'motionReviewed', 'heard', 'creativelyAccepted'])
        assert before == sql('SELECT id,state,receipt_json FROM editor_jobs WHERE release_id=? ORDER BY id', (job['release_id'],)) and before_holds == holds()
        assert SOURCE_HASH == hashlib.sha256(SOURCE.read_bytes()).hexdigest() and HASHES == {name: hashlib.sha256((APP / name).read_bytes()).hexdigest() for name in FILES}
        stop.set(); thread.join(timeout=5)
        assert not sampling_errors and sample()['nativeContainers'] == 0 and not samples[-1]['capacity']
        peak = max(row['nativeContainers'] for row in samples)
        assert peak == (0 if proof['reused'] else 1)
        receipt = {'scope': 'local full-length synthetic film ending preview only', 'passed': True,
                   'testedAt': time.time(), 'sourceNativeReceipt': SOURCE.name, 'sourceNativeReceiptSha256': SOURCE_HASH,
                   'sourceHashes': HASHES, 'editorJobId': job_id, 'bundle': bundle, 'independentFrameChecks': checks,
                   'timings': {'originalDownloadSeconds': round(download_seconds, 3), 'endingPreviewSeconds': round(generation_seconds, 3),
                               'cachedReplaySeconds': round(replay_seconds, 3)},
                   'resumedStoredPreviewVerification': proof['reused'], 'peakNativeContainersObserved': peak,
                   'finalNativeContainersObserved': 0, 'capacitySlotReleased': True,
                   'checks': ['real-cli-download-binds-original-140mb-5753-frame-film',
                              'ten-second-ending-preview-includes-last-encoded-frame',
                              'exact-ending-audio-range-correlates-with-shorter-source-tail',
                              'five-private-derived-files-hash-and-completely-decode',
                              'four-full-resolution-late-frames-match-independent-source-seeks',
                              'cached-ending-replay-preserves-bytes-without-native-compute',
                              'original-six-output-receipt-and-both-pal-pal-holds-unchanged',
                              'shared-native-capacity-cleared-after-operation'],
                   'newFilmRenderSubmitted': False, 'gpuInferenceSubmitted': False, 'cloudVerified': False,
                   'cloudPerformanceVerified': False, 'palPalKitCompleted': False,
                   'semanticReviewed': False, 'motionReviewed': False, 'heard': False, 'creativelyAccepted': False}
    finally:
        stop.set()
        if thread.is_alive(): thread.join(timeout=5)
        if token:
            http.request(http.EDITOR, '/v1/operator/tokens/revoke', 'POST', {'targetToken': token}, token=http.OPERATOR)
            assert sql('SELECT enabled FROM editor_tokens WHERE hash=?', (hashlib.sha256(token.encode()).hexdigest(),))[0]['enabled'] == 0
        (ROOT / 'samples.json').write_text(json.dumps(samples, indent=2))
        if receipt:
            receipt['diagnosticTokenRevoked'] = True
            (APP / 'docs/editor/review-preview-long-runtime-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return receipt


if __name__ == '__main__':
    result = main()
    print(json.dumps({'passed': result['passed'], 'checks': result['checks'], 'cloudVerified': False}), flush=True)
