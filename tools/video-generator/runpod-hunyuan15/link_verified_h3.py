"""Expose only publisher-hash-verified weights to ComfyUI; never overwrite files."""
import hashlib
import json
from pathlib import Path

root = Path('/workspace/urvashi-h3')
cache = root / 'models-verified'
plan = json.loads((root / 'download-plan.json').read_text())
for record in plan:
    source = cache / record['destination']
    assert source.stat().st_size == record['bytes'], source
    with source.open('rb') as stream:
        assert hashlib.file_digest(stream, 'sha256').hexdigest() == record['sha256'], source
for record in plan:
    source = cache / record['destination']
    target = Path('/workspace/ComfyUI-H3/models') / record['destination']
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() or target.is_symlink():
        assert target.resolve() == source.resolve(), target
    else:
        target.symlink_to(source)
print('VERIFIED_AND_LINKED_ALL_FIVE_MODELS', flush=True)
