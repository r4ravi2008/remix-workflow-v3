import copy
import json
import shutil
from pathlib import Path

from engine import canonical, execute, hash_file, render, verify_output


ROOT = Path('/tmp/editor-canary')
(ROOT / 'assets').mkdir(parents=True, exist_ok=True)
audio = ROOT / 'assets' / 'master'
visual = ROOT / 'assets' / 'scene'
mask = ROOT / 'assets' / 'mask'
execute(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'sine=frequency=440:sample_rate=48000:duration=2', '-f', 'lavfi', '-i', 'sine=frequency=660:sample_rate=48000:duration=2', '-filter_complex', '[0:a][1:a]amerge=inputs=2[a]', '-map', '[a]', '-c:a', 'pcm_s16le', '-f', 'wav', str(audio)])
execute(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'testsrc2=size=640x360:rate=24:duration=2', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-f', 'mp4', str(visual)])
execute(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'color=black:s=640x360', '-vf', 'drawbox=x=320:y=0:w=320:h=360:color=white:t=fill', '-frames:v', '1', '-c:v', 'png', '-f', 'image2', str(mask)])
assets = [
    {'id': 'master', 'kind': 'audio', 'sha256': hash_file(audio), 'bytes': audio.stat().st_size, 'width': 0, 'height': 0, 'duration': 2},
    {'id': 'scene', 'kind': 'video', 'sha256': hash_file(visual), 'bytes': visual.stat().st_size, 'width': 640, 'height': 360, 'duration': 2},
    {'id': 'mask', 'kind': 'mask', 'sha256': hash_file(mask), 'bytes': mask.stat().st_size, 'width': 640, 'height': 360, 'duration': 0},
]
compositions = []
for index, identity in enumerate(['film', 'short-1', 'short-2', 'short-3', 'thumbnail', 'artwork']):
    image = identity in {'thumbnail', 'artwork'}
    width, height = (1920, 1920) if identity == 'artwork' else (1080, 1920) if identity.startswith('short-') else (1920, 1080)
    compositions.append({'id': identity, 'width': width, 'height': height, 'frames': 1 if image else 48, 'rationale': f'Synthetic canary composition {index}; this is not Pal Pal footage.',
                         'audio': None if image else {'assetId': 'master', 'startSeconds': 0},
                         'clips': [{'id': 'scene-1', 'assetId': 'scene', 'at': 0, 'inFrame': 0, 'frames': 1 if image else 48,
                                    'transform': {'centerX': 0.2 + index * 0.1, 'centerY': 0.5, 'zoom': 1}, 'color': {'brightness': 0, 'contrast': 1, 'saturation': 1}, 'fadeIn': 0, 'fadeOut': 0,
                                    'reactive': {'maskAssetId': 'mask', 'audioSha256': assets[0]['sha256'], 'points': [{'frame': 0, 'value': 0}, {'frame': 12, 'value': 1}, {'frame': 24, 'value': 0}, {'frame': 48, 'value': 1}]} if identity == 'film' else None}],
                         'captions': [{'id': 'lyric-1', 'kind': 'lyric', 'start': 0, 'end': 1 if image else 48, 'text': 'ప్రతి నిమిషం', 'font': 'Noto Sans Telugu', 'size': 64, 'marginBottom': 100}]})
project = {'schemaVersion': 1, 'releaseId': 'synthetic-canary', 'briefSha256': 'a' * 64, 'audioSha256': assets[0]['sha256'], 'language': 'Telugu', 'lyrics': 'ప్రతి నిమిషం', 'fps': 24, 'assets': assets, 'compositions': compositions}
(ROOT / 'project.json').write_text(canonical(project), encoding='utf8')
receipt = render(project, ROOT, lambda args: execute(args), lambda progress: print(json.dumps(progress), flush=True))
failures = []
corrupt = ROOT / 'corrupt.mp4'
content = (ROOT / 'outputs' / 'film.mp4').read_bytes()
corrupt.write_bytes(content[:len(content) // 2])
try:
    verify_output(corrupt, project, compositions[0], ROOT)
    raise AssertionError('Corrupt output passed QC.')
except ValueError:
    failures.append('corrupt-output-rejected')
silent = ROOT / 'silent.mp4'
execute(['ffmpeg', '-v', 'error', '-y', '-i', str(ROOT / 'outputs' / 'film.mp4'), '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-map', '0:v', '-map', '1:a', '-t', '2', '-c:v', 'copy', '-c:a', 'aac', str(silent)])
try:
    verify_output(silent, project, compositions[0], ROOT)
    raise AssertionError('Silent replacement passed source-audio QC.')
except ValueError:
    failures.append('silent-audio-rejected')
wrong = copy.deepcopy(compositions[0])
wrong['width'] = 1080
try:
    verify_output(ROOT / 'outputs' / 'film.mp4', project, wrong, ROOT)
    raise AssertionError('Wrong canvas passed QC.')
except ValueError:
    failures.append('wrong-canvas-rejected')
shortened = ROOT / 'shortened-film.mp4'
execute(['ffmpeg', '-v', 'error', '-y', '-i', str(ROOT / 'outputs' / 'film.mp4'), '-t', str(47 / 24), '-c:v', 'libx264', '-c:a', 'aac', str(shortened)])
short_comp = copy.deepcopy(compositions[0])
short_comp['frames'] = 47
try:
    verify_output(shortened, project, short_comp, ROOT)
    raise AssertionError('A frame-short film passed full-master QC.')
except ValueError as error:
    if 'complete canonical audio master' not in str(error):
        raise
    failures.append('frame-short-master-rejected')
receipt.update({'scope': 'local-linux-amd64-container-synthetic-canary', 'cloudVerified': False, 'palPalKitCompleted': False, 'negativeChecks': failures})
(ROOT / 'receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf8')
execute(['ffmpeg', '-v', 'error', '-y', '-ss', '0.75', '-i', str(ROOT / 'outputs' / 'film.mp4'), '-frames:v', '1', str(ROOT / 'film-frame.png')])
print(json.dumps({'ok': True, 'outputs': len(receipt['outputs']), 'negativeChecks': failures}), flush=True)
