"""Build Telugu lyric cards and a Resolve FCPXML with an editable overlay track."""
from __future__ import annotations

import json
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path('/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/urvashi/music-video')
OUT=ROOT/'resolve/motion-v5-finish-v1'
CARDS=OUT/'telugu-lyric-cards'
FPS=24

def run(args:list[str])->None:
    subprocess.run(args,check=True)

def main()->None:
    CARDS.mkdir(exist_ok=True)
    srt=(OUT/'urvashi-telugu-lyrics-candidate.srt').read_text(encoding='utf-8')
    blocks=[b.strip().splitlines() for b in srt.strip().split('\n\n')]
    def parse(tc:str)->int:
        hh,mm,rest=tc.split(':');ss,ms=rest.split(',')
        return round((int(hh)*3600+int(mm)*60+int(ss)+int(ms)/1000)*FPS)
    cues=[]
    for block in blocks:
        start,end=map(parse,block[1].split(' --> '))
        text=' '.join(block[2:])
        assert 0<=start<end<=4482
        cues.append((start,end,text))
    for i,(start,end,text) in enumerate(cues,1):
        card=CARDS/f'lyric-{i:02d}.png'
        if card.exists(): continue
        with tempfile.TemporaryDirectory(prefix='urvashi-lyric-') as temp:
            glyph=Path(temp)/'glyph.png'
            shadow=Path(temp)/'shadow.png'
            run(['pango-view','--no-display','--background=transparent','--foreground=#F7F0E4FF',
                 '--font=Kohinoor Telugu Bold 54','--pixels','--margin=14','--single-par',
                 f'--text={text}',f'--output={glyph}'])
            run(['magick',str(glyph),'-channel','A','-blur','0x7','+channel',
                 '-channel','RGB','-fill','#141B22','-colorize','100','+channel',str(shadow)])
            run(['magick','-size','1920x1080','canvas:transparent',
                 '-fill','#C13442','-draw','polygon 274,977 284,977 267,1028 257,1028',
                 str(shadow),'-gravity','south','-geometry','+0+13','-composite',
                 str(glyph),'-gravity','south','-geometry','+0+18','-composite',str(card)])
    tree=ET.parse(OUT/'urvashi-v5-existing-motion-story-master-candidate.fcpxml')
    project=tree.getroot().find('.//project')
    assert project is not None
    project.set('name','URVASHI V5 STORY FILM - TELUGU LYRIC DESIGN v1')
    resources=tree.getroot().find('./resources')
    assert resources is not None
    spine=tree.getroot().find('.//spine')
    assert spine is not None
    first=spine.find('./asset-clip')
    assert first is not None
    for i,(start,end,text) in enumerate(cues,1):
        ref=f'lyric{i:02d}'
        ET.SubElement(resources,'asset',id=ref,name=f'Urvashi Telugu lyric {i:02d}',
                      src=(CARDS/f'lyric-{i:02d}.png').as_uri(),start='0s',duration='0s',
                      hasVideo='1',format='r1')
        ET.SubElement(first,'asset-clip',ref=ref,lane='1',offset=f'{start}/{FPS}s',
                      start='0s',duration=f'{end-start}/{FPS}s',name=f'LYRIC {i:02d} {text}')
    target=OUT/'urvashi-v5-story-film-telugu-lyric-design-v1.fcpxml'
    ET.indent(tree,space='  ')
    tree.write(target,encoding='utf-8',xml_declaration=True)
    (CARDS/'manifest.json').write_text(json.dumps([
        {'index':i,'startFrame':a,'endFrameExclusive':b,'text':t,'path':str(CARDS/f'lyric-{i:02d}.png')}
        for i,(a,b,t) in enumerate(cues,1)],ensure_ascii=False,indent=2)+'\n')
    print(target,len(cues))

if __name__=='__main__': main()
