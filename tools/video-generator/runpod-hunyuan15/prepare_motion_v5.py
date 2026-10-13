"""Hash-bound motion job preflight; never submits paid jobs."""
import hashlib
import json
import math
from pathlib import Path

ROOT = Path('/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/urvashi/music-video')
BASE = ROOT / 'hyperreal-story-review-v5'
OUT = ROOT / 'motion-production-v5'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build():
    contract = BASE / 'edit-contract.json'
    plan = json.loads(contract.read_text())
    jobs = []
    for cut in plan['cuts']:
        source = BASE / cut['sourceFile']
        digest = sha(source)
        assert digest == cut['sha256'], cut['cutId']
        frames = cut['durationFrames']
        assert cut['endFrameExclusive'] - cut['startFrame'] == frames
        issues = []
        if frames > 192:
            issues.append('SHOT_EXCEEDS_EIGHT_SECONDS_REQUIRES_ALTERNATE_COVERAGE')
        if cut.get('reviewFraming') in ('woman', 'man'):
            issues.append('ANIMATIC_REFRAME_REQUIRES_PRODUCTION_COVERAGE')
        if cut['anchorId'] == 'S35-I01':
            issues.append('REJECTED_ENDING_REQUIRES_NONEXPLICIT_CLOSER_ANCHOR')
        camera = 'Very slow lateral anamorphic tracking; preserve deliberate negative space.'
        if 'phone' in source.name or cut['cutId'] == 'C031':
            camera = 'Locked long-lens composition with tiny natural hand and breathing movement; phone screen stays blank for Resolve graphics.'
        if cut['cutId'] in ('C023', 'C024'):
            camera = 'One brief controlled lateral tracking burst; stable horizon and coherent forward walking.'
        if cut['cutId'] == 'C007':
            camera = 'Smooth backward tracking at walking pace. Woman ahead/right, man behind/left; independent forward eyelines, no mutual stare or approach.'
        if cut['cutId'] == 'C008':
            camera = 'Almost locked long-lens observation across the empty desks. Keep several metres and empty chairs between the two people; only a fleeting glance.'
        jobs.append({
            'jobId': cut['cutId'], 'anchorId': cut['anchorId'],
            'anchorPath': str(source), 'anchorSha256': digest,
            'timelineInFrame': cut['startFrame'], 'timelineOutFrameExclusive': cut['endFrameExclusive'],
            'requiredUsableFrames': frames, 'fps': 24,
            'minimumOutputFramesWithHandles': frames + 24,
            'referenceMode': 'single-anchor I2V; do not morph into the next unrelated scene',
            'prompt': ('One continuous cinematic shot using the attached anchor as the first-frame composition. '
                       + cut['storyBeat'] + '. ' + camera
                       + ' Preserve faces, wardrobe, architecture, lighting and screen direction. Natural restrained movement. '
                       'No speaking or singing mouths, no added text, no scene changes, no zoom pulses or handheld shake. '
                       'No nudity or explicit sexual action. Maintain photographic detail and stable anatomy.'),
            'status': 'BLOCKED_EDITORIAL_REPAIR' if issues else 'AWAITING_IMAGE_AND_SEQUENCE_REVIEW',
            'issues': issues, 'submissionAllowed': False,
            'sourceInFrame': None, 'downloadedOriginal': None,
        })
    assert jobs[0]['timelineInFrame'] == 0
    assert jobs[-1]['timelineOutFrameExclusive'] == 4482
    assert all(a['timelineOutFrameExclusive'] == b['timelineInFrame'] for a, b in zip(jobs, jobs[1:]))
    groups = []
    for job in jobs:
        group = next((g for g in reversed(groups)
                      if g['anchorSha256'] == job['anchorSha256']
                      and job['timelineOutFrameExclusive'] - g['timelineOriginFrame'] <= 192), None)
        if group is None:
            group = {'generationId': job['jobId'], 'anchorSha256': job['anchorSha256'],
                     'timelineOriginFrame': job['timelineInFrame'], 'placements': [],
                     'requiredFramesWithHandles': 0}
            groups.append(group)
        source_in = job['timelineInFrame'] - group['timelineOriginFrame']
        group['placements'].append({'cutId': job['jobId'], 'sourceInFrame': source_in,
                                    'sourceOutFrameExclusive': source_in + job['requiredUsableFrames']})
        group['requiredFramesWithHandles'] = max(group['requiredFramesWithHandles'], source_in + job['requiredUsableFrames'] + 24)
        group['nativeFrames'] = min(192, max(124, 17 * math.ceil((group['requiredFramesWithHandles'] - 5) / 17) + 5))
        group['availableTailHandleFrames'] = group['nativeFrames'] - (group['requiredFramesWithHandles'] - 24)
        group['transitionConstraint'] = ('Use hard cuts or transitions within reviewed visible frames; no ungenerated tail handles'
                                        if group['availableTailHandleFrames'] < 24 else '24 or more tail handle frames planned')
        assert group['nativeFrames'] <= 192
        job['generationId'] = group['generationId']
        job['plannedSourceInFrame'] = source_in
    return {
        'schemaVersion': 1, 'status': 'PREFLIGHT_NOT_SUBMITTED',
        'contractPath': str(contract), 'contractSha256': sha(contract),
        'providerOrder': ['RunPod', 'Grok Imagine only after budget exhaustion or documented quality failure'],
        'budgetCeilingUSD': 7.24, 'reserveUSD': 0.50, 'topUpAllowed': False,
        'allocationRequires': ['fresh balance', 'all-in hourly quote', 'verified bounded shutdown', 'reviewed inputs'],
        'audioSha256': sha(ROOT / 'audio/urvashi-suno-master.mp3'),
        'generationGroups': groups,
        'repeatPolicy': 'Nearby returns to the same anchor share a continuously advancing motion plate; source never restarts. Distant return motifs get a separate generation.',
        'jobs': jobs,
    }


if __name__ == '__main__':
    result = build()
    OUT.mkdir(exist_ok=True)
    (OUT / 'job-preflight.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({'jobs': len(result['jobs']), 'verifiedFrames': sum(j['requiredUsableFrames'] for j in result['jobs']),
                      'editorialBlocks': [j['jobId'] for j in result['jobs'] if j['issues']], 'submitted': 0}))
