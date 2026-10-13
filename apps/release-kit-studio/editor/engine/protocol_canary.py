import copy
import hashlib
import json
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path


FIXTURES = Path('/fixtures')
ROOT = Path('/tmp/protocol-canary')
ROOT.mkdir(exist_ok=True)
CHECKS = []


def request(path, method='GET', value=None, binary=None, expected=200):
    data = binary if binary is not None else json.dumps(value, ensure_ascii=False).encode() if value is not None else None
    attempt = urllib.request.Request('http://127.0.0.1:8080' + path, data=data, method=method,
                                     headers={'Content-Type': 'application/octet-stream' if binary is not None else 'application/json'})
    try:
        with urllib.request.urlopen(attempt, timeout=60) as response:
            status, content = response.status, response.read()
    except urllib.error.HTTPError as error:
        status, content = error.code, error.read()
    if status != expected:
        raise AssertionError(f'{method} {path}: expected {expected}, received {status}: {content[:500]!r}')
    return json.loads(content) if binary is None and '/outputs/' not in path else content


def sources(identity, project):
    for asset in project['assets']:
        content = (FIXTURES / 'assets' / asset['id']).read_bytes()
        result = request(f'/jobs/{identity}/assets/{asset["id"]}', 'PUT', binary=content)
        if b'"verified": true' not in result:
            raise AssertionError('Source checksum was not verified.')


server = subprocess.Popen(['python3', '/app/server.py'], env={'PATH': '/usr/local/bin:/usr/bin:/bin', 'EDITOR_SCRATCH': str(ROOT / 'jobs')})
try:
    for _ in range(80):
        try:
            health = request('/health')
            break
        except urllib.error.URLError:
            time.sleep(0.1)
    else:
        raise AssertionError('Native HTTP server did not become ready.')
    if not health['h264'] or 'Noto Sans Telugu' not in health['fonts']:
        raise AssertionError('Native capabilities missing.')
    CHECKS.append('http-capabilities-readback')
    project = json.loads((FIXTURES / 'project.json').read_text())
    project['compositions'] = [project['compositions'][0]]
    payload = {'jobId': 'protocol-render', 'project': project}
    request('/jobs', 'POST', payload, expected=201)
    if request('/jobs', 'POST', payload)['state'] != 'staging':
        raise AssertionError('Exact intent replay changed the job.')
    CHECKS.append('exact-intent-replay')
    conflict = copy.deepcopy(payload)
    conflict['project']['compositions'][0]['clips'][0]['color']['brightness'] = 0.1
    request('/jobs', 'POST', conflict, expected=409)
    CHECKS.append('changed-intent-rejected')
    request('/jobs', 'POST', {'jobId': 'parallel-render', 'project': project}, expected=409)
    CHECKS.append('one-active-native-job')
    request('/jobs/unknown', expected=404)
    CHECKS.append('missing-outcome-needs-reconciliation')
    corrupt = bytearray((FIXTURES / 'assets' / 'master').read_bytes())
    corrupt[-1] ^= 1
    request('/jobs/protocol-render/assets/master', 'PUT', binary=bytes(corrupt), expected=422)
    CHECKS.append('source-checksum-rejected')
    sources('protocol-render', project)
    request('/jobs/protocol-render/run', 'POST', expected=202)
    for _ in range(600):
        status = request('/jobs/protocol-render')
        if status['state'] in {'ready', 'failed', 'cancelled'}:
            break
        time.sleep(0.2)
    if status['state'] != 'ready':
        raise AssertionError('HTTP render failed: ' + json.dumps(status))
    CHECKS.append('http-render-progress-and-completion')
    artifact = request('/jobs/protocol-render/outputs/film')
    measured = status['receipt']['outputs'][0]
    if hashlib.sha256(artifact).hexdigest() != measured['sha256'] or len(artifact) != measured['bytes']:
        raise AssertionError('Downloaded bytes differ from the render receipt.')
    CHECKS.append('output-byte-readback')
    request('/jobs', 'POST', {'jobId': 'cold-verifier', 'project': project, 'verificationOnly': True}, expected=201)
    sources('cold-verifier', project)
    request('/jobs/cold-verifier/verification/film', 'PUT', binary=artifact)
    verified = request('/jobs/cold-verifier/verify', 'POST', {'outputId': 'film'})
    if verified['sha256'] != measured['sha256'] or not verified['audio']['comparison']['passed']:
        raise AssertionError('Independent verifier did not bind canonical audio and stored bytes.')
    if (ROOT / 'jobs' / 'cold-verifier' / 'outputs').exists():
        raise AssertionError('Verification-only hydration unexpectedly rendered output.')
    CHECKS.append('cold-verification-without-rerender')
    request('/jobs/cold-verifier/verification/film', 'PUT', binary=artifact[:len(artifact) // 2])
    request('/jobs/cold-verifier/verify', 'POST', {'outputId': 'film'}, expected=422)
    CHECKS.append('corrupt-readback-rejected')
    request('/jobs', 'POST', {'jobId': 'cancel-staged', 'project': project}, expected=201)
    if request('/jobs/cancel-staged/cancel', 'POST')['state'] != 'cancelled':
        raise AssertionError('Owned staged job was not cancelled.')
    if request('/jobs/cancel-staged/run', 'POST', expected=202)['state'] != 'cancelled':
        raise AssertionError('Cancelled work was restarted.')
    CHECKS.append('cancelled-intent-does-not-restart')
    receipt = {'scope': 'local-linux-amd64-container-http-protocol', 'checks': CHECKS, 'passed': True,
               'cloudVerified': False, 'palPalKitCompleted': False, 'motionReviewed': False, 'heard': False, 'creativelyAccepted': False,
               'renderReceipt': status['receipt']}
    (ROOT / 'receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2))
    print(json.dumps({'ok': True, 'checks': CHECKS}), flush=True)
finally:
    server.terminate()
    server.wait(timeout=10)
