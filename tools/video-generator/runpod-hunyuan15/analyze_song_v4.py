"""Full-length signal review, with no claim of auditory verification."""
import json, hashlib, subprocess
from pathlib import Path
import numpy as np

root=Path('/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/urvashi/music-video')
out=root/'hyperreal-story-review-v4'; out.mkdir(exist_ok=True)
master=root/'audio/urvashi-suno-master.mp3'
digest=hashlib.sha256(master.read_bytes()).hexdigest()
assert digest=='55134cca7e18f7cfb487bb0eca0bde43d9a4d238f18494054c537d1371f1f5aa'
x=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(master),'-ac','1','-ar','16000','-f','f32le','-']),dtype='<f4')
n=2048; hop=320
windows=np.lib.stride_tricks.sliding_window_view(x,n)[::hop]
spec=np.abs(np.fft.rfft(windows*np.hanning(n),axis=1))**2
freq=np.fft.rfftfreq(n,1/16000)
bands={name:np.sqrt(spec[:,(freq>=a)&(freq<b)].mean(axis=1)) for name,a,b in [('bass',35,180),('body',180,1000),('presence',1000,4000),('air',4000,8000)]}
rms=np.sqrt((windows**2).mean(axis=1)+1e-12)
flux=np.maximum(np.diff(np.log1p(spec),axis=0),0).mean(axis=1)
beats=json.loads((root/'analysis/urvashi-current/audio-map-measured.json').read_text())
assert beats['sha256']==digest
markers=json.loads((root/'resolve/lyric-vocalization-marker-map-v1.json').read_text())['markers']
lyrics=[m for m in markers if not m['id'].endswith('-end')]
for m in lyrics:
    if m['endTime']>160: m['endTime']=157.38; m['correction']='CTC tail through silence rejected; provisional vocal ending 157.38s'
sections=[(0,13.75,'instrumental opening'),(13.75,32.92,'intro vocal motif and instrumental runway'),(32.92,46.75,'chorus'),(46.75,68.12,'post chorus'),(68.12,82.5,'instrumental connection'),(82.5,103.875,'verse'),(103.875,111.16,'verse vocal refrain'),(111.16,122.5,'lyric build'),(122.5,136.125,'final chorus'),(136.125,157.38,'outro vocal'),(157.38,180.25,'instrumental release'),(180.25,186.75,'ending')]
rows=[]
for a,b,label in sections:
    lo,hi=int(a/.02),min(len(rms),int(b/.02))
    rows.append({'range':[a,b],'label':label,'fullMixDbFS':round(float(20*np.log10(np.sqrt(np.mean(rms[lo:hi]**2)))),2),'bandRelativeLevels':{k:round(float(20*np.log10(np.sqrt(np.mean(v[lo:hi]**2))+1e-10)),2) for k,v in bands.items()},'meanSpectralFlux':round(float(flux[lo:min(hi,len(flux))].mean()),5)})
changes=[]
for name,v in {'fullMix':rms,**bands}.items():
    scores=[]
    for t in np.arange(3,183,.25):
        i=int(t/.02); pre=np.sqrt(np.mean(v[i-100:i]**2)); post=np.sqrt(np.mean(v[i:i+100]**2))
        scores.append((abs(20*np.log10((post+1e-9)/(pre+1e-9))),float(t),float(20*np.log10((post+1e-9)/(pre+1e-9)))))
    chosen=[]
    for _,t,d in sorted(scores,reverse=True):
        if all(abs(t-p['time'])>4 for p in chosen): chosen.append({'time':t,'changeDb':round(d,2),'kind':'rise candidate' if d>0 else 'dip candidate'})
        if len(chosen)==12: break
    changes.append({'band':name,'events':sorted(chosen,key=lambda p:p['time'])})
quarter=[]
for t in np.arange(0,186.5,.25):
    i=int(t/.02); j=min(len(rms),i+12)
    quarter.append({'t':float(t),'dbFS':round(float(20*np.log10(np.sqrt(np.mean(rms[i:j]**2))+1e-10)),2)})
result={'audio':str(master),'sha256':digest,'rangeAnalyzed':[0,186.75],'heard':'PENDING_UNAVAILABLE','method':'Fresh 128ms Hann STFT, 20ms hop, broadband RMS and four spectral bands across entire recording; 2s before/after contrast. Bands are not isolated instruments. Energy rises are not automatically drops. CTC phrase alignment remains provisional.','sections':rows,'layerChanges':changes,'quarterSecondEnergy':quarter,'lyricPhrases':lyrics,'measuredBeatTimes':beats['beats'],'estimatedBpm':beats['estimated_bpm'],'beatCaveat':'Estimated pulse, not verified bar/downbeat labels; no rigid BPM grid used','vocalBurstEvidence':json.loads((root/'hyperreal-story-review-v3/vocal-cue-analysis.json').read_text())['repeatedPhraseSpectralMatches']}
(out/'whole-song-analysis.json').write_text(json.dumps(result,indent=2,ensure_ascii=False))
print(json.dumps({'sections':rows,'changes':changes},indent=2))
