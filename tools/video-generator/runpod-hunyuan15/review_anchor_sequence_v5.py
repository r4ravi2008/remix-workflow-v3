"""Build chronological inspection sheets without changing production media."""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw

BASE = Path('/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/urvashi/music-video/hyperreal-story-review-v5')
plan = json.loads((BASE / 'edit-contract.json').read_text())
out = BASE / 'sequence-inspection'
out.mkdir(exist_ok=True)
records = []
for offset in range(0, len(plan['cuts']), 8):
    sheet = Image.new('RGB', (1920, 4 * 570), '#202020')
    draw = ImageDraw.Draw(sheet)
    for index, cut in enumerate(plan['cuts'][offset:offset + 8]):
        path = BASE / cut['sourceFile']
        sha = hashlib.sha256(path.read_bytes()).hexdigest()
        assert sha == cut['sha256'], cut['cutId']
        with Image.open(path) as source:
            assert source.size == (1920, 1080), path
            rgb = source.convert('RGB')
            assert rgb.crop((0, 0, 1920, 145)).getbbox() is None, path
            assert rgb.crop((0, 935, 1920, 1080)).getbbox() is None, path
            x, y = (index % 2) * 960, (index // 2) * 570
            sheet.paste(rgb.resize((960, 540)), (x, y))
            draw.text((x + 12, y + 545), f"{cut['cutId']} {cut['anchorId']} | {cut['startFrame']/24:.3f} - {cut['endFrameExclusive']/24:.3f}s", fill='white')
        records.append({'cutId': cut['cutId'], 'path': str(path), 'sha256': sha,
                        'canvas': [1920, 1080], 'matteTopBottom': 145})
    sheet.save(out / f'page-{offset // 8 + 1:02d}.jpg', quality=94)
(out / 'technical-audit.json').write_text(json.dumps({'status': 'TECHNICAL_PASS_VISUAL_REVIEW_SEPARATE', 'records': records}, indent=2))
print(json.dumps({'cuts': len(records), 'pages': (len(records)+7)//8, 'output': str(out)}))
