"""Preserve generated revisions and add coverage without moving locked cuts."""
import copy
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path('/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/urvashi/music-video')
GEN = Path('/Users/aira/.codex/generated_images/01a0c2ed-a2ed-75a2-87c3-6ec62fc9482d')
REV = ROOT / 'anchor-revisions-v5'
OUT = ROOT / 'hyperreal-story-review-v5'
OLD = ROOT / 'hyperreal-story-review-v4'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
specs = [
    ('S23-I02', '104375', 'bridge-woman', 'exec-561b3966-fc0e-4e1e-93f1-0dbce6713ee9.png'),
    ('S23-I03', '104708', 'bridge-man', 'exec-40b7cf31-1321-4dbd-9804-8a83b7bc330f.png'),
    ('S31-I02', '148750', 'corridor-respectful-wait', 'exec-733fa5dc-43a9-4a65-8834-ab2b30fe797c.png'),
    ('S35-I03', '175500', 'chosen-closeness-reaction', 'exec-19544ddf-374a-4268-8f17-187e2d5793cb.png'),
]
OUT.mkdir(exist_ok=True)
(OUT / 'anchors').mkdir(exist_ok=True)
revisions = []
new = {}
for aid, token, slug, filename in specs:
    name = f'{aid}__T{token}__{slug}__openai-imagegen.png'
    original = REV / '00-originals' / name
    normalized = REV / '01-anchor-images' / name
    if original.exists():
        assert sha(original) == sha(GEN / filename)
    else:
        shutil.copy2(GEN / filename, original)
    if not normalized.exists():
        subprocess.run(['magick', str(original), '-resize', '1920x790^', '-gravity', 'center', '-extent', '1920x790', '-background', 'black', '-extent', '1920x1080', str(normalized)], check=True)
    new[aid] = normalized
    revisions.append({'anchorId': aid, 'original': str(original), 'originalSha256': sha(original), 'normalized': str(normalized), 'sha256': sha(normalized), 'status': 'FRAME_INSPECTED_ORIGINAL_NORMALIZED_REVIEW_PENDING', 'provider': 'OpenAI ImageGen', 'promptFile': 'prompts.json', 'transform': 'resize cover and center crop to 1920x790; 145px black top/bottom'})
new['S35-I02'] = REV / '01-anchor-images/S35-I02__T171000__chosen-closeness__openai-imagegen.png'
new['S27-I02'] = ROOT / 'source-of-truth-hyperreal-v1/01-anchor-images/S27-I02__T134750__invitation-tap__openai-imagegen.png'
plan = json.loads((OLD / 'edit-contract.json').read_text())
original_starts = {c['cutId']: c['startFrame'] for c in plan['cuts']}
for cut in plan['cuts']:
    source = OLD / cut['sourceFile']
    dest = OUT / 'anchors' / source.name
    shutil.copy2(source, dest)
    assert sha(dest) == cut['sha256']

def replace(cut, aid):
    source = new[aid]
    dest = OUT / 'anchors' / source.name
    shutil.copy2(source, dest)
    cut.update(anchorId=aid, sourceFile='anchors/' + source.name, displayAnchorFile='anchors/' + source.name, sha256=sha(dest))
    cut.pop('reviewFraming', None)

byid = {c['cutId']: c for c in plan['cuts']}
replace(byid['C026b'], 'S23-I02')
replace(byid['C026c'], 'S23-I03')
byid['C026b']['storyBeat'] = 'She looks out toward the lake; a restrained response, not mutual eyeline matching.'
byid['C026c']['storyBeat'] = 'He looks toward her; attention remains patient.'
replace(byid['C040'], 'S35-I02')
byid['C040']['storyBeat'] = 'Standing together at the window, they choose closeness and hold hands.'
for parent, cid, frame, aid, beat in [
    ('C031', 'C031b', 3146, 'S27-I02', 'She considers the invitation, then chooses to reply; messages remain editor overlays.'),
    ('C035', 'C035b', 3570, 'S31-I02', 'Reverse angle: he waits at a respectful distance while she chooses.'),
    ('C040', 'C040b', 4212, 'S35-I03', 'She rests her head on his shoulder; held hands and city reflections resolve the closeness.')]:
    c = copy.deepcopy(byid[parent])
    c.update(cutId=cid, startFrame=frame, storyBeat=beat)
    replace(c, aid)
    plan['cuts'].append(c)
plan['cuts'].sort(key=lambda c: c['startFrame'])
for i, c in enumerate(plan['cuts']):
    end = plan['cuts'][i+1]['startFrame'] if i+1 < len(plan['cuts']) else 4482
    c.update(endFrameExclusive=end, durationFrames=end-c['startFrame'], startSeconds=c['startFrame']/24, endSeconds=end/24, endSecondsExclusive=end/24)
    c['endTimecodeExclusive'] = f'{end//86400:02}:{end//1440%60:02}:{end//24%60:02}:{end%24:02}'
    assert 0 < c['durationFrames'] <= 192
    if c['cutId'] in original_starts:
        assert c['startFrame'] == original_starts[c['cutId']]
plan.update(timelineName='URVASHI STORY CUT v5 - MOTION PRODUCTION', status='PREPARED_NOT_APPLIED_IN_RESOLVE', sourceCatalog='source-catalog.json')
plan['revisionV5'] = {'lockedPriorBoundariesPreserved': True, 'newCoverageCuts': ['C031b', 'C035b', 'C040b'], 'maximumShotFrames': max(c['durationFrames'] for c in plan['cuts']), 'messageOverlayRule': 'Carry C031 message animation in absolute timeline time across C031b, do not reset invitation or reply.', 'ending': 'Non-explicit affectionate closeness replaces distant seating', 'bridgeCoverage': 'Generated individual full-resolution anchors replace animatic crops'}
(OUT / 'edit-contract.json').write_text(json.dumps(plan, indent=2, ensure_ascii=False) + '\n')
(REV / 'revisions.json').write_text(json.dumps(revisions, indent=2) + '\n')
catalog = {'status': 'REVIEW_CANDIDATE', 'inheritedCatalog': str(OLD / 'source-catalog.json'), 'revisions': str(REV / 'revisions.json'), 'assets': [{'anchorId': c['anchorId'], 'path': c['sourceFile'], 'sha256': c['sha256'], 'cutId': c['cutId']} for c in plan['cuts']]}
(OUT / 'source-catalog.json').write_text(json.dumps(catalog, indent=2) + '\n')
print(json.dumps({'cuts': len(plan['cuts']), 'frames': sum(c['durationFrames'] for c in plan['cuts']), 'maxShotSeconds': plan['revisionV5']['maximumShotFrames']/24, 'resolveApplied': False}))
