"""Download each completed owned batch clip promptly; never submit GPU jobs."""
import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path
from proxy_transfer import run_command

parser = argparse.ArgumentParser()
parser.add_argument('--port', type=int)
parser.add_argument('--proxy-user')
parser.add_argument('--host', default='195.26.233.56')
parser.add_argument('--stage', required=True, type=Path)
parser.add_argument('--deadline', required=True, type=float)
args = parser.parse_args()
assert bool(args.port) != bool(args.proxy_user), 'Choose direct SSH or the PTY proxy'
plan = json.loads((args.stage / 'plan.json').read_text())
pending = {j['jobId'] for j in plan['jobs']}
assert all(k.isalnum() for k in pending)
identity = '/Users/aira/.ssh/runpod_gymson_ed25519'
assert all(c.isdigit() or c == '.' for c in args.host), 'Use verified direct IPv4 from RunPod'
host = 'root@' + args.host
ssh = ['ssh','-i',identity,'-p',str(args.port),'-o','BatchMode=yes','-o','ConnectTimeout=10',host]
scp = ['scp','-i',identity,'-P',str(args.port),'-o','BatchMode=yes','-o','ConnectTimeout=10']
while pending and time.time() < args.deadline:
    for key in sorted(pending):
        local_report = args.stage / (key + '.result.json')
        if local_report.exists():
            prior = json.loads(local_report.read_text())
            assert prior['localSHA256Verified'] and hashlib.sha256(Path(prior['localOriginal']).read_bytes()).hexdigest() == prior['media']['sha256']
            pending.remove(key)
            continue
        remote_report = '/workspace/urvashi-h3/batch-v5/' + key + '.result.json'
        command = 'test -f ' + remote_report + ' && cat ' + remote_report
        if args.proxy_user:
            output, returncode = run_command(args.proxy_user, identity, command)
        else:
            response = subprocess.run(ssh + [command], capture_output=True, text=True, timeout=30)
            output, returncode = response.stdout, response.returncode
        if returncode:
            continue
        report = json.loads(output)
        assert report['jobId'] == key and report['status'] == 'GENERATED_UNREVIEWED'
        media = report['media']
        remote = media['path']
        assert remote.startswith('/workspace/ComfyUI-H3/output/urvashi-h3/' + key + '-v5') and remote.endswith('.mp4')
        target = args.stage / Path(remote).name
        if args.proxy_user:
            transfer = ['python3', str(Path(__file__).with_name('proxy_transfer.py')), '--user', args.proxy_user,
                        '--identity', identity, '--download-dir', str(args.stage), '--get', remote + '=' + target.name]
            for suffix in ('receipt', 'workflow', 'history'):
                name = key + '.' + suffix + '.json'
                transfer += ['--get', '/workspace/urvashi-h3/batch-v5/' + name + '=' + name]
            subprocess.run(transfer, check=True, timeout=240)
        elif not target.exists():
            subprocess.run(scp + [host + ':' + remote, str(target)], check=True, timeout=120)
        assert hashlib.sha256(target.read_bytes()).hexdigest() == media['sha256']
        assert target.stat().st_size == media['bytes']
        if not args.proxy_user:
            for suffix in ('receipt','workflow','history'):
                subprocess.run(scp + [host + ':/workspace/urvashi-h3/batch-v5/' + key + '.' + suffix + '.json', str(args.stage)], check=True, timeout=60)
        report['localOriginal'] = str(target)
        report['localSHA256Verified'] = True
        (args.stage / (key + '.result.json')).write_text(json.dumps(report, indent=2))
        pending.remove(key)
        print(json.dumps({'event':'DOWNLOADED_HASH_VERIFIED','jobId':key,'path':str(target),'sha256':media['sha256']}), flush=True)
    if pending:
        time.sleep(10)
if pending:
    raise SystemExit('Download observer deadline; pending=' + ','.join(sorted(pending)))
print('ALL_BATCH_ORIGINALS_DOWNLOADED', flush=True)
