"""Install the owned Mac outbound worker without changing Resolve or the GPU provider."""
import json
import os
from pathlib import Path
import plistlib
import re
import shutil
import subprocess
import sys

APP = Path(__file__).resolve().parent.parent
LABEL = 'com.dabbitech.release-kit-studio.worker'

def install(config_path):
    config_path = config_path.resolve(strict=True)
    config = json.loads(config_path.read_text())
    required = ('baseUrl', 'token', 'workstationConfig', 'localState', 'planRegistry')
    if not all(config.get(key) for key in required):
        raise RuntimeError('Complete the private worker configuration before installation; credentials are withheld.')
    if config_path.stat().st_mode & 0o077:
        raise RuntimeError('The private worker configuration must have mode 600.')
    bun = shutil.which('bun')
    if not bun:
        raise RuntimeError('Bun is not available in the installation environment.')
    domain = 'gui/' + str(os.getuid())
    target = domain + '/' + LABEL
    observed = subprocess.run(['launchctl', 'print', target], capture_output=True, text=True)
    if observed.returncode == 0:
        raise RuntimeError('The service is already registered; inspect its current job before changing it.')
    path = Path.home() / 'Library/LaunchAgents' / (LABEL + '.plist')
    if path.exists():
        raise RuntimeError('A launch-agent file already exists; preserve and inspect it before replacing it.')
    state = Path(config['localState'])
    state.mkdir(parents=True, exist_ok=True, mode=0o700)
    logs = {}
    for key, name in [('StandardOutPath', 'service-stdout.log'), ('StandardErrorPath', 'service-stderr.log')]:
        log = state / name
        log.touch(exist_ok=True)
        log.chmod(0o600)
        logs[key] = str(log)
    document = {
        'Label': LABEL,
        'ProgramArguments': [bun, str(APP / 'agent/service.ts'), str(config_path)],
        'WorkingDirectory': str(APP),
        'RunAtLoad': True, 'KeepAlive': True, 'ThrottleInterval': 30, 'ExitTimeOut': 45,
        'EnvironmentVariables': {'PATH': os.environ.get('PATH', '/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin')},
        **logs,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        plistlib.dump(document, stream)
    path.chmod(0o600)
    subprocess.run(['plutil', '-lint', str(path)], check=True, capture_output=True)
    subprocess.run(['launchctl', 'bootstrap', domain, str(path)], check=True, capture_output=True)
    result = subprocess.run(['launchctl', 'print', target], check=True, capture_output=True, text=True).stdout
    pid = re.search(r'^\s*pid = (\d+)', result, re.MULTILINE)
    receipt = {'label': LABEL, 'domain': domain, 'configPath': str(config_path), 'plist': str(path),
        'registered': True, 'pid': int(pid.group(1)) if pid else None, 'credentialsWithheld': True,
        'productionScope': 'outbound local API worker; full release and hosted end-to-end remain pending'}
    (APP / 'docs/service-install-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt))

if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Pass the private worker configuration path.')
    install(Path(sys.argv[1]))
