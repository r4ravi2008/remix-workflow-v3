#!/usr/bin/env python3
"""Generate a beat-locked 3D-space tunnel overlay for the R13 Resolve revision.

The source is canonical WAV. The output is a black-backed Screen carrier, so Resolve
can composite the tunnel behind the Bharatanatyam silhouette and transliterated lyrics.
"""
from __future__ import annotations
import argparse, math, os, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

FPS=24.0
W,H=960,540
BPM=127.01100762066172
PERIOD=60.0/BPM
ORIGIN=0.243871569

CYAN=(28,205,238)
CRIMSON=(224,40,62)
GOLD=(212,167,60)
WHITE=(212,242,246)


def audio_features(path: str, frames: int):
    with wave.open(path,'rb') as wf:
        sr=wf.getframerate(); ch=wf.getnchannels(); n=wf.getnframes()
        raw=wf.readframes(n)
    x=np.frombuffer(raw,dtype=np.int32).astype(np.float32)
    if ch>1: x=x.reshape(-1,ch).mean(axis=1)
    x/=max(1.0, np.max(np.abs(x)))
    out=np.zeros((frames,4),dtype=np.float32)
    for i in range(frames):
        t=(i+0.5)/FPS
        c=int(t*sr)
        half=int(0.105*sr)
        a=max(0,c-half); b=min(len(x),c+half)
        seg=x[a:b]
        if len(seg)<8: seg=np.pad(seg,(0,8-len(seg)))
        rms=float(np.sqrt(np.mean(seg*seg)+1e-9))
        # Fixed FFT window keeps values comparable across the full song.
        win=seg[:min(len(seg),4096)]
        if len(win)<4096: win=np.pad(win,(0,4096-len(win)))
        win=win*np.hanning(len(win))
        spec=np.abs(np.fft.rfft(win))
        freqs=np.fft.rfftfreq(len(win),1/sr)
        def band(lo,hi):
            m=(freqs>=lo)&(freqs<hi)
            return float(np.mean(spec[m])) if np.any(m) else 0.0
        out[i]=[rms,band(25,180),band(180,2200),band(2200,9500)]
    # robust full-file normalization; retain rests instead of forcing a floor.
    for j in range(4):
        p=np.percentile(out[:,j],[20,95])
        out[:,j]=np.clip((out[:,j]-p[0])/max(1e-6,p[1]-p[0]),0,1)
    return out


def smooth(v, radius=3):
    k=np.ones(radius*2+1,dtype=np.float32)/(radius*2+1)
    return np.convolve(v,k,mode='same')


