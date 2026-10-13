import array
import hashlib
import importlib.util
import json
import math
import os
import re
import subprocess
from pathlib import Path


VERSION = 'release-kit-engine/0.1.0'
IDS = {'film', 'short-1', 'short-2', 'short-3', 'thumbnail', 'artwork'}
FONTS = {'Noto Sans Telugu', 'Noto Sans Devanagari', 'Noto Sans Tamil', 'Noto Sans'}
spec = importlib.util.spec_from_file_location('editor_visual_diagnostics', Path(__file__).with_name('visual_diagnostics.py'))
visual = importlib.util.module_from_spec(spec)
spec.loader.exec_module(visual)


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def hash_file(path):
    before = path.stat()
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    after = path.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise ValueError('Media changed while hashing.')
    return digest.hexdigest()


def execute(args, timeout=900):
    result = subprocess.run(args, stdin=subprocess.DEVNULL, capture_output=True, timeout=timeout, check=False)
    if result.returncode:
        raise ValueError('Media tool failed: ' + result.stderr.decode(errors='replace')[-2000:])
    return result


def probe(path):
    return json.loads(execute(['ffprobe', '-v', 'error', '-count_frames', '-show_streams', '-show_format', '-of', 'json', str(path)]).stdout)


def decoded_audio_duration(path):
    pcm = execute([
        'ffmpeg', '-v', 'error', '-xerror', '-nostdin',
        '-protocol_whitelist', 'file,pipe', '-format_whitelist',
        'wav,mp3,aac,flac,ogg,mov,matroska,webm,aiff,asf',
        '-i', str(path), '-map', '0:a:0', '-vn', '-ac', '1', '-ar', '16000',
        '-t', '900.25', '-f', 's16le', '-',
    ], timeout=120).stdout
    if len(pcm) % 2:
        raise ValueError('Decoded audio contains an incomplete PCM sample.')
    duration = len(pcm) / 2 / 16000
    if not 0 < duration <= 900:
        raise ValueError('Decoded audio duration is outside the release contract.')
    return duration


def capabilities():
    filters = execute(['ffmpeg', '-hide_banner', '-filters']).stdout.decode()
    encoders = execute(['ffmpeg', '-hide_banner', '-encoders']).stdout.decode()
    fonts = [font for font in sorted(FONTS) if font in execute(['fc-match', '-f', '%{family}', font]).stdout.decode().split(',')]
    return {'version': VERSION, 'ffmpeg': execute(['ffmpeg', '-version']).stdout.decode().splitlines()[0],
            'filters': {name: name in filters for name in ['ass', 'eq', 'maskedmerge', 'sendcmd', 'scale', 'crop', 'fade']},
            'h264': 'libx264' in encoders, 'fonts': fonts, 'gpuRequired': False,
            'features': ['cuts', 'source-trims', 'portrait-framing', 'fades', 'sdr-color', 'native-captions', 'canonical-audio', 'masked-reactivity', 'mp4', 'jpeg', 'decode-qc', 'audio-correlation', 'frame-diagnostics', 'review-previews'],
            'unsupported': ['arbitrary-graphs', 'arbitrary-commands', 'optical-flow', 'tracked-masks', 'layered-transitions', 'lut', 'resolve-project-import']}


def bounded_number(value, minimum, maximum):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not minimum <= value <= maximum:
        raise ValueError('Recipe contains an out-of-range number.')
    return value


