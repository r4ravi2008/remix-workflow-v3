"""Prepare private local fonts and a two-second, six-output CLI demo."""
import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'engine'))
from engine import capabilities, canonical, execute, hash_file

FONT_REVISION = '9710da1eacb3be272583c3224dcb70f9da6eadbb'
FONTS = {
    'notosans': 'NotoSans[wdth,wght].ttf',
    'notosanstelugu': 'NotoSansTelugu[wdth,wght].ttf',
    'notosansdevanagari': 'NotoSansDevanagari[wdth,wght].ttf',
    'notosanstamil': 'NotoSansTamil[wdth,wght].ttf',
}


def setup(root):
    for tool in ['ffmpeg', 'ffprobe', 'fc-match', 'fc-cache']:
        if not shutil.which(tool):
            raise ValueError(f'{tool} is required. Install FFmpeg and fontconfig before local setup.')
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    fonts = root / 'fonts'
    fonts.mkdir(exist_ok=True, mode=0o700)
    receipts = []
    for family, filename in FONTS.items():
        base = f'https://raw.githubusercontent.com/google/fonts/{FONT_REVISION}/ofl/{family}/'
        destination = fonts / filename
        for name in [filename, 'OFL.txt']:
            target = destination if name == filename else fonts / (family + '-OFL.txt')
            if not target.exists():
                request = urllib.request.Request(base + urllib.parse.quote(name), headers={'User-Agent': 'release-kit-local-editor'})
                with urllib.request.urlopen(request, timeout=30) as response:
                    content = response.read(8 * 1024 * 1024 + 1)
                if len(content) > 8 * 1024 * 1024:
                    raise ValueError('Font download exceeds its size limit.')
                temporary = target.with_suffix('.download')
                temporary.write_bytes(content)
                temporary.chmod(0o600)
                temporary.replace(target)
        receipts.append({'file': filename, 'sha256': hash_file(destination), 'source': base + urllib.parse.quote(filename)})
    config = ET.Element('fontconfig')
    ET.SubElement(config, 'dir').text = str(fonts)
    ET.SubElement(config, 'cachedir').text = str(root / 'font-cache')
    config_path = root / 'fonts.conf'
    ET.ElementTree(config).write(config_path, encoding='utf-8', xml_declaration=True)
    os.environ['FONTCONFIG_FILE'] = str(config_path)
    execute(['fc-cache', '-f', str(fonts)])
    measured = capabilities()
    if len(measured['fonts']) != 4 or not measured['h264'] or not all(measured['filters'].values()):
        raise ValueError('The local engine does not have its required codecs, filters and shaping fonts.')
    (root / 'setup-receipt.json').write_text(json.dumps({'fontRevision': FONT_REVISION, 'fonts': receipts, 'engine': measured}, indent=2), encoding='utf8')
    demo(root / 'demo')
    return {'prepared': True, 'state': str(root), 'fonts': measured['fonts'], 'gpuRequired': False, 'cloudflareRequired': False}


def demo(root):
    root.mkdir(exist_ok=True, mode=0o700)
    if (root / 'recipe.json').exists():
        return
    audio, visual, mask = root / 'master.wav', root / 'scene.mp4', root / 'mask.png'
    execute(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'sine=frequency=440:sample_rate=48000:duration=2', '-f', 'lavfi', '-i', 'sine=frequency=660:sample_rate=48000:duration=2', '-filter_complex', '[0:a][1:a]amerge=inputs=2[a]', '-map', '[a]', '-c:a', 'pcm_s16le', str(audio)])
    execute(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'testsrc2=size=640x360:rate=24:duration=2', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', str(visual)])
    execute(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'color=black:s=640x360', '-vf', 'drawbox=x=320:y=0:w=320:h=360:color=white:t=fill', '-frames:v', '1', '-update', '1', str(mask)])
    assets = [
        {'id': 'demo-master', 'kind': 'audio', 'sha256': hash_file(audio), 'bytes': audio.stat().st_size, 'width': 0, 'height': 0, 'duration': 2},
        {'id': 'demo-scene', 'kind': 'video', 'sha256': hash_file(visual), 'bytes': visual.stat().st_size, 'width': 640, 'height': 360, 'duration': 2},
        {'id': 'demo-mask', 'kind': 'mask', 'sha256': hash_file(mask), 'bytes': mask.stat().st_size, 'width': 640, 'height': 360, 'duration': 0},
    ]
    compositions = []
    for index, identity in enumerate(['film', 'short-1', 'short-2', 'short-3', 'thumbnail', 'artwork']):
        still = identity in {'thumbnail', 'artwork'}
        width, height = (1920, 1920) if identity == 'artwork' else (1080, 1920) if identity.startswith('short-') else (1920, 1080)
        frames = 1 if still else 48
        clip = {'id': 'scene-1', 'assetId': 'demo-scene', 'at': 0, 'inFrame': 0, 'frames': frames,
                'transform': {'centerX': 0.25 + index * .1, 'centerY': .5, 'zoom': 1},
                'color': {'brightness': 0, 'contrast': 1, 'saturation': 1}, 'fadeIn': 0, 'fadeOut': 0, 'reactive': None}
        if identity == 'film':
            clip['reactive'] = {'maskAssetId': 'demo-mask', 'audioSha256': assets[0]['sha256'], 'points': [{'frame': 0, 'value': 0}, {'frame': 12, 'value': 1}, {'frame': 24, 'value': 0}, {'frame': 48, 'value': 1}]}
        compositions.append({'id': identity, 'width': width, 'height': height, 'frames': frames,
            'rationale': f'Local synthetic {identity} demo; independent framing, Indic captions and masked film reactivity.',
            'audio': None if still else {'assetId': 'demo-master', 'startSeconds': 0}, 'clips': [clip],
            'captions': [{'id': 'lyric-1', 'kind': 'lyric', 'start': 0, 'end': frames, 'text': 'ప్రతి నిమిషం', 'font': 'Noto Sans Telugu', 'size': 64, 'marginBottom': 100}]})
    project = {'schemaVersion': 1, 'releaseId': 'local-demo', 'briefSha256': '0' * 64, 'audioSha256': assets[0]['sha256'], 'language': 'Telugu', 'lyrics': 'ప్రతి నిమిషం', 'fps': 24, 'assets': assets, 'compositions': compositions}
    (root / 'recipe.json').write_text(canonical(project), encoding='utf8')
    for asset in assets:
        (root / (asset['id'] + '.json')).write_text(canonical(asset), encoding='utf8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('state', type=Path)
    args = parser.parse_args()
    print(json.dumps(setup(args.state.resolve())))
