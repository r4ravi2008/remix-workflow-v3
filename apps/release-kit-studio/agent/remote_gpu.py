"""Fixed GPU operations inside a genuine Herdr pane; source data never becomes shell code."""
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
import time

SERVICE = Path(__file__).resolve().parent
PROJECT = SERVICE.parent.parent
sys.path.insert(0, str(SERVICE / 'helpers'))
from comfy_job import Client, collect, read_json, reconcile, status, submit, write_json
from asset_snapshot import fingerprint

COMFY = PROJECT / 'tools/ltx-video-generator/comfyui'
LEASE = PROJECT / 'runs/.gpu-inference-lease.json'
CLIENT = Client('http://127.0.0.1:8188')

def safe_path(raw, root=PROJECT):
    path = Path(raw).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('GPU paths must be contained in the configured production project')
    return path

def release_if_terminal(attempt, result):
    if result['state'] not in ('generated-unreviewed', 'failed') or not LEASE.exists():
        return
    lease = read_json(LEASE)
    if lease.get('service') == 'release-kit-studio' and lease.get('job_id') == attempt['id'] and lease.get('ledger') == attempt['ledger']:
        write_json(safe_path(attempt['ledger']) / attempt['id'] / 'lease-released.json', {**lease, 'terminal': result, 'released_epoch': time.time()})
        LEASE.unlink()

def run(request):
    if os.environ.get('HERDR_ENV') != '1' or socket.gethostname() != 'rkwindows11':
        raise RuntimeError('Expected the verified Herdr-managed WSL workstation')
    action = request['action']
    if action == 'observe':
        from remote_observation import run as observe
        return observe(request['observation'])
    if action == 'probe':
        queue = CLIENT.request('/queue')
        gpu = subprocess.run(['/usr/lib/wsl/lib/nvidia-smi', '--query-gpu=name,memory.total,driver_version', '--format=csv,noheader'], check=True, capture_output=True, text=True).stdout.strip()
        return {'managed': True, 'hostname': socket.gethostname(), 'gpu': gpu, 'queueIdle': not queue.get('queue_running') and not queue.get('queue_pending'), 'lease': read_json(LEASE) if LEASE.exists() else None, 'modelsReady': (COMFY/'models/checkpoints').is_dir() and bool(CLIENT.request('/object_info'))}
    attempt = request['attempt']
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,95}', attempt['id']):
        raise ValueError('Invalid immutable GPU attempt ID')
    directory = safe_path(attempt['ledger']) / attempt['id']
    directory.mkdir(parents=True, exist_ok=True)
    if action == 'ensure':
        if (directory/'intent.json').exists():
            intent=read_json(directory/'intent.json')
            if fingerprint(read_json(safe_path(attempt['workflow']))) != intent['workflow_sha256']:
                raise ValueError('Planned graph differs from the saved attempt; preserve it and create a reviewed new attempt')
            result=status(CLIENT,directory) if (directory/'receipt.json').exists() else reconcile(CLIENT,directory)
            release_if_terminal(attempt,result)
            return result
        action='submit'
    if action == 'submit':
        if (directory / 'intent.json').exists():
            raise ValueError('Attempt already has an intent; status or reconcile it before considering any new attempt')
        owner = {'service': 'release-kit-studio', 'job_id': attempt['id'], 'ledger': attempt['ledger'], 'reserved_epoch': time.time()}
        with LEASE.open('x') as stream:
            json.dump(owner, stream)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            result = submit(CLIENT, directory, read_json(safe_path(attempt['workflow'])), read_json(safe_path(attempt['inputs'])), read_json(safe_path(attempt['bindings'])), safe_path(attempt['inputRoot']), time.time()+7200, 1800)
            write_json(directory/'gpu-reservation.json', {**owner, 'result': result})
            return result
        except BaseException:
            if not (directory/'intent.json').exists() and LEASE.exists() and read_json(LEASE) == owner:
                LEASE.unlink()
            raise
    if action in ('status', 'reconcile'):
        result = status(CLIENT, directory) if action == 'status' else reconcile(CLIENT, directory)
        release_if_terminal(attempt, result)
        return result
    if action == 'collect':
        result = collect(CLIENT, directory, safe_path(attempt['outputRoot']), safe_path(attempt['archive']), attempt['outputNode'])
        release_if_terminal(attempt, result)
        return result
    raise ValueError('Unsupported GPU operation')

if __name__ == '__main__':
    request = read_json(Path(sys.argv[1]))
    response = safe_path(request['response'], SERVICE/'requests')
    try:
        result = run(request)
        write_json(response, {'ok': True, 'result': result, 'error': None})
    except Exception as error:
        write_json(response, {'ok': False, 'result': None, 'error': str(error)})
        raise
