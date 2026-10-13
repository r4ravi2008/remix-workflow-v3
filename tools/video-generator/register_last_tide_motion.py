"""Preserve one downloaded Grok original and create bounded QC evidence."""
import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from prepare_last_tide_v6 import BASE, OUT

p = argparse.ArgumentParser()
p.add_argument('anchor_id')
p.add_argument('download', type=Path)
p.add_argument('post_url')
a = p.parse_args()
root = BASE / 'source-of-truth/05-abstract-supplement-v6'
destdir = root / 'motion-originals'
destdir.mkdir(exist_ok=True)
dest = destdir / f'{a.anchor_id}__grok-imagine__original.mp4'
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
if dest.exists():
    assert digest(dest) == digest(a.download), 'Never overwrite an original'
else:
    shutil.copy2(a.download, dest)
probe = json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(dest)]))
video = next(s for s in probe['streams'] if s['codec_type']=='video' and not s.get('disposition',{}).get('attached_pic'))
assert float(video['duration']) <= 6.1, 'Outside the six-second generation contract'
subprocess.run(['ffmpeg','-v','error','-i',str(dest),'-map','0:v:0','-f','null','-'],check=True)
qc = subprocess.run(['ffmpeg','-hide_banner','-i',str(dest),'-map','0:v:0','-vf','freezedetect=n=-45dB:d=0.6,blackdetect=d=0.08:pix_th=0.05','-an','-f','null','-'],capture_output=True,text=True,check=True)
qcpath = OUT / f'{a.anchor_id}-motion-technical-qc.txt'
qcpath.write_text(qc.stderr)
contact = OUT / f'{a.anchor_id}-motion-contact.jpg'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(dest),'-vf','fps=2,scale=480:-1,tile=4x3','-frames:v','1',str(contact)],check=True)
record = {'anchorId':a.anchor_id,'originalPath':str(dest),'sha256':digest(dest),'postUrl':a.post_url,
          'width':video['width'],'height':video['height'],'fps':video['r_frame_rate'],'frames':video.get('nb_frames'),
          'durationSeconds':float(video['duration']),'decodePassed':True,'qcLog':str(qcpath),'contactSheet':str(contact),
          'status':'generated_downloaded_measured_pending_motion_review',
          'frameInspected':False,'watchedAtNormalSpeed':False,'acceptedForFinal':False}
(OUT/f'{a.anchor_id}-motion-record.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
