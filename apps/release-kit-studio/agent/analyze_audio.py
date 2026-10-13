"""Read-only music measurements. Timing and interpretation remain unreviewed."""
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import subprocess
import sys

INPUT_OPTIONS = ['-protocol_whitelist', 'file,pipe', '-format_whitelist',
                 'wav,mp3,aac,flac,ogg,mov,matroska,webm,aiff,asf']
spec = importlib.util.spec_from_file_location('analysis_audio', Path(__file__).with_name('audio-perception.py'))
audio = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audio)


def percentile(values, fraction):
    ordered = sorted(values)
    position = fraction * (len(ordered) - 1)
    lower, upper = math.floor(position), math.ceil(position)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def normalized(values):
    smoothed = [sum(values[max(0, i - 1):i + 2]) /
                len(values[max(0, i - 1):i + 2]) for i in range(len(values))]
    low, high = percentile(smoothed, .1), percentile(smoothed, .9)
    return [min(1, max(0, (value - low) / max(high - low, 1e-8)))
            for value in smoothed]


def measure(source, filters):
    graph = ','.join([
        'aresample=24000', *filters, 'asetnsamples=n=1000:p=1',
        'astats=metadata=1:reset=1',
        'ametadata=print:key=lavfi.astats.Overall.RMS_level:file=-',
    ])
    result = subprocess.run([
        'ffmpeg', '-v', 'error', '-nostdin', *INPUT_OPTIONS, '-i', str(source),
        '-map', '0:a:0', '-af', graph, '-t', '900.25', '-vn', '-f', 'null', '-',
    ], capture_output=True, text=True, check=True, timeout=120)
    levels = re.findall(r'lavfi\.astats\.Overall\.RMS_level=([^\s]+)', result.stdout)
    if not levels:
        raise ValueError('No decoded audio measurements were produced')
    values = [float(value) for value in levels]
    if any(math.isnan(value) or value == math.inf for value in values):
        raise ValueError('Invalid decoded audio levels')
    return [0 if value == -math.inf else 10 ** (value / 20) for value in values]


def analyze(source, output):
    before = source.stat()
    with source.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    probe = json.loads(subprocess.run([
        'ffprobe', '-v', 'error', *INPUT_OPTIONS, '-select_streams', 'a:0',
        '-show_streams', '-show_format', '-of', 'json', str(source),
    ], capture_output=True, text=True, check=True, timeout=30).stdout)
    stream = probe['streams'][0]
    duration = audio.decoded_audio_duration(source)
    if not math.isfinite(duration) or not 0 < duration <= 900.15:
        raise ValueError('Measured audio duration is outside the release contract')
    rms = measure(source, [])
    bass = measure(source, ['highpass=f=35', 'lowpass=f=150'])
    if len(rms) != len(bass) or abs(len(rms) / 24 - duration) > .15:
        raise ValueError('Decoded measurements do not cover the complete song')
    energy, bass_energy = normalized(rms), normalized(bass)
    response = [.22 + .58 * (.65 * low + .35 * full)
                for low, full in zip(bass_energy, energy)]
    onset = [0] + [max(0, after - before) for before, after in zip(bass, bass[1:])]
    lag_candidates = range(round(60 * 24 / 150), round(60 * 24 / 80) + 1)
    mean = sum(onset) / len(onset)
    centered = [value - mean for value in onset]
    correlations = [(sum(a * b for a, b in zip(centered, centered[lag:])), lag)
                    for lag in lag_candidates if lag < len(onset)]
    grid = None
    if correlations and max(onset) > 1e-8:
        correlation, lag = max(correlations)
        if correlation > 0:
            phase = max(range(lag), key=lambda offset:
                        sum(onset[offset::lag]) / len(onset[offset::lag]))
            grid = {
                'tempoBpm': 60 * 24 / lag,
                'times': [round(frame / 24, 6) for frame in range(phase, len(onset), lag)],
                'method': 'bass onset autocorrelation at 24 fps; coarse candidate',
                'heardOrApproved': False,
            }
    after = source.stat()
    if (before.st_ino, before.st_size, before.st_mtime_ns) != (
            after.st_ino, after.st_size, after.st_mtime_ns):
        raise ValueError('Canonical audio changed during analysis')
    receipt = {
        'schemaVersion': 2,
        'method': 'FFmpeg decoded per-channel RMS and 35-150 Hz filtered RMS',
        'sourceSha256': digest, 'sourceBytes': before.st_size,
        'durationSeconds': duration, 'sampleRate': int(stream['sample_rate']),
        'channels': stream['channels'], 'fps': 24, 'frameCount': len(rms),
        'rms': [round(value, 6) for value in rms],
        'environmentGain': [round(value, 6) for value in response],
        'proposedBeatGrid': grid,
        'protectedLayers': ['people', 'lyrics', 'story props'],
        'fullSongHeard': False,
    }
    output.write_text(json.dumps(receipt, indent=2) + '\n')
    output.chmod(0o600)
    print(json.dumps({key: receipt[key] for key in [
        'sourceSha256', 'durationSeconds', 'frameCount', 'sampleRate']}))


if __name__ == '__main__':
    analyze(Path(sys.argv[1]), Path(sys.argv[2]))
