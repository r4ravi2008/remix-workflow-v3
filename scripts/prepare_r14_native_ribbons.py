from pathlib import Path
import hashlib
import json
import math
import time
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

P = Path('/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/nuvvantene-istam-deep-house/music-video/rebuild-r10-neon-space')
source = P / 'resolve/R05-canonical.wav'
with wave.open(str(source)) as wav:
    assert (wav.getsampwidth(), wav.getnchannels(), wav.getframerate()) == (3, 2, 48000)
    raw = wav.readframes(wav.getnframes())
    frame_count = wav.getnframes()
packed = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3).astype(np.int32)
values = packed[:, 0] | (packed[:, 1] << 8) | (packed[:, 2] << 16)
values = np.where(values & 0x800000, values - 0x1000000, values)
samples = values.reshape(-1, 2).astype(np.float64) / 8388608.0
assert len(samples) == frame_count == 10638000
assert hashlib.sha256(source.read_bytes()).hexdigest() == '9769452de248e4c05029f678fe3eac2d0ae0134161e7636356af641379e9396c'
fps = 24
rms = np.sqrt(np.mean(samples.reshape(5319, 2000, 2) ** 2, axis=(1, 2)))
level = np.clip((rms - np.quantile(rms, .12)) / (np.quantile(rms, .95) - np.quantile(rms, .12)), 0, 1)
smoothed = np.zeros(len(level))
state = 0.0
for n, value in enumerate(level):
    coefficient = math.exp(-1 / (fps * (.10 if value > state else .40)))
    state = coefficient * state + (1 - coefficient) * value
    smoothed[n] = state
start, end = 614, 948
beat_period = .4724
origin = .243871569
beats = [origin + beat_period * k for k in range(500) if start / fps <= origin + beat_period * k < end / fps]
accents = [round(t * fps) - start for t in beats if round((t - origin) / beat_period) % 8 == 0]
record = {
    'revision': 'R14-native-ribbons-a01',
    'canonical_audio': str(source),
    'sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'decode': {'sample_bytes': 3, 'signed_bits': 24, 'sample_rate': 48000, 'channels': 2, 'sample_frames': len(samples), 'duration': len(samples)/48000, 'peak': float(np.max(np.abs(samples)))},
    'proof_source_frames': [start, end],
    'proof_frames': end - start,
    'emission': [round(.62 + .18 * float(v), 6) for v in smoothed[start:end]],
    'selected_accents': accents,
    'estimated_grid': {'bpm': 60 / beat_period, 'origin_seconds': origin, 'listening_verified': False, 'maximum_frame_rounding_ms': 1000 / (2 * fps)},
    'camera': {'forward_only': True, 'formula_z': '8-0.014*time-0.000004*time*time', 'position_integrated': True},
    'geometry': {'width_animated': False, 'radius': .010, 'cyan_paths': 3, 'crimson_traces': 1},
    'review': {'measured': True, 'frame_inspected': False, 'watched': False, 'heard': False, 'creative_acceptance': False}
}
(P/'analysis/r14-native/audio-controls-a01.json').write_text(json.dumps(record, indent=2)+'\n')
polygons = {
    'S01': [(.302,.337),(.332,.300),(.358,.319),(.367,.372),(.379,.391),(.405,.323),(.424,.241),(.410,.231),(.390,.332),(.355,.390),(.326,.403),(.280,.469),(.231,.512),(.196,.529),(.200,.551),(.269,.517),(.311,.468),(.312,.519),(.277,.569),(.256,.645),(.268,.729),(.284,.768),(.279,.791),(.308,.799),(.326,.774),(.305,.733),(.342,.696),(.366,.726),(.377,.774),(.400,.792),(.414,.778),(.397,.738),(.410,.694),(.419,.649),(.393,.594),(.361,.527),(.363,.456),(.381,.410),(.367,.359)],
    'S03': [(.0,.57),(.70,.57),(.70,.81),(.0,.81)],
    'S04': [(.0,.700),(.112,.712),(.195,.591),(.258,.495),(.299,.408),(.298,.311),(.306,.258),(.334,.325),(.371,.300),(.365,.280),(.335,.293),(.360,.247),(.351,.239),(.317,.284),(.284,.275),(.273,.368),(.248,.420),(.171,.548),(.094,.624),(.0,.650)]
}
for name, points in polygons.items():
    matte = Image.new('L', (1920,1080), 0)
    ImageDraw.Draw(matte).polygon([(round(x*1920),round(y*1080)) for x,y in points],fill=255)
    matte = matte.filter(ImageFilter.MaxFilter(21)).filter(ImageFilter.GaussianBlur(2))
    matte.save(P/f'analysis/r14-native/{name}-subject-matte-a01.png')
reservation = Path('/tmp/remix-resolve-reservation.json')
claim = {'owner_thread':'01a0ff3f-8968-7922-a88b-74ed982185f8','project':'NUVVANTENE - R10 - ONE ORBIT','scope':'R14 native 3D diagnostic','reserved_epoch':time.time(),'status':'active'}
if reservation.exists():
    prior=json.loads(reservation.read_text())
    assert prior.get('status') != 'active' or prior.get('owner_thread') == claim['owner_thread'], prior
reservation.write_text(json.dumps(claim,indent=2)+'\n')
(P/'records/r14-native/resource-reservation.json').write_text(json.dumps(claim,indent=2)+'\n')
print(json.dumps({k:v for k,v in record.items() if k != 'emission'}))
