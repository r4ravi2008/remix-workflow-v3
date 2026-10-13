"""Measure the rendered story review without claiming creative approval."""
import json
import subprocess
import sys
from pathlib import Path
import numpy as np
from PIL import Image

base=Path(sys.argv[1])
video=base/(base.name.replace('hyperreal','urvashi')+'.mp4')
plan=json.loads((base/'edit-contract.json').read_text())
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(video)]))
v=next(s for s in probe['streams'] if s['codec_type']=='video')
assert (v['width'],v['height'],int(v['nb_frames']),v['r_frame_rate'])==(1920,1080,4482,'24/1')
assert any(s['codec_type']=='audio' for s in probe['streams'])
decode=subprocess.run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'],capture_output=True,text=True)
assert decode.returncode==0 and not decode.stderr,decode.stderr
results=[]
for c in plan['cuts']:
    t=(c['startFrame']+c['durationFrames']//2)/24
    frame=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(video),'-frames:v','1','-vf','scale=192:108','-f','rawvideo','-pix_fmt','rgb24','-'])
    actual=np.frombuffer(frame,dtype=np.uint8).reshape(108,192,3).astype(float)
    source=np.array(Image.open(base/'anchors'/Path(c['sourceFile']).name).convert('RGB').resize((192,108))).astype(float)
    # Compare right-hand picture, excluding the three intended left-side graphic overlays.
    delta=np.abs(actual[16:92,100:190]-source[16:92,100:190]).mean()
    assert delta<18,(c['cutId'],delta)
    results.append({'cutId':c['cutId'],'meanAbsoluteDifference':round(float(delta),3),'sourceMatched':True})
for label,seconds in [('coffee-message',61),('absence-message',113),('oyo-message',129),('okay-reply',134),('scene-five',20)]:
    subprocess.run(['ffmpeg','-v','error','-ss',str(seconds),'-i',str(video),'-frames:v','1','-update','1',str(base/(label+'.png'))],check=True)
report={'status':'MEASURED_PASS_CREATIVE_REVIEW_PENDING','video':str(video),'frames':4482,'fps':24,'durationSeconds':186.75,'fullDecode':'PASS','sourceMatches':results,'normalSpeedWatched':'PENDING','heard':'PENDING','userApproval':'PENDING'}
(base/'render-qc.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'frames':4482,'sourceMatchedCuts':len(results),'fullDecode':'PASS','review':'PENDING'}))