def validate_recipe(project):
    if project['schemaVersion'] != 1 or project['fps'] != 24 or len(project['compositions']) > 6 or len(project['assets']) > 600:
        raise ValueError('Unsupported project version, rate or size.')
    for asset in project['assets']:
        if not re.fullmatch(r'[a-zA-Z0-9_-]{1,80}', asset['id']) or not re.fullmatch(r'[a-f0-9]{64}', asset['sha256']):
            raise ValueError('Unsafe asset identity.')
        bounded_number(asset['bytes'], 1, 2147483648)
    for comp in project['compositions']:
        if comp['id'] not in IDS or len(comp['clips']) > 500 or len(comp['captions']) > 1000:
            raise ValueError('Unsupported composition.')
        bounded_number(comp['frames'], 1, 21600)
        for field in ['width', 'height']:
            bounded_number(comp[field], 16, 1920)
        for clip in comp['clips']:
            if not re.fullmatch(r'[a-zA-Z0-9_-]{1,80}', clip['id']):
                raise ValueError('Unsafe clip identity.')
            for field in ['at', 'inFrame', 'fadeIn', 'fadeOut']:
                bounded_number(clip[field], 0, 21600)
            bounded_number(clip['frames'], 1, 21600)
            bounded_number(clip['transform']['zoom'], 1, 4)
            for field in ['centerX', 'centerY']:
                bounded_number(clip['transform'][field], 0, 1)
            bounded_number(clip['color']['brightness'], -0.2, 0.2)
            bounded_number(clip['color']['contrast'], 0.5, 2)
            bounded_number(clip['color']['saturation'], 0, 2)
            if clip['reactive']:
                if clip['reactive']['audioSha256'] != project['audioSha256'] or len(clip['reactive']['points']) > 21601:
                    raise ValueError('Invalid reactive envelope.')
                for point in clip['reactive']['points']:
                    bounded_number(point['frame'], 0, 21600)
                    bounded_number(point['value'], 0, 1)
        for cue in comp['captions']:
            if cue['font'] not in FONTS or len(cue['text']) > 1000:
                raise ValueError('Unsupported caption.')
            bounded_number(cue['size'], 16, 160)
            bounded_number(cue['marginBottom'], 0, 600)
            bounded_number(cue['start'], 0, 21600)
            bounded_number(cue['end'], 1, 21600)


def inspect_sources(project, root):
    measurements = {}
    for asset in project['assets']:
        path = root / 'assets' / asset['id']
        if not path.is_file() or path.stat().st_size != asset['bytes'] or hash_file(path) != asset['sha256']:
            raise ValueError('Source bytes do not match the immutable asset: ' + asset['id'])
        media = probe(path)
        stream = next((stream for stream in media['streams'] if stream['codec_type'] == ('audio' if asset['kind'] == 'audio' else 'video')), None)
        if not stream:
            raise ValueError('Source stream is missing: ' + asset['id'])
        if asset['kind'] != 'audio' and (stream['width'], stream['height']) != (asset['width'], asset['height']):
            raise ValueError('Source dimensions differ from the project.')
        if asset['kind'] == 'video' and (stream.get('color_transfer') in {'smpte2084', 'arib-std-b67'} or stream.get('color_primaries') == 'bt2020'):
            raise ValueError('HDR sources require an explicit color conform; SDR relabelling is disabled.')
        duration = decoded_audio_duration(path) if asset['kind'] == 'audio' else float(media['format'].get('duration', stream.get('duration', 0)))
        if asset['kind'] in {'audio', 'video'} and abs(duration - asset['duration']) > 1 / 24:
            raise ValueError('Source duration differs from the project.')
        measurements[asset['id']] = {'sha256': asset['sha256'], 'bytes': asset['bytes'], 'width': stream.get('width', 0), 'height': stream.get('height', 0), 'duration': duration}
    return measurements


def time_ass(frame):
    centiseconds = round(frame / 24 * 100)
    return f'{centiseconds // 360000}:{centiseconds // 6000 % 60:02d}:{centiseconds // 100 % 60:02d}.{centiseconds % 100:02d}'


