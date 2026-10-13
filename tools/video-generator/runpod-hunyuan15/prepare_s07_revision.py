import json, hashlib, shutil, subprocess
from pathlib import Path
from PIL import Image
import numpy as np
root=Path('/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/urvashi/music-video')
base=root/'anchor-revisions-v4'
src=Path('/Users/aira/.codex/generated_images/01a0c2ed-a2ed-75a2-87c3-6ec62fc9482d/exec-7119edce-492d-4430-bc83-36dd127bfbbb.png')
name='S07-I02__T028875__independent-forward-walk__openai-imagegen.png'
original=base/'00-originals'/name; dest=base/'01-anchor-images'/name
assert not original.exists()
shutil.copy2(src,original)
a=np.array(Image.open(src).convert('RGB')); rows=np.where(a.mean(axis=(1,2))>8)[0]
y0,y1=int(rows[0]),int(rows[-1])+1
h=y1-y0; w=round(h*1920/790); x0=(a.shape[1]-w)//2
subprocess.run(['magick',str(original),'-crop',f'{w}x{h}+{x0}+{y0}','+repage','-resize','1920x790!','-background','black','-gravity','center','-extent','1920x1080',str(dest)],check=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
revision={'anchorId':'S07-I02','replaces':'S07-I01','original':str(original),'originalSha256':sha(original),'normalized':str(dest),'normalizedSha256':sha(dest),'crop':[x0,y0,w,h],'canvas':[1920,1080],'activePicture':[1920,790],'matteTopBottom':145,'status':'FRAME_INSPECTED_REVIEW_CANDIDATE','inspection':'Woman looks ahead; man behind independently, no mutual eye contact. Same wardrobe and office.','provider':'built-in ImageGen','placement':{'cutId':'C007','startFrame':693,'endFrameExclusive':790},'prompt':'S07-PROMPT.md'}
(base/'S07-revision.json').write_text(json.dumps(revision,indent=2))
path=base/'candidate-edit-contract.json'; plan=json.loads(path.read_text())
c=next(c for c in plan['cuts'] if c['cutId']=='C007')
c.update(anchorId='S07-I02',motionAnchorIds=['S07-I02'],sourceFile=str(dest),displayAnchorFile=str(dest),sha256=sha(dest),storyBeat='Independent office routines; she walks ahead and he follows at a distance, without mutual eye contact.')
plan['walkingAnchorRevision']=str(base/'S07-revision.json')
path.write_text(json.dumps(plan,indent=2,ensure_ascii=False))
print(json.dumps(revision,indent=2))
