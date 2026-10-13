"""Read back the real local service and exercise hold isolation without submitting inference."""
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

APP = Path(__file__).resolve().parent.parent

def check(config_path):
    config = json.loads(config_path.read_text())
    base = config['baseUrl']
    operator = next(line.split('=', 1)[1] for line in (APP/'.env').read_text().splitlines() if line.startswith('STUDIO_OPERATOR_TOKEN='))
    def request(path, worker=None, session=None, body=None):
        headers = {'Origin': base, 'Content-Type': 'application/json'}
        if worker: headers['Authorization'] = 'Bearer ' + worker
        if session: headers['Cookie'] = session
        data = json.dumps(body).encode() if body is not None else None
        try:
            with urllib.request.urlopen(urllib.request.Request(base+path, data=data, headers=headers), timeout=20) as response:
                return response.status, json.load(response)
        except urllib.error.HTTPError as error:
            return error.code, json.load(error)
    code, release = request('/api/releases/'+config['releaseId'], session=config['session'])
    assert code == 200 and release['state'] == 'waiting-for-direction'
    job = release['job']
    invalid = {'briefSha256': '0'*64, 'audioSha256': '0'*64, 'reviewEvidence': 'Invalid-binding HTTP diagnostic only'}
    assert request('/api/worker/jobs/'+job['id']+'/resume', worker=config['token'], body=invalid)[0] == 409
    private = APP/'.local/service-isolation-device.json'
    if private.exists():
        previous = json.loads(private.read_text())
        assert request('/api/operator/devices/'+previous['id']+'/revoke', worker=operator, body={})[0] == 200
        assert request('/api/worker/holds', worker=previous['token'])[0] == 401
        private.unlink()
    code, other = request('/api/operator/devices', worker=operator, body={'name': 'Worker hold isolation diagnostic'})
    assert code == 201
    private.write_text(json.dumps(other)); private.chmod(0o600)
    assert request('/api/worker/holds', worker=other['token'])[1]['jobs'] == []
    assert request('/api/worker/jobs/'+job['id'], worker=other['token'])[0] == 404
    assert request('/api/worker/jobs/'+job['id']+'/resume', worker=other['token'], body=invalid)[0] == 409
    assert request('/api/operator/devices/'+other['id']+'/revoke', worker=operator, body={})[0] == 200
    assert request('/api/worker/holds', worker=other['token'])[0] == 401
    private.unlink()
    code, after = request('/api/releases/'+config['releaseId'], session=config['session'])
    assert code == 200 and after['job']['attempt'] == job['attempt'] and after['state'] == release['state']
    launch = subprocess.run(['launchctl', 'print', 'gui/'+str(os.getuid())+'/com.dabbitech.release-kit-studio.worker'], check=True, capture_output=True, text=True).stdout
    pid = re.search(r'^\s*pid = (\d+)', launch, re.MULTILINE)
    assert pid and re.search(r'^\s*state = running', launch, re.MULTILINE)
    status = json.loads((Path(config['localState'])/'service-status.json').read_text())
    assert status['pid'] == int(pid.group(1)) and any(held['id'] == job['id'] for held in status['held'])
    before = json.loads((APP/'.local/service-observation-before.json').read_text())
    assert status['observedAt'] > before['service']['observedAt']
    assert before['release']['job']['attempt'] == after['job']['attempt']
    receipt = {'runtime': 'Alchemy native local D1/R2 with a live launchd worker', 'testedAt': time.time(),
        'pid': int(pid.group(1)), 'serviceState': status['state'], 'pollObservedAt': status['observedAt'],
        'earlierPollObservedAt': before['service']['observedAt'], 'releaseId': config['releaseId'],
        'jobId': job['id'], 'attempt': job['attempt'], 'releaseState': after['state'],
        'durableHoldWithoutReclaim': True, 'changedBriefResumeRejected': True, 'otherWorkerHoldHidden': True,
        'otherWorkerStatusHidden': True, 'otherWorkerResumeRejected': True, 'diagnosticDeviceRevoked': True,
        'diagnosticCredentialRemoved': True, 'readyOutputs': len(after['assets']),
        'newInferenceSubmitted': False, 'resolveMutated': False, 'hostedProductionVerified': False, 'fullKitComplete': False}
    (APP/'docs/service-runtime-receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt))

if __name__ == '__main__':
    if len(sys.argv) != 2: raise SystemExit('Pass the private local worker configuration path.')
    check(Path(sys.argv[1]))
