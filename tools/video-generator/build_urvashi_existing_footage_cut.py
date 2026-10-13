"""Conform the existing Urvashi v5 motion to the locked song/story cut.

Two storyboard placements without dedicated motion are represented by explicit
returning motifs: C004 for C039 and C001 for C041. This is an editable Resolve
interchange, not a rendered or creatively approved master.
"""
from __future__ import annotations

import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path('/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/urvashi/music-video')
OUT = ROOT / 'resolve/motion-v5-finish-v1'
FPS = 24

def digest(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()

def time(frame: int) -> str:
    return f'{frame}/{FPS}s'

def main() -> None:
    plan = json.loads((OUT/'assembly-plan.json').read_text())
    assert plan['totalFrames'] == 4482 and plan['fps'] == FPS
    assert digest(Path(plan['audio'])) == plan['audioSha256']
    placements = plan['placements']
    assert len(placements) == 49
    tree = ET.parse(ROOT/'hyperreal-story-review-v5/story-cut.fcpxml')
    project = tree.getroot().find('.//project')
    assert project is not None
    project.set('name','URVASHI V5 EXISTING MOTION - STORY BEAT MASTER CANDIDATE')
    resources = {a.get('id'): a for a in tree.getroot().findall('./resources/asset')}
    rows = tree.getroot().findall('.//spine/asset-clip')
    assert len(rows) == 49
    treatments = {'C039': {'source':'C004','in':10,'out':124,'transitionIn':0,
                           'baked':'C039-returning-portrait-retimed-v1.mov','frames':132,
                           'purpose':'returning autonomy portrait; privacy choice'},
                  'C041': {'source':'C001','in':14,'out':158,'transitionIn':2,
                           'baked':'C041-returning-city-retimed-v1.mov','frames':156,
                           'purpose':'city bookend after chosen closeness'}}
    audit=[]
    for row, place in zip(rows,placements,strict=True):
        cid=place['cutId']
        assert row.get('name').split()[0]==cid
        asset=resources[row.get('ref')]
        if cid in treatments:
            mapping=treatments[cid]
            sid=mapping['source']
            source_in,source_out=0,mapping['frames']
            decision=mapping['purpose']
        elif cid=='C027':
            sid=place['selectedAssetId']
            source_in,source_out=0,96
            decision='subtle editorial push over near-static source opening'
        else:
            sid=place['selectedAssetId']
            source_in=place['sourceStartFrame']
            source_out=place['sourceEndFrameExclusive']
            decision='storyboard source'
        media=plan['assets'][sid]
        target=(OUT/'media'/treatments[cid]['baked'] if cid in treatments else
                OUT/'media'/'C027-editorial-push-v1.mov' if cid=='C027' else
                Path(media['normalized']))
        assert target.exists()
        sha=digest(target)
        if cid not in treatments and cid!='C027':
            assert sha==media['normalizedReceipt']['normalizedSha256']
            assert source_out<=media['normalizedReceipt']['frames']
        duration=place['timelineEndFrameExclusive']-place['timelineStartFrame']
        assert duration>0
        if cid in treatments or cid=='C027':
            assert source_out==duration
        asset.set('src',target.as_uri())
        asset.set('name',cid+' returning motion' if cid in treatments else
                  cid+' editorial push' if cid=='C027' else sid+' v5 motion')
        asset.set('duration',time(duration if cid in treatments or cid=='C027' else media['normalizedReceipt']['frames']))
        row.set('name',cid+' '+sid+' MOTION')
        row.set('start',time(source_in))
        assert row.get('offset')==time(place['timelineStartFrame'])
        assert row.get('duration')==time(duration)
        if source_out-source_in!=duration:
            mapping=ET.SubElement(row,'timeMap',frameSampling='frame-blending')
            ET.SubElement(mapping,'timept',time='0s',value=time(source_in),interp='linear')
            ET.SubElement(mapping,'timept',time=time(duration),value=time(source_out),interp='linear')
        audit.append({'cutId':cid,'assetId':sid,'timeline':[place['timelineStartFrame'],place['timelineEndFrameExclusive']],
                      'source':[source_in,source_out],'decision':decision,'media':str(target),'sha256':sha})
    assert [a['timeline'][0] for a in audit[1:]]==[a['timeline'][1] for a in audit[:-1]]
    assert audit[-1]['timeline'][1]==4482
    target=OUT/'urvashi-v5-existing-motion-story-master-candidate.fcpxml'
    ET.indent(tree,space='  ')
    tree.write(target,encoding='utf-8',xml_declaration=True)
    lyrics=json.loads((ROOT/'analysis/urvashi-current/lyrics-timestamps-candidate.json').read_text())['lyrics']
    def clean(s:str)->str:
        return re.sub(r'(?i)take it easy','టేక్ ఇట్ ఈజీ',s).replace('...','…')
    def srt_time(frame:int)->str:
        ms=round(frame*1000/FPS)
        h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
        return f'{h:02}:{m:02}:{s:02},{ms:03}'
    cues=[]
    # The CTC candidate attaches its final word to the end of the file, but
    # the separated vocal falls silent at 157.38 s. Keep the instrumental
    # outro clean until a listening review establishes a later vocal.
    vocal_outro_end_frame = round(157.38 * FPS)
    for item in lyrics:
        start=max(0,round(item['start_time']*FPS))
        end=min(4482,max(start+1,round(item['end_time']*FPS)))
        if item is lyrics[-1] and end > vocal_outro_end_frame:
            end = vocal_outro_end_frame
        cues.append({'startFrame':start,'endFrameExclusive':end,'text':clean(item['text']),'section':item['section']})
    srt='\n'.join(f"{i}\n{srt_time(c['startFrame'])} --> {srt_time(c['endFrameExclusive'])}\n{c['text']}\n" for i,c in enumerate(cues,1))
    (OUT/'urvashi-telugu-lyrics-candidate.srt').write_text(srt,encoding='utf-8')
    report={'status':'READY_FOR_RESOLVE_IMPORT_REVIEW_CANDIDATE','timelineFrames':4482,'timelineFps':24,
            'sourceVideoCount':len(plan['assets']),'storyCutCount':49,'gapFrames':0,
            'audioSha256':plan['audioSha256'],'fcpxml':str(target),'fcpxmlSha256':digest(target),
            'lyricSrt':str(OUT/'urvashi-telugu-lyrics-candidate.srt'),'lyricCues':len(cues),
            'returningMotifs':treatments,'placements':audit,'rendered':False,'normalSpeedReview':'PENDING'}
    (OUT/'existing-footage-conform-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['status','storyCutCount','sourceVideoCount','gapFrames','lyricCues','fcpxml']},ensure_ascii=False))

if __name__=='__main__': main()
