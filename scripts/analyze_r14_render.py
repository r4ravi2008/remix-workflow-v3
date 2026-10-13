"""Decode and sample the exact Resolve R14 export; no acceptance inference."""
from pathlib import Path
import hashlib,json,subprocess,argparse
import numpy as np
from PIL import Image,ImageDraw

P=Path('/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/nuvvantene-istam-deep-house/music-video/rebuild-r10-neon-space')
parser=argparse.ArgumentParser();parser.add_argument('--attempt',default='a01');args=parser.parse_args()
attempt=args.attempt
render=P/f'renders/r14-native/nuvvantene-r14-native-ribbons-full-{attempt}.mp4'
plan=json.loads((P/f'records/r14-native/full-timeline-plan-{attempt}.json').read_text())
frames=set(plan['review_anchors'])
for s in plan['shots']:
    a,b=s['recordStart'],s['recordEnd'];frames.update([a,min(a+10,b-1),(a+b-1)//2,max(a,b-11),b-1])
for cue in plan['lyric_events']:
    a,b=cue['start'],cue['end'];frames.update([a,min(a+10,b-1),(a+b-1)//2,max(a,b-9),b-1])
frames=sorted(frames)
out=P/f'analysis/r14-native/full-{attempt}-frames';out.mkdir(exist_ok=True)
select='+'.join(f'eq(n\\,{i})' for i in frames)
subprocess.run(['/opt/homebrew/bin/ffmpeg','-v','error','-i',str(render),'-vf','select='+select,'-fps_mode','vfr','-y',str(out/'sample-%05d.png')],check=True)
for k,frame in enumerate(frames,1):(out/f'sample-{k:05}.png').rename(out/f'frame-{frame:05}.png')
for batch in range(6):
    rows=plan['shots'][batch*6:(batch+1)*6]
    sheet=Image.new('RGB',(1536,len(rows)*320))
    for row,s in enumerate(rows):
        a,b=s['recordStart'],s['recordEnd']
        for col,frame in enumerate([a,(a+b-1)//2,b-1]):
            im=Image.open(out/f'frame-{frame:05}.png');im.thumbnail((512,288))
            sheet.paste(im,(col*512,row*320))
            ImageDraw.Draw(sheet).text((col*512+6,row*320+292),f"{s['id']} / {frame} / {frame/24:.2f}s",fill='white')
    sheet.save(P/f'analysis/r14-native/full-{attempt}-shot-sheet-{batch+1}.png')
for batch in range(4):
    rows=plan['lyric_events'][batch*6:(batch+1)*6]
    sheet=Image.new('RGB',(1536,max(1,len(rows))*320))
    for row,cue in enumerate(rows):
        a,b=cue['start'],cue['end']
        for col,frame in enumerate([min(a+10,b-1),(a+b-1)//2,max(a,b-9)]):
            im=Image.open(out/f'frame-{frame:05}.png');im.thumbnail((512,288))
            sheet.paste(im,(col*512,row*320))
            ImageDraw.Draw(sheet).text((col*512+6,row*320+292),f"{cue['id']} / {frame}",fill='white')
    sheet.save(P/f'analysis/r14-native/full-{attempt}-lyric-sheet-{batch+1}.png')
probe=json.loads(subprocess.run(['/opt/homebrew/bin/ffprobe','-v','error','-show_streams','-show_format','-of','json',str(render)],capture_output=True,text=True,check=True).stdout)
decode=subprocess.run(['/opt/homebrew/bin/ffmpeg','-v','error','-i',str(render),'-f','null','-'],capture_output=True,text=True)
assert decode.returncode==0,decode.stderr
video=next(s for s in probe['streams'] if s['codec_type']=='video')
assert (video['width'],video['height'],video['r_frame_rate'],int(video['nb_frames']))==(1920,1080,'24/1',5319)
record={'render':str(render),'sha256':hashlib.file_digest(render.open('rb'),'sha256').hexdigest(),'probe':probe,'full_decode_exit':decode.returncode,'decode_errors':decode.stderr,'sampled_frames':frames,'sampling_is_not_normal_speed_review':True,'frame_inspection_status':'pending model inspection of saved sheets','watched':False,'heard':False,'creative_acceptance':False}
raw=subprocess.run(['/opt/homebrew/bin/ffmpeg','-v','error','-i',str(render),'-vf','scale=96:54','-pix_fmt','gray','-f','rawvideo','-'],capture_output=True,check=True).stdout
pixels=np.frombuffer(raw,np.uint8).reshape(5319,54,96)
maxima=pixels.max(axis=(1,2));means=pixels.mean(axis=(1,2))
near_black=np.flatnonzero(maxima<=2).tolist()
unexpected=[f for f in near_black if not (f<48 or f>=5254)]
changes=np.mean(np.abs(np.diff(pixels.astype(np.int16),axis=0)),axis=(1,2))
scan={'method':'All 5319 decoded frames downsampled to 96x54 grayscale; maximum <=2 classifies near-black. This is technical screening, not perceptual acceptance.','near_black_frames':near_black,'near_black_outside_authored_opening_48_and_ending_64_fades':unexpected,'mean_luma_range':[float(means.min()),float(means.max())],'consecutive_identical_thumbnail_pairs':np.flatnonzero(changes==0).tolist(),'normal_speed_watched':False,'heard':False}
(P/f'records/r14-native/full-frame-scan-{attempt}.json').write_text(json.dumps(scan,indent=2)+'\n')
record['frame_scan']=str(P/f'records/r14-native/full-frame-scan-{attempt}.json')
(P/f'records/r14-native/full-render-technical-{attempt}.json').write_text(json.dumps(record,indent=2)+'\n')
print({'video_frames':video['nb_frames'],'sampled_frames':len(frames),'duration':video['duration'],'size':render.stat().st_size,'sha256':record['sha256']})
