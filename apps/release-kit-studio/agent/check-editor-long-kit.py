"""Local native kit proof: full length, compressed source, or frame diagnostics."""
import copy
from contextlib import closing
from functools import partial
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sqlite3
import subprocess
import sys
import time
import uuid

APP = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('editor_canary_http', APP / 'agent/check-editor.py')
http = importlib.util.module_from_spec(spec)
spec.loader.exec_module(http)
http.request = partial(http.request, timeout=600)
assert http.STUDIO == 'http://localhost:1337' and http.EDITOR == 'http://localhost:1339'
RESUME = len(sys.argv) == 3 and sys.argv[1] == 'resume'
DIAGNOSTICS = sys.argv[1:] == ['diagnostics']
COMPRESSED = sys.argv[1:] == ['compressed'] or DIAGNOSTICS
assert not sys.argv[1:] or RESUME or COMPRESSED, 'Use no arguments, compressed, diagnostics, or resume RUN_ROOT.'
ROOT = Path(sys.argv[2]).resolve() if RESUME else APP / '.local' / (('editor-compressed-kit-' if COMPRESSED else 'editor-long-kit-') + str(uuid.uuid4()))
assert ROOT.parent == APP / '.local' and ROOT.name.startswith(('editor-long-kit-', 'editor-compressed-kit-'))
assert not RESUME or (ROOT / 'private.json').is_file(), 'A live scoped checkpoint is required.'
(ROOT / 'assets').mkdir(parents=True, mode=0o700, exist_ok=RESUME)
DATABASE = next((APP / '.alchemy/local/d1/cloudflare-runtime-D1DatabaseObject').glob('*.sqlite'))
DURATION = 2 if COMPRESSED else 239.68
FRAMES = math.ceil(DURATION * 24)
SHORT_FRAMES = FRAMES if COMPRESSED else 720
SOURCE_FILES = ['editor/render-object.ts', 'editor/render-coordinator.ts', 'editor/artifact.ts', 'editor/catalog.ts', 'editor/capacity.ts', 'editor/engine/Dockerfile', 'editor/engine/engine.py', 'editor/engine/visual_diagnostics.py', 'editor/engine/server.py', 'editor/project.ts', 'editor/archive.ts', 'editor/zip.ts', 'agent/check-editor-long-kit.py']
SOURCE_HASHES = {name: hashlib.sha256((APP / name).read_bytes()).hexdigest() for name in SOURCE_FILES}
samples = []
status_retries = 0


def sql(query, values=()):
    with closing(sqlite3.connect(f'file:{DATABASE}?mode=ro', uri=True)) as database:
        database.row_factory = sqlite3.Row
        return [dict(row) for row in database.execute(query, values)]


def render_status(job_id, token):
    global status_retries
    for attempt in range(4):
        try:
            return http.request(http.EDITOR, '/v1/tools/render.status', 'POST', {'jobId': job_id}, token=token)[0]
        except AssertionError as error:
            if attempt == 3 or 'received 500:' not in str(error) or '"code":"editor_error"' not in str(error):
                raise
            status_retries += 1
            print(json.dumps({'phase': 'retry-status-read', 'jobId': job_id, 'attempt': attempt + 1}), flush=True)
            time.sleep(1)


def sample():
    names = subprocess.check_output(['docker', 'ps', '--format', '{{.Names}}'], text=True).splitlines()
    native = [name for name in names if name.startswith('workerd-release-kit-editor-preview-RenderObject-') and not name.endswith('-proxy')]
    holders = sql('SELECT job_id,tenant_id,purpose FROM editor_capacity')
    record = {'at': time.time(), 'nativeContainers': len(native), 'capacity': holders}
    samples.append(record)
    assert len(native) <= 1 and len(holders) <= 1
    return record


def held_jobs():
    config = json.loads((APP / '.local/local-worker.json').read_text())
    result, _ = http.request(http.STUDIO, '/api/worker/holds', token=config['token'])
    return sorted([{key: job[key] for key in ('id', 'attempt', 'state')} for job in result['jobs']], key=lambda job: job['id'])


def media(command):
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-nostdin', *command], check=True, capture_output=True, timeout=180)


