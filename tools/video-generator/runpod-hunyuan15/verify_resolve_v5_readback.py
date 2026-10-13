"""Compare Resolve's exported provisional still timeline to the sealed v5 contract."""
import hashlib
import json
import xml.etree.ElementTree as ET
from fractions import Fraction
from pathlib import Path
from urllib.parse import unquote, urlparse

base = Path('/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/urvashi/music-video/hyperreal-story-review-v5')
plan = json.loads((base / 'edit-contract.json').read_text())
export = base / 'resolve-v5-readback.fcpxml'
root = ET.parse(export).getroot()
resources = {item.attrib['id']: item for item in root.find('resources')}
sequence = root.find('./library/event/project/sequence')
fmt = resources[sequence.attrib['format']]
assert fmt.attrib['width'] == '1920' and fmt.attrib['height'] == '1080'
assert Fraction(fmt.attrib['frameDuration'][:-1]) == Fraction(1, 24)
frames = lambda value: Fraction(value[:-1]) * 24
assert frames(sequence.attrib['duration']) == 4482
clips = sequence.findall('./spine/ref-clip')
assert len(clips) == len(plan['cuts']) == 49
records = []
for actual, expected in zip(clips, plan['cuts']):
    assert actual.attrib['name'].split()[0] == expected['cutId']
    assert frames(actual.attrib['offset']) == expected['startFrame']
    assert frames(actual.attrib['duration']) == expected['durationFrames']
    media = resources[actual.attrib['ref']]
    video = media.find('./sequence/spine/video')
    asset = resources[video.attrib['ref']]
    path = Path(unquote(urlparse(asset.attrib['src']).path))
    assert path == base / expected['sourceFile']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected['sha256']
    records.append({'cutId': expected['cutId'], 'startFrame': expected['startFrame'],
                    'durationFrames': expected['durationFrames'], 'source': str(path),
                    'sha256': expected['sha256']})
audio = [item for item in sequence.iter('asset-clip') if resources[item.attrib['ref']].get('hasAudio') == '1']
assert len(audio) == 1 and frames(audio[0].attrib['duration']) == 4482
audio_path = Path(unquote(urlparse(resources[audio[0].attrib['ref']].attrib['src']).path))
assert str(audio_path) == plan['audio']
assert hashlib.sha256(audio_path.read_bytes()).hexdigest() == plan['audioSha256']
result = {'status': 'RESOLVE_STILL_IMPORT_EXACT_READBACK_PASS_NOT_MOTION_DELIVERY',
          'timeline': root.find('./library/event/project').attrib['name'],
          'exportSha256': hashlib.sha256(export.read_bytes()).hexdigest(),
          'frames': 4482, 'fps': 24, 'cuts': records,
          'audioSha256': plan['audioSha256'], 'messagesAndLyrics': 'NOT_PRESENT_IN_THIS_PROVISIONAL_IMPORT'}
(base / 'resolve-v5-verification.json').write_text(json.dumps(result, indent=2))
print(json.dumps({'status': result['status'], 'cuts': len(records), 'frames': 4482}))
