import json
import math
import re
import time


def make_preview(source, comp, payload, root):
    from engine import audio_compare, execute, hash_file, probe
    start, frames = payload['startFrame'], payload['frames']
    samples = payload['sampleFrames']
    still = comp['id'] in {'thumbnail', 'artwork'}
    if (type(start) is not int or type(frames) is not int or not 0 <= start < comp['frames'] or
            not 1 <= frames <= 240 or start + frames > comp['frames'] or
            still and (start != 0 or frames != 1) or not isinstance(samples, list) or
            not 1 <= len(samples) <= 8 or len(set(samples)) != len(samples) or
            any(type(frame) is not int or not start <= frame < start + frames for frame in samples)):
        raise ValueError('Preview must select bounded exact source frames.')
    if not re.fullmatch(r'[a-f0-9]{64}', payload['bundleId']) or not re.fullmatch(r'[a-f0-9]{64}', payload['sourceSha256']):
        raise ValueError('Preview identity is invalid.')
    before = source.stat()
    if hash_file(source) != payload['sourceSha256']:
        raise ValueError('Preview source differs from the completed artifact.')
    destination = root / 'previews' / payload['bundleId']
    destination.mkdir(parents=True, exist_ok=False)
    ratio = min(1, 960 / max(comp['width'], comp['height']))
    width, height = math.floor(comp['width'] * ratio / 2) * 2, math.floor(comp['height'] * ratio / 2) * 2
    started = time.monotonic()

    def run(args):
        remaining = 600 - (time.monotonic() - started)
        if remaining <= 0:
            raise ValueError('Preview exceeded its ten-minute deadline.')
        return execute(['ffmpeg', '-v', 'error', '-xerror', '-nostdin', '-threads', '2', *args], timeout=remaining)

    proxy = destination / ('preview.jpg' if still else 'preview.mp4')
    if still:
        run(['-i', str(source), '-vf', f'scale={width}:{height}:in_color_matrix=auto:out_color_matrix=bt601:out_range=full,format=yuvj420p', '-frames:v', '1', '-q:v', '2', str(proxy)])
    else:
        video = f'[0:v]trim=start_frame={start}:end_frame={start + frames},setpts=PTS-STARTPTS,scale={width}:{height}[v]'
        audio = f'[0:a]atrim=start={start / 24:.9f}:end={(start + frames) / 24:.9f},asetpts=PTS-STARTPTS[a]'
        run(['-i', str(source), '-filter_complex_threads', '1', '-filter_complex', video + ';' + audio,
             '-map', '[v]', '-map', '[a]', '-frames:v', str(frames), '-t', str(frames / 24),
             '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23', '-pix_fmt', 'yuv420p',
             '-c:a', 'aac', '-b:a', '192k', '-ac', '2', '-ar', '48000', '-movflags', '+faststart', str(proxy)])
    files = []

    def measure(path, requested_frames, w, h, source_frame, video=False):
        metadata = probe(path)
        stream = next(item for item in metadata['streams'] if item['codec_type'] == 'video')
        if (stream['width'], stream['height'], int(stream.get('nb_read_frames', 0)), stream['codec_name']) != (w, h, requested_frames, 'h264' if video else 'mjpeg'):
            raise ValueError('Derived preview measurements differ from the recipe.')
        run(['-i', str(path), '-f', 'null', '-'])
        comparison = None
        if video:
            numerator, denominator = stream['avg_frame_rate'].split('/')
            audio_stream = next((item for item in metadata['streams'] if item['codec_type'] == 'audio'), None)
            if abs(int(numerator) / int(denominator) - 24) > .001 or not audio_stream or audio_stream['codec_name'] != 'aac' or audio_stream['channels'] != 2 or int(audio_stream['sample_rate']) != 48000:
                raise ValueError('Review video needs exact rate and stereo AAC audio.')
            source_audio = json.loads(execute(['ffprobe', '-v', 'error', '-select_streams', 'a:0',
                                             '-show_entries', 'stream=duration', '-of', 'json', str(source)]).stdout)['streams'][0]
            duration = min(frames / 24, float(source_audio['duration']) - start / 24)
            comparison = audio_compare(path, source, start / 24, duration)
            if not comparison['passed'] or abs(float(audio_stream.get('duration', 0)) - duration) > 2 / 24:
                raise ValueError('Review audio differs from the original encoded range.')
        size = path.stat().st_size
        if not 0 < size <= 33554432:
            raise ValueError('Preview file exceeds its bounded transfer size.')
        files.append({'name': path.name, 'sha256': hash_file(path), 'bytes': size,
                      'width': w, 'height': h, 'frames': requested_frames, 'fps': 24 if video else 0,
                      'duration': frames / 24 if video else 0, 'sourceFrame': source_frame,
                      'completeDecode': True, 'audioComparison': comparison})

    measure(proxy, frames if not still else 1, width, height, None if not still else start, not still)
    ordered = sorted(samples)
    selection = '+'.join(f'eq(n\\,{frame})' for frame in ordered)
    run(['-i', str(source), '-vf', f'select={selection},scale=iw:ih:in_color_matrix=auto:out_color_matrix=bt601:out_range=full,format=yuvj420p',
         '-vsync', '0', '-frames:v', str(len(ordered)), '-q:v', '2', '-start_number', '0', str(destination / 'selected-%02d.jpg')])
    selected = sorted(destination.glob('selected-*.jpg'))
    if len(selected) != len(ordered):
        raise ValueError('Decoded sample count differs from the exact source frame selection.')
    for frame, selected_path in zip(ordered, selected):
        path = destination / f'frame-{frame:06d}.jpg'
        selected_path.rename(path)
        measure(path, 1, comp['width'], comp['height'], frame)
    after = source.stat()
    if (before.st_ino, before.st_size, before.st_mtime_ns) != (after.st_ino, after.st_size, after.st_mtime_ns):
        raise ValueError('Original artifact changed during preview generation.')
    receipt = {'files': files, 'sampleFrames': sorted(samples), 'sourceSha256': payload['sourceSha256'],
               'startFrame': start, 'frames': frames, 'bundleId': payload['bundleId']}
    (destination / 'receipt.json').write_text(json.dumps(receipt))
    return receipt
