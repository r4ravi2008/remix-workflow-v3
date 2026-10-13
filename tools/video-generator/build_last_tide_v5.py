"""Author an editable Resolve direction test from existing, selected motion ranges."""
import json
from pathlib import Path
from xml.etree import ElementTree as E

BASE = Path('/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/hello-ammai-progressive-deep-house/music-video')
OUT = BASE / 'resolve/v5-deadpan'
OUT.mkdir(parents=True, exist_ok=True)
(OUT / 'renders').mkdir(exist_ok=True)
old = json.loads((BASE / 'resolve/resolve-edit-map-v4.json').read_text())
sources = {}
for clip in old['items']:
    if clip.get('style') == 'wide-original':
        sources.setdefault(clip['scene'], clip['path'])

# Source ranges are half open. Camera motion comes from the source; no animated scaling.
# The water insert is an environmental crop, with both performers outside its viewport.
shots = [
    ('C01', 0, 129, 129, 'Empty jetty; a route before anyone occupies it', None),
    ('C02', 20, 123, 129, 'Arjun observes, held at a distance', None),
    ('C11', 0, 103, 129, 'Water and ivory light; presence registered indirectly', 'water'),
    ('C03', 0, 44, 64, 'Tara notices; exit before the broad smile', None),
    ('C04', 28, 87, 86, 'One passing silk gesture; bodies remain contextual', None),
    ('C06', 0, 43, 43, 'Step across the boundary; action insert', None),
    ('C07', 0, 65, 65, 'A single short pursuit burst with open distance', None),
    ('C10', 0, 50, 86, 'The landscape marks her route', 'environment'),
    ('C13', 0, 103, 129, 'Paper boat: memory hinted through an object', None),
]
total = sum(s[3] for s in shots)
root = E.Element('fcpxml', version='1.8')
res = E.SubElement(root, 'resources')
E.SubElement(res, 'format', id='timelineFormat', name='FFVideoFormat1080p24', frameDuration='1/24s', width='1920', height='1080', colorSpace='1-1-1 (Rec. 709)')
E.SubElement(res, 'format', id='sourceFormat', frameDuration='1/24s', width='1920', height='804', colorSpace='1-1-1 (Rec. 709)')
for scene, *_ in shots:
    E.SubElement(res, 'asset', id=scene, name=Path(sources[scene]).stem, src=Path(sources[scene]).as_uri(), start='0s', duration=f'{241 if scene == "C01" else 145}/24s', hasVideo='1', format='sourceFormat')
audio = BASE / 'audio/hello-ammai-progressive-deep-house-selected-master.mp3'
E.SubElement(res, 'asset', id='song', name=audio.stem, src=audio.as_uri(), start='0s', duration='5462/24s', hasAudio='1', audioSources='1', audioChannels='2', audioRate='48000')
lib = E.SubElement(root, 'library')
event = E.SubElement(lib, 'event', name='The Last Tide - direction tests')
name = 'THE LAST TIDE - V5 DEADPAN DIRECTION TEST'
project = E.SubElement(event, 'project', name=name)
seq = E.SubElement(project, 'sequence', format='timelineFormat', duration=f'{total}/24s', tcStart='0s', tcFormat='NDF', audioLayout='stereo', audioRate='48k')
spine = E.SubElement(seq, 'spine')
cursor = 0
items = []
for scene, source_in, source_out, duration, purpose, crop in shots:
    clip = E.SubElement(spine, 'asset-clip', ref=scene, name=scene+' - '+purpose, offset=f'{cursor}/24s', start='0s', duration=f'{duration}/24s')
    tm = E.SubElement(clip, 'timeMap', frameSampling='frame-blending')
    E.SubElement(tm, 'timept', time='0s', value=f'{source_in}/24s', interp='linear')
    E.SubElement(tm, 'timept', time=f'{duration}/24s', value=f'{source_out}/24s', interp='linear')
    if cursor == 0:
        E.SubElement(clip, 'asset-clip', ref='song', lane='-1', offset='0s', start='0s', duration=f'{total}/24s', audioRole='music')
    items.append(dict(scene=scene, sourcePath=sources[scene], sourceIn=source_in, sourceOut=source_out, recordStart=cursor, duration=duration, purpose=purpose, crop=crop))
    cursor += duration
E.indent(root)
E.ElementTree(root).write(OUT/'direction-test.fcpxml', encoding='utf-8', xml_declaration=True)
plan = dict(timeline=name, fps=24, totalFrames=total, durationSeconds=total/24, items=items, status='provisional_direction_test', audioSha256='f93aa25209633151dcd6c9df1f74f571e6f573b9de55e847833c4475b0a375d6', constraints=dict(repeatedSourceWindows=0, animatedZooms=0, reversedPlayback=0, pursuitBursts=1, literalCinema=False), limitations=['Sources contain camera/acting choices that editing cannot replace.', 'Auditory review and creative approval remain pending.'])
(OUT/'direction-test-plan.json').write_text(json.dumps(plan, indent=2)+'\n')

def lua_str(value):
    return json.dumps(str(value), ensure_ascii=False)

lua = f'''local r=Resolve()
local pm=r:GetProjectManager()
local p=assert(pm:GetCurrentProject())
assert(p:GetName()=="THE LAST TIDE - BEAT EDIT V4", "Wrong active project")
assert(not p:IsRenderingInProgress(), "Another render is running")
for i=1,p:GetTimelineCount() do
    local existing=p:GetTimelineByIndex(i)
    if existing:GetName()=={lua_str(name)} then
        assert(p:SetCurrentTimeline(existing))
        print("REUSED",existing:GetName())
        return
    end
end
assert(pm:SaveProject())
local base={lua_str(OUT)}
local backup=io.open(base.."/before-v5.drp","rb")
if backup then backup:close() else
    assert(pm:ExportProject(p:GetName(),base.."/before-v5.drp",true))
end
local t=assert(p:GetMediaPool():ImportTimelineFromFile(base.."/direction-test.fcpxml",{{importSourceClips=true}}))
assert(p:SetCurrentTimeline(t))
assert(t:SetStartTimecode("00:00:00:00"))
local clips=t:GetItemListInTrack("video",1)
assert(#clips=={len(shots)}, "Wrong video count")
assert(t:GetEndFrame()-t:GetStartFrame()=={total}, "Wrong duration")
assert(#t:GetItemListInTrack("audio",1)==1, "Wrong audio count")
assert(pm:SaveProject())
assert(t:SetCurrentTimecode("00:00:07:00"))
print("IMPORTED",t:GetName(),#clips,t:GetEndFrame()-t:GetStartFrame())
dump(clips[1]:GetProperties())
dump(t:GetOutputBlanking())
assert(pm:SaveProject())
'''
(OUT/'import-test.lua').write_text(lua)
print(json.dumps(dict(output=str(OUT),frames=total,seconds=total/24,shots=len(shots)),indent=2))
