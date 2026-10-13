"""Versioned musical-review candidate. No GPU generation or approval promotion."""
import copy
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
import numpy as np
from PIL import Image

root=Path('/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/urvashi/music-video')
out=root/'hyperreal-story-review-v3'
old=root/'hyperreal-story-review-v2'
plan=json.loads((old/'edit-contract.json').read_text())
pool=json.loads((old/'source-catalog.json').read_text())
by={a['anchorId']:a for a in pool['assets']}
generated=Path('/Users/aira/.codex/generated_images/01a0c2ed-a2ed-75a2-87c3-6ec62fc9482d/exec-913f39a1-698b-4dfb-bf93-15e7f7773887.png')
revisions=root/'anchor-revisions-v3'
for p in [revisions/'00-originals',revisions/'01-anchor-images',out/'anchors']: p.mkdir(parents=True,exist_ok=True)
name='S05-I02__T017708__admiration-before-approach__openai-imagegen.png'
original=revisions/'00-originals'/name
normalized=revisions/'01-anchor-images'/name
assert not original.exists(), 'Do not overwrite an existing revision'
shutil.copy2(generated,original)
im=np.asarray(Image.open(original).convert('RGB'))
rows=np.where(im.mean(axis=(1,2))>4)[0]
y0,y1=int(rows[0]),int(rows[-1]+1)
height=y1-y0; width=round(height*1920/790); x0=(im.shape[1]-width)//2
subprocess.run(['magick',str(original),'-crop',f'{width}x{height}+{x0}+{y0}','+repage','-resize','1920x790!','-background','black','-gravity','center','-extent','1920x1080',str(normalized)],check=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
revision={'anchorId':'S05-I02','replaces':'S05-I01','status':'FRAME_INSPECTED_USER_REVIEW_PENDING','provider':'openai-imagegen','original':str(original),'originalSha256':sha(original),'active':str(normalized),'activeSha256':sha(normalized),'transform':{'crop':[x0,y0,width,height],'active':[1920,790],'canvas':[1920,1080],'matteTopBottom':145},'direction':'Same man notices same woman across lobby, quietly admiring; no mirror. Next shot is approach at gate. No baked text.'}
(revisions/'revision.json').write_text(json.dumps(revision,indent=2))
for a in pool['assets']:
 src=old/'anchors'/Path(a['active']['file']).name
 assert sha(src)==a['active']['sha256']
 shutil.copy2(src,out/'anchors'/src.name)
shutil.copy2(normalized,out/'anchors'/name)
cuts=copy.deepcopy(plan['cuts'])
bycut={c['cutId']:c for c in cuts}
bycut['C005'].update(anchorId='S05-I02',sourceFile='01-anchor-images/'+name,sha256=sha(normalized),storyBeat='He notices her from across the lobby; quiet admiration before approaching her at the gate.',motionAnchorIds=['S05-I02'])
starts={'C011':46.77,'C012':48.75,'C013':55.06,'C014':58.64,'C015':63.94,'C020':82.5,'C021':85.88,'C022':89.62,'C023':93.3,'C024':96.64,'C025':98.125,'C026':103.88,'C032':136.14,'C033':136.45,'C034':136.79,'C035':143.76,'C036':153.78}
for cid,seconds in starts.items(): bycut[cid]['startFrame']=round(seconds*24)
for cid,aid in [('C023','S20-I01'),('C024','S21-I01'),('C025','S22-I01'),('C026','S23-I01')]:
 a=by[aid]; bycut[cid].update(anchorId=aid,sourceFile=a['active']['file'],sha256=a['active']['sha256'],beat=a['beatSlug'],storyBeat=a['beatSlug'],motionAnchorIds=[aid])
for cid,aid,t in [('C011b','N08C-I01',47.08),('C011c','N08B-I01',47.42)]:
 a=by[aid]; c=copy.deepcopy(bycut['C011']); c.update(cutId=cid,anchorId=aid,startFrame=round(t*24),sourceFile=a['active']['file'],sha256=a['active']['sha256'],beat=a['beatSlug'],storyBeat='Reciprocal glance within the same invitation, not a second invitation.',motionAnchorIds=[aid]); cuts.append(c)
cuts.sort(key=lambda c:c['startFrame'])
beats=json.loads((root/'analysis/urvashi-current/audio-map-measured.json').read_text())['beats']
for i,c in enumerate(cuts):
 c['endFrameExclusive']=cuts[i+1]['startFrame'] if i+1<len(cuts) else 4482
 c['durationFrames']=c['endFrameExclusive']-c['startFrame']; assert c['durationFrames']>0
 c['startSeconds']=c['startFrame']/24; c['endSeconds']=c['endFrameExclusive']/24
 c['transition']='cut'; c['timingStatus']='lyric-and-signal-derived-candidate-listening-pending'
 c['nearestBeatSeconds']=min(beats,key=lambda b:abs(b-c['startSeconds']))
 c['beatOffsetFrames']=c['startFrame']-round(c['nearestBeatSeconds']*24)
 # Superseded source-timestamp metadata must not masquerade as edit authority.
 for k in ['startTimecode','endTimecode','durationSeconds','canonicalSeconds','adjustmentFrames']: c.pop(k,None)
plan.update(cuts=cuts,timelineName='URVASHI STORY CUT v3 - MUSICAL REVIEW',timingPolicy='musical-phrases-and-measured-vocal-candidates',status='REVIEW_CANDIDATE_LISTENING_AND_USER_APPROVAL_PENDING',sourceCatalog=str(old/'source-catalog.json'),anchorRevision=revision,messageOwner='Resolve Fusion only; never anchors or model inputs')
plan['motionIntent']=[{'rangeSeconds':[39.96,46.75],'instruction':'Quiet held framing and slow physical movement through the do-not-rush and take-it-easy lyric; no zoom pulse.'},{'rangeSeconds':[46.77,48.75],'instruction':'Brief reciprocal-glance cuts on the three vocal attacks; maintain continuous source progression when returning to either character.'},{'rangeSeconds':[98.125,103.88],'instruction':'Slow lateral bridge movement on the night-slows/world-fades lyric; future motion plate only, not a frozen-frame substitute.'},{'rangeSeconds':[136.14,137.0],'instruction':'Three-shot departure/cab/city burst keyed to the repeated vocal attacks.'},{'rangeSeconds':[143.76,153.78],'instruction':'Long unbroken hotel-corridor movement during take-it-easy and come-closer-slowly; future footage slow motion subject to source-fps and artifact review.'}]
(out/'edit-contract.json').write_text(json.dumps(plan,indent=2))
(out/'source-catalog.json').write_text(json.dumps(pool,indent=2))
print(json.dumps({'cuts':len(cuts),'replacement':str(normalized),'output':str(out)}))
