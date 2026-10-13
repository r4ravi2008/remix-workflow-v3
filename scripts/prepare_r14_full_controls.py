"""Bind full-song controls and matte references; no picture rendering."""
from pathlib import Path
import hashlib,json,math,wave
import numpy as np
from PIL import Image,ImageChops,ImageDraw,ImageFilter

P=Path('/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/nuvvantene-istam-deep-house/music-video/rebuild-r10-neon-space')
A=P/'analysis/r14-native'
src=P/'resolve/R05-canonical.wav'
assert hashlib.sha256(src.read_bytes()).hexdigest()=='9769452de248e4c05029f678fe3eac2d0ae0134161e7636356af641379e9396c'
with wave.open(str(src)) as wav:
    assert (wav.getsampwidth(),wav.getnchannels(),wav.getframerate(),wav.getnframes())==(3,2,48000,10638000)
    raw=wav.readframes(wav.getnframes())
p=np.frombuffer(raw,dtype=np.uint8).reshape(-1,3).astype(np.int32)
v=p[:,0]|(p[:,1]<<8)|(p[:,2]<<16)
v=np.where(v&0x800000,v-0x1000000,v)
s=v.reshape(-1,2).astype(float)/8388608
rms=np.sqrt(np.mean(s.reshape(5319,2000,2)**2,axis=(1,2)))
lo,hi=np.quantile(rms,[.12,.95]);level=np.clip((rms-lo)/(hi-lo),0,1)
state=0.;emission=[]
for value in level:
    coefficient=math.exp(-1/(24*(.10 if value>state else .40)))
    state=coefficient*state+(1-coefficient)*value
    emission.append(round(.62+.18*state,6))
controls={'revision':'R14-full-native-a01','frames':5319,'fps':24,'canonical_audio':str(src),'audio_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'emission':emission,'camera_z':'8-0.014*time-0.000004*time*time','accents':[round((.243871569+.4724*k)*24) for k in range(470) if k%8==0 and (.243871569+.4724*k)*24<5319],'beat_grid_status':'estimated; listening pending','audio_decode':'signed packed PCM24, stereo 48000 Hz','response_scope':'native environment emission only; fixed geometry widths; figure and lyrics excluded'}
(A/'full-controls-a01.json').write_text(json.dumps(controls,indent=2)+'\n')
for shot in ['S01','S03','S04']:
    union=Image.new('L',(1920,1080),0)
    for f in sorted((A/f'{shot}-matte-sequence-a03').glob('*.png')):
        union=ImageChops.lighter(union,Image.open(f).convert('L'))
    # Candidate variants have slightly different hand/garment positions.
    union=union.resize((512,288),Image.Resampling.LANCZOS).filter(ImageFilter.MaxFilter(15)).filter(ImageFilter.GaussianBlur(1.5))
    union.resize((1920,1080),Image.Resampling.LANCZOS).save(A/f'{shot}-full-motion-envelope-a01.png')
matte=Image.new('L',(1024,576),0);draw=ImageDraw.Draw(matte)
draw.ellipse((281,183,371,274),fill=255)
for points in [
    [(305,225),(363,227),(382,307),(372,338),(299,345),(295,290)],
    [(167,272),(213,274),(241,267),(265,250),(268,209),(283,185),(302,198),(307,273),(344,274),(350,211),(370,187),(392,201),(394,251),(407,274),(457,260),(500,234),(519,259),(511,286),(483,308),(415,329),(355,326),(313,330),(257,321),(217,325),(180,307)],
    [(306,303),(372,302),(431,370),(437,399),(394,426),(419,454),(264,454),(267,427),(247,393),(253,367)]
]:draw.polygon(points,fill=255)
matte=matte.resize((512,288),Image.Resampling.LANCZOS).filter(ImageFilter.MaxFilter(15)).filter(ImageFilter.GaussianBlur(1.5))
matte.resize((1920,1080),Image.Resampling.LANCZOS).save(A/'S02-full-motion-envelope-a01.png')
claim_path=Path('/tmp/remix-resolve-reservation.json');claim=json.loads(claim_path.read_text())
assert claim['owner_thread']=='01a0ff3f-8968-7922-a88b-74ed982185f8' and claim['status']=='active'
claim['scope']='R14 native 3D full provisional revision; prior full-film authorization retained'
claim_path.write_text(json.dumps(claim,indent=2)+'\n')
(P/'records/r14-native/resource-reservation.json').write_text(json.dumps(claim,indent=2)+'\n')
print({'frames':len(emission),'emission_range':[min(emission),max(emission)],'accents':len(controls['accents'])})
