"""Local review-preview proof using an existing immutable synthetic native kit."""
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
spec = importlib.util.spec_from_file_location('preview_http', APP / 'agent/check-editor.py')
http = importlib.util.module_from_spec(spec)
spec.loader.exec_module(http)
assert http.STUDIO == 'http://localhost:1337' and http.EDITOR == 'http://localhost:1339'
ROOT = APP / '.local' / ('editor-preview-' + str(uuid.uuid4()))
ROOT.mkdir(mode=0o700)
DATABASE = next((APP / '.alchemy/local/d1/cloudflare-runtime-D1DatabaseObject').glob('*.sqlite'))
SOURCE = APP / 'docs/editor/frame-diagnostics-runtime-receipt.json'
source = json.loads(SOURCE.read_text())
assert source['passed'] and source['sourceAudioIsSynthetic'] and not source['cloudVerified']
SOURCE_HASH = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
SOURCE_FILES = ['editor/preview.ts', 'editor/api.ts', 'editor/render-object.ts', 'editor/render-coordinator.ts', 'editor/catalog.ts',
                'editor/store.ts', 'editor/engine/engine.py', 'editor/engine/server.py',
                'editor/engine/preview.py', 'editor/engine/Dockerfile', 'agent/editor-cli.ts',
                'agent/editor-request.ts', 'agent/check-editor-preview.py']
SOURCE_HASHES = {name: hashlib.sha256((APP / name).read_bytes()).hexdigest() for name in SOURCE_FILES}
samples = []
sampler_errors = []


def sql(query, values=()):
    with closing(sqlite3.connect(f'file:{DATABASE}?mode=ro', uri=True)) as database:
        database.row_factory = sqlite3.Row
        return [dict(row) for row in database.execute(query, values)]


def sample():
    names = subprocess.check_output(['docker', 'ps', '--format', '{{.Names}}'], text=True).splitlines()
    native = sum(name.startswith('workerd-release-kit-editor-preview-RenderObject-') and not name.endswith('-proxy') for name in names)
    grants = sql('SELECT job_id,purpose FROM editor_capacity')
    assert native <= 1 and len(grants) <= 1
    record = {'at': time.time(), 'nativeContainers': native, 'capacity': grants}
    samples.append(record)
    return record


def holds():
    config = json.loads((APP / '.local/local-worker.json').read_text())
    result, _ = http.request(http.STUDIO, '/api/worker/holds', token=config['token'])
    return sorted([{key: job[key] for key in ('id', 'attempt', 'state')} for job in result['jobs']], key=lambda row: row['id'])


def ffmpeg(*args):
    return subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-nostdin', *args], check=True, capture_output=True, timeout=180).stdout


def preview(token, request, name):
    request_path = ROOT / (name + '-request.json')
    request_path.write_text(json.dumps(request)); request_path.chmod(0o600)
    directory = ROOT / name
    run = subprocess.run(['bun', 'agent/editor-cli.ts', 'preview', str(request_path), str(directory)], cwd=APP,
                         env={**os.environ, 'EDITOR_URL': http.EDITOR, 'EDITOR_TOKEN': token},
                         capture_output=True, text=True, timeout=650)
    if run.returncode:
        raise AssertionError('Preview CLI failed: ' + run.stderr[-2000:])
    proof = json.loads(run.stdout)
    bundle = json.loads((directory / 'receipt.json').read_text())
    for file in bundle['files']:
        path = directory / file['name']
        assert path.stat().st_size == file['bytes'] and hashlib.sha256(path.read_bytes()).hexdigest() == file['sha256']
        ffmpeg('-i', str(path), '-f', 'null', '-')
    print(json.dumps({'phase': name, 'filesVerified': proof['filesVerified'], 'reused': proof['reused']}), flush=True)
    return directory, proof, bundle


