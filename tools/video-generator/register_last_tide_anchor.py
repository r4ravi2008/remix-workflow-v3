"""Preserve an ImageGen original and record exact canvas normalization."""
import argparse
import hashlib
import json
import shutil
from PIL import Image
from prepare_last_tide_v6 import BASE, OUT

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

p=argparse.ArgumentParser()
p.add_argument('id')
p.add_argument('original',type=__import__('pathlib').Path)
p.add_argument('slug')
p.add_argument('--source-active-box',type=int,nargs=4,metavar=('LEFT','TOP','RIGHT','BOTTOM'),help='Visually verified source active picture; remove baked mattes before normalization')
a=p.parse_args()
plan=json.loads((OUT/'full-film-plan.json').read_text())
shot=next(x for x in plan['shots'] if x['sourceId']==a.id)
root=BASE/'source-of-truth/05-abstract-supplement-v6'
for folder in ['originals','anchors','model-inputs']: (root/folder).mkdir(parents=True,exist_ok=True)
original=root/'originals'/f'{a.id}__{a.slug}__imagegen-original.png'
if original.exists(): assert sha(original)==sha(a.original),'Never overwrite a generated original'
else: shutil.copy2(a.original,original)
image=Image.open(original).convert('RGB')
w,h=image.size
source_box=tuple(a.source_active_box or (0,0,w,h))
assert 0 <= source_box[0] < source_box[2] <= w and 0 <= source_box[1] < source_box[3] <= h
image=image.crop(source_box)
cw0,ch0=image.size
target_ratio=1920/804
if cw0/ch0>target_ratio:
    cw=int(ch0*target_ratio); box=((cw0-cw)//2,0,(cw0+cw)//2,ch0)
else:
    ch=int(cw0/target_ratio); box=(0,(ch0-ch)//2,cw0,(ch0+ch)//2)
active=image.crop(box).resize((1920,804),Image.Resampling.LANCZOS)
stem=f'{shot["id"]}-I02__T{round(shot["recordInFrame"]/24*1000):06}__{a.slug}__imagegen'
model=root/'model-inputs'/f'{stem}__active.png'
anchor=root/'anchors'/f'{stem}.png'
active.save(model)
canvas=Image.new('RGB',(1920,1080)); canvas.paste(active,(0,138)); canvas.save(anchor)
catalog=root/'catalog.json'
data=json.loads(catalog.read_text()) if catalog.exists() else {'schemaVersion':1,'anchors':[]}
entry={'id':a.id,'shotId':shot['id'],'origin':'generated','provider':'OpenAI built-in ImageGen',
       'originalPath':str(original),'originalSha256':sha(original),'originalDimensions':[w,h],
       'anchorPath':str(anchor),'anchorSha256':sha(anchor),'modelInputPath':str(model),'modelInputSha256':sha(model),
       'sourceActiveBox':source_box,'cropBox':box,'activeDimensions':[1920,804],'canvasDimensions':[1920,1080],'matteTopBottom':138,
       'intendedTimelineFrames':[shot['recordInFrame'],shot['recordOutFrame']],
       'status':'generated-unreviewed','review':{'fullSizeInspected':False,'sequenceInspected':False}}
previous=next((x for x in data['anchors'] if x['id']==a.id),None)
if previous and previous['originalSha256'] != entry['originalSha256']:
    previous=dict(previous, status='superseded', supersededBySha256=entry['originalSha256'])
    data.setdefault('supersededAnchors',[]).append(previous)
elif previous:
    entry=previous  # Idempotent registration must not erase existing review evidence.
data['anchors']=[x for x in data['anchors'] if x['id']!=a.id]+[entry]
catalog.write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps(entry,indent=2))
