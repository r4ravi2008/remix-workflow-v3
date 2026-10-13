#!/usr/bin/env python3
"""Freeze and verify selected files across hosts; no uploads or generation."""
import argparse
import hashlib
import json
from pathlib import Path
import sys


def file_hash(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def contained(root, relative):
    root = root.resolve()
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise ValueError('Expected a nonempty relative file path')
    path = (root / relative).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError(f'Missing or out-of-root file: {relative}')
    return path


def create(root, paths):
    if not paths or len(paths) != len(set(paths)):
        raise ValueError('Select a nonempty unique file list')
    files = []
    for relative in sorted(paths):
        path = contained(root, relative)
        if path.stat().st_size == 0:
            raise ValueError(f'Empty source file: {relative}')
        files.append({'path': relative, 'bytes': path.stat().st_size, 'sha256': file_hash(path)})
    body = {'schema_version': 1, 'files': files}
    return {**body, 'snapshot_sha256': fingerprint(body)}


def verify(root, snapshot):
    if snapshot.get('schema_version') != 1 or not isinstance(snapshot.get('files'), list) or not snapshot['files']:
        raise ValueError('Invalid snapshot')
    body = {k: snapshot[k] for k in ('schema_version', 'files')}
    if fingerprint(body) != snapshot.get('snapshot_sha256'):
        raise ValueError('Snapshot definition changed')
    seen = set()
    for record in snapshot['files']:
        relative = record['path']
        if relative in seen:
            raise ValueError(f'Duplicate snapshot path: {relative}')
        seen.add(relative)
        path = contained(root, relative)
        if path.stat().st_size != record['bytes'] or file_hash(path) != record['sha256']:
            raise ValueError(f'Source mismatch: {relative}')
    return {'verified': True, 'files': len(seen), 'snapshot_sha256': snapshot['snapshot_sha256']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    make = sub.add_parser('create')
    make.add_argument('--root', required=True, type=Path)
    make.add_argument('--output', required=True, type=Path)
    make.add_argument('paths', nargs='+')
    check = sub.add_parser('verify')
    check.add_argument('--root', required=True, type=Path)
    check.add_argument('--manifest', required=True, type=Path)
    args = parser.parse_args()
    try:
        if args.command == 'create':
            snapshot = create(args.root, args.paths)
            with args.output.open('x') as stream:
                json.dump(snapshot, stream, indent=2)
                stream.write('\n')
            print(json.dumps({'snapshot': str(args.output), 'files': len(snapshot['files']),
                              'snapshot_sha256': snapshot['snapshot_sha256']}))
        else:
            print(json.dumps(verify(args.root, json.loads(args.manifest.read_text()))))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({'error': str(error)}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