def main():
    before_holds = holds()
    job_id = source['editorJobId']
    row = sql('SELECT * FROM editor_jobs WHERE id=?', (job_id,))[0]
    assert row['state'] == 'ready'
    before_jobs = sql('SELECT id,state,receipt_json FROM editor_jobs WHERE release_id=? ORDER BY id', (row['release_id'],))
    assert sample()['nativeContainers'] == 0 and not samples[-1]['capacity']
    token = session = foreign = receipt = None
    stop = threading.Event()
    def sampling():
        while not stop.wait(.2):
            try: sample()
            except Exception as error: sampler_errors.append(str(error)); return
    thread = threading.Thread(target=sampling, daemon=True)
    try:
        catalog, _ = http.request(http.EDITOR, '/v1/tools')
        tool = next(item for item in catalog['tools'] if item['name'] == 'artifact.preview')
        assert tool['input']['properties']['frames']['maximum'] == 240
        credential, _ = http.request(http.EDITOR, '/v1/operator/tokens', 'POST', {'tenantId': row['tenant_id']}, token=http.OPERATOR, expected=201)
        token = credential['token']
        request = {'jobId': job_id, 'outputId': 'film', 'startFrame': 6, 'frames': 36, 'sampleFrames': [6, 23, 24, 41]}
        thread.start()
        directory, proof, bundle = preview(token, request, 'film-range')
        assert proof['reused'] is False and proof['filesVerified'] == 5
        original = next(item for item in source['outputs'] if item['id'] == 'film')
        assert bundle['source']['sha256'] == original['sha256'] and bundle['source']['bytes'] == original['bytes']
        assert bundle['startFrame'] == 6 and bundle['frames'] == 36 and bundle['sampleFrames'] == [6, 23, 24, 41]
        movie = bundle['files'][0]
        assert (movie['width'], movie['height'], movie['frames']) == (960, 540, 36) and movie['audioComparison']['passed'] is True
        assert all(bundle[key] is False for key in ['semanticReviewed', 'motionReviewed', 'heard', 'creativelyAccepted'])
        assert sample()['nativeContainers'] == 0 and not samples[-1]['capacity']
        cache_start = len(samples)
        _, replay, replay_bundle = preview(token, request, 'film-replay')
        assert replay['reused'] is True and replay_bundle == bundle
        assert all(item['nativeContainers'] == 0 and not item['capacity'] for item in samples[cache_start:])
        _, still, still_bundle = preview(token, {'jobId': job_id, 'outputId': 'thumbnail', 'startFrame': 0, 'frames': 1, 'sampleFrames': []}, 'thumbnail')
        assert still['filesVerified'] == 2 and still_bundle['files'][0]['audioComparison'] is None
        assert still_bundle['files'][0]['name'] == 'preview.jpg'
        prefix = f'/v1/jobs/{job_id}/previews/{bundle["bundleId"]}/'
        content, headers = http.request(http.EDITOR, prefix + 'preview.mp4', token=token, raw=True)
        assert content == (directory / 'preview.mp4').read_bytes()
        part, ranged = http.request(http.EDITOR, prefix + 'preview.mp4', token=token, raw=True, expected=206, extra={'Range': 'bytes=11-47'})
        assert part == content[11:48] and ranged['Content-Range'] == f'bytes 11-47/{len(content)}'
        assert headers['X-Source-Sha256'] == original['sha256']
        session, foreign = http.principal()
        http.request(http.EDITOR, prefix + 'preview.mp4', token=foreign, raw=True, expected=404)
        http.request(http.EDITOR, '/v1/tools/artifact.preview', 'POST', request, token=foreign, expected=404)
        http.request(http.EDITOR, '/v1/tools/artifact.preview', 'POST', {**request, 'frames': 241}, token=token, expected=400)
        http.request(http.EDITOR, '/v1/tools/artifact.preview', 'POST', {**request, 'startFrame': 24, 'frames': 36}, token=token, expected=422)
        parent, _ = http.request(http.EDITOR, f'/v1/jobs/{job_id}/outputs/film', token=token)
        original_path = ROOT / 'original-film.mp4'; original_path.write_bytes(parent)
        assert hashlib.sha256(parent).hexdigest() == original['sha256']
        frame_checks = []
        for file in bundle['files'][1:]:
            frame = file['sourceFrame']
            reference = ffmpeg('-ss', f'{max(0, frame / 24 - .00001):.9f}', '-i', str(original_path), '-frames:v', '1', '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-')
            candidate = ffmpeg('-i', str(directory / file['name']), '-frames:v', '1', '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-')
            assert len(reference) == len(candidate) == 1920 * 1080 * 3
            error = sum(abs(left - right) for left, right in zip(reference, candidate)) / len(reference)
            assert error < 3, f'Full-resolution source frame {frame} differs: {error}'
            frame_checks.append({'sourceFrame': frame, 'meanAbsoluteRgbError': error, 'threshold': 3, 'width': 1920, 'height': 1080})
        stop.set(); thread.join(timeout=5)
        assert not sampler_errors and max(item['nativeContainers'] for item in samples) == 1
        assert sample()['nativeContainers'] == 0 and not samples[-1]['capacity']
        assert holds() == before_holds and sql('SELECT id,state,receipt_json FROM editor_jobs WHERE release_id=? ORDER BY id', (row['release_id'],)) == before_jobs
        assert SOURCE_HASH == hashlib.sha256(SOURCE.read_bytes()).hexdigest()
        assert SOURCE_HASHES == {name: hashlib.sha256((APP / name).read_bytes()).hexdigest() for name in SOURCE_FILES}
        receipt = {'scope': 'local Workerd/D1/R2 review-preview verification only', 'passed': True, 'testedAt': time.time(),
                   'sourceHashes': SOURCE_HASHES, 'sourceNativeReceipt': 'frame-diagnostics-runtime-receipt.json',
                   'sourceNativeReceiptSha256': SOURCE_HASH, 'editorJobId': job_id, 'bundle': bundle,
                   'stillBundle': still_bundle, 'independentFrameChecks': frame_checks,
                   'checks': ['bounded-agent-tool-schema-advertised', 'real-cli-verifies-exact-video-range-and-five-files',
                              'native-preview-audio-correlates-with-original-range', 'four-full-resolution-source-frames-match-independent-seeks',
                              'cached-replay-preserves-bytes-without-native-compute', 'still-preview-has-two-images-and-no-invented-audio',
                              'private-full-and-range-downloads-match-cli-bytes', 'foreign-tenant-creation-and-download-rejected',
                              'oversize-and-out-of-source-ranges-rejected', 'source-kit-and-both-pal-pal-holds-unchanged',
                              'one-native-container-at-peak-zero-after-verification'],
                   'newFilmRenderSubmitted': False, 'gpuInferenceSubmitted': False, 'peakNativeContainersObserved': 1,
                   'finalNativeContainersObserved': 0, 'capacitySlotReleased': True,
                   'cloudVerified': False, 'palPalKitCompleted': False, 'motionReviewed': False, 'heard': False, 'creativelyAccepted': False}
    finally:
        stop.set()
        if thread.is_alive(): thread.join(timeout=5)
        for credential in [token, foreign]:
            if credential:
                http.request(http.EDITOR, '/v1/operator/tokens/revoke', 'POST', {'targetToken': credential}, token=http.OPERATOR)
                assert sql('SELECT enabled FROM editor_tokens WHERE hash=?', (hashlib.sha256(credential.encode()).hexdigest(),))[0]['enabled'] == 0
        if session: http.request(http.STUDIO, '/api/auth/logout', 'POST', {}, session=session)
        (ROOT / 'samples.json').write_text(json.dumps(samples, indent=2))
        if receipt:
            receipt['diagnosticTokensRevoked'] = True
            receipt['diagnosticSessionLoggedOut'] = True
            (APP / 'docs/editor/review-preview-runtime-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return receipt


if __name__ == '__main__':
    result = main()
    print(json.dumps({'passed': result['passed'], 'checks': result['checks'], 'cloudVerified': False}), flush=True)
