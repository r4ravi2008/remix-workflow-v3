"""Repair full-figure coverage and inspect source/matte pairs before Resolve use."""
from pathlib import Path
import json, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

P=Path('/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/nuvvantene-istam-deep-house/music-video/rebuild-r10-neon-space')
A=P/'analysis/r14-native'
matte=Image.new('L',(1024,576),0)
d=ImageDraw.Draw(matte)
# Source-derived head, arm and skirt coverage preserves hands and ankles.
# The far edges of the source orbit stay outside the protected silhouette.
d.ellipse((265,125,400,265),fill=255)
d.polygon([(120,145),(530,145),(535,245),(465,270),(400,285),
           (375,330),(275,330),(245,285),(120,250)],fill=255)
d.polygon([(265,255),(395,255),(445,330),(470,425),(430,525),
           (215,525),(200,420),(225,335)],fill=255)
matte=matte.filter(ImageFilter.MaxFilter(25)).filter(ImageFilter.GaussianBlur(5))
matte.resize((1920,1080),Image.Resampling.LANCZOS).save(A/'S02-full-figure-coverage.png')
readback=json.loads((P/'records/r14-native/full-native-readback-a01.json').read_text())
sources=list(dict.fromkeys(b['source'] for b in readback['body'] if 'S02-full' in b['matte']))
rows=[]
for path in sources:
    frames=[]
    for f in [0,60,123]:
        raw=subprocess.run(['/opt/homebrew/bin/ffmpeg','-v','error','-i',path,'-vf',f'select=eq(n\\,{f})','-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True,check=True).stdout
        array=np.frombuffer(raw,np.uint8).reshape(576,1024,3)
        protected=(array.astype(float)*np.asarray(matte)[:,:,None]/255).astype(np.uint8)
        frames.append(Image.fromarray(protected))
    rows.append((Path(path).stem,frames))
for batch in range(2):
    group=rows[batch*4:(batch+1)*4]
    sheet=Image.new('RGB',(1536,len(group)*310))
    for row,(name,frames) in enumerate(group):
        for col,im in enumerate(frames):
            im.thumbnail((512,288));sheet.paste(im,(col*512,row*310))
            ImageDraw.Draw(sheet).text((col*512+5,row*310+291),f'{name} / {[0,60,123][col]}',fill='white')
    sheet.save(A/f'S02-full-mask-a02-review-{batch+1}.png')
print({'sources':len(sources),'matte':str(A/'S02-full-figure-coverage.png'),'source_frames':len(sources)*3})
