#!/usr/bin/env python3
"""Measure R13 visual response against the canonical 127.011 BPM grid."""
from __future__ import annotations
import json, math, pathlib, re, subprocess
WORKSPACE=pathlib.Path('/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/nuvvantene-istam-deep-house/music-video/rebuild-r10-neon-space')
FILM=WORKSPACE/'renders/r13-final/nuvvantene-r13-telugu-orbital-voyage-full-v2.mp4'
OVERLAY=WORKSPACE/'renders/r13-overlays/r13-space-tunnel-540p-v1.mp4'
RECORD=WORKSPACE/'records/r13-reactivity-v1.json'
BPM=127.01100762066172; FPS=24.0; PERIOD=60.0/BPM; ORIGIN=0.243871569

def series(path):
 p=subprocess.run(['ffmpeg','-v','info','-i',str(path),'-vf','signalstats,metadata=print:file=-','-f','null','-'],capture_output=True,text=True,check=True)
 s=p.stdout+'\n'+p.stderr
 keys=['YAVG','UAVG','VAVG','YDIF','UDIF','VDIF']
 out={k:[float(x) for x in re.findall(rf'signalstats\.{k}=([0-9.]+)',s)] for k in keys}
 if not out['YAVG']: raise RuntimeError('no signalstats for '+str(path))
 return out

def corr(xs,ys):
 n=min(len(xs),len(ys)); xs=xs[:n]; ys=ys[:n]; xm=sum(xs)/n; ym=sum(ys)/n
 num=sum((x-xm)*(y-ym) for x,y in zip(xs,ys)); den=(sum((x-xm)**2 for x in xs)*sum((y-ym)**2 for y in ys))**0.5
 return num/den if den else 0.0

def beat_series(n):
 pulse=[]; cosine=[]; down=[]
 for i in range(n):
  t=i/FPS; phase=2*math.pi*(t-ORIGIN)/PERIOD; c=math.cos(phase)
  cosine.append(c); pulse.append(max(0,c)**4)
  p=(t-ORIGIN+PERIOD)%PERIOD; down.append(math.exp(-p/0.08))
 return cosine,pulse,down

def metrics(d):
 n=len(d['YAVG']); c,p,down=beat_series(n)
 return {'frames_measured':n,'duration_seconds':n/FPS,'yavg_mean':sum(d['YAVG'])/n,'yavg_min':min(d['YAVG']),'yavg_max':max(d['YAVG']),'beat_cosine_correlation':corr(d['YAVG'],c),'beat_pulse_correlation':corr(d['YAVG'],p),'downbeat_pulse_correlation':corr(d['YAVG'],down),'uavg_mean':sum(d['UAVG'])/n,'vavg_mean':sum(d['VAVG'])/n,'ydif_mean':sum(d['YDIF'])/n if d['YDIF'] else None}
film=series(FILM); overlay=series(OVERLAY)
record={'revision':'R13-space-travel-reactive-v1','canonical_audio_sha256':'9769452de248e4c05029f678fe3eac2d0ae0134161e7636356af641379e9396c','beat_grid':{'bpm':BPM,'period_seconds':PERIOD,'origin_seconds':ORIGIN,'fps':FPS},'measurement':{'film':{'path':str(FILM),**metrics(film)},'space_tunnel_overlay':{'path':str(OVERLAY),**metrics(overlay)}},'construction_evidence':{'overlay_features':['RMS','low band 25-180Hz','mid band 180-2200Hz','high band 2200-9500Hz'],'beat_envelope':'80ms downbeat decay at measured beat origin','resolve_nodes':['ImagePlane3D','Camera3D','Merge3D','Renderer3D','FastNoise','Displace','SoftGlow'],'resolve_track':'V11','resolve_composite':'Screen','resolve_opacity':60.0,'anchor_count':95,'anchor_interval_seconds':2.375},'comparison':{'previous_r12_full_film_downbeat_correlation':0.2734821522095027,'r13_full_film_downbeat_correlation':metrics(film)['downbeat_pulse_correlation'],'previous_r12_space_depth_overlay_not_available':True},'review_state':{'measured':True,'frame_inspected':True,'watched_normal_speed':False,'heard_normal_speed':False,'creative_accepted':False}}
RECORD.write_text(json.dumps(record,indent=2)+'\n'); print(json.dumps(record,indent=2))
