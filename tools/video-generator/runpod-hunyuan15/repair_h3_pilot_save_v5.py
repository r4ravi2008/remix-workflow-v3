"""Fix only the failed save-node serialization, reusing cached generated frames."""
import json
import time
from pathlib import Path
from run_batch import request_json

root = Path('/workspace/urvashi-h3')
receipt_path = root / 'pilot-save-repair-receipt.json'
if receipt_path.exists():
    print(receipt_path.read_text())
else:
    original = json.loads((root / 'pilot-receipt.json').read_text())
    history = request_json('http://127.0.0.1:8189/history/' + original['promptId'])[original['promptId']]
    errors = [data for event, data in history['status']['messages'] if event == 'execution_error']
    assert len(errors) == 1 and errors[0]['node_id'] == '17', errors
    graph = json.loads((root / 'pilot-workflow.json').read_text())
    graph['17']['inputs'].update({'format': 'mp4', 'format.codec': 'h264', 'format.codec.encoding': 're-encode', 'format.codec.encoding.crf': 16})
    (root / 'pilot-save-repair-workflow.json').write_text(json.dumps(graph, indent=2))
    response = request_json('http://127.0.0.1:8189/prompt', {'prompt': graph})
    assert response.get('prompt_id'), response
    receipt = {**original, 'promptId': response['prompt_id'], 'originalPromptId': original['promptId'], 'submittedEpoch': time.time(), 'repair': 'Only save node changed; upstream nodes unchanged for cache reuse'}
    receipt_path.write_text(json.dumps(receipt, indent=2))
    print(json.dumps(receipt))
