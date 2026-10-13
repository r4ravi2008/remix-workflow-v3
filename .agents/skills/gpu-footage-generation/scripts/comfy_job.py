#!/usr/bin/env python3
"""One recoverable ComfyUI job. No GPU rental, model setup, cross-host copy or approval."""
import argparse
import json
import math
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import urlsplit
import uuid

from asset_snapshot import contained, file_hash, fingerprint, verify


class Client:
    def __init__(self, url):
        parts = urlsplit(url)
        if parts.scheme not in ('http', 'https') or not parts.hostname or parts.username or parts.password or parts.query or parts.fragment:
            raise ValueError('Use an HTTP(S) endpoint without embedded credentials, query or fragment')
        self.url = url.rstrip('/')

    def request(self, route, payload=None):
        data = None if payload is None else json.dumps(payload).encode()
        request = urllib.request.Request(self.url + route, data=data,
                                         headers={'Content-Type': 'application/json'})
        # POSTs intentionally have no automatic retries.
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)


def write_json(path, value):
    temporary = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    try:
        with temporary.open('x') as stream:
            json.dump(value, stream, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def read_json(path):
    return json.loads(path.read_text())


def job_directory(ledger, job):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,95}', job):
        raise ValueError('Use a stable alphanumeric attempt ID with optional hyphens/underscores')
    directory = ledger / job
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def validate_bindings(workflow, snapshot, bindings):
    if not isinstance(bindings, list) or not bindings:
        raise ValueError('Declare the graph input bindings for this anchor-based job')
    files = {entry['path'] for entry in snapshot['files']}
    bound = set()
    for binding in bindings:
        node_id, field, path = binding['node'], binding['input'], binding['path']
        if path not in files or workflow[node_id]['inputs'].get(field) != path:
            raise ValueError('Workflow input does not match the verified snapshot binding')
        if (node_id, field) in bound:
            raise ValueError('Duplicate workflow input binding')
        bound.add((node_id, field))
    for node_id, node in workflow.items():
        if node.get('class_type') in ('LoadImage', 'LoadImageMask') and (node_id, 'image') not in bound:
            raise ValueError('Unbound LoadImage input; include every conditioning image')


def submit(client, directory, workflow, snapshot, bindings, input_root, deadline, reserve_seconds):
    if (directory / 'intent.json').exists() or (directory / 'receipt.json').exists():
        raise ValueError('Attempt already has an intent/receipt; use status or reconcile, never blindly resubmit')
    if not math.isfinite(deadline) or not math.isfinite(reserve_seconds) or reserve_seconds <= 0 or time.time() + reserve_seconds >= deadline:
        raise ValueError('Insufficient deadline reserve; do not submit another job')
    verify(input_root, snapshot)
    if not isinstance(workflow, dict) or not workflow:
        raise ValueError('Expected a nonempty ComfyUI API graph')
    validate_bindings(workflow, snapshot, bindings)
    objects = client.request('/object_info')
    for node in workflow.values():
        if not isinstance(node, dict) or node.get('class_type') not in objects or not isinstance(node.get('inputs'), dict):
            raise ValueError('Graph has an unavailable node class or invalid inputs')
    queue = client.request('/queue')
    if queue.get('queue_running') or queue.get('queue_pending'):
        raise ValueError('Queue is occupied; inspect ownership or wait for the existing job')
    intent = {'schema_version': 1, 'job_id': directory.name, 'token': uuid.uuid4().hex,
              'submitted_epoch': time.time(), 'endpoint': client.url,
              'workflow_sha256': fingerprint(workflow), 'snapshot_sha256': snapshot['snapshot_sha256'],
              'bindings_sha256': fingerprint(bindings)}
    # Exclusive creation arbitrates concurrent callers before any POST can spend GPU time.
    with (directory / 'intent.json').open('x') as stream:
        json.dump(intent, stream, indent=2)
        stream.flush()
        os.fsync(stream.fileno())
    write_json(directory / 'workflow.json', workflow)
    write_json(directory / 'inputs.json', snapshot)
    write_json(directory / 'bindings.json', bindings)
    try:
        response = client.request('/prompt', {'prompt': workflow, 'client_id': intent['token'],
                                             'extra_data': {'footage_job_token': intent['token']}})
    except urllib.error.HTTPError as error:
        with error:
            body = error.read(1024 * 1024).decode('utf-8', errors='replace')
        try:
            detail = json.loads(body)
        except ValueError:
            detail = {'body': body}
        write_json(directory / 'submission-response.json', {'http_status': error.code, 'detail': detail})
        raise ValueError('Submission HTTP error; inspect saved response and reconcile before a new attempt') from error
    if not response.get('prompt_id') or response.get('error') or response.get('node_errors'):
        write_json(directory / 'submission-response.json', response)
        raise ValueError('Submission rejected or ambiguous; inspect saved response and server state')
    receipt = {**intent, 'prompt_id': response['prompt_id']}
    write_json(directory / 'receipt.json', receipt)
    return {'state': 'submitted', 'prompt_id': receipt['prompt_id']}


