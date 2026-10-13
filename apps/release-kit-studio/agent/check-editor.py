import copy
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path


APP = Path(__file__).resolve().parent.parent
STUDIO = os.environ.get('STUDIO_URL', 'http://localhost:1337')
EDITOR = os.environ.get('EDITOR_URL', 'http://localhost:1339')
FIXTURE = APP / '.local/editor-canary-r02'
OPERATOR = next(line.split('=', 1)[1] for line in (APP / '.env').read_text().splitlines() if line.startswith('STUDIO_OPERATOR_TOKEN='))
CHECKS = []


def request(base, path, method='GET', value=None, session=None, token=None, binary=None, expected=200, extra=None, raw=False, timeout=120):
    data = binary if binary is not None else json.dumps(value, ensure_ascii=False).encode() if value is not None else None
    headers = {'Content-Type': 'application/json', 'Origin': base}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    if session:
        headers['Cookie'] = session
    if extra:
        headers.update(extra)
    attempt = urllib.request.Request(base + path, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(attempt, timeout=timeout) as response:
            status, content, readback = response.status, response.read(), response.headers
    except urllib.error.HTTPError as error:
        status, content, readback = error.code, error.read(), error.headers
    if status != expected:
        detail = content[:1000].decode(errors='replace') if 'application/json' in readback.get('Content-Type', '') else f'{len(content)} response bytes'
        raise AssertionError(f'{method} {path}: expected {expected}, received {status}: {detail}')
    return (content if raw or binary is not None or '/outputs/' in path else json.loads(content)), readback


def principal():
    invite, _ = request(STUDIO, '/api/operator/invites', 'POST', {'tenantName': 'Editor synthetic canary ' + str(uuid.uuid4())}, token=OPERATOR, expected=201)
    account, headers = request(STUDIO, '/api/auth/exchange', 'POST', {'token': invite['token']})
    session = headers['Set-Cookie'].split(';', 1)[0]
    token, _ = request(EDITOR, '/v1/operator/tokens', 'POST', {'tenantId': account['tenant']['id']}, token=OPERATOR, expected=201)
    return session, token['token']


def main():
    health, _ = request(STUDIO, '/api/editor/health')
    if not health['rendererConfigured'] or health['service'] != 'release-kit-editor':
        raise AssertionError('Studio service binding does not reach the editor.')
    CHECKS.append('studio-to-editor-service-binding')
    request(EDITOR, '/v1/tools/project.inspect', 'POST', {'projectId': 'canary-project', 'revision': None}, expected=401)
    request(EDITOR, '/v1/tools/project.inspect', 'POST', {'projectId': 'canary-project', 'revision': None}, token='invalid-token', expected=401)
    CHECKS.append('missing-and-invalid-credentials-rejected')
    session, token = principal()
    other_session, other_token = principal()
    project = json.loads((FIXTURE / 'project.json').read_text())
    audio = next(asset for asset in project['assets'] if asset['kind'] == 'audio')
    brief = {'title': 'Editor synthetic canary', 'lyrics': project['lyrics'], 'language': project['language'], 'audioName': 'canary.wav', 'audioSha256': audio['sha256'], 'audioBytes': audio['bytes'], 'audioDuration': audio['duration'],
             'profile': {'name': 'Editor canary', 'identity': 'Synthetic technical test. No creative acceptance.', 'palette': 'Midnight city', 'intensity': 'Restrained'}}
    release, _ = request(STUDIO, '/api/releases', 'POST', {'requestKey': str(uuid.uuid4()), 'brief': brief}, session=session, expected=201)
    project['releaseId'] = release['id']
    project['briefSha256'] = hashlib.sha256(json.dumps(brief, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()
    private = APP / '.local/editor-http-private'
    private.mkdir(mode=0o700, exist_ok=True)
    for asset in project['assets']:
        metadata = private / (asset['id'] + '.json')
        metadata.write_text(json.dumps(asset))
        run = subprocess.run(['bun', 'agent/editor-cli.ts', 'upload', str(metadata), str(FIXTURE / 'assets' / asset['id'])], cwd=APP, env={**os.environ, 'EDITOR_URL': EDITOR, 'EDITOR_TOKEN': token}, capture_output=True, text=True)
        if run.returncode:
            raise AssertionError('CLI upload failed: ' + run.stderr[:1000])
        readback = json.loads(run.stdout)
        if not readback['uploaded'] or readback['metadata']['sha256'] != asset['sha256']:
            raise AssertionError('CLI immutable upload readback failed.')
    CHECKS.append('cli-to-worker-to-private-r2-media-upload')
    request(EDITOR, '/v1/tools/media.inspect', 'POST', {'assetId': 'master'}, token=other_token, expected=404)
    CHECKS.append('tenant-media-isolation')
    commit = {'projectId': 'canary-project', 'expectedRevision': 0, 'intentId': 'initial-edit', 'project': project}
    first, _ = request(EDITOR, '/v1/tools/project.commit', 'POST', commit, token=token)
    request(STUDIO, '/api/editor/tools/project.inspect', 'POST', {'projectId': 'canary-project', 'revision': None}, session=session, extra={'Origin': 'https://foreign.example'}, expected=403)
    CHECKS.append('cookie-origin-protection')
    replay, _ = request(EDITOR, '/v1/tools/project.commit', 'POST', commit, token=token)
    if first['revision'] != 1 or replay['revision'] != 1:
        raise AssertionError('Revision replay changed the project.')
    CHECKS.append('worker-d1-revision-and-intent-replay')
    request(EDITOR, '/v1/tools/project.inspect', 'POST', {'projectId': 'canary-project', 'revision': None}, token=other_token, expected=404)
    CHECKS.append('tenant-project-isolation')
    changed = copy.deepcopy(commit)
    changed['project']['compositions'][0]['clips'][0]['transform']['centerX'] = 0.4
    request(EDITOR, '/v1/tools/project.commit', 'POST', changed, token=token, expected=409)
    stale = {**changed, 'intentId': 'stale-edit'}
    request(EDITOR, '/v1/tools/project.commit', 'POST', stale, token=token, expected=409)
    CHECKS.append('changed-intent-and-stale-revision-rejected')
    frozen = copy.deepcopy(commit)
    frozen['intentId'] = 'wrong-source'
    frozen['project']['audioSha256'] = '0' * 64
    request(EDITOR, '/v1/tools/project.commit', 'POST', frozen, token=token, expected=409)
    CHECKS.append('frozen-source-binding')
    job_request = {'projectId': 'canary-project', 'revision': 1, 'intentId': 'render-film', 'mode': 'diagnostic', 'outputId': 'film'}
    job, _ = request(EDITOR, '/v1/tools/render.start', 'POST', job_request, token=token, expected=202)
    private_state = private / 'runtime.json'
    private_state.write_text(json.dumps({'token': token, 'jobId': job['jobId'], 'releaseId': release['id']}))
    private_state.chmod(0o600)
    replay_job, _ = request(EDITOR, '/v1/tools/render.start', 'POST', job_request, token=token, expected=202)
    if replay_job['jobId'] != job['jobId']:
        raise AssertionError('Render replay created duplicate work.')
    CHECKS.append('cloud-runtime-render-intent-replay')
    request(EDITOR, '/v1/tools/render.status', 'POST', {'jobId': job['jobId']}, token=other_token, expected=404)
    CHECKS.append('tenant-job-isolation')
    for _ in range(150):
        status, _ = request(EDITOR, '/v1/tools/render.status', 'POST', {'jobId': job['jobId']}, token=token)
        if status['state'] in {'ready', 'failed', 'cancelled', 'uncertain'}:
            break
        time.sleep(1)
    if status['state'] != 'ready':
        raise AssertionError('Worker/container render did not complete: ' + json.dumps(status))
    CHECKS.append('worker-container-private-r2-render-readback')
    artifact, _ = request(EDITOR, f'/v1/jobs/{job["jobId"]}/outputs/film', token=token)
    receipt = status['receipt']
    if hashlib.sha256(artifact).hexdigest() != receipt['outputs'][0]['sha256'] or not receipt['storedByteReadback'] or not receipt['receiptStored']:
        raise AssertionError('Stored output differs from its verified receipt.')
    destination = private / (job['jobId'] + '.mp4')
    run = subprocess.run(['bun', 'agent/editor-cli.ts', 'download', job['jobId'], 'film', str(destination)], cwd=APP, env={**os.environ, 'EDITOR_URL': EDITOR, 'EDITOR_TOKEN': token}, capture_output=True, text=True)
    if run.returncode or hashlib.sha256(destination.read_bytes()).hexdigest() != receipt['outputs'][0]['sha256']:
        raise AssertionError('CLI private artifact download failed: ' + run.stderr[:1000])
    CHECKS.append('cli-private-download-with-checksum')
    verified, _ = request(EDITOR, '/v1/tools/artifact.verify', 'POST', {'jobId': job['jobId'], 'outputId': 'film'}, token=token)
    if verified['sha256'] != receipt['outputs'][0]['sha256']:
        raise AssertionError('Independent Worker verification differs from stored output.')
    CHECKS.append('independent-stored-byte-verification')
    review = {'jobId': job['jobId'], 'outputId': 'film', 'sha256': verified['sha256'], 'kind': 'creatively-accepted', 'startFrame': 0, 'endFrame': 48, 'method': 'invalid agent self-approval test', 'notes': 'This should be rejected.'}
    request(EDITOR, '/v1/tools/artifact.review', 'POST', review, token=token, expected=403)
    CHECKS.append('agent-cannot-self-grant-creative-acceptance')
    request(EDITOR, '/v1/tools/artifact.review', 'POST', {**review, 'kind': 'frame-inspected', 'sha256': '0' * 64}, token=token, expected=422)
    CHECKS.append('stale-artifact-review-rejected')
    cancellation = {**job_request, 'intentId': 'cancel-render'}
    cancel_job, _ = request(EDITOR, '/v1/tools/render.start', 'POST', cancellation, token=token, expected=202)
    cancelled, _ = request(EDITOR, '/v1/tools/render.cancel', 'POST', {'jobId': cancel_job['jobId']}, token=token)
    if cancelled['state'] != 'cancelled' or cancelled['receipt'] is not None:
        raise AssertionError('Owned render cancellation did not close the attempt without promotion.')
    cancelled_replay, _ = request(EDITOR, '/v1/tools/render.start', 'POST', cancellation, token=token, expected=202)
    if cancelled_replay['jobId'] != cancel_job['jobId'] or cancelled_replay['state'] != 'cancelled':
        raise AssertionError('Cancelled intent replay restarted work.')
    CHECKS.append('worker-cancellation-and-replay-fence')
    result = {'scope': 'alchemy-local-workerd-d1-r2-cloudflare-container-synthetic-canary', 'testedAt': time.time(), 'checks': CHECKS, 'passed': True,
              'releaseId': release['id'], 'jobId': job['jobId'], 'cloudVerified': False, 'palPalKitCompleted': False, 'motionReviewed': False, 'heard': False, 'creativelyAccepted': False, 'receipt': receipt}
    (APP / 'docs/editor/worker-runtime-receipt.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    for diagnostic_token in [token, other_token]:
        request(EDITOR, '/v1/operator/tokens/revoke', 'POST', {'targetToken': diagnostic_token}, token=OPERATOR)
        request(EDITOR, '/v1/tools/project.inspect', 'POST', {'projectId': 'canary-project', 'revision': None}, token=diagnostic_token, expected=401)
    private_state.unlink()
    CHECKS.append('diagnostic-agent-tokens-revoked')
    result['checks'] = CHECKS
    result['diagnosticCredentialsRevoked'] = True
    (APP / 'docs/editor/worker-runtime-receipt.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'ok': True, 'scope': result['scope'], 'checks': CHECKS}))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(json.dumps({'ok': False, 'checksCompleted': CHECKS, 'error': str(error)}), file=sys.stderr)
        sys.exit(1)
