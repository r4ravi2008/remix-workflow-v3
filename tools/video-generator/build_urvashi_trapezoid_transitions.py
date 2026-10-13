"""Make short alpha transition plates for the Resolve Urvashi V5 edit.

Each plate reveals the incoming clip's unused source frames before its clean
storyboard cut. The full film is assembled and rendered in Resolve.
"""
from __future__ import annotations

import json
import math
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path('/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/urvashi/music-video')
OUT=ROOT/'resolve/motion-v5-finish-v1'
PLATES=OUT/'trapezoid-transition-plates'
FPS=24
W,H=1920,1080
TOP,BOTTOM=145,935

def run(args:list[str])->None: subprocess.run(args,check=True)
def polygon(points:list[tuple[float,float]])->str:
    return ' '.join(f'{round(x)},{round(y)}' for x,y in points)

def design(family:str,p:float)->tuple[list[list[tuple[float,float]]],list[tuple[tuple[float,float],tuple[float,float]]]]:
    dy=math.tan(math.radians(14))*(BOTTOM-TOP)/2
    if family in ('crimson_diagonal','broad_threshold'):
        lead=-250+p*(W+500)
        if family=='broad_threshold': lead=-380+p*(W+760)
        return [[(-400,TOP),(lead+dy,TOP),(lead-dy,BOTTOM),(-400,BOTTOM)]], [((lead+dy,TOP),(lead-dy,BOTTOM))]
    if family=='parallel_trapezoid':
        edge=-150+p*(W/2+180)
        left=[(-200,TOP),(edge+dy,TOP),(edge-dy,BOTTOM),(-200,BOTTOM)]
        right=[(W+200,TOP),(W-edge+dy,TOP),(W-edge-dy,BOTTOM),(W+200,BOTTOM)]
        return [left,right],[((edge+dy,TOP),(edge-dy,BOTTOM)),((W-edge+dy,TOP),(W-edge-dy,BOTTOM))]
    if family=='architectural_shutter':
        shapes=[];lines=[]
        for base in (0,640,1280):
            edge=base-100+p*760
            shapes.append([(base,TOP),(edge+dy/3,TOP),(edge-dy/3,BOTTOM),(base,BOTTOM)])
            lines.append(((edge+dy/3,TOP),(edge-dy/3,BOTTOM)))
        return shapes,lines
    if family=='portrait_slit':
        half=p*1100
        a=W/2-half;b=W/2+half
        return [[(a-dy/2,TOP),(b+dy/2,TOP),(b-dy/2,BOTTOM),(a+dy/2,BOTTOM)]], [((a-dy/2,TOP),(a+dy/2,BOTTOM)),((b+dy/2,TOP),(b-dy/2,BOTTOM))]
    if family=='reflection_split':
        half=p*1100
        left=[(W/2-half,TOP),(W/2,TOP),(W/2,BOTTOM),(W/2-half,BOTTOM)]
        right=[(W/2,TOP),(W/2+half,TOP),(W/2+half,BOTTOM),(W/2,BOTTOM)]
        return [left,right],[((W/2-half,TOP),(W/2-half,BOTTOM)),((W/2+half,TOP),(W/2+half,BOTTOM))]
    if family=='crossed_trapezoid':
        edge=-160+p*(W/2+220)
        left=[(-200,TOP),(edge+dy,TOP),(edge-dy,BOTTOM),(-200,BOTTOM)]
        right=[(W+200,TOP),(W-edge-dy,TOP),(W-edge+dy,BOTTOM),(W+200,BOTTOM)]
        return [left,right],[((edge+dy,TOP),(edge-dy,BOTTOM)),((W-edge-dy,TOP),(W-edge+dy,BOTTOM))]
    raise ValueError(family)

