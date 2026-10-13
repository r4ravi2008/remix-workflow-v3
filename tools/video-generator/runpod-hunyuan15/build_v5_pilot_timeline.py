"""Prepare a separate Resolve review timeline with the user-approved C007 motion."""
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

root = Path('/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/urvashi/music-video')
production = root / 'motion-production-v5'
source = production / 'C007-v5-pilot_00001_.mp4'
digest = hashlib.sha256(source.read_bytes()).hexdigest()
assert digest == '0bc00f0e5ea311ed02097a4f41ce970dbdd319b3bb7ca7da2906ff5bbd1fce82'
destination = production / 'resolve-pilot'
destination.mkdir(exist_ok=True)
normalized = destination / 'C007-v5-pilot-1080p-prores.mov'
if not normalized.exists():
    subprocess.run(['ffmpeg', '-v', 'error', '-i', str(source), '-map', '0:v:0', '-an',
                    '-vf', 'scale=1920:800:flags=lanczos,crop=1920:790:0:5,pad=1920:1080:0:145:black,setsar=1',
                    '-c:v', 'prores_ks', '-profile:v', '3', '-pix_fmt', 'yuv422p10le',
                    '-r', '24', str(normalized)], check=True)
probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-count_frames', '-show_streams', '-of', 'json', str(normalized)]))
assert len(probe['streams']) == 1
video = probe['streams'][0]
assert (video['width'], video['height'], video['r_frame_rate'], int(video['nb_read_frames'])) == (1920,1080,'24/1',124)
tree = ET.parse(root / 'hyperreal-story-review-v5/story-cut.fcpxml')
resources = tree.getroot().find('resources')
asset = next(a for a in resources.findall('asset') if a.get('id') == 'v6')
asset.set('src', normalized.as_uri())
asset.set('name', 'C007 user-approved H3 pilot')
asset.set('duration', '124/24s')
project = tree.getroot().find('.//project')
project.set('name', 'URVASHI v5.1 - PARTIAL MOTION REVIEW C007')
clips = tree.getroot().findall('.//spine/asset-clip')
assert len(clips) == 49
clip = next(c for c in clips if c.get('name').split()[0] == 'C007')
assert (clip.get('offset'),clip.get('duration'),clip.get('start')) == ('693/24s','97/24s','0s')
assert clip.find('timeMap') is None
clip.set('name', 'C007 S07-I02 H3 MOTION')
target = destination / 'partial-motion-C007.fcpxml'
ET.indent(tree, space='  ')
tree.write(target, encoding='utf-8', xml_declaration=True)
record = {'status':'PREPARED_NOT_YET_IMPORTED', 'timeline':project.get('name'), 'fcpxml':str(target),
          'rawOriginal':str(source), 'rawSHA256':digest, 'normalizedMedia':str(normalized),
          'normalizedSHA256':hashlib.sha256(normalized.read_bytes()).hexdigest(),
          'geometry':'1536x640 scaled without stretch to 1920x800; crop 5px top/bottom; pad 145px top/bottom. Native generation remains 1536x640.',
          'audio':'Generated audio excluded; original canonical song retained unchanged in XML.',
          'motionPlacement':{'cut':'C007','timelineInFrame':693,'timelineOutExclusive':790,'sourceInFrame':0,'sourceOutExclusive':97,'tailFrames':27},
          'remainingStillCuts':48,'finalDelivery':False}
(destination / 'assembly.json').write_text(json.dumps(record,indent=2))
print(json.dumps(record))
