"""Build a provisional Resolve subtitle sidecar without altering canonical lyrics."""
import hashlib
import json
from prepare_last_tide_v6 import OUT, MASTER, EXPECTED

def stamp(frame):
    ms = round(frame * 1000 / 24)
    h, rest = divmod(ms, 3600000)
    m, rest = divmod(rest, 60000)
    s, ms = divmod(rest, 1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'

source = OUT / 'lyrics-alignment-v2-candidate.json'
alignment = json.loads(source.read_text())
assert alignment['audioSha256'] == EXPECTED
assert hashlib.sha256(MASTER.read_bytes()).hexdigest() == EXPECTED
display = json.loads((OUT / 'lyrics-display.json').read_text())['lines']
assert len(alignment['lyrics']) == len(display) == 39
blocks, cues = [], []
previous_end = 0
for i, (line, expected) in enumerate(zip(alignment['lyrics'], display), 1):
    assert line['id'] == expected['id']
    assert line['display'] == expected['transliteration']
    assert line['text'] == expected['canonical']
    start, end = round(line['start_time'] * 24), round(line['end_time'] * 24)
    assert 0 <= previous_end <= start < end <= 5463, line
    previous_end = end
    text = line['display']
    # No editorial paraphrase, dropped echoes, or forced beat snapping.
    blocks.append(f'{i}\n{stamp(start)} --> {stamp(end)}\n{text}\n')
    cues.append({'id': line['id'], 'startFrame': start, 'endFrame': end,
                 'display': text, 'reviewFlags': line.get('reviewFlags', []),
                 'maxQuantizationErrorMs': round(max(abs(start/24-line['start_time']), abs(end/24-line['end_time']))*1000, 3)})
path = OUT / 'the-last-tide-transliterated-PROVISIONAL.srt'
path.write_text('\n'.join(blocks), encoding='utf-8')
report = {'status': 'prepared_not_imported_auditory_and_font_review_pending',
          'audioSha256': EXPECTED, 'alignmentSha256': hashlib.sha256(source.read_bytes()).hexdigest(),
          'srtPath': str(path), 'srtSha256': hashlib.sha256(path.read_bytes()).hexdigest(),
          'fps': 24, 'cueCount': len(cues), 'canonicalUnchanged': True,
          'timingPolicy': 'Nearest 24fps frame; preserve vocal timing, never snap words to beat grid.',
          'resolveStyle': {'fontSizePixels': 38, 'color': 'ivory', 'location': 'lower 138px matte', 'maximumLines': 2, 'animation': 'none'},
          'cues': cues}
(OUT / 'subtitle-import-report.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k: report[k] for k in ['status','cueCount','srtPath','srtSha256']}, indent=2))