def captions_ass(comp, destination):
    lines = [f'[Script Info]\nScriptType: v4.00+\nPlayResX: {comp["width"]}\nPlayResY: {comp["height"]}\nWrapStyle: 0',
             '[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding']
    for index, cue in enumerate(comp['captions']):
        lines.append(f'Style: cue{index},{cue["font"]},{cue["size"]},&H00FFFFFF,&H00FFFFFF,&H00101010,&H80000000,0,0,0,0,100,100,0,0,1,2,1,2,40,40,{cue["marginBottom"]},1')
    lines.append('[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text')
    for index, cue in enumerate(comp['captions']):
        if any(char in cue['text'] for char in ['\\', '{', '}']):
            raise ValueError('ASS control characters are unsupported in caption text.')
        text = cue['text'].replace('\r', '').replace('\n', r'\N')
        lines.append(f'Dialogue: 0,{time_ass(cue["start"])},{time_ass(cue["end"])},cue{index},,0,0,0,,{text}')
    destination.write_text('\n'.join(lines), encoding='utf8')


def envelope_value(points, frame):
    if frame <= points[0]['frame']:
        return points[0]['value']
    for left, right in zip(points, points[1:]):
        if left['frame'] <= frame <= right['frame']:
            weight = (frame - left['frame']) / (right['frame'] - left['frame'])
            return left['value'] + (right['value'] - left['value']) * weight
    return points[-1]['value']