def make_frame(i, feat, total_frames, prev_points, seed_points):
    t=i/FPS
    rms,low,mid,high=map(float,feat)
    # 24fps beat envelope with 80ms decay, plus a phrase-level four-beat swell.
    phase=(t-ORIGIN)%PERIOD
    beat=math.exp(-phase/0.080)
    beat2=0.5*(1+math.sin((t-ORIGIN)/(PERIOD*4)*2*math.pi-math.pi/2))
    energy=0.18+0.34*rms+0.25*low+0.16*mid+0.12*high
    speed=0.10+0.26*energy+0.22*beat
    tilt=0.11*math.sin(t*0.47)+0.04*mid
    # Draw at 2x logical scale and downsample for cleaner glows.
    scale=2
    im=Image.new('RGB',(W*scale,H*scale),(0,0,0))
    d=ImageDraw.Draw(im,'RGB')
    cx,cy=W*0.5,H*0.52
    # edge-vignette keeps the centre behind the character comparatively clear.
    def colour(c,a):
        return tuple(int(v*max(0,min(1,a))) for v in c)
    # Perspective rays and tunnel rings. The radial field is intentionally sparse.
    ring_count=9
    zoff=(t*speed)%1.0
    for k in range(ring_count):
        z=((k/ring_count)-zoff)%1.0
        r=20+z*650
        pulse=1.0+0.13*beat*(1.0-z)
        rx=r*pulse; ry=r*(0.45+0.11*math.sin(t*0.63+z*4))
        # protect the centre; rings still flash around the silhouette.
        alpha=(0.10+0.36*beat+0.12*energy)*(0.35+0.65*z)
        col=CYAN if k%3 else GOLD
        pts=[]
        for q in range(25):
            a=2*math.pi*q/24+tilt+0.07*math.sin(t*0.8+z*3)
            x=cx+math.cos(a)*rx
            y=cy+math.sin(a)*ry
            pts.append((int(x*scale),int(y*scale)))
        d.line(pts,fill=colour(col,alpha),width=max(1,int((1.0+2.4*beat)*scale/2)),joint='curve')
    # Rays give the travelling-through-space depth cue.
    for q in range(22):
        a=2*math.pi*q/22+tilt*0.7
        r0=38+18*beat; r1=580+160*energy
        x0=cx+math.cos(a)*r0; y0=cy+math.sin(a)*r0*0.55
        x1=cx+math.cos(a)*r1; y1=cy+math.sin(a)*r1*0.55
        alpha=0.07+0.16*energy+0.30*beat*(q%4==0)
        col=GOLD if q%7==0 else CYAN
        d.line((int(x0*scale),int(y0*scale),int(x1*scale),int(y1*scale)),fill=colour(col,alpha),width=max(1,int((1+high*2)*scale/2)))
    # Stable seeded stars move towards the lens, so motion is coherent across frames.
    for j,(sx,sy,sz,sc) in enumerate(seed_points):
        z=(sz-(t*speed*(0.7+0.5*sc)))%1.0
        rad=4+z*670
        x=cx+sx*rad+math.sin(t*0.31+j)*5*mid
        y=cy+sy*rad*0.56+math.cos(t*0.23+j)*4*high
        if x<-30 or x>W+30 or y<-30 or y>H+30: continue
        alpha=0.16+0.55*energy+0.85*beat*(0.2+0.8*sc)
        col=CRIMSON if j%13==0 and beat>0.15 else (GOLD if j%7==0 else CYAN)
        rr=(1.0+3.0*z)*(0.6+1.4*high)
        d.ellipse((int((x-rr)*scale),int((y-rr)*scale),int((x+rr)*scale),int((y+rr)*scale)),fill=colour(col,alpha))
    # The beat portal stays outside the subject's chest/face area.
    if beat>0.02:
        for q in range(3):
            r=76+beat*92+q*16
            box=((cx-r)*scale,(cy-r*0.55)*scale,(cx+r)*scale,(cy+r*0.55)*scale)
            d.ellipse(box,outline=colour(CRIMSON if q==0 else CYAN,0.25*beat*(1-q*0.2)+0.04),width=max(1,int((1+beat*3)*scale/2)))
    # A subtle topological grid enters only on stronger low/mid energy.
    if energy>0.46:
        for q in range(5):
            y=H*(0.15+q*0.16)+math.sin(t*0.5+q)*8*mid
            d.line((0,int(y*scale),W*scale,int((y+20*math.sin(t*0.7+q))*scale)),fill=colour(GOLD,0.05+0.10*low),width=1*scale)
    im=im.resize((W,H),Image.Resampling.LANCZOS)
    # Add a short glow pass only on loud/high-frequency frames.
    if high>0.55 or beat>0.72:
        glow=im.filter(ImageFilter.GaussianBlur(radius=2.4+1.8*high))
        im=Image.blend(im,glow,0.16+0.14*high+0.10*beat)
    return im


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--audio',required=True)
    ap.add_argument('--out',required=True)
    ap.add_argument('--frames',type=int,default=None)
    ap.add_argument('--duration',type=float,default=None)
    ap.add_argument('--png',default=None)
    a=ap.parse_args()
    if a.frames is None:
        a.frames=int(round((a.duration or 221.625)*FPS))
    feats=audio_features(a.audio,a.frames)
    # Smooth only the continuous energy bands. Beat envelope remains crisp.
    for j in range(4): feats[:,j]=smooth(feats[:,j],2)
    rng=np.random.default_rng(1307)
    seed=[]
    for _ in range(110):
        ang=rng.uniform(0,2*math.pi); rad=rng.uniform(0.12,1.0); z=rng.uniform(0,1); sc=rng.uniform(0.1,1.0)
        seed.append((math.cos(ang)*rad,math.sin(ang)*rad,z,sc))
    os.makedirs(os.path.dirname(a.out),exist_ok=True)
    cmd=['ffmpeg','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','medium','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',a.out]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    for i in range(a.frames):
        frame=make_frame(i,feats[i],a.frames,None,seed)
        if a.png and i==int(round(0.5*FPS)):
            frame.save(a.png)
        proc.stdin.write(frame.tobytes())
    proc.stdin.close(); rc=proc.wait()
    if rc: raise SystemExit(rc)
    print({'output':a.out,'frames':a.frames,'fps':FPS,'duration':a.frames/FPS,'bpm':BPM,'beat_period':PERIOD,'origin':ORIGIN,'features':'rms,low,mid,high'})

if __name__=='__main__': main()
