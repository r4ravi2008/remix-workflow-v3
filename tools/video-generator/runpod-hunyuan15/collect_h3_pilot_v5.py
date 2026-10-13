"""Observe an existing pilot only; preserve its terminal result without resubmission."""
import argparse
import json
import time
from pathlib import Path

from run_batch import find_output, probe, request_json

root = Path('/workspace/urvashi-h3')
parser = argparse.ArgumentParser()
parser.add_argument('--prefix', default='pilot')
args = parser.parse_args()
assert args.prefix in {'pilot', 'pilot-save-repair'}
receipt = json.loads((root / f'{args.prefix}-receipt.json').read_text())
prompt_id = receipt['promptId']
deadline = receipt['submittedEpoch'] + 2400
while time.time() < deadline:
    history = request_json('http://127.0.0.1:8189/history/' + prompt_id)
    result = history.get(prompt_id)
    if result:
        (root / f'{args.prefix}-history.json').write_text(json.dumps(result, indent=2))
        status = result.get('status', {})
        output = find_output(result, Path('/workspace/ComfyUI-H3/output'), 'C007-v5-pilot')
        report = {
            'promptId': prompt_id,
            'status': status,
            'collectedEpoch': time.time(),
            'submittedEpoch': receipt['submittedEpoch'],
            'reviewStatus': 'PROVISIONAL_GENERATED_UNREVIEWED',
            'media': probe(output) if output else None,
        }
        (root / f'{args.prefix}-result.json').write_text(json.dumps(report, indent=2))
        print(json.dumps(report), flush=True)
        raise SystemExit(0 if output and status.get('status_str') == 'success' else 1)
    time.sleep(15)
raise SystemExit('Pilot observation deadline reached; no resubmission. Stop supervised pod if still running.')
