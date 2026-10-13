"""Fresh signal measurements; candidate lyric identity is not auditory proof."""
import hashlib
import json
import subprocess
from pathlib import Path
import numpy as np

root=Path('/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/urvashi/music-video')
out=root/'hyperreal-story-review-v3'
out.mkdir(exist_ok=True)
master=root/'audio/urvashi-suno-master.mp3'
assert hashlib.sha256(master.read_bytes()).hexdigest()=='55134cca7e18f7cfb487bb0eca0bde43d9a4d238f18494054c537d1371f1f5aa'
stemroot=root/'analysis/urvashi-current/stems-v1'
def read(path):
    return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-vn','-ac','1','-ar','16000','-f','f32le','-']),dtype='<f4').copy()
signals={name:read(stemroot/(name+'.wav')) for name in ['vocal-reference','percussion-proxy','bass-proxy','harmonic-proxy']}
signals['full-mix']=read(master)
env={name:np.sqrt((x[:len(x)//160*160].reshape(-1,160)**2).mean(1)+1e-15) for name,x in signals.items()}
v=np.convolve(env['vocal-reference'],np.ones(5)/5,mode='same')
windows=[('post-chorus',44,50.8,48.72),('verse-return',101.5,108,106.0),('outro-return',133.5,140,138.1)]
result={'audioSha256':hashlib.sha256(master.read_bytes()).hexdigest(),'method':'10ms RMS envelopes; 50ms smoothing; local peaks with 180ms minimum separation. Lyrics identity comes from canonical text + existing CTC candidate; not listening verified. Proxies are filters, not isolated instrument stems.','windows':[]}
for name,start,end,preme in windows:
    lo,hi=round(start*100),round(end*100)
    local=v[lo:hi]; threshold=float(np.max(local)*0.12)
    peak_indices=[i for i in range(lo+2,hi-2) if v[i]>=max(v[i-2:i+3]) and v[i]>threshold]
    picked=[]
    for i in sorted(peak_indices,key=lambda i:v[i],reverse=True):
        if all(abs(i-j)>=18 for j in picked): picked.append(i)
    runs=[]; active=local>threshold
    for i in range(1,len(active)-4):
        if active[i-1] and not active[i] and active[i:i+4].sum()>0: active[i:i+4]=True
    edges=np.diff(np.r_[False,active,False].astype(int)); starts=np.where(edges==1)[0]; ends=np.where(edges==-1)[0]
    runs=[{'start':round(start+a/100,2),'end':round(start+b/100,2)} for a,b in zip(starts,ends) if b-a>=8]
    row={'name':name,'range':[start,end],'candidatePremeStart':preme,'vocalRuns':runs,'vocalPeaks':[{'time':i/100,'relativeAmplitude':round(float(v[i]/max(local)),3)} for i in sorted(picked)],'layers':{}}
    for layer,e in env.items():
        row['layers'][layer]=[{'second':t,'rms':round(float(e[int(t*100):int((t+.25)*100)].mean()),5)} for t in np.arange(start,end,.25).tolist()]
    result['windows'].append(row)
    if not (out/(name+'-full-mix.wav')).exists():
        subprocess.run(['ffmpeg','-v','error','-n','-ss',str(start),'-i',str(master),'-t',str(end-start),'-vn','-c:a','pcm_s16le',str(out/(name+'-full-mix.wav'))],check=True)
mix=signals['full-mix']
frames=np.lib.stride_tricks.sliding_window_view(mix,1024)[::160]
spectrum=np.abs(np.fft.rfft(frames*np.hanning(1024),axis=1))[:,16:193]
features=np.log1p(spectrum)
features=(features-features.mean(axis=0))/(features.std(axis=0)+1e-6)
template=features[13612:13702]
template=template-template.mean()
matches=[]
for a,b in [(44,48),(102,105),(134,137)]:
    candidates=[]
    for i in range(a*100,b*100):
        x=features[i:i+len(template)]; x=x-x.mean()
        corr=float((x*template).sum()/(np.linalg.norm(x)*np.linalg.norm(template)+1e-9))
        candidates.append((corr,i/100))
    best=sorted(candidates,reverse=True)[:1][0]
    matches.append({'searchRange':[a,b],'templateStart':136.12,'matchedStart':best[1],'spectralCorrelation':round(best[0],4)})
result['repeatedPhraseSpectralMatches']=matches
section_edges=[0,13.78,33.08,46.75,68.12,82.5,111.16,122.5,136.14,157.38,186.75]
result['sectionEnergyDbFS']=[{'rangeSeconds':[a,b], 'layers':{name:round(float(20*np.log10(np.sqrt(np.mean(e[round(a*100):round(b*100)]**2))+1e-12)),2) for name,e in env.items()}} for a,b in zip(section_edges,section_edges[1:])]
result['layerChangeCandidates']=[]
for name in ['percussion-proxy','bass-proxy','harmonic-proxy']:
    e=env[name]
    curve=np.array([np.sqrt(np.mean(e[i:i+100]**2)) for i in range(0,len(e)-100,25)])
    db=20*np.log10(curve+1e-9); changes=np.abs(db[8:]-db[:-8])
    picked=[]
    for i in np.argsort(changes)[::-1]:
        t=(int(i)+4)*.25
        if 5<t<180 and all(abs(t-p['time'])>4 for p in picked):
            picked.append({'time':t,'twoSecondDifferenceDb':round(float(db[i+8]-db[i]),2)})
        if len(picked)==6: break
    result['layerChangeCandidates'].append({'layer':name,'candidates':sorted(picked,key=lambda p:p['time'])})
(out/'vocal-cue-analysis.json').write_text(json.dumps(result,indent=2))
print(json.dumps([{k:v for k,v in row.items() if k!='layers'} for row in result['windows']],indent=2))
print(json.dumps(matches,indent=2))