def bound_intent(client, directory):
    intent = read_json(directory / 'intent.json')
    if intent['endpoint'] != client.url:
        raise ValueError('Endpoint differs from saved intent; verify the server and migrate records explicitly')
    if fingerprint(read_json(directory / 'workflow.json')) != intent['workflow_sha256']:
        raise ValueError('Saved workflow changed after submission')
    snapshot = read_json(directory / 'inputs.json')
    body = {k: snapshot[k] for k in ('schema_version', 'files')}
    if fingerprint(body) != intent['snapshot_sha256']:
        raise ValueError('Saved source snapshot changed after submission')
    if fingerprint(read_json(directory / 'bindings.json')) != intent['bindings_sha256']:
        raise ValueError('Saved workflow input bindings changed after submission')
    return intent


def token_match(entry, intent):
    if not isinstance(entry, list) or len(entry) < 4 or not isinstance(entry[3], dict):
        return False
    extra = entry[3]
    match = extra.get('footage_job_token') == intent['token'] or extra.get('client_id') == intent['token']
    if match and fingerprint(entry[2]) != intent['workflow_sha256']:
        raise ValueError('Token matched a different graph; manual reconciliation required')
    return match


def reconcile(client, directory):
    intent = bound_intent(client, directory)
    if (directory / 'receipt.json').exists():
        return status(client, directory)
    queue = client.request('/queue')
    history = client.request('/history')
    matches = {entry[1] for key in ('queue_running', 'queue_pending')
               for entry in queue.get(key, []) if token_match(entry, intent)}
    matches.update(prompt_id for prompt_id, record in history.items()
                   if token_match(record.get('prompt'), intent))
    if len(matches) != 1:
        raise ValueError(f'Uncertain submission: {len(matches)} matching prompt IDs; preserve intent and investigate')
    receipt = {**intent, 'prompt_id': matches.pop(), 'recovered_epoch': time.time()}
    write_json(directory / 'receipt.json', receipt)
    return status(client, directory)


def receipt_for(client, directory):
    intent = bound_intent(client, directory)
    receipt = read_json(directory / 'receipt.json')
    if any(receipt.get(key) != value for key, value in intent.items()):
        raise ValueError('Receipt does not match intent')
    return receipt


def status(client, directory):
    receipt = receipt_for(client, directory)
    prompt_id = receipt['prompt_id']
    history = client.request('/history/' + prompt_id).get(prompt_id)
    if history:
        write_json(directory / 'history.json', history)
        state = history.get('status', {})
        if state.get('status_str') == 'success' and state.get('completed') is True:
            return {'state': 'generated-unreviewed', 'prompt_id': prompt_id}
        return {'state': 'failed' if state.get('status_str') == 'error' else 'pending', 'prompt_id': prompt_id}
    queue = client.request('/queue')
    for key, name in [('queue_running', 'running'), ('queue_pending', 'queued')]:
        if any(entry[1] == prompt_id for entry in queue.get(key, [])):
            return {'state': name, 'prompt_id': prompt_id}
    return {'state': 'unknown-do-not-resubmit', 'prompt_id': prompt_id}


def videos(value):
    if isinstance(value, dict):
        if isinstance(value.get('filename'), str) and Path(value['filename']).suffix.lower() in ('.mp4', '.mov', '.webm', '.mkv'):
            yield value
        for child in value.values():
            yield from videos(child)
    elif isinstance(value, list):
        for child in value:
            yield from videos(child)


def probe_video(path):
    probe = subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0',
                            '-show_entries', 'stream=width,height,r_frame_rate,nb_read_frames:format=duration',
                            '-of', 'json', str(path)], check=True, capture_output=True, text=True, timeout=300)
    data = json.loads(probe.stdout)
    stream = data['streams'][0]
    if int(stream['nb_read_frames']) <= 0 or int(stream['width']) <= 0 or int(stream['height']) <= 0:
        raise ValueError('Output has no usable decoded video')
    subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-i', str(path), '-map', '0:v:0', '-f', 'null', '-'],
                   check=True, capture_output=True, timeout=300)
    return data