def make_plate(source:Path,source_start:int,length:int,family:str,target:Path)->None:
    with tempfile.TemporaryDirectory(prefix='urvashi-trapezoid-') as tmp:
        d=Path(tmp)
        run(['ffmpeg','-v','error','-y','-i',str(source),'-vf',
             f'trim=start_frame={source_start}:end_frame={source_start+length},setpts=PTS-STARTPTS',
             '-frames:v',str(length),str(d/'src-%03d.png')])
        assert len(list(d.glob('src-*.png')))==length
        for k in range(length):
            p=(k+1)/length
            shapes,lines=design(family,p)
            body=''.join(f'<polygon points="{polygon(q)}" fill="white" />' for q in shapes)
            svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"><rect width="100%" height="100%" fill="black"/>{body}</svg>'
            mask=d/f'mask-{k+1:03d}.svg';mask.write_text(svg)
            cmd=['magick',str(d/f'src-{k+1:03d}.png'),str(mask),'-alpha','off',
                 '-compose','CopyOpacity','-composite']
            if k<length-1:
                for (x1,y1),(x2,y2) in lines:
                    if max(x1,x2)<-10 or min(x1,x2)>W+10: continue
                    cmd+=['-stroke','#C13442','-strokewidth','3','-draw',
                          f'line {round(x1)},{round(y1)} {round(x2)},{round(y2)}']
            cmd.append(str(d/f'out-{k+1:03d}.png'))
            run(cmd)
        run(['ffmpeg','-v','error','-y','-framerate',str(FPS),'-i',str(d/'out-%03d.png'),
             '-frames:v',str(length),'-c:v','qtrle','-pix_fmt','argb',str(target)])

def main()->None:
    PLATES.mkdir(exist_ok=True)
    plan=json.loads((OUT/'assembly-plan.json').read_text())
    tree=ET.parse(OUT/'urvashi-v5-story-film-telugu-lyric-design-v1.fcpxml')
    project=tree.getroot().find('.//project')
    assert project is not None
    project.set('name','URVASHI V5 STORY FILM - BEAT TRAPEZOID + TELUGU v3')
    assets={a.get('id'):a for a in tree.getroot().findall('./resources/asset')}
    resources=tree.getroot().find('./resources')
    spine=tree.getroot().find('.//spine')
    assert resources is not None and spine is not None
    first=spine.find('./asset-clip'); assert first is not None
    cuts={c.get('name').split()[0]:c for c in spine.findall('./asset-clip')}
    manifest=[]
    for i,event in enumerate(plan['transitions'],1):
        incoming=cuts[event['incoming']]
        asset=assets[incoming.get('ref')]
        # Resolve's FCPXML URL is percent-encoded; use urlsplit/unquote.
        from urllib.parse import unquote,urlsplit
        source=Path(unquote(urlsplit(asset.get('src')).path))
        length=event['durationFrames']
        start=int(incoming.get('start').split('/')[0])-length
        if event['incoming'] in ('C027','C039','C041'):
            motif={'C027':('C027',0),'C039':('C004',0),'C041':('C001',2)}[event['incoming']]
            source=Path(plan['assets'][motif[0]]['normalized'])
            start=motif[1]
        assert start>=0,(event['incoming'],start)
        target=PLATES/f"T{i:02d}-{event['family']}-{event['incoming']}.mov"
        if not target.exists(): make_plate(source,start,length,event['family'],target)
        ref=f'transition{i:02d}'
        ET.SubElement(resources,'asset',id=ref,name=f"T{i:02d} {event['family']}",
                      src=target.as_uri(),start='0s',duration=f'{length}/{FPS}s',hasVideo='1',format='r1')
        ET.SubElement(first,'asset-clip',ref=ref,lane='2',
                      offset=f"{event['startFrame']}/{FPS}s",start='0s',duration=f'{length}/{FPS}s',
                      name=f"T{i:02d} {event['family']} {event['outgoing']} to {event['incoming']}")
        manifest.append({'id':i,'family':event['family'],'outgoing':event['outgoing'],'incoming':event['incoming'],
                         'timeline':[event['startFrame'],event['endFrameExclusive']],
                         'source':[start,start+length],'plate':str(target)})
    target=OUT/'urvashi-v5-story-film-beat-trapezoid-telugu-v3.fcpxml'
    ET.indent(tree,space='  ')
    tree.write(target,encoding='utf-8',xml_declaration=True)
    (PLATES/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(target,len(manifest))

if __name__=='__main__': main()
