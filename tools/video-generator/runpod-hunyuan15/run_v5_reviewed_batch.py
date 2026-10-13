"""Run a small explicitly reviewed H3 batch, recovering receipts without duplicate spend."""
import argparse
import hashlib
import json
import time
from pathlib import Path
from PIL import Image
from run_batch import find_output, probe, request_json, workflow

parser = argparse.ArgumentParser()
parser.add_argument('--plan', required=True, type=Path)
parser.add_argument('--deadline', required=True, type=float)
parser.add_argument('--job-reserve-seconds', type=int, default=900)
args = parser.parse_args()
assert args.job_reserve_seconds >= 600, 'Keep at least ten minutes per-job deadline headroom'
root = Path('/workspace/urvashi-h3')
plan = json.loads(args.plan.read_text())
assert 1 <= len(plan['jobs']) <= 4
assert plan['provider'] == 'RunPod' and plan['topUpAllowed'] is False
url = 'http://127.0.0.1:8189'
out = root / 'batch-v5'
out.mkdir(exist_ok=True)
for job in plan['jobs']:
    key = job['jobId']
    assert key.isalnum() and job['reviewedForGeneration'] is True
    prefix = out / key
    result_path = prefix.with_suffix('.result.json')
    receipt_path = prefix.with_suffix('.receipt.json')
    intent_path = prefix.with_suffix('.submitting.json')
    if result_path.exists():
        existing = json.loads(result_path.read_text())
        assert existing['status'] == 'GENERATED_UNREVIEWED', existing
        assert existing['receipt']['anchorSha256'] == job['anchorSha256'], 'Completed job has stale anchor'
        assert existing['placements'] == job['placements'], 'Completed job has stale placement ranges'
        print(json.dumps(existing), flush=True)
        continue
    if receipt_path.exists():
        receipt = json.loads(receipt_path.read_text())
        assert receipt['anchorSha256'] == job['anchorSha256'], 'Submitted job has stale anchor; do not reuse'
    else:
        assert not intent_path.exists(), 'Uncertain submission; reconcile queue/history before retry'
        if time.time() + args.job_reserve_seconds >= args.deadline:
            raise SystemExit('Insufficient time reserve for next job; stop supervised pod')
        original = root / 'anchors-v5' / (key + '.png')
        assert hashlib.sha256(original.read_bytes()).hexdigest() == job['anchorSha256']
        image_path = Path('/workspace/ComfyUI-H3/input') / (key + '-v5.png')
        with Image.open(original) as image:
            assert image.size == (1920, 1080)
            image.crop((12, 145, 1908, 935)).resize((1536, 640), Image.Resampling.LANCZOS).save(image_path)
        frames = job['nativeFrames']
        assert 124 <= frames <= 192 and (frames - 5) % 17 == 0
        graph = workflow({'jobId': key + '-v5', 'prompt': job['prompt'], 'nativeLength': frames, 'seed': job['seed']}, image_path.name, None)
        graph['8']['inputs'].update(width=1536, height=640)
        graph['16']['inputs']['codec'] = 'none'
        graph['17']['inputs'].pop('codec', None)
        graph['17']['inputs'].update({'format': 'mp4', 'format.codec': 'h264', 'format.codec.encoding': 're-encode', 'format.codec.encoding.crf': 16})
        prefix.with_suffix('.workflow.json').write_text(json.dumps(graph, indent=2))
        intent = {'jobId': key, 'anchorSha256': job['anchorSha256'], 'submittedEpoch': time.time(), 'clientId': 'urvashi-v5-' + key, 'modelInputSha256': hashlib.sha256(image_path.read_bytes()).hexdigest()}
        intent_path.write_text(json.dumps(intent, indent=2))
        response = request_json(url + '/prompt', {'prompt': graph, 'client_id': intent['clientId']})
        assert response.get('prompt_id'), response
        receipt = {**intent, 'promptId': response['prompt_id']}
        receipt_path.write_text(json.dumps(receipt, indent=2))
        print(json.dumps({'event': 'SUBMITTED', **receipt}), flush=True)
    while time.time() < args.deadline:
        history = request_json(url + '/history/' + receipt['promptId']).get(receipt['promptId'])
        if history:
            prefix.with_suffix('.history.json').write_text(json.dumps(history, indent=2))
            assert history['status']['status_str'] == 'success', history['status']
            media = find_output(history, Path('/workspace/ComfyUI-H3/output'), key + '-v5')
            assert media is not None
            report = {'jobId': key, 'status': 'GENERATED_UNREVIEWED', 'receipt': receipt, 'completedEpoch': time.time(), 'media': probe(media), 'placements': job['placements']}
            video = next(s for s in report['media']['streams'] if s['codec_type'] == 'video')
            assert int(video['nb_read_frames']) >= job['nativeFrames']
            result_path.write_text(json.dumps(report, indent=2))
            print(json.dumps(report), flush=True)
            break
        time.sleep(10)
    else:
        raise SystemExit('Batch deadline reached; stop supervised pod, do not resubmit')
print('BATCH_COMPLETE_STOP_SUPERVISED_POD', flush=True)
