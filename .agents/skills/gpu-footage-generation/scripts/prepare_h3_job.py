#!/usr/bin/env python3
"""Parameterize the historically verified H3 I2V graph; does not submit or crop images."""
import argparse
import json
from pathlib import Path
import re


def prepare(anchor, prompt, width, height, frames, fps, seed, job):
    if Path(anchor).is_absolute() or '..' in Path(anchor).parts or not anchor:
        raise ValueError('Anchor must be relative to the verified ComfyUI input root')
    if not prompt.strip():
        raise ValueError('Supply a visual shot prompt')
    if width <= 0 or height <= 0 or width % 32 or height % 32:
        raise ValueError('This H3 recipe uses positive dimensions on a 32-pixel grid')
    if frames < 22 or (frames - 5) % 17:
        raise ValueError('This H3 recipe uses frame count 17n+5 with n >= 1; verify against the live node')
    if fps <= 0 or seed < 0 or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,95}', job):
        raise ValueError('Invalid fps, seed or attempt ID')
    graph = json.loads((Path(__file__).parent.parent / 'assets/h3-i2v-api.json').read_text())
    graph['6']['inputs']['image'] = anchor
    graph['8']['inputs'].update(prompt=prompt, width=width, height=height, length=frames)
    graph['9']['inputs']['noise_seed'] = seed
    graph['16']['inputs']['fps'] = fps
    graph['17']['inputs']['filename_prefix'] = 'footage/' + job
    return graph, [{'node': '6', 'input': 'image', 'path': anchor}]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--anchor', required=True)
    parser.add_argument('--prompt-file', required=True, type=Path)
    parser.add_argument('--width', required=True, type=int)
    parser.add_argument('--height', required=True, type=int)
    parser.add_argument('--frames', required=True, type=int)
    parser.add_argument('--fps', required=True, type=int)
    parser.add_argument('--seed', required=True, type=int)
    parser.add_argument('--job', required=True)
    parser.add_argument('--directory', required=True, type=Path, help='New prepared-job directory')
    args = parser.parse_args()
    graph, bindings = prepare(args.anchor, args.prompt_file.read_text(), args.width, args.height,
                              args.frames, args.fps, args.seed, args.job)
    args.directory.mkdir(parents=True, exist_ok=False)
    (args.directory / 'workflow.json').write_text(json.dumps(graph, indent=2) + '\n')
    (args.directory / 'bindings.json').write_text(json.dumps(bindings, indent=2) + '\n')
    print(json.dumps({'directory': str(args.directory), 'state': 'prepared-unsubmitted',
                      'note': 'Verify live runtime, model hashes, anchors and budget before submission.'}))


if __name__ == '__main__':
    main()
