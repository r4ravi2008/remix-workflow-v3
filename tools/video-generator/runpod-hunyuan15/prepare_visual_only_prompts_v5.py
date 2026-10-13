"""Version unsubmitted prompts after the observed C014 typography failure."""
import copy
import json
import re
import shutil
from prepare_motion_v5 import OUT, sha

changed = []
for number in range(5, 14):
    stage = OUT / f'batch-{number:02d}'
    original = stage / 'plan.json'
    plan = json.loads(original.read_text())
    changes = []
    for job in plan['jobs']:
        sentences = re.split(r'(?<=[.!?])\s+', job['prompt'])
        removed = [s for s in sentences if re.search(r'\b(Resolve|editor|graphics)\b', s, re.I)]
        if removed:
            job['prompt'] = ' '.join(s for s in sentences if s not in removed)
            job['prompt'] += ' Preserve plain unmarked background surfaces and keep the phone back toward camera.'
            changes.append({'jobId': job['jobId'], 'removedSentences': removed})
    if changes:
        target = stage / 'plan-visual-only-v2.json'
        assert not target.exists(), 'Do not overwrite a possibly submitted revision'
        plan['promptRevision'] = {'reason': 'C014 generated lettering; remove nonvisual postproduction references',
                                  'originalPlanSHA256': sha(original), 'changes': changes}
        target.write_text(json.dumps(plan, indent=2) + '\n')
        changed.append(str(target))

source = json.loads((OUT / 'batch-04/plan.json').read_text())
job = copy.deepcopy(next(j for j in source['jobs'] if j['jobId'] == 'C014'))
job.update(jobId='C014R1', seed=job['seed'] + 100000, replacesGenerationId='C014',
           prompt='One uninterrupted photographic shot of the same woman seated at the cafe table. She quietly studies the phone in her hand, makes one natural blink, and pauses thoughtfully. The back of the phone always faces the camera. Her other hand stays lightly against her cheek. Preserve her face, hair, cream top, charcoal jacket, cup, candle and red wall. The left wall stays plain, solid red and completely unmarked throughout. Almost locked long-lens camera with only a tiny lateral drift. Natural breathing and subtle hair movement. Lips remain gently closed. No letters, words, symbols, logos, subtitles, overlays, speaking, singing, added objects, cuts or scene changes. Stable anatomy and photographic detail.')
stage = OUT / 'retry-01'
stage.mkdir(exist_ok=True)
assert not (stage / 'plan.json').exists()
shutil.copy2(job['anchorPath'], stage / 'C014R1.png')
assert sha(stage / 'C014R1.png') == job['anchorSha256']
retry = {**source, 'jobs': [job], 'scope': 'Second C014 attempt after exact first take rejected for generated typography; unchanged accepted anchor and locked timing',
         'attemptNumber': 2, 'maxAttempts': 3}
(stage / 'plan.json').write_text(json.dumps(retry, indent=2) + '\n')
print(json.dumps({'versionedPlans': changed, 'retryPlan': str(stage / 'plan.json'), 'submitted': False}))
