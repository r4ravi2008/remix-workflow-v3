"""Preserve the requested S08 replacement as a review-only anchor revision."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

root = Path('/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/urvashi')
base = root / 'music-video/anchor-revisions-v4'
source = Path('/Users/aira/.codex/generated_images/01a0c2ed-a2ed-75a2-87c3-6ec62fc9482d/exec-ac7e4cbc-a7b5-4500-bc40-adc5e8b876a7.png')
name = 'S08-I02__T032917__distant-first-notice__openai-imagegen.png'
original = base / '00-originals' / name
anchor = base / '01-anchor-images' / name
assert not original.exists(), 'Revision already exists'
original.parent.mkdir(parents=True, exist_ok=True)
anchor.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(source, original)
subprocess.run(['magick', str(original), '-crop', '1672x688+0+126', '+repage', '-resize', '1920x790!', '-background', 'black', '-gravity', 'center', '-extent', '1920x1080', str(anchor)], check=True)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
plan = json.loads((root / 'music-video/hyperreal-story-review-v3/edit-contract.json').read_text())
cut = next(c for c in plan['cuts'] if c['cutId'] == 'C008')
revision = {
    'anchorId': 'S08-I02', 'replaces': 'S08-I01', 'provider': 'built-in ImageGen',
    'status': 'FRAME_INSPECTED_USER_REVIEW_PENDING',
    'original': str(original), 'originalSha256': sha(original),
    'normalized': str(anchor), 'normalizedSha256': sha(anchor),
    'transform': {'sourceCrop': [0, 126, 1672, 688], 'activeSize': [1920, 790], 'matteTopBottom': 145},
    'placement': {'cutId': 'C008', 'startFrame': 790, 'endFrameExclusive': 898, 'fps': 24},
    'inspection': 'Three empty chairs separate the same identifiable colleagues across the desk. Preserved wardrobe, left/right positions and office palette. No touching or baked text. Neighbor shots inspected; previous shared lobby shot remains unchanged.',
    'resolveUpdate': 'PENDING; existing v3 MP4 and native timeline still show old S08-I01. Do not use that old anchor for further motion generation.',
    'prompt': 'PROMPT.md',
}
(base / 'revision.json').write_text(json.dumps(revision, indent=2) + '\n')
for c in plan['cuts']:
    c['displayAnchorFile'] = c['sourceFile']
    c['endSecondsExclusive'] = c['endFrameExclusive'] / plan['fps']
    f = c['endFrameExclusive']
    c['endTimecodeExclusive'] = f'{f // 86400:02}:{f // 1440 % 60:02}:{f // 24 % 60:02}:{f % 24:02}'
cut.update(anchorId='S08-I02', sourceFile=str(anchor), displayAnchorFile=str(anchor), motionAnchorIds=['S08-I02'], sha256=sha(anchor), storyBeat='Reserved mutual notice across several metres of empty desk; proximity develops later.')
plan['status'] = 'ANCHOR_REPLACEMENT_REVIEW_CANDIDATE_NOT_YET_IN_RESOLVE'
plan['pendingAnchorRevision'] = str(base / 'revision.json')
(base / 'candidate-edit-contract.json').write_text(json.dumps(plan, indent=2) + '\n')
meta_path = root / 'meta.json'
meta = json.loads(meta_path.read_text())
meta['pending_anchor_revision_v4'] = {'revision': 'music-video/anchor-revisions-v4/revision.json', 'editContract': 'music-video/anchor-revisions-v4/candidate-edit-contract.json', 'status': revision['status'], 'affectedCut': 'C008', 'timingUnchanged': True, 'resolveUpdate': 'PENDING', 'generationGate': 'NO_GPU_GENERATION_BEFORE_APPROVAL'}
meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + '\n')
print(json.dumps(revision, indent=2))
