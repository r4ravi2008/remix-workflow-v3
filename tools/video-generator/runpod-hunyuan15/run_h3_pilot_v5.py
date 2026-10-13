"""Submit exactly one hash-bound pilot; recover its prompt ID after interruption."""
import argparse
import hashlib
import json
import time
from pathlib import Path
from run_batch import request_json, workflow

parser = argparse.ArgumentParser()
parser.add_argument('--submit', action='store_true')
args = parser.parse_args()
root = Path('/workspace/urvashi-h3')
receipt = root / 'pilot-receipt.json'
url = 'http://127.0.0.1:8189'
if receipt.exists():
    saved = json.loads(receipt.read_text())
    print(json.dumps({'receipt': saved, 'history': request_json(url + '/history/' + saved['promptId'])}))
else:
    assert args.submit, 'No existing pilot receipt; explicit --submit required'
    preflight = json.loads((root / 'job-preflight.json').read_text())
    job = next(j for j in preflight['jobs'] if j['jobId'] == 'C007')
    image = Path('/workspace/ComfyUI-H3/input/C007.png')
    original = root / 'C007-anchor.png'
    assert hashlib.sha256(original.read_bytes()).hexdigest() == job['anchorSha256']
    from PIL import Image
    with Image.open(original) as anchor:
        assert anchor.size == (1920, 1080)
        anchor.crop((12, 145, 1908, 935)).resize((1536, 640), Image.Resampling.LANCZOS).save(image)
    graph = workflow({'jobId': 'C007-v5-pilot', 'prompt': job['prompt'], 'nativeLength': 124, 'seed': 2026092207}, 'C007.png', None)
    # Slight side crop maintains aspect ratio while matching the model's 32px grid.
    graph['8']['inputs']['width'] = 1536
    graph['8']['inputs']['height'] = 640
    # Encode once at the requested quality rather than transcoding an H.264 intermediate.
    graph['16']['inputs']['codec'] = 'none'
    graph['17']['inputs'].update({'format': 'mp4', 'format.codec': 'h264', 'format.codec.encoding': 're-encode', 'format.codec.encoding.crf': 16})
    graph['17']['inputs'].pop('codec', None)
    (root / 'pilot-workflow.json').write_text(json.dumps(graph, indent=2))
    result = request_json(url + '/prompt', {'prompt': graph})
    assert result.get('prompt_id'), result
    saved = {'promptId': result['prompt_id'], 'submittedEpoch': time.time(), 'cutId': 'C007', 'anchorSha256': job['anchorSha256'], 'modelInputSha256': hashlib.sha256(image.read_bytes()).hexdigest(), 'modelInputCrop': [12,145,1896,790], 'nativeFrames': 124, 'outputCanvas': [1536, 640], 'status': 'SUBMITTED_UNREVIEWED', 'purpose': 'ISOLATED_PROVISIONAL_DIAGNOSTIC_NOT_ACCEPTED_PRODUCTION'}
    receipt.write_text(json.dumps(saved, indent=2))
    print(json.dumps(saved))
