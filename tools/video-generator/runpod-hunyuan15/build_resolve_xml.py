"""Create FCPXML still-image edit from the sealed review contract."""
import json
import sys
from pathlib import Path
import xml.etree.ElementTree as E
from build_story_cut import lua

base = Path(sys.argv[1])
plan = json.loads((base / 'edit-contract.json').read_text())
(base/'review-plan.lua').write_text('return '+lua(plan))
root = E.Element('fcpxml', version='1.8')
r = E.SubElement(root, 'resources')
E.SubElement(r, 'format', id='r1', name='FFVideoFormat1080p24', frameDuration='1/24s', width='1920', height='1080', colorSpace='1-1-1 (Rec. 709)')
for i, c in enumerate(plan['cuts']):
    E.SubElement(r, 'asset', id=f'v{i}', name=c['anchorId'], src=(base/'anchors'/Path(c['sourceFile']).name).as_uri(), start='0s', duration='0s', hasVideo='1', format='r1')
E.SubElement(r, 'asset', id='song', name='Urvashi canonical song', src=Path(plan['audio']).as_uri(), start='0s', duration=f"{plan['totalFrames']}/24s", hasAudio='1', audioSources='1', audioChannels='2', audioRate='48000')
lib = E.SubElement(root, 'library')
event = E.SubElement(lib, 'event', name='Urvashi story review')
project = E.SubElement(event, 'project', name=plan.get('timelineName','URVASHI STORY CUT v2 - REVIEW CANDIDATE'))
seq = E.SubElement(project, 'sequence', format='r1', duration=f"{plan['totalFrames']}/24s", tcStart='0s', tcFormat='NDF', audioLayout='stereo', audioRate='48k')
spine = E.SubElement(seq, 'spine')
for i, c in enumerate(plan['cuts']):
    item = E.SubElement(spine, 'asset-clip', ref=f'v{i}', name=c['cutId']+' '+c['anchorId'], offset=f"{c['startFrame']}/24s", start='0s', duration=f"{c['durationFrames']}/24s")
    if i == 0:
        E.SubElement(item, 'asset-clip', ref='song', lane='-1', offset='0s', start='0s', duration=f"{plan['totalFrames']}/24s", audioRole='music')
E.indent(root)
E.ElementTree(root).write(base/'story-cut.fcpxml', encoding='utf-8', xml_declaration=True)
print(base/'story-cut.fcpxml')
