import argparse
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from engine import IDS, capabilities, hash_file, render, validate_recipe, verify_output
from preview import make_preview


ROOT = Path(os.environ.get('EDITOR_SCRATCH', '/tmp/release-kit-editor'))
ROOT.mkdir(parents=True, exist_ok=True)
LOCK = threading.RLock()
JOBS = {}


def atomic_json(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False), encoding='utf8')
    temporary.replace(path)


def state(job):
    return {key: value for key, value in job.items() if key not in {'process', 'cancel', 'root', 'project'}}


def update(job, **values):
    with LOCK:
        job.update(values)
        atomic_json(job['root'] / 'state.json', state(job))


def execute_job(job):
    started = time.monotonic()

    def run(args):
        if job['cancel'].is_set():
            raise ValueError('Render cancelled.')
        if time.monotonic() - started > 1800:
            raise ValueError('Render exceeded its 30-minute job deadline.')
        with (job['root'] / 'ffmpeg.log').open('ab') as log:
            process = subprocess.Popen(args, stdin=subprocess.DEVNULL, stdout=log, stderr=log, start_new_session=True)
            with LOCK:
                job['process'] = process
                if job['cancel'].is_set():
                    os.killpg(process.pid, signal.SIGTERM)
            try:
                code = process.wait(timeout=max(1, 1800 - (time.monotonic() - started)))
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
                raise ValueError('Native render deadline exceeded.')
            finally:
                with LOCK:
                    job['process'] = None
            if code:
                raise ValueError('Native render failed: ' + (job['root'] / 'ffmpeg.log').read_text(errors='replace')[-1500:])

    try:
        update(job, state='running')
        receipt = render(job['project'], job['root'], run, lambda progress: update(job, progress=progress))
        if job['cancel'].is_set():
            update(job, state='cancelled')
        else:
            atomic_json(job['root'] / 'receipt.json', receipt)
            update(job, state='ready', receipt=receipt, progress={'phase': 'verified', 'completedOutputs': len(receipt['outputs']), 'totalOutputs': len(receipt['outputs'])})
    except Exception as error:
        update(job, state='cancelled' if job['cancel'].is_set() else 'failed', error=str(error))


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        return

    def json(self, value, status=200):
        data = json.dumps(value, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def payload(self):
        length = int(self.headers.get('Content-Length', 0))
        if not 0 < length <= 4 * 1024 * 1024:
            raise ValueError('Invalid JSON body size.')
        return json.loads(self.rfile.read(length))

    def job(self):
        match = re.fullmatch(r'/jobs/([a-zA-Z0-9_-]{1,80})(?:/(.*))?', self.path)
        if not match or match[1] not in JOBS:
            raise KeyError('Unknown job; reconcile the editor ledger before replaying.')
        return JOBS[match[1]], match[2] or ''

    def dispatch(self):
        if self.path == '/health' and self.command == 'GET':
            return self.json(capabilities())
        if self.path == '/jobs' and self.command == 'POST':
            payload = self.payload()
            identity = payload['jobId']
            if not re.fullmatch(r'[a-zA-Z0-9_-]{1,80}', identity):
                raise ValueError('Invalid job ID.')
            project = payload['project']
            validate_recipe(project)
            fingerprint = hashlib.sha256(json.dumps(project, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
            with LOCK:
                if identity in JOBS:
                    if JOBS[identity]['fingerprint'] != fingerprint:
                        return self.json({'error': 'Intent content conflict.'}, 409)
                    return self.json(state(JOBS[identity]))
                if any(job['state'] in {'staging', 'running'} for job in JOBS.values()):
                    return self.json({'error': 'One active native job per container.'}, 409)
                root = ROOT / identity
                if root.exists():
                    return self.json({'error': 'Existing scratch outcome requires reconciliation.'}, 409)
                (root / 'assets').mkdir(parents=True)
                verification = payload.get('verificationOnly', False) is True
                job = {'jobId': identity, 'fingerprint': fingerprint, 'state': 'ready' if verification else 'staging', 'verificationOnly': verification, 'progress': {'phase': 'verification' if verification else 'staging', 'completedOutputs': 0}, 'receipt': None, 'error': None,
                       'project': project, 'root': root, 'cancel': threading.Event(), 'process': None}
                JOBS[identity] = job
                atomic_json(root / 'project.json', project)
                update(job)
            return self.json(state(job), 201)
        job, suffix = self.job()
        if suffix.startswith('assets/') and self.command == 'PUT':
            identity = suffix.removeprefix('assets/')
            asset = next((asset for asset in job['project']['assets'] if asset['id'] == identity), None)
            if not asset or (job['state'] != 'staging' and not job['verificationOnly']):
                raise ValueError('Asset is not part of the staged immutable recipe.')
            length = int(self.headers.get('Content-Length', 0))
            if length != asset['bytes'] or not 0 < length <= 100 * 1024 * 1024:
                raise ValueError('Asset byte count differs from recipe.')
            destination = job['root'] / 'assets' / identity
            temporary = destination.with_suffix('.upload')
            digest = hashlib.sha256()
            remaining = length
            with temporary.open('wb') as stream:
                while remaining:
                    block = self.rfile.read(min(remaining, 1024 * 1024))
                    if not block:
                        raise ValueError('Truncated asset upload.')
                    digest.update(block)
                    stream.write(block)
                    remaining -= len(block)
            if digest.hexdigest() != asset['sha256']:
                temporary.unlink()
                raise ValueError('Source checksum does not match the recipe.')
            temporary.replace(destination)
            return self.json({'id': identity, 'verified': True})
        if suffix == 'run' and self.command == 'POST':
            with LOCK:
                if job['state'] == 'staging' and not job['verificationOnly']:
                    update(job, state='running')
                    threading.Thread(target=execute_job, args=(job,), daemon=True).start()
            return self.json(state(job), 202)
        if suffix == 'cancel' and self.command == 'POST':
            with LOCK:
                job['cancel'].set()
                process = job['process']
                if process and process.poll() is None:
                    os.killpg(process.pid, signal.SIGTERM)
                if job['state'] == 'staging':
                    update(job, state='cancelled')
            return self.json(state(job))
        if suffix == 'verify' and self.command == 'POST':
            payload = self.payload()
            identity = payload['outputId']
            if identity not in IDS:
                raise ValueError('Invalid output.')
            comp = next(comp for comp in job['project']['compositions'] if comp['id'] == identity)
            candidate = job['root'] / 'verification' / identity
            return self.json(verify_output(candidate, job['project'], comp, job['root']))
        if suffix == 'preview' and self.command == 'POST':
            payload = self.payload()
            identity = payload['outputId']
            if identity not in IDS or job['state'] != 'ready':
                raise ValueError('Review preview requires completed output.')
            comp = next(comp for comp in job['project']['compositions'] if comp['id'] == identity)
            return self.json(make_preview(job['root'] / 'verification' / identity, comp, payload, job['root']))
        preview_file = re.fullmatch(r'previews/([a-f0-9]{64})/(preview\.(?:mp4|jpg)|frame-[0-9]{6}\.jpg)', suffix)
        if preview_file and self.command == 'GET' and job['state'] == 'ready':
            directory = job['root'] / 'previews' / preview_file[1]
            receipt = json.loads((directory / 'receipt.json').read_text())
            if preview_file[2] not in {item['name'] for item in receipt['files']}:
                raise ValueError('Preview file is not in its completed receipt.')
            path = directory / preview_file[2]
            self.send_response(200)
            self.send_header('Content-Length', str(path.stat().st_size))
            self.send_header('Content-Type', 'application/octet-stream')
            self.end_headers()
            with path.open('rb') as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b''):
                    self.wfile.write(block)
            return
        if suffix.startswith('verification/') and self.command == 'PUT':
            identity = suffix.removeprefix('verification/')
            if identity not in IDS or job['state'] != 'ready':
                raise ValueError('Verification needs a completed output.')
            length = int(self.headers.get('Content-Length', 0))
            if not 0 < length <= 2147483648:
                raise ValueError('Verification input size is out of bounds.')
            directory = job['root'] / 'verification'
            directory.mkdir(exist_ok=True)
            with (directory / identity).open('wb') as stream:
                remaining = length
                while remaining:
                    block = self.rfile.read(min(remaining, 1024 * 1024))
                    if not block:
                        raise ValueError('Truncated verification upload.')
                    stream.write(block)
                    remaining -= len(block)
            return self.json({'storedForVerification': True})
        if suffix.startswith('outputs/') and self.command == 'GET':
            identity = suffix.removeprefix('outputs/')
            if identity not in IDS or job['state'] != 'ready':
                raise ValueError('Output is not ready.')
            path = job['root'] / 'outputs' / (identity + ('.jpg' if identity in {'thumbnail', 'artwork'} else '.mp4'))
            self.send_response(200)
            self.send_header('Content-Length', str(path.stat().st_size))
            self.send_header('Content-Type', 'application/octet-stream')
            self.end_headers()
            with path.open('rb') as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b''):
                    self.wfile.write(block)
            return
        if not suffix and self.command == 'GET':
            return self.json(state(job))
        return self.json({'error': 'Unknown native tool route.'}, 404)

    def handle_request(self):
        try:
            self.dispatch()
        except KeyError as error:
            self.json({'error': str(error)}, 404)
        except Exception as error:
            self.json({'error': str(error)}, 422)

    do_GET = handle_request
    do_POST = handle_request
    do_PUT = handle_request


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', type=int, default=8080)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)

    def terminate(_signal, _frame):
        with LOCK:
            for job in JOBS.values():
                job['cancel'].set()
                process = job.get('process')
                if process and process.poll() is None:
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.wait(timeout=5)
                    except ProcessLookupError:
                        pass
        server.server_close()
        sys.exit(0)

    signal.signal(signal.SIGTERM, terminate)
    signal.signal(signal.SIGINT, terminate)
    print(json.dumps({'host': args.host, 'port': server.server_port}), flush=True)
    server.serve_forever()
