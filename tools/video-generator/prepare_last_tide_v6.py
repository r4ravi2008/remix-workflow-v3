"""Prepare audio-bound editorial inputs, preserving every generated source."""
import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WS = Path(json.loads((ROOT / '.remix-workspace-root.json').read_text())['workspaceRoot']) / 'hello-ammai-progressive-deep-house'
BASE = WS / 'music-video'
OUT = BASE / 'resolve/v6-full-film'
MASTER = BASE / 'audio/hello-ammai-progressive-deep-house-selected-master.mp3'
EXPECTED = 'f93aa25209633151dcd6c9df1f74f571e6f573b9de55e847833c4475b0a375d6'
WORDS = dict(zip(
    'సాథియా ఓ మెరుపుల మాయా దిల్ దియా హాయిలొ పడిపోయా ప్రతి నిమిషం పరవశమే నిను తలచిన వేళా ఉదయం పరిమళమే నువు నడిచిన నేలా హల్లో అమ్మాయి దిల్లో గిటారే మోగించావే లవ్లీ బుజ్జాయి కల్లో carnival కార్నీవాల్ జరిపించావే ఒకటే మనసిదీ మనసే పడినదీ కనుకే త్వరపడీ జతగా నడుమరీ నీతోనే వచ్చానే వెనకే నీవల్లే మానేసా కునుకే'.split(),
    'Saathiya O Merupula Maaya Dil Diya Haayilo Padipoyaa Prathi Nimisham Paravashame Ninu Thalachina Velaa Udayam Parimalame Nuvu Nadichina Nelaa Hello Ammaayi Dillo Gitaare Moginchaave Lovely Bujjaayi Kallo Carnival Carnival Jaripinchaave Okate Manasidhi Manase Padinadhi Kanuke Thvarapadi Jathagaa Nadumari Neethone Vachchaane Venake Neevalle Maanesaa Kunuke'.split(), strict=True))


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def prepare():
    assert hashlib.sha256(MASTER.read_bytes()).hexdigest() == EXPECTED
    OUT.mkdir(parents=True, exist_ok=True)
    canonical = WS / 'hello-ammai-progressive-deep-house-lyrics.txt'
    lines = []
    for raw in canonical.read_text().splitlines():
        text = raw.strip().strip('(){}').strip()
        if text:
            lines.append(text)
    display = []
    for i, text in enumerate(lines):
        tokens = text.split()
        assert all(w in WORDS for w in tokens), text
        display.append({'id': f'L{i+1:02}', 'canonical': text,
                        'transliteration': ' '.join(WORDS[w] for w in tokens),
                        'status': 'transliterated_candidate_not_translation'})
    save('lyrics-display.json', {'audioSha256': EXPECTED,
         'canonicalPath': str(canonical), 'canonicalSha256': hashlib.sha256(canonical.read_bytes()).hexdigest(),
         'transliterationPolicy': 'User explicitly requests Latin-letter Telugu. Canonical source unchanged. Parenthetical echoes included for alignment testing; not silently discarded.',
         'lines': display})
    (OUT / 'lyrics-for-alignment.txt').write_text('[Full song]\n' + '\n'.join(lines) + '\n')
    (OUT / 'lyrics-transliterated.txt').write_text('\n'.join(x['transliteration'] for x in display) + '\n')
    print(f'Prepared {len(lines)} canonical/display lines', flush=True)


def analyze():
    import librosa
    import numpy as np
    y, sr = librosa.load(MASTER, sr=22050)
    hop = 256
    onset = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)
    _, frames = librosa.beat.beat_track(onset_envelope=onset, sr=sr, hop_length=hop, bpm=133.929, trim=False)
    times = librosa.frames_to_time(frames, sr=sr, hop_length=hop)
    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=hop)[0]
    save('measured-beats.json', {'audioSha256': EXPECTED, 'audioPath': str(MASTER),
         'durationSeconds': len(y)/sr, 'fps': 24, 'fixedTempoPrior': 133.929,
         'method': 'librosa beat_track with fixed tempo prior; onset envelope at 256/22050 second resolution',
         'heard': False, 'downbeatVerified': False,
         'beats': [{'index': int(i), 'seconds': round(float(t), 6), 'frame24': round(float(t)*24),
                    'onsetStrength': round(float(onset[f]), 5)} for i, (t, f) in enumerate(zip(times, frames))],
         'energy1s': [{'seconds': i, 'rms': round(float(np.mean(rms[int(i*sr/hop):int((i+1)*sr/hop)])), 6)}
                      for i in range(int(len(y)/sr))]})
    print(f'Measured {len(times)} beat candidates', flush=True)


def align():
    spec = importlib.util.spec_from_file_location('repo_lyric_alignment', ROOT/'tools/acapella-extractor/align_lyrics.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sections, lines = module.parse_suno_lyrics(OUT/'lyrics-for-alignment.txt')
    words = module.run_ctc_alignment(MASTER, lines, 'tel')
    grouped = module.group_words_to_lines(words, sections, lines)
    display = json.loads((OUT/'lyrics-display.json').read_text())['lines']
    assert len(grouped) == len(display)
    for i, (line, text) in enumerate(zip(grouped, display)):
        line['id'] = text['id']
        line['display'] = text['transliteration']
        line['reviewFlags'] = []
        dur = line['end_time'] - line['start_time']
        if dur < .8 and len(line['words']) > 1:
            line['reviewFlags'].append('implausibly_short_phrase')
        if dur > 6:
            line['reviewFlags'].append('long_phrase_or_silence_stretch')
        for left, right in zip(line['words'], line['words'][1:]):
            if right['start_time'] - left['end_time'] > 2:
                line['reviewFlags'].append('large_internal_word_gap')
        for word in line['words']:
            if word['end_time']-word['start_time'] > 4:
                line['reviewFlags'].append('stretched_word')
        line['status'] = 'forced_alignment_candidate_auditory_review_pending'
    save('lyrics-alignment-candidate.json', {'audioSha256': EXPECTED, 'audioPath': str(MASTER),
         'alignmentInput': 'canonical full mix, not another song or inherited stem',
         'method': 'local MMS CTC forced alignment through repository aligner',
         'heard': False, 'approved': False, 'lyrics': grouped})
    print(f'Aligned {len(grouped)} lines; {sum(bool(x["reviewFlags"]) for x in grouped)} flagged', flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--align', action='store_true')
    args = p.parse_args()
    prepare()
    analyze()
    if args.align:
        align()
