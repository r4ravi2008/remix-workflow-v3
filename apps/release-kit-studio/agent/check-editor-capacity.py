"""Local Workerd admission proof with real native renders and scoped cleanup."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import time
import uuid

APP = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('editor_canary_http', APP / 'agent/check-editor.py')
http = importlib.util.module_from_spec(spec)
spec.loader.exec_module(http)
assert http.STUDIO == 'http://localhost:1337' and http.EDITOR == 'http://localhost:1339'
ROOT = APP / '.local' / ('editor-capacity-' + str(uuid.uuid4()))
ROOT.mkdir(mode=0o700)
database = next((APP / '.alchemy/local/d1/cloudflare-runtime-D1DatabaseObject').glob('*.sqlite'))
principals = []
jobs = []
samples = []
checks = []
SOURCE_FILES = ['editor/capacity.ts', 'editor/render-object.ts', 'editor/render-coordinator.ts', 'agent/editor-request.ts', 'agent/editor.ts', 'migrations/0004_editor_capacity.sql']
source_hashes = {name: hashlib.sha256((APP / name).read_bytes()).hexdigest() for name in SOURCE_FILES}


def sql(query, parameters=()):
    with sqlite3.connect(database) as connection:
        connection.row_factory = sqlite3.Row
        return [dict(row) for row in connection.execute(query, parameters)]


def sample():
    holder = sql('SELECT job_id,tenant_id,purpose FROM editor_capacity')
    lines = subprocess.run(['docker', 'ps', '--format', '{{json .}}'], capture_output=True, text=True, check=True).stdout.splitlines()
    native = [row for line in lines if (row := json.loads(line))['Names'].startswith('workerd-release-kit-editor-preview-RenderObject-') and not row['Names'].endswith('-proxy')]
    record = {'at': time.time(), 'capacityHolders': holder, 'nativeContainerCount': len(native)}
    samples.append(record)
    assert len(holder) <= 1 and len(native) <= 1
    return holder


def status(entry):
    return http.request(http.EDITOR, '/v1/tools/render.status', 'POST', {'jobId': entry['jobId']}, token=entry['token'])[0]


def setup(principal, project_id, upload):
    session, token = principal
    project = copy.deepcopy(json.loads((http.FIXTURE / 'project.json').read_text()))
    audio = next(asset for asset in project['assets'] if asset['kind'] == 'audio')
    brief = {'title': 'Capacity synthetic canary', 'lyrics': project['lyrics'], 'language': project['language'], 'audioName': 'canary.wav', 'audioSha256': audio['sha256'], 'audioBytes': audio['bytes'], 'audioDuration': audio['duration'], 'profile': {'name': 'Capacity canary', 'identity': 'Synthetic scheduling proof', 'palette': 'Midnight city', 'intensity': 'Restrained'}}
    release, _ = http.request(http.STUDIO, '/api/releases', 'POST', {'requestKey': str(uuid.uuid4()), 'brief': brief}, session=session, expected=201)
    project['releaseId'] = release['id']
    project['briefSha256'] = hashlib.sha256(json.dumps(brief, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    if upload:
        for asset in project['assets']:
            content = (http.FIXTURE / 'assets' / asset['id']).read_bytes()
            assert len(content) == asset['bytes'] and hashlib.sha256(content).hexdigest() == asset['sha256']
            http.request(http.EDITOR, '/v1/media', 'POST', asset, token=token, expected=201)
            http.request(http.EDITOR, '/v1/media/' + asset['id'], 'PUT', token=token, binary=content, extra={'Content-Type': 'application/octet-stream'})
    committed, _ = http.request(http.EDITOR, '/v1/tools/project.commit', 'POST', {'projectId': project_id, 'expectedRevision': 0, 'intentId': 'commit-' + project_id, 'project': project}, token=token)
    assert committed['revision'] == 1
    return {'token': token, 'releaseId': release['id'], 'render': {'projectId': project_id, 'revision': 1, 'intentId': 'render-' + project_id, 'mode': 'diagnostic', 'outputId': 'film'}}


def start(entry):
    result, _ = http.request(http.EDITOR, '/v1/tools/render.start', 'POST', entry['render'], token=entry['token'], expected=202)
    entry['jobId'] = result['jobId']; jobs.append(entry)
    private = ROOT / 'private.json'
    private.write_text(json.dumps({'principals': principals, 'jobs': jobs})); private.chmod(0o600)
    return entry


def main():
    assert not sql('SELECT * FROM editor_capacity')
    assert not sql("SELECT id FROM editor_jobs WHERE state IN ('queued','staging','running','verifying','cancel-requested','uncertain')")
    first_principal = http.principal(); principals.append(first_principal)
    other_principal = http.principal(); principals.append(other_principal)
    first = setup(first_principal, 'capacity-first', True)
    second = setup(other_principal, 'capacity-other', True)
    cancelled = setup(first_principal, 'capacity-cancelled', False)
    start(first)
    for _ in range(100):
        holder = sample()
        if holder: break
        time.sleep(0.1)
    assert holder and holder[0]['job_id'] == first['jobId']
    start(second); start(cancelled)
    for _ in range(30):
        queued = status(second)
        if queued['state'] == 'queued' and queued['progress']['phase'] == 'waiting-for-render-capacity': break
        time.sleep(0.1)
    assert queued['state'] == 'queued' and queued['progress']['phase'] == 'waiting-for-render-capacity'
    checks.append('second-tenant-waits-without-booting-another-native-container')
    before = sample()
    stopped, _ = http.request(http.EDITOR, '/v1/tools/render.cancel', 'POST', {'jobId': cancelled['jobId']}, token=cancelled['token'])
    assert stopped['state'] == 'cancelled' and sample() == before
    replay, _ = http.request(http.EDITOR, '/v1/tools/render.start', 'POST', cancelled['render'], token=cancelled['token'], expected=202)
    assert replay['state'] == 'cancelled' and replay['jobId'] == cancelled['jobId']
    checks.append('queued-cancellation-preserves-the-active-tenant-and-cancelled-replay')
    http.request(http.EDITOR, '/v1/tools/render.status', 'POST', {'jobId': first['jobId']}, token=second['token'], expected=404)
    checks.append('queued-and-running-job-tenant-isolation')
    deadline = time.time() + 240
    while time.time() < deadline:
        first_status = status(first); second_status = status(second); holder = sample()
        if first_status['state'] == 'ready' and holder and holder[0]['job_id'] == second['jobId']: break
        assert first_status['state'] not in ['failed','uncertain'] and second_status['state'] not in ['failed','uncertain']
        time.sleep(0.25)
    assert first_status['state'] == 'ready' and holder and holder[0]['job_id'] == second['jobId']
    rejected, headers = http.request(http.EDITOR, '/v1/tools/artifact.verify', 'POST', {'jobId': first['jobId'], 'outputId': 'film'}, token=first['token'], expected=503)
    assert rejected['code'] == 'render_capacity_busy' and headers['Retry-After'] == '5'
    checks.append('cold-verification-shares-editor-capacity-and-returns-explicit-backoff')
    client = ROOT / 'verification-input.json'
    client.write_text(json.dumps({'token': first['token'], 'jobId': first['jobId']})); client.chmod(0o600)
    log = (ROOT / 'verification-client.log').open('w')
    child = subprocess.Popen(['bun', 'agent/check-editor-capacity-client.ts', str(client), str(ROOT / 'verification-result.json')], cwd=APP, stdout=log, stderr=subprocess.STDOUT)
    deadline = time.time() + 240
    while time.time() < deadline:
        first_status = status(first); second_status = status(second); holder = sample()
        if first_status['state'] == second_status['state'] == 'ready' and child.poll() is not None and not holder: break
        assert first_status['state'] not in ['failed','uncertain'] and second_status['state'] not in ['failed','uncertain']
        time.sleep(0.25)
    assert child.poll() == 0 and first_status['state'] == second_status['state'] == 'ready' and not sample()
    log.close()
    verification = json.loads((ROOT / 'verification-result.json').read_text())
    assert verification['statuses'][0] == 503 and verification['statuses'][-1] == 200
    assert verification['result']['sha256'] == first_status['receipt']['outputs'][0]['sha256']
    checks.append('real-agent-client-waits-for-capacity-and-reverifies-the-same-stored-bytes')
    results = []
    for entry, ready in [(first, first_status), (second, second_status)]:
        content, _ = http.request(http.EDITOR, '/v1/jobs/' + entry['jobId'] + '/outputs/film', token=entry['token'])
        measured = ready['receipt']['outputs'][0]
        assert hashlib.sha256(content).hexdigest() == measured['sha256'] and len(content) == measured['bytes']
        destination = ROOT / (entry['jobId'] + '.mp4'); destination.write_bytes(content)
        subprocess.run(['ffmpeg', '-v', 'error', '-i', str(destination), '-f', 'null', '-'], capture_output=True, check=True, timeout=60)
        results.append({'jobId': entry['jobId'], 'releaseId': entry['releaseId'], 'sha256': measured['sha256'], 'bytes': measured['bytes'], 'frames': measured['frames'], 'completeDownloadedDecode': True})
    checks.append('two-tenant-renders-have-verified-private-output-hashes-and-complete-decodes')
    assert max(row['nativeContainerCount'] for row in samples) == 1
    assert sample() == [] and samples[-1]['nativeContainerCount'] == 0
    checks.append('one-native-container-observed-at-peak-and-zero-after-verified-handoff')
    assert source_hashes == {name: hashlib.sha256((APP / name).read_bytes()).hexdigest() for name in SOURCE_FILES}
    return {'scope': 'local Workerd/D1/R2 and native container scheduling only', 'testedAt': time.time(), 'passed': True, 'checks': checks, 'sourceHashes': source_hashes, 'outputs': results, 'cancelledJobId': cancelled['jobId'], 'peakNativeContainersObserved': 1, 'finalNativeContainersObserved': 0, 'capacitySlotReleased': True, 'verificationStatuses': verification['statuses'], 'cloudVerified': False, 'palPalKitCompleted': False, 'motionReviewed': False, 'heard': False, 'creativelyAccepted': False}


if __name__ == '__main__':
    receipt = None
    try:
        receipt = main()
    finally:
        for entry in jobs:
            current = status(entry)
            if current['state'] not in ['ready','failed','cancelled']:
                http.request(http.EDITOR, '/v1/tools/render.cancel', 'POST', {'jobId': entry['jobId']}, token=entry['token'])
        for session, token in principals:
            http.request(http.EDITOR, '/v1/operator/tokens/revoke', 'POST', {'targetToken': token}, token=http.OPERATOR)
            http.request(http.STUDIO, '/api/auth/logout', 'POST', {}, session=session)
            assert sql('SELECT enabled FROM editor_tokens WHERE hash=?', (hashlib.sha256(token.encode()).hexdigest(),))[0]['enabled'] == 0
            assert not sql('SELECT hash FROM sessions WHERE hash=?', (hashlib.sha256(session.split('=', 1)[1].encode()).hexdigest(),))
        for name in ['private.json','verification-input.json']:
            (ROOT / name).unlink(missing_ok=True)
        (ROOT / 'samples.json').write_text(json.dumps(samples, indent=2))
        if receipt:
            receipt['diagnosticTokensRevoked'] = True; receipt['diagnosticSessionsLoggedOut'] = True
            (APP / 'docs/editor/capacity-runtime-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
            print(json.dumps(receipt))
