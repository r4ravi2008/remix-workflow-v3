"""Stage second attempts for exact rejected takes without changing anchors or cuts."""
import copy
import hashlib
import json
import shutil
from pathlib import Path

workspace = Path('/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/urvashi')
motion = workspace / 'music-video/motion-production-v5'
dispositions = json.loads((motion / 'motion-dispositions.json').read_text())
stage = motion / 'retry-02'
stage.mkdir(exist_ok=True)
specs = {
    'C031': ('batch-09', 'One continuous photographic shot of this same woman alone, seated with her phone. Her lips are softly pressed together and stay in the same neutral closed-mouth expression throughout the entire shot. Her eyes stay on the phone. Only a small natural blink, subtle breathing and tiny finger adjustment. Preserve her face, hair, charcoal blazer, pale top, phone grip, red wall and night skyline. The back of the phone faces the camera throughout. The left red wall stays plain and unmarked. Almost locked long-lens camera with a very slight lateral drift. Silent contemplation, no dialogue performance, no smiling change, no speaking, no singing, no words or typography, no added people, no scene change. Stable hands and photographic detail.'),
    'C035b': ('batch-10', 'One uninterrupted photographic medium shot of this single man alone in the hotel corridor. He stays on his exact floor position with both hands resting in his pockets and a quiet neutral closed-mouth expression. He briefly shifts his eyes toward the empty right edge, then holds his gaze. Preserve his face, dark shirt and jacket, corridor lighting and architecture. No one enters the frame at any moment; the right edge and background remain empty of people. Tiny natural breathing and one blink. Almost locked long-lens camera, minimal lateral movement, no forward approach. No woman, no additional character, no reflected person, no conversation, no speaking or singing, no outfit change, no text, no scene change. Maintain realistic detail and stable anatomy.'),
}
jobs = []
for key, (batch, prompt) in specs.items():
    rejected = dispositions[key]
    assert rejected['status'] == 'REJECTED'
    result = json.loads((motion / batch / (key + '.result.json')).read_text())
    assert hashlib.sha256(Path(result['localOriginal']).read_bytes()).hexdigest() == rejected['sha256']
    source = next(j for j in json.loads((motion / batch / 'plan.json').read_text())['jobs'] if j['jobId'] == key)
    job = copy.deepcopy(source)
    job.update(jobId=key + 'R1', generationId=key, replacesGenerationId=key,
               prompt=prompt, seed=source['seed'] + 100000)
    anchor = Path(job['anchorPath'])
    assert hashlib.sha256(anchor.read_bytes()).hexdigest() == job['anchorSha256']
    target = stage / (job['jobId'] + '.png')
    if target.exists():
        assert hashlib.sha256(target.read_bytes()).hexdigest() == job['anchorSha256']
    else:
        shutil.copyfile(anchor, target)
    jobs.append(job)
plan = {
    'provider': 'RunPod', 'topUpAllowed': False, 'jobs': jobs,
    'pilotUserApproval': 'Yes, continue with this quality',
    'scope': 'Second attempts only for C031 speech-like mouth shapes and C035b invented woman; unchanged accepted anchors and fixed placements',
    'contractSha256': hashlib.sha256((workspace / 'music-video/hyperreal-story-review-v5/edit-contract.json').read_bytes()).hexdigest(),
    'attemptNumber': 2, 'maxAttempts': 3,
}
path = stage / 'plan.json'
if path.exists():
    assert json.loads(path.read_text()) == plan, 'Existing retry plan differs; preserve it'
else:
    path.write_text(json.dumps(plan, indent=2) + '\n')
print(json.dumps({'stage': str(stage), 'jobs': [j['jobId'] for j in jobs], 'submitted': False}))