def render_clip(project, comp, clip, root, run):
    asset = next(asset for asset in project['assets'] if asset['id'] == clip['assetId'])
    source = root / 'assets' / asset['id']
    args = ['ffmpeg', '-hide_banner', '-y', '-v', 'error', '-threads', '2']
    if asset['kind'] == 'image':
        args += ['-loop', '1']
    else:
        args += ['-ss', str(clip['inFrame'] / 24)]
    args += ['-i', str(source)]
    color = clip['color']
    base = f'fps=24,trim=end_frame={clip["frames"]},setpts=PTS-STARTPTS,eq=brightness={color["brightness"]}:contrast={color["contrast"]}:saturation={color["saturation"]},format=yuv444p'
    filters = []
    if clip['reactive']:
        reactive = clip['reactive']
        mask = next(asset for asset in project['assets'] if asset['id'] == reactive['maskAssetId'])
        args += ['-loop', '1', '-i', str(root / 'assets' / mask['id'])]
        commands = root / f'{comp["id"]}-{clip["id"]}-pulse.cmd'
        offset = round((comp['audio']['startSeconds'] if comp['audio'] else 0) * 24) + clip['at']
        commands.write_text('\n'.join(f'{frame / 24:.8f} eq@pulse brightness {0.10 * envelope_value(reactive["points"], offset + frame):.8f};' for frame in range(clip['frames'])), encoding='ascii')
        filters += [f'[0:v]{base},split=2[original][effect]', f'[effect]sendcmd=f={commands},eq@pulse=brightness=0[lit]', '[1:v]format=gray[mask]', '[original][lit][mask]maskedmerge[visual]']
    else:
        filters += [f'[0:v]{base}[visual]']
    transform = clip['transform']
    width = math.ceil(comp['width'] * transform['zoom'] / 2) * 2
    height = math.ceil(comp['height'] * transform['zoom'] / 2) * 2
    tail = f'scale={width}:{height}:force_original_aspect_ratio=increase,crop={comp["width"]}:{comp["height"]}:(iw-ow)*{transform["centerX"]}:(ih-oh)*{transform["centerY"]},setsar=1'
    if clip['fadeIn']:
        tail += f',fade=t=in:st=0:d={clip["fadeIn"] / 24}'
    if clip['fadeOut']:
        tail += f',fade=t=out:st={(clip["frames"] - clip["fadeOut"]) / 24}:d={clip["fadeOut"] / 24}'
    filters += [f'[visual]{tail},format=yuv420p[out]']
    recipe = root / f'{comp["id"]}-{clip["id"]}.filters'
    recipe.write_text(';\n'.join(filters), encoding='ascii')
    destination = root / f'{comp["id"]}-{clip["id"]}.mp4'
    args += ['-filter_complex_threads', '1', '-filter_complex_script', str(recipe), '-map', '[out]', '-frames:v', str(clip['frames']), '-an', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', str(destination)]
    run(args)
    if int(next(stream for stream in probe(destination)['streams'] if stream['codec_type'] == 'video').get('nb_read_frames', 0)) != clip['frames']:
        raise ValueError('Clip did not produce exact frame coverage; implicit looping is disabled.')
    return destination


def pcm(path, start, duration):
    data = execute(['ffmpeg', '-v', 'error', '-ss', str(start), '-i', str(path), '-t', str(duration), '-vn', '-ac', '2', '-ar', '4000', '-f', 'f32le', '-'], timeout=300).stdout
    result = array.array('f')
    result.frombytes(data)
    return result


def audio_compare(path, source, start, duration):
    original = pcm(source, start, duration)
    encoded = pcm(path, 0, duration)
    count = min(len(original), len(encoded)) // 2
    if count < max(10, duration * 4000 - 400):
        raise ValueError('Decoded audio is shorter than its source range.')
    values = []
    for channel in [0, 1]:
        left = original[channel:count * 2:2]
        right = encoded[channel:count * 2:2]
        xy = sum(a * b for a, b in zip(left, right))
        xx = sum(a * a for a in left)
        yy = sum(b * b for b in right)
        values.append(xy / math.sqrt(xx * yy) if xx * yy > 1e-12 else (1.0 if xx + yy < 1e-12 else 0.0))
    return {'channelCosine': values, 'threshold': 0.99, 'passed': min(values) >= 0.99, 'sampleRate': 4000, 'sourceStartSeconds': start, 'sourceDurationSeconds': duration}


def verify_output(path, project, comp, root):
    before = path.stat()
    measurement = probe(path)
    video = next(stream for stream in measurement['streams'] if stream['codec_type'] == 'video')
    image = comp['id'] in {'thumbnail', 'artwork'}
    if (video['width'], video['height']) != (comp['width'], comp['height']):
        raise ValueError('Output dimensions differ from the composition.')
    frames = int(video.get('nb_read_frames', 0))
    if frames != comp['frames']:
        raise ValueError('Output frame count differs from the composition.')
    if video['codec_name'] != ('mjpeg' if image else 'h264'):
        raise ValueError('Output codec does not match the preset.')
    execute(['ffmpeg', '-v', 'error', '-xerror', '-i', str(path), '-f', 'null', '-'])
    receipt = {'id': comp['id'], 'width': video['width'], 'height': video['height'], 'frames': frames, 'duration': 0 if image else frames / 24, 'fps': 0 if image else 24,
               'codec': video['codec_name'], 'pixelFormat': video.get('pix_fmt'), 'sha256': hash_file(path), 'bytes': path.stat().st_size, 'completeDecode': True,
               'motionReviewed': False, 'heard': False, 'creativelyAccepted': False, 'audio': None}
    if not image:
        num, den = video['avg_frame_rate'].split('/')
        if abs(float(num) / float(den) - 24) > 0.001:
            raise ValueError('Output frame rate does not match the preset.')
        audio = next((stream for stream in measurement['streams'] if stream['codec_type'] == 'audio'), None)
        if not audio or audio['channels'] != 2 or int(audio['sample_rate']) != 48000 or audio['codec_name'] != 'aac':
            raise ValueError('Output must include stereo 48 kHz AAC audio.')
        source = root / 'assets' / comp['audio']['assetId']
        if hash_file(source) != project['audioSha256']:
            raise ValueError('Verification source differs from the canonical audio checksum.')
        source_duration = decoded_audio_duration(source)
        if comp['id'] == 'film' and comp['frames'] / 24 + 0.000001 < source_duration:
            raise ValueError('Film ends before the complete canonical audio master.')
        duration = min(comp['frames'] / 24, source_duration - comp['audio']['startSeconds'])
        comparison = audio_compare(path, source, comp['audio']['startSeconds'], duration)
        if not comparison['passed'] or abs(float(audio.get('duration', 0)) - duration) > 2 / 24:
            raise ValueError('Encoded audio does not match the canonical source range.')
        levels = execute(['ffmpeg', '-hide_banner', '-i', str(path), '-vn', '-af', 'ebur128=peak=true', '-f', 'null', '-']).stderr.decode(errors='replace')
        integrated = re.findall(r'I:\s+(-?[\d.]+) LUFS', levels)
        peak = re.findall(r'Peak:\s+(-?[\d.]+) dBFS', levels)
        receipt['audio'] = {'codec': 'aac', 'channels': 2, 'sampleRate': 48000, 'duration': float(audio.get('duration', 0)), 'sourceSha256': project['audioSha256'],
                            'comparison': comparison, 'integratedLufs': float(integrated[-1]) if integrated else None, 'truePeakDbfs': float(peak[-1]) if peak else None}
    pixels = execute(['ffmpeg', '-v', 'error', '-xerror', '-nostdin', '-i', str(path), '-map', '0:v:0', '-an',
                      '-vf', 'scale=32:18:flags=area,format=rgb24,format=gray', '-vsync', '0', '-frames:v', str(comp['frames'] + 1),
                      '-f', 'rawvideo', '-'], timeout=600).stdout
    receipt['frameDiagnostics'] = visual.analyze_frames(pixels, project, comp)
    after = path.stat()
    if (before.st_ino, before.st_size, before.st_mtime_ns) != (after.st_ino, after.st_size, after.st_mtime_ns):
        raise ValueError('Output changed during independent verification.')
    return receipt


def render(project, root, run, progress):
    validate_recipe(project)
    engine = capabilities()
    if not engine['h264'] or not all(engine['filters'].values()):
        raise ValueError('Required native engine capability is unavailable.')
    requested_fonts = {cue['font'] for comp in project['compositions'] for cue in comp['captions']}
    if not requested_fonts.issubset(set(engine['fonts'])):
        raise ValueError('A required shaping font is unavailable; fallback fonts are disabled.')
    sources = inspect_sources(project, root)
    output_dir = root / 'outputs'
    output_dir.mkdir(exist_ok=True)
    outputs = []
    for comp in project['compositions']:
        clips = [render_clip(project, comp, clip, root, run) for clip in sorted(comp['clips'], key=lambda clip: clip['at'])]
        concat = root / f'{comp["id"]}.concat'
        concat.write_text('\n'.join(f"file '{path}'" for path in clips), encoding='utf8')
        ass = root / f'{comp["id"]}.ass'
        captions_ass(comp, ass)
        image = comp['id'] in {'thumbnail', 'artwork'}
        destination = output_dir / (comp['id'] + ('.jpg' if image else '.mp4'))
        args = ['ffmpeg', '-hide_banner', '-y', '-v', 'error', '-threads', '2', '-f', 'concat', '-safe', '0', '-i', str(concat)]
        if comp['audio']:
            args += ['-ss', str(comp['audio']['startSeconds']), '-i', str(root / 'assets' / comp['audio']['assetId'])]
        args += ['-map', '0:v:0']
        if comp['captions']:
            args += ['-vf', f'ass={ass}']
        if image:
            args += ['-frames:v', '1', '-an', '-c:v', 'mjpeg', '-q:v', '2', '-update', '1', str(destination)]
        else:
            args += ['-map', '1:a:0', '-t', str(comp['frames'] / 24), '-c:v', 'libx264' if comp['captions'] else 'copy']
            if comp['captions']:
                args += ['-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p']
            args += ['-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2', '-movflags', '+faststart', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', str(destination)]
        run(args)
        progress({'phase': 'verifying', 'outputId': comp['id'], 'completedOutputs': len(outputs), 'totalOutputs': len(project['compositions'])})
        outputs.append(verify_output(destination, project, comp, root))
        progress({'phase': 'rendering', 'completedOutputs': len(outputs), 'totalOutputs': len(project['compositions'])})
    return {'schemaVersion': 1, 'engine': engine, 'projectSha256': hashlib.sha256(canonical(project).encode()).hexdigest(), 'sources': sources, 'outputs': outputs,
            'measured': True, 'motionReviewed': False, 'heard': False, 'creativelyAccepted': False}