def collect(client, directory, output_root, archive, output_node=None):
    if status(client, directory)['state'] != 'generated-unreviewed':
        raise ValueError('Wait for successful save completion before collecting')
    history = read_json(directory / 'history.json')
    outputs = history.get('outputs', {})
    candidates = list(videos(outputs.get(output_node, {}) if output_node else outputs))
    unique = {(c.get('subfolder', ''), c['filename'], c.get('type')) for c in candidates}
    if len(unique) != 1:
        raise ValueError('Expected one video output; select an --output-node with exactly one original')
    subfolder, name, output_type = unique.pop()
    if output_type != 'output' or Path(name).name != name:
        raise ValueError('Expected a history-named output file')
    source = contained(output_root, str(Path(subfolder) / name))
    stat_before = source.stat()
    media = probe_video(source)
    digest = file_hash(source)
    stat_after = source.stat()
    if (stat_before.st_size, stat_before.st_mtime_ns) != (stat_after.st_size, stat_after.st_mtime_ns):
        raise ValueError('Output is still changing; wait for the writer')
    archive.mkdir(parents=True, exist_ok=True)
    target = archive / (directory.name + source.suffix.lower())
    if target.exists():
        if file_hash(target) != digest:
            raise ValueError('Archive target differs; preserve both and investigate')
    else:
        partial = archive / (target.name + '.' + uuid.uuid4().hex + '.partial')
        try:
            shutil.copyfile(source, partial)
            if file_hash(partial) != digest:
                raise ValueError('Copied bytes do not match completed original')
            # Link is atomic and refuses to overwrite a concurrently archived result.
            os.link(partial, target)
        finally:
            partial.unlink(missing_ok=True)
    receipt = receipt_for(client, directory)
    result = {'state': 'generated-unreviewed', 'host': socket.gethostname(),
              'collected_epoch': time.time(), 'receipt': receipt, 'source': str(source),
              'archive': str(target.resolve()), 'bytes': stat_after.st_size, 'sha256': digest,
              'media': media, 'full_video_decode': True, 'watched_normal_speed': False}
    write_json(directory / 'result.json', result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', required=True, help='Verified server URL; prefer an SSH-forwarded loopback endpoint')
    parser.add_argument('--ledger', required=True, type=Path)
    parser.add_argument('--job', required=True, help='Unique immutable attempt ID')
    sub = parser.add_subparsers(dest='command', required=True)
    submit_parser = sub.add_parser('submit')
    submit_parser.add_argument('--workflow', required=True, type=Path)
    submit_parser.add_argument('--inputs', required=True, type=Path)
    submit_parser.add_argument('--input-root', required=True, type=Path)
    submit_parser.add_argument('--bindings', required=True, type=Path, help='JSON list of node/input/path bindings to the verified snapshot')
    submit_parser.add_argument('--deadline', required=True, type=float, help='Unix seconds; admission guard, NOT pod shutdown')
    submit_parser.add_argument('--reserve-seconds', required=True, type=float, help='Measured worst-case job plus save/transfer reserve')
    sub.add_parser('status')
    sub.add_parser('reconcile')
    collect_parser = sub.add_parser('collect')
    collect_parser.add_argument('--output-root', required=True, type=Path)
    collect_parser.add_argument('--archive', required=True, type=Path)
    collect_parser.add_argument('--output-node')
    args = parser.parse_args()
    try:
        client = Client(args.url)
        directory = job_directory(args.ledger, args.job)
        if args.command == 'submit':
            result = submit(client, directory, read_json(args.workflow), read_json(args.inputs), read_json(args.bindings),
                            args.input_root, args.deadline, args.reserve_seconds)
        elif args.command == 'status':
            result = status(client, directory)
        elif args.command == 'reconcile':
            result = reconcile(client, directory)
        else:
            result = collect(client, directory, args.output_root, args.archive, args.output_node)
        print(json.dumps(result, indent=2))
        return 1 if result['state'] in ('failed', 'unknown-do-not-resubmit') else 0
    except (OSError, ValueError, KeyError, TypeError, IndexError, subprocess.SubprocessError) as error:
        print(json.dumps({'error': str(error), 'action': 'Inspect saved intent/receipt and server state before retrying.'}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
