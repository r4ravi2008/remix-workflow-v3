"""Hash-bound decode checks and measured throughput, never creative approval."""
import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--stage', required=True, type=Path)
parser.add_argument('--compute-hourly-usd', type=float, default=0.84)
parser.add_argument('--job-compute-hourly-usd', action='append', default=[], metavar='JOB=RATE')
args = parser.parse_args()
job_rates = {}
for override in args.job_compute_hourly_usd:
    key, value = override.split('=', 1)
    assert key.isalnum() and key not in job_rates
    job_rates[key] = float(value)
    assert job_rates[key] > 0
assert args.compute_hourly_usd > 0
rows = []
for receipt_file in sorted(args.stage.glob('*.result.json')):
    receipt = json.loads(receipt_file.read_text())
    path = Path(receipt['localOriginal'])
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest == receipt['media']['sha256']
    cmd = ['ffmpeg', '-hide_banner', '-nostdin', '-v', 'info', '-xerror',
           '-i', str(path), '-an', '-vf',
           'blackdetect=d=0.1:pix_th=0.1,freezedetect=n=-50dB:d=0.5',
           '-f', 'null', '-']
    decoded = subprocess.run(cmd, capture_output=True, text=True)
    events = [line for line in decoded.stderr.splitlines()
              if 'black_start:' in line or 'freeze_start:' in line]
    seconds = float(receipt['media']['format']['duration'])
    elapsed = receipt['completedEpoch'] - receipt['receipt']['submittedEpoch']
    hourly_rate = job_rates.get(receipt['jobId'], args.compute_hourly_usd)
    cost = elapsed / 3600 * hourly_rate
    rows.append({'jobId': receipt['jobId'], 'sha256': digest,
                 'fullDecodePassed': decoded.returncode == 0,
                 'detectedEvents': events, 'generatedSeconds': seconds,
                 'submissionToReceiptSeconds': elapsed,
                 'estimatedComputeUSD': cost, 'computeHourlyUSD': hourly_rate,
                 'estimatedComputeUSDPerGeneratedSecond': cost / seconds,
                 'acceptedSeconds': None, 'normalSpeedReview': 'PENDING'})
    (args.stage / (receipt['jobId'] + '.decode.log')).write_text(decoded.stderr)
assert rows, 'No downloaded results to check'
report = {'checkedAtUTC': datetime.now(timezone.utc).isoformat(),
          'status': 'TECHNICAL_CHECKS_ONLY', 'clips': rows,
          'computeHourlyUSD': args.compute_hourly_usd,
          'jobComputeHourlyUSDOverrides': job_rates,
          'costExclusions': ['pod startup', 'idle time', 'storage', 'retries', 'other jobs'],
          'billingStatus': 'ESTIMATED_NOT_SETTLED_INVOICE',
          'normalSpeedAcceptance': 'PENDING',
          'resolveTouched': False}
(args.stage / 'technical-qc.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
if any(not row['fullDecodePassed'] or row['detectedEvents'] for row in rows):
    raise SystemExit(1)
