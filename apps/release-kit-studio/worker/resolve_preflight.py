#!/usr/bin/env python3
import argparse
import hashlib
import importlib
import json
import platform
import socket
import subprocess
import sys
from pathlib import Path


def digest(path):
    with path.open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description='Read-only Resolve worker and staged-input verification.')
    parser.add_argument('--expected-hostname', required=True)
    parser.add_argument('--provider', required=True)
    parser.add_argument('--worker-id', required=True)
    parser.add_argument('--sdk-dir', type=Path, required=True)
    parser.add_argument('--input-root', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--receipt', type=Path, required=True)
    parser.add_argument('--nvidia-smi', default='nvidia-smi', help='GPU query executable; WSL commonly uses /usr/lib/wsl/lib/nvidia-smi.')
    args = parser.parse_args()
    if socket.gethostname() != args.expected_hostname:
        raise RuntimeError('Hostname does not match the verified worker. No Resolve connection attempted.')
    if args.receipt.exists():
        raise RuntimeError('Receipt already exists; choose a new preflight attempt path.')
    root = args.input_root.resolve(strict=True)
    manifest = json.loads(args.manifest.read_text())
    verified = []
    for asset in manifest['assets']:
        path = (root / asset['path']).resolve(strict=True)
        if not path.is_relative_to(root):
            raise RuntimeError('Staged input escapes the input root.')
        actual = digest(path)
        if actual != asset['sha256']:
            raise RuntimeError(f"Input hash mismatch: {asset['id']}")
        if path.stat().st_size != asset['bytes']:
            raise RuntimeError(f"Input size mismatch: {asset['id']}")
        verified.append({'id': asset['id'], 'sha256': actual, 'bytes': path.stat().st_size})
    sdk = args.sdk_dir.resolve(strict=True)
    if not (sdk / 'DaVinciResolveScript.py').is_file():
        raise RuntimeError('The official Resolve scripting module was not found.')
    gpu = subprocess.run([args.nvidia_smi, '--query-gpu=name,memory.total,driver_version', '--format=csv,noheader'], check=True, capture_output=True, text=True, timeout=15)
    sys.path.insert(0, str(sdk))
    bmd = importlib.import_module('DaVinciResolveScript')
    resolve = bmd.scriptapp('Resolve')
    if not resolve:
        raise RuntimeError('Resolve scripting is unavailable. Start the activated worker instance and verify local scripting.')
    product = resolve.GetProductName()
    if 'Studio' not in product:
        raise RuntimeError('Resolve Studio was not read back. Activation/capabilities remain unverified.')
    manager = resolve.GetProjectManager()
    if not manager:
        raise RuntimeError('Resolve project manager is not ready.')
    project = manager.GetCurrentProject()
    receipt = {'schemaVersion': 1, 'provider': args.provider, 'workerId': args.worker_id, 'hostname': socket.gethostname(), 'os': platform.platform(), 'gpu': gpu.stdout.strip(), 'resolveProduct': product, 'resolveVersion': resolve.GetVersionString(), 'currentProject': project.GetName() if project else None, 'inputs': verified, 'evidence': {'inputHashes': 'verified', 'resolveConnection': 'verified', 'renderCanary': 'pending', 'watched': False, 'heard': False}}
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    with args.receipt.open('x') as output:
        json.dump(receipt, output, indent=2)
        output.write('\n')
    print(json.dumps({'preflight': 'passed', 'inputCount': len(verified), 'renderCanary': 'pending', 'receipt': str(args.receipt)}))


if __name__ == '__main__':
    main()
