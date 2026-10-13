import argparse
import json
import struct
from pathlib import Path


def boxes(stream, start, end):
    cursor = start
    while cursor < end:
        stream.seek(cursor)
        header = stream.read(8)
        if len(header) != 8:
            raise ValueError('Truncated box header')
        size, kind = struct.unpack('>I4s', header)
        header_size = 8
        if size == 1:
            extended = stream.read(8)
            if len(extended) != 8:
                raise ValueError('Truncated extended box header')
            size = struct.unpack('>Q', extended)[0]
            header_size = 16
        if size == 0:
            size = end - cursor
        if size < header_size or cursor + size > end:
            raise ValueError('Box range exceeds its parent')
        yield kind, cursor + header_size, cursor + size
        cursor += size


def child(stream, parent, kind):
    for box in boxes(stream, parent[1], parent[2]):
        if box[0] == kind:
            return box
    raise ValueError(f'Missing {kind!r} box')


def contents(stream, box):
    size = box[2] - box[1]
    if size > 64 * 1024 * 1024:
        raise ValueError('Metadata box exceeds inspection limit')
    stream.seek(box[1])
    data = stream.read(size)
    if len(data) != size:
        raise ValueError('Truncated metadata box')
    return data


def inspect(path):
    with path.open('rb') as stream:
        root = (b'root', 0, path.stat().st_size)
        moov = child(stream, root, b'moov')
        tracks = []
        for trak in boxes(stream, moov[1], moov[2]):
            if trak[0] != b'trak':
                continue
            mdia = child(stream, trak, b'mdia')
            header = contents(stream, child(stream, mdia, b'mdhd'))
            if header[0] == 0:
                timescale, duration = struct.unpack_from('>II', header, 12)
            elif header[0] == 1:
                timescale = struct.unpack_from('>I', header, 20)[0]
                duration = struct.unpack_from('>Q', header, 24)[0]
            else:
                raise ValueError('Unsupported media header version')
            handler = contents(stream, child(stream, mdia, b'hdlr'))[8:12].decode('ascii')
            stbl = child(stream, child(stream, mdia, b'minf'), b'stbl')
            descriptions = contents(stream, child(stream, stbl, b'stsd'))
            codec = descriptions[12:16].decode('ascii')
            sizes = contents(stream, child(stream, stbl, b'stsz'))
            sample_count = struct.unpack_from('>I', sizes, 8)[0]
            timing = contents(stream, child(stream, stbl, b'stts'))
            entries = struct.unpack_from('>I', timing, 4)[0]
            pairs = [struct.unpack_from('>II', timing, 8 + index * 8) for index in range(entries)]
            timing_count = sum(count for count, _ in pairs)
            timing_ticks = sum(count * delta for count, delta in pairs)
            if timing_count != sample_count or timescale <= 0:
                raise ValueError('Inconsistent sample timing table')
            row = {
                'handler': handler, 'codec': codec, 'timescale': timescale,
                'durationTicks': duration, 'sampleCount': sample_count,
                'timingCount': timing_count, 'timingTicks': timing_ticks,
                'timingEntries': [list(pair) for pair in pairs],
            }
            if handler == 'vide':
                width, height = struct.unpack_from('>HH', descriptions, 40)
                row.update({'width': width, 'height': height})
            tracks.append(row)
        return {'path': str(path.resolve()), 'bytes': path.stat().st_size, 'tracks': tracks}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=Path)
    args = parser.parse_args()
    print(json.dumps(inspect(args.path), indent=2))
