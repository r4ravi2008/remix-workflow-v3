"""Audit only current catalog entries; retain superseded assets untouched."""
import hashlib
import importlib.util
import json
import shutil
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw
from prepare_last_tide_v6 import ROOT, BASE, OUT

root = BASE / 'source-of-truth/05-abstract-supplement-v6'
catalog = json.loads((root / 'catalog.json').read_text())
anchors = sorted(catalog['anchors'], key=lambda x: x['intendedTimelineFrames'][0])
assert len({x['id'] for x in anchors}) == len(anchors)
spec = importlib.util.spec_from_file_location('anchor_audit', ROOT / '.agents/skills/music-video-director/scripts/anchor_audit.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
with tempfile.TemporaryDirectory(prefix='last-tide-active-anchor-audit-') as scratch:
    for entry in anchors:
        for path_key, hash_key in [('originalPath', 'originalSha256'), ('anchorPath', 'anchorSha256'), ('modelInputPath', 'modelInputSha256')]:
            path = Path(entry[path_key])
            assert hashlib.sha256(path.read_bytes()).hexdigest() == entry[hash_key], path
        shutil.copy2(entry['anchorPath'], Path(scratch) / Path(entry['anchorPath']).name)
    report = module.audit(json.loads((BASE / 'anchor-library-policy.json').read_text()), Path(scratch))
report['directory'] = str(root / 'anchors')
report['scope'] = 'Current catalog entries only; superseded files preserved but excluded.'
report['catalogSha256'] = hashlib.sha256((root / 'catalog.json').read_bytes()).hexdigest()
(OUT / 'abstract-anchor-audit.json').write_text(json.dumps(report, indent=2) + '\n')
sheet = Image.new('RGB', (1440, ((len(anchors) + 2) // 3) * 296), '#161616')
draw = ImageDraw.Draw(sheet)
for i, entry in enumerate(anchors):
    x, y = (i % 3) * 480, (i // 3) * 296
    with Image.open(entry['anchorPath']) as frame:
        sheet.paste(frame.resize((480, 270)), (x, y))
    draw.text((x + 10, y + 273), f"{entry['id']} / {entry['shotId']} / {entry['intendedTimelineFrames'][0] / 24:.2f}s", fill='ivory')
sheet.save(OUT / 'abstract-anchor-sequence.jpg', quality=94)
print(json.dumps({k: report[k] for k in ['imageCount', 'technicalPass', 'technicalIssues', 'possibleDuplicates']}, indent=2))