def fixture():
    media(['-f', 'lavfi', '-i', f'sine=frequency=440:sample_rate=48000:duration={DURATION}', '-af', 'pan=stereo|c0=c0|c1=0.8*c0', '-c:a', 'pcm_s16le', '-f', 'wav', str(ROOT / 'assets/master')])
    if COMPRESSED:
        (ROOT / 'assets/master').rename(ROOT / 'master.wav')
        media(['-i', str(ROOT / 'master.wav'), '-c:a', 'libmp3lame', '-b:a', '192k', '-f', 'mp3', str(ROOT / 'assets/master')])
    media(['-f', 'lavfi', '-i', 'testsrc2=size=640x360:rate=24', '-frames:v', str(FRAMES), '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '30', '-pix_fmt', 'yuv420p', '-f', 'mp4', str(ROOT / 'assets/scene')])
    (ROOT / 'assets/mask').write_bytes((http.FIXTURE / 'assets/mask').read_bytes())
    project = copy.deepcopy(json.loads((http.FIXTURE / 'project.json').read_text()))
    for asset in project['assets']:
        path = ROOT / 'assets' / asset['id']
        asset['bytes'] = path.stat().st_size
        asset['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        if asset['kind'] == 'audio':
            asset['duration'] = DURATION
        elif asset['kind'] == 'video':
            asset['duration'] = FRAMES / 24
        assert asset['bytes'] <= 100 * 1024 * 1024
    master = next(asset for asset in project['assets'] if asset['kind'] == 'audio')
    project['audioSha256'] = master['sha256']
    for index, composition in enumerate(project['compositions']):
        composition['frames'] = FRAMES if composition['id'] == 'film' else SHORT_FRAMES if composition['id'].startswith('short-') else 1
        clip = composition['clips'][0]
        clip['frames'] = composition['frames']
        if composition['id'].startswith('short-'):
            composition['audio']['startSeconds'] = 0 if COMPRESSED else (index - 1) * 60
            clip['inFrame'] = 0 if COMPRESSED else (index - 1) * 60 * 24
        if clip['reactive']:
            clip['reactive']['audioSha256'] = master['sha256']
            clip['reactive']['points'] = [{'frame': frame, 'value': value} for frame, value in [(0, 0), (FRAMES // 3, 1), (2 * FRAMES // 3, 0), (FRAMES, 1)]]
        composition['rationale'] = f'Synthetic technical fixture {index}; no real-song direction or creative acceptance.'
    if DIAGNOSTICS:
        held_image = ROOT / 'assets/held-image'
        media(['-i', str(ROOT / 'assets/scene'), '-frames:v', '1', '-f', 'image2', '-vcodec', 'png', str(held_image)])
        media(['-loop', '1', '-i', str(held_image), '-r', '24', '-frames:v', str(FRAMES), '-c:v', 'libx264', '-preset', 'ultrafast', '-pix_fmt', 'yuv420p', '-f', 'mp4', str(ROOT / 'assets/frozen')])
        media(['-f', 'lavfi', '-i', 'color=black:size=640x360:rate=24', '-frames:v', str(FRAMES), '-c:v', 'libx264', '-preset', 'ultrafast', '-pix_fmt', 'yuv420p', '-f', 'mp4', str(ROOT / 'assets/black')])
        for asset_id, kind in [('held-image', 'image'), ('frozen', 'video'), ('black', 'video')]:
            path = ROOT / 'assets' / asset_id
            project['assets'].append({'id': asset_id, 'kind': kind, 'bytes': path.stat().st_size,
                                      'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                                      'width': 640, 'height': 360, 'duration': 0 if kind == 'image' else DURATION})
        film = next(comp for comp in project['compositions'] if comp['id'] == 'film')
        left = film['clips'][0]
        left.update({'frames': 24, 'fadeIn': 0, 'fadeOut': 0})
        right = copy.deepcopy(left)
        right.update({'id': 'scene-right', 'at': 24, 'inFrame': 24})
        film['clips'].append(right)
        for index, asset_id in enumerate(['frozen', 'black', 'held-image'], start=1):
            comp = next(row for row in project['compositions'] if row['id'] == f'short-{index}')
            comp['captions'] = []
            comp['clips'][0].update({'assetId': asset_id, 'fadeIn': 0, 'fadeOut': 0, 'reactive': None})
    (ROOT / 'fixture-project.json').write_text(json.dumps(project, ensure_ascii=False, indent=2))
    return project, master


def main():
    before_holds = held_jobs()
    session = token = release_id = job_id = receipt = None
    checks = []
    timings = {}
    try:
        if DIAGNOSTICS:
            catalog, _ = http.request(http.EDITOR, '/v1/tools')
            tool = next(row for row in catalog['tools'] if row['name'] == 'artifact.verify')
            assert tool['output']['properties']['frameDiagnostics']['properties']['method']['enum'] == ['all-frame-reduced-rgb-luma/v1']
            checks.append('worker-advertises-current-frame-diagnostic-output-schema')
        if RESUME:
            checkpoint = json.loads((ROOT / 'private.json').read_text())
            session, token = checkpoint['session'], checkpoint['token']
            release_id, job_id = checkpoint['releaseId'], checkpoint['jobId']
            saved = sql('SELECT created_at,release_id FROM editor_jobs WHERE id=?', (job_id,))
            assert len(saved) == 1 and saved[0]['release_id'] == release_id
            snapshot, _ = http.request(http.EDITOR, '/v1/tools/project.inspect', 'POST', {'projectId': 'long-native-kit', 'revision': 1}, token=token)
            project = snapshot['project']
            master = next(asset for asset in project['assets'] if asset['kind'] == 'audio')
            assert master['duration'] == DURATION and project['releaseId'] == release_id
            for asset in project['assets']:
                content = (ROOT / 'assets' / asset['id']).read_bytes()
                assert len(content) == asset['bytes'] and hashlib.sha256(content).hexdigest() == asset['sha256']
            began = time.monotonic() - (time.time() - saved[0]['created_at'])
            checks.append('existing-native-render-resumed-without-submitting-another-intent')
        else:
            assert not sql("SELECT id FROM editor_jobs WHERE state IN ('queued','staging','running','verifying','cancel-requested','uncertain')")
            assert not sample()['capacity']
            print(json.dumps({'phase': 'preparing-full-length-fixture', 'frames': FRAMES, 'sourceSeconds': DURATION}), flush=True)
            project, master = fixture()
            session, token = http.principal()
            brief = {'title': 'Compressed audio regression' if COMPRESSED else 'Full-length synthetic technical kit', 'lyrics': project['lyrics'], 'language': project['language'], 'audioName': 'synthetic-2s.mp3' if COMPRESSED else 'synthetic-239.68s.wav', 'audioSha256': master['sha256'], 'audioBytes': master['bytes'], 'audioDuration': DURATION, 'profile': {'name': 'Native length check', 'identity': 'Synthetic technical proof only', 'palette': 'Midnight city', 'intensity': 'Restrained'}}
            release, _ = http.request(http.STUDIO, '/api/releases', 'POST', {'requestKey': str(uuid.uuid4()), 'brief': brief}, session=session, expected=201)
            release_id = project['releaseId'] = release['id']
            project['briefSha256'] = hashlib.sha256(json.dumps(brief, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
            for asset in project['assets']:
                content = (ROOT / 'assets' / asset['id']).read_bytes()
                http.request(http.EDITOR, '/v1/media', 'POST', asset, token=token, expected=201)
                http.request(http.EDITOR, '/v1/media/' + asset['id'], 'PUT', token=token, binary=content, extra={'Content-Type': 'application/octet-stream'})
            committed, _ = http.request(http.EDITOR, '/v1/tools/project.commit', 'POST', {'projectId': 'long-native-kit', 'expectedRevision': 0, 'intentId': 'long-native-commit', 'project': project}, token=token)
            assert committed['revision'] == 1
            start = {'projectId': 'long-native-kit', 'revision': 1, 'intentId': 'long-native-render', 'mode': 'kit', 'outputId': None}
            private = ROOT / 'private.json'
            private.write_text(json.dumps({'session': session, 'token': token, 'releaseId': release_id, 'intent': start})); private.chmod(0o600)
            began = time.monotonic()
            job, _ = http.request(http.EDITOR, '/v1/tools/render.start', 'POST', start, token=token, expected=202)
            job_id = job['jobId']
            private.write_text(json.dumps({'session': session, 'token': token, 'releaseId': release_id, 'jobId': job_id, 'intent': start})); private.chmod(0o600)
            replay, _ = http.request(http.EDITOR, '/v1/tools/render.start', 'POST', start, token=token, expected=202)
            assert replay['jobId'] == job_id
            checks.append('compressed-source-immutable-kit-intent-replay' if COMPRESSED else 'full-length-immutable-kit-intent-replay')
        last_progress = None
        deadline = time.monotonic() + 1900
        while time.monotonic() < deadline:
            status = render_status(job_id, token)
            current_sample = sample()
            progress = json.dumps({'state': status['state'], 'progress': status['progress']}, sort_keys=True)
            if progress != last_progress:
                print(json.dumps({'phase': 'native-render', 'elapsedSeconds': round(time.monotonic() - began, 1), 'jobId': job_id, 'state': status['state'], 'progress': status['progress']}), flush=True)
                last_progress = progress
            if status['state'] in ['ready', 'failed', 'cancelled', 'uncertain']:
                break
            time.sleep(5)
        assert status['state'] == 'ready', json.dumps(status)
        timings['renderAndStoredReadbackSeconds'] = round(time.monotonic() - began, 3)
        native_receipt = status['receipt']
        assert len(native_receipt['outputs']) == 6 and len({output['id'] for output in native_receipt['outputs']}) == 6
        film = next(output for output in native_receipt['outputs'] if output['id'] == 'film')
        assert film['frames'] == FRAMES and film['duration'] >= DURATION
        assert all(output['frames'] == SHORT_FRAMES for output in native_receipt['outputs'] if output['id'].startswith('short-'))
        checks.append('48-frame-compressed-master-four-videos-and-two-stills' if COMPRESSED else '5753-frame-full-film-three-720-frame-promos-and-two-stills')
        if DIAGNOSTICS:
            diagnostics = {output['id']: output['frameDiagnostics'] for output in native_receipt['outputs']}
            assert all(row['completeFrameCoverage'] is True and row['semanticReviewed'] is False for row in diagnostics.values())
            assert diagnostics['short-1']['reviewSuggested'] is True and diagnostics['short-1']['nearStaticRanges']
            assert diagnostics['short-2']['reviewSuggested'] is True and diagnostics['short-2']['counts']['nearBlackFrames'] == FRAMES
            assert diagnostics['short-3']['reviewSuggested'] is False
            assert diagnostics['short-3']['nearStaticRanges'][0]['expected'] is True
            assert diagnostics['short-3']['nearStaticRanges'][0]['context'] == 'declared-image-hold'
            assert diagnostics['film']['joinMeasurements'][0]['atFrame'] == 24
            checks.append('all-frame-black-freeze-declared-hold-and-planned-join-diagnostics')
        while sample()['capacity'] and time.monotonic() < deadline:
            time.sleep(1)
        assert not sample()['capacity']
        checks.append('full-kit-stored-before-confirmed-native-termination')
        verification_started = time.monotonic()
        outputs = []
        for output in native_receipt['outputs']:
            if output['id'] == 'film':
                client_input = ROOT / 'verification-client-input.json'
                client_output = ROOT / 'verification-client-output.json'
                client_input.write_text(json.dumps({'token': token, 'jobId': job_id})); client_input.chmod(0o600)
                client = subprocess.run(['bun', 'agent/check-editor-capacity-client.ts', str(client_input), str(client_output)], cwd=APP, check=True, capture_output=True, text=True, timeout=600)
                verified = json.loads(client_output.read_text())['result']
                client_input.unlink()
                checks.append('real-agent-client-completes-full-film-cold-verification')
            else:
                verified, _ = http.request(http.EDITOR, '/v1/tools/artifact.verify', 'POST', {'jobId': job_id, 'outputId': output['id']}, token=token)
            assert verified['completeDecode'] is True and verified['sha256'] == output['sha256'] and verified['bytes'] == output['bytes']
            assert verified['frameDiagnostics']['sampledFrames'] == output['frames']
            assert verified['frameDiagnostics'] == output['frameDiagnostics']
            content, _ = http.request(http.EDITOR, f'/v1/jobs/{job_id}/outputs/{output["id"]}', token=token)
            assert len(content) == output['bytes'] and hashlib.sha256(content).hexdigest() == output['sha256']
            extension = '.jpg' if output['id'] in ['thumbnail', 'artwork'] else '.mp4'
            destination = ROOT / (output['id'] + extension)
            destination.write_bytes(content)
            subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-i', str(destination), '-f', 'null', '-'], capture_output=True, check=True, timeout=180)
            outputs.append({'id': output['id'], 'sha256': output['sha256'], 'bytes': output['bytes'], 'frames': output['frames'], 'width': output['width'], 'height': output['height'], 'duration': output['duration'], 'frameDiagnostics': verified['frameDiagnostics'], 'independentStoredVerification': True, 'completeDownloadedDecode': True})
            print(json.dumps({'phase': 'verified-output', 'outputId': output['id'], 'bytes': output['bytes']}), flush=True)
            sample()
        timings['coldVerificationAndDownloadedDecodeSeconds'] = round(time.monotonic() - verification_started, 3)
        checks += ['six-cold-independent-stored-verifications-match-rendered-bytes', 'six-private-downloads-hash-and-completely-decode']
        archive_started = time.monotonic()
        located, _ = http.request(http.EDITOR, '/v1/tools/kit.locate', 'POST', {'jobId': job_id}, token=token)
        archive, _ = http.request(http.EDITOR, f'/v1/jobs/{job_id}/archive', token=token, raw=True)
        archive_path = ROOT / 'technical-kit.zip'
        archive_path.write_bytes(archive)
        descriptor_path = ROOT / 'archive-descriptor.json'
        descriptor_path.write_text(json.dumps(located))
        verification = subprocess.run(['python3', 'agent/verify-kit.py', str(archive_path), str(descriptor_path)], cwd=APP, capture_output=True, text=True, check=True, timeout=180)
        archive_proof = json.loads(verification.stdout)
        timings['archiveAndIndependentVerificationSeconds'] = round(time.monotonic() - archive_started, 3)
        checks.append('private-kit-archive-and-eight-independent-entry-checks')
        assert held_jobs() == before_holds
        assert SOURCE_HASHES == {name: hashlib.sha256((APP / name).read_bytes()).hexdigest() for name in SOURCE_FILES}
        final_sample = sample()
        assert not final_sample['capacity'] and final_sample['nativeContainers'] == 0
        checks += ['both-assigned-pal-pal-holds-unchanged', 'one-native-container-at-peak-zero-after-final-verification']
        receipt = {'scope': 'local Workerd/D1/R2 all-frame diagnostic regression only' if DIAGNOSTICS else 'local Workerd/D1/R2 compressed-source regression only' if COMPRESSED else 'local Workerd/D1/R2 full-length synthetic kit performance only', 'testedAt': time.time(), 'passed': True, 'checks': checks, 'sourceHashes': SOURCE_HASHES, 'clientSourceHashes': {name: hashlib.sha256((APP / name).read_bytes()).hexdigest() for name in ['agent/editor-request.ts', 'agent/check-editor-capacity-client.ts']}, 'releaseId': release_id, 'editorJobId': job_id, 'sourceAudioDuration': DURATION, 'sourceAudioSha256': master['sha256'], 'sourceAudioIsSynthetic': True, 'nativeReceipt': native_receipt, 'outputs': outputs, 'timings': timings, 'archive': {'bytes': len(archive), 'sha256': hashlib.sha256(archive).hexdigest(), 'verification': archive_proof}, 'peakNativeContainersObserved': max(row['nativeContainers'] for row in samples), 'finalNativeContainersObserved': 0, 'capacitySlotReleased': True, 'gpuInferenceSubmitted': False, 'cloudVerified': False, 'cloudPerformanceVerified': False, 'palPalKitCompleted': False, 'motionReviewed': False, 'heard': False, 'creativelyAccepted': False}
        receipt['statusReadRetries'] = status_retries
        return receipt
    finally:
        if token and release_id:
            # Read authoritative IDs if a start response was lost; never submit a new intent.
            for entry in sql('SELECT id,state FROM editor_jobs WHERE release_id=?', (release_id,)):
                if entry['state'] not in ['ready', 'failed', 'cancelled']:
                    http.request(http.EDITOR, '/v1/tools/render.cancel', 'POST', {'jobId': entry['id']}, token=token)
        if token:
            http.request(http.EDITOR, '/v1/operator/tokens/revoke', 'POST', {'targetToken': token}, token=http.OPERATOR)
            assert sql('SELECT enabled FROM editor_tokens WHERE hash=?', (hashlib.sha256(token.encode()).hexdigest(),))[0]['enabled'] == 0
        if session:
            http.request(http.STUDIO, '/api/auth/logout', 'POST', {}, session=session)
            assert not sql('SELECT hash FROM sessions WHERE hash=?', (hashlib.sha256(session.split('=', 1)[1].encode()).hexdigest(),))
        (ROOT / 'private.json').unlink(missing_ok=True)
        (ROOT / 'verification-client-input.json').unlink(missing_ok=True)
        (ROOT / 'samples.json').write_text(json.dumps(samples, indent=2))
        if receipt:
            receipt['diagnosticTokensRevoked'] = True
            receipt['diagnosticSessionsLoggedOut'] = True
            (APP / 'docs/editor' / ('frame-diagnostics-runtime-receipt.json' if DIAGNOSTICS else 'compressed-kit-runtime-receipt.json' if COMPRESSED else 'long-kit-runtime-receipt.json')).write_text(json.dumps(receipt, indent=2) + '\n')


if __name__ == '__main__':
    result = main()
    print(json.dumps({'passed': result['passed'], 'checks': result['checks'], 'timings': result['timings'], 'cloudVerified': False, 'palPalKitCompleted': False}), flush=True)
