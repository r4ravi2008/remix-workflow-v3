"""Read-only Linux finishing and local model inventory in the managed workstation pane."""
import json
import os
from pathlib import Path
import platform
import shutil
import socket
import subprocess
import sys
import time
import urllib.request


def query(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=15)
        return {'code': result.returncode, 'stdout': result.stdout.strip()[:6000],
                'stderr': result.stderr.strip()[:500]}
    except (OSError, subprocess.TimeoutExpired) as error:
        return {'error': type(error).__name__}


def local_json(url):
    try:
        with urllib.request.urlopen(url, timeout=4) as response:
            return json.load(response)
    except Exception:
        return None


def main():
    if os.environ.get('HERDR_ENV') != '1' or socket.gethostname() != 'rkwindows11':
        raise RuntimeError('Run inventory only in the verified managed workstation pane')
    output = Path(sys.argv[1]).resolve()
    run = Path('/home/r4ravi2008/projects/remix-workflow-v3/runs/release-kit-service').resolve()
    if not output.is_relative_to(run):
        raise RuntimeError('Inventory receipt must stay under the owned service run')
    sdk = Path('/opt/resolve/Developer/Scripting/Modules/DaVinciResolveScript.py')
    binary = Path('/opt/resolve/bin/resolve')
    tools = {name: shutil.which(name) for name in ['python3', 'ffmpeg', 'ffprobe',
             'docker', 'podman', 'ollama', 'vulkaninfo', 'glxinfo', 'clinfo']}
    processes = query(['ps', '-eo', 'comm='])
    running = [name for name in processes.get('stdout', '').splitlines()
               if any(part in name.lower() for part in ['resolve', 'ollama', 'llama', 'vllm'])]
    ollama = local_json('http://127.0.0.1:11434/api/tags')
    model_cache = Path.home() / '.cache/huggingface/hub'
    cached = sorted(path.name for path in model_cache.glob('models--*')) if model_cache.is_dir() else []
    docker = query([tools['docker'], 'ps', '--format', '{{.Names}} {{.Image}}']) if tools['docker'] else None
    receipt = {
        'schemaVersion': 1, 'observedAt': time.time(), 'hostname': socket.gethostname(),
        'managed': True, 'platform': platform.platform(), 'kernel': platform.release(),
        'osRelease': Path('/etc/os-release').read_text(),
        'displayPresent': bool(os.environ.get('DISPLAY')),
        'waylandPresent': bool(os.environ.get('WAYLAND_DISPLAY')),
        'resolve': {'binaryPresent': binary.is_file(), 'sdkPresent': sdk.is_file(),
                    'runningProcessNames': running,
                    'binaryDependencies': query(['ldd', str(binary)]) if binary.is_file() else None,
                    'productAndLicenseVerified': False, 'renderCanaryVerified': False},
        'gpu': query(['/usr/lib/wsl/lib/nvidia-smi', '--query-gpu=name,memory.total,memory.used,driver_version', '--format=csv,noheader']),
        'tools': tools, 'containers': docker,
        'localModels': {'ollama': [model.get('name') for model in ollama.get('models', [])] if ollama else None,
                        'huggingFaceCaches': cached},
        'inferenceSubmitted': False, 'resolveLaunched': False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2) + '\n')
    output.chmod(0o600)
    print(json.dumps(receipt))


if __name__ == '__main__':
    main()
