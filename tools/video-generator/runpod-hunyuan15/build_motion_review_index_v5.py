"""Build a local original-clip review gallery, not an edit or acceptance record."""
import html
import json
from pathlib import Path
from urllib.parse import quote

from prepare_motion_v5 import OUT

inventory = json.loads((OUT / 'downloaded-inventory.json').read_text())
cards = []
for key, asset in sorted(inventory['assets'].items()):
    media = Path(asset['path'])
    relative = media.relative_to(OUT)
    slots = [p for p in inventory['placements'] if p['assetId'] == key]
    timing = ', '.join(
        f"{p['cutId']} {p['timelineInFrame']/24:.3f}–{p['timelineOutFrameExclusive']/24:.3f}s"
        for p in slots) or 'Not selected for a current placement'
    review = relative.parent / 'scoped-review.md'
    review_link = (f'<a href="{quote(str(review))}">Scoped review notes</a>'
                   if (OUT / review).exists() else '')
    status = html.escape(asset['reviewStatus'])
    cards.append(f'''<article id="{html.escape(key)}">
<h2>{html.escape(key)} <small>{status}</small></h2>
<p>{html.escape(timing)}</p>
<video controls muted playsinline preload="none" src="{quote(str(relative))}"></video>
<p><a href="{quote(str(relative))}">Open original MP4</a> {review_link}</p>
<details><summary>Original SHA256</summary><code>{asset['sha256']}</code></details>
</article>''')

document = f'''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Urvashi — original motion review</title>
<style>
body{{font:16px system-ui;background:#141419;color:#ececf0;max-width:1250px;margin:2rem auto;padding:0 1rem}}
a{{color:#a9cdff}}h1{{font-size:1.6rem}}h2{{font-size:1.1rem}}small{{font-size:.7rem;color:#b7b7c5}}
main{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,480px),1fr));gap:1rem}}
article{{padding:1rem;background:#202029;border-radius:10px}}video{{width:100%;background:black}}
code{{overflow-wrap:anywhere;font-size:.7rem}}.notice{{padding:1rem;border:1px solid #a18b56;margin-bottom:1rem}}
</style><h1>Urvashi — downloaded originals</h1>
<div class="notice"><strong>Review candidates, not the final film.</strong>
{inventory['downloadedGenerations']} of {inventory['requiredGenerations']} planned generations downloaded;
{inventory['downloadedOriginals']} original attempts retained. Generated audio is muted by default and is not the song master.
Play at normal speed to inspect faces, hands, movement and camera direction. Read each scoped note before selecting a take.
Rejected attempts are preserved here for comparison. No Resolve assembly or creative approval is implied.</div>
<main>{''.join(cards)}</main></html>'''
(OUT / 'REVIEW.html').write_text(document)
print(OUT / 'REVIEW.html')
