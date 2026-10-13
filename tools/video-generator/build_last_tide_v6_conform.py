"""Build a source-verified, explicitly provisional Resolve conform, not a final edit."""
import hashlib
import json
import subprocess
from fractions import Fraction
from pathlib import Path
from xml.etree import ElementTree as E

from prepare_last_tide_v6 import BASE, OUT


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def probe(path):
    return json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)
    ]))


def time(frames):
    seconds = Fraction(frames) / 24
    return f'{seconds.numerator}/{seconds.denominator}s'


def build():
    plan_path = OUT / 'full-film-plan.json'
    handle_path = OUT / 'transition-handle-candidates.json'
    plan = json.loads(plan_path.read_text())
    handles = json.loads(handle_path.read_text())
    assert handles['planSha256'] == digest(plan_path), 'Stale handle allocation'
    assert plan['timeline']['fps'] == 24
    audio = BASE / 'audio/hello-ammai-progressive-deep-house-selected-master.mp3'
    assert digest(audio) == plan['audioSha256'], 'Canonical song changed'
    ap = probe(audio)
    audio_duration = Fraction(ap['format']['duration'])
    assert abs(float(audio_duration) - 227.6) < .1
    rows = []
    seen = set()
    cursor = 0
    for shot, handle in zip(plan['shots'], handles['shots'], strict=True):
        assert shot['id'] == handle['shotId']
        sid = shot['sourceId']
        assert sid not in seen, 'Repeated source, requires explicit review'
        seen.add(sid)
        if sid.startswith('A'):
            record = json.loads((OUT / f'{sid}-motion-record.json').read_text())
            path = Path(record['originalPath'])
            sha = digest(path)
            assert sha == record['sha256'], 'Motion original changed'
        else:
            path = Path(shot['path'])
            sha = digest(path)
        media = probe(path)
        video = next(s for s in media['streams'] if s['codec_type'] == 'video')
        assert Fraction(video['r_frame_rate']) == 24
        frames = int(video['nb_frames'])
        lo, hi = handle['sourceWindowFrames']
        assert 0 <= lo < hi <= frames
        clean_in, clean_out = handle['cleanRecordFrames']
        assert clean_in == cursor and clean_out > clean_in
        cursor = clean_out
        source_in = Fraction(handle['sourceAtCleanIn'])
        source_out = Fraction(handle['sourceAtCleanOut'])
        speed = Fraction(handle['speedRatio'])
        assert source_out - source_in == (clean_out - clean_in) * speed
        rows.append({
            'shotId': shot['id'], 'sourceId': sid, 'path': str(path), 'sha256': sha,
            'width': video['width'], 'height': video['height'], 'frames': frames,
            'recordFrames': [clean_in, clean_out],
            'sourceCleanFrames': [str(source_in), str(source_out)],
            'sourceWindowFrames': [lo, hi], 'speedRatio': str(speed),
            'speedPercent': round(float(speed) * 100, 3), 'framing': shot['framing'],
            'purpose': shot['purpose'], 'status': 'provisional_not_accepted',
            'pictureFitOnly': True,
        })
    assert cursor == plan['timeline']['totalFrames'] == 5463
    root = E.Element('fcpxml', version='1.8')
    res = E.SubElement(root, 'resources')
    E.SubElement(res, 'format', id='timelineFormat', name='FFVideoFormat1080p24',
                 frameDuration='1/24s', width='1920', height='1080', colorSpace='1-1-1 (Rec. 709)')
    for w, h in sorted({(r['width'], r['height']) for r in rows}):
        E.SubElement(res, 'format', id=f'format{w}x{h}', frameDuration='1/24s',
                     width=str(w), height=str(h), colorSpace='1-1-1 (Rec. 709)')
    for row in rows:
        E.SubElement(res, 'asset', id=row['sourceId'], name=Path(row['path']).stem,
                     src=Path(row['path']).as_uri(), start='0s', duration=time(row['frames']),
                     hasVideo='1', format=f"format{row['width']}x{row['height']}")
    E.SubElement(res, 'asset', id='song', name=audio.stem, src=audio.as_uri(), start='0s',
                 duration=f'{audio_duration.numerator}/{audio_duration.denominator}s',
                 hasAudio='1', audioSources='1', audioChannels='2', audioRate='48000')
    library = E.SubElement(root, 'library')
    event = E.SubElement(library, 'event', name='The Last Tide - provisional conform')
    name = 'THE LAST TIDE - V6 PROVISIONAL CONFORM - NO FINISH'
    project = E.SubElement(event, 'project', name=name)
    seq = E.SubElement(project, 'sequence', format='timelineFormat', duration=time(cursor),
                       tcStart='0s', tcFormat='NDF', audioLayout='stereo', audioRate='48k')
    spine = E.SubElement(seq, 'spine')
    for row in rows:
        start, end = row['recordFrames']
        duration = end - start
        clip = E.SubElement(spine, 'asset-clip', ref=row['sourceId'],
                            name=f"{row['shotId']} {row['sourceId']} - PROVISIONAL",
                            offset=time(start), start='0s', duration=time(duration))
        tm = E.SubElement(clip, 'timeMap', frameSampling='frame-blending')
        E.SubElement(tm, 'timept', time='0s', value=time(row['sourceCleanFrames'][0]), interp='linear')
        E.SubElement(tm, 'timept', time=time(duration), value=time(row['sourceCleanFrames'][1]), interp='linear')
        E.SubElement(clip, 'adjust-conform', type='fit')
        if start == 0:
            E.SubElement(clip, 'asset-clip', ref='song', lane='-1', offset='0s', start='0s',
                         duration=f'{audio_duration.numerator}/{audio_duration.denominator}s', audioRole='music')
    E.indent(root)
    xml_path = OUT / 'full-film-PROVISIONAL-conform.fcpxml'
    E.ElementTree(root).write(xml_path, encoding='utf-8', xml_declaration=True)
    reread = E.parse(xml_path)
    clips = reread.findall('.//spine/asset-clip')
    assert len(clips) == 40
    assert len(reread.findall('.//asset-clip[@ref="song"]')) == 1
    report = {
        'status': 'offline_conform_prepared_not_imported_not_final', 'timelineName': name,
        'xmlPath': str(xml_path), 'xmlSha256': digest(xml_path),
        'planSha256': digest(plan_path), 'handlePlanSha256': digest(handle_path),
        'audioSha256': digest(audio), 'audioDurationSeconds': float(audio_duration),
        'timelineFrames': cursor, 'shotCount': len(rows), 'uniqueSources': len(seen),
        'sourceHashesVerified': True, 'sourceRangesWithinMedia': True,
        'monotonicMappings': True, 'timelineGapFrames': 0, 'clips': rows,
        'unresolved': [
            'Native Resolve import, timeline readback and diagnostic render are required.',
            'All 39 transitions remain planned only; this diagnostic uses clean cuts.',
            'S15/C10 and S17/C11 environmental crops still require native setup and review.',
            'Fit preserves aspect ratio, but mixed active picture ratios still need uniform matte conform.',
            'Retimed cadence, optical flow choice, source endpoint and normal-speed review remain pending.',
            'No final grade or lyric text is applied; separate provisional SRT awaits native import.',
            'The final audio tail and all lyric alignment require listening; technical evidence is not approval.',
        ],
    }
    (OUT / 'full-film-conform-report.json').write_text(json.dumps(report, indent=2) + '\n')
    expected = ','.join('{' + str(r['recordFrames'][0]) + ',' + str(r['recordFrames'][1]) + '}' for r in rows)
    lua = '''-- Provisional diagnostic only. Never switches projects or stops a render.
local r=assert(Resolve(), "Resolve connection unavailable")
local pm=r:GetProjectManager()
local p=assert(pm:GetCurrentProject(), "No current project")
assert(p:GetName()=="THE LAST TIDE - BEAT EDIT V4", "Wrong active project; do not switch automatically")
assert(not p:IsRenderingInProgress(), "A render is running; leave it untouched")
local name=TIMELINE_NAME
local t=nil
for i=1,p:GetTimelineCount() do
  local candidate=p:GetTimelineByIndex(i)
  if candidate:GetName()==name then t=candidate; break end
end
if not t then
  assert(pm:SaveProject(), "Save failed")
  local backup=BACKUP_PATH
  local f=io.open(backup,"rb")
  if f then f:close() else assert(pm:ExportProject(p:GetName(),backup,true), "Backup failed") end
  t=assert(p:GetMediaPool():ImportTimelineFromFile(XML_PATH,{importSourceClips=true}), "Import failed")
end
assert(p:SetCurrentTimeline(t))
assert(t:SetStartTimecode("00:00:00:00"))
local clips=t:GetItemListInTrack("video",1)
assert(#clips==40,"Unexpected clip count; inspect without reimporting")
local origin=t:GetStartFrame()
assert(t:GetEndFrame()-origin==5463,"Unexpected timeline duration")
local expected={EXPECTED_RANGES}
for i,c in ipairs(clips) do
  assert(c:GetStart()-origin==expected[i][1],"Unexpected clip start: "..i)
  assert(c:GetEnd()-origin==expected[i][2],"Unexpected clip end: "..i)
end
local audio=t:GetItemListInTrack("audio",1)
assert(#audio==1,"Unexpected audio count")
assert(pm:SaveProject())
print("PROVISIONAL_CONFORM_IMPORTED_NOT_FINISHED",t:GetName(),#clips,t:GetEndFrame()-origin)
print("NEXT: render diagnostic, verify time maps, framing, then implement planned transitions and lyrics")
'''.replace('TIMELINE_NAME', json.dumps(name)).replace('BACKUP_PATH', json.dumps(str(OUT / 'before-v6-conform.drp'))).replace('XML_PATH', json.dumps(str(xml_path))).replace('EXPECTED_RANGES', expected)
    (OUT / 'import-PROVISIONAL-conform.lua').write_text(lua)
    print(json.dumps({k: report[k] for k in ['status', 'shotCount', 'uniqueSources', 'timelineFrames',
                                             'sourceRangesWithinMedia', 'timelineGapFrames']}, indent=2))


if __name__ == '__main__':
    build()
