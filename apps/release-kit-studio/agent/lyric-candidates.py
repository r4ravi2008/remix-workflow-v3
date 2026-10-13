"""Chronological lyric proposals; canonical words and failed recognition remain unchanged."""
import difflib
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys
import time
import unicodedata

spec = importlib.util.spec_from_file_location('candidate_audio', Path(__file__).with_name('audio-perception.py'))
audio = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audio)
MODEL = 'Systran/faster-whisper-large-v3'
REVISION = 'edaa852ec7e145841d8ffdb056a99866b5f0a478'


def normalized(text):
    return ''.join(c for c in unicodedata.normalize('NFC', text) if unicodedata.category(c)[0] in 'LMN').casefold()


def recognized_words(segments, duration):
    words, excluded = [], []
    previous_end = 0.
    for row in segments:
        start, end = row['start'], row['end']
        if not all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) for v in [start, end, row['avgLogprob'], row['noSpeechProbability']]):
            raise ValueError('Recognition contains non-finite segment evidence')
        valid_segment = 0 <= start < end <= duration + .02 and start >= previous_end - .02
        previous_end = end
        last = start
        for index, word in enumerate(row['words']):
            values = [word['start'], word['end'], word['probability']]
            finite = all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) for v in values)
            valid = finite and valid_segment and start - .02 <= word['start'] < word['end'] <= end + .02 and word['start'] >= last - .02 and 0 <= word['probability'] <= 1
            if finite:
                last = word['end']
            reasons = []
            if not valid:
                reasons.append('invalid-source-range')
            if not isinstance(word['text'], str) or '\ufffd' in word['text'] or not normalized(word['text']):
                reasons.append('invalid-recognized-word')
            warnings = []
            if finite and word['probability'] < .6 or row['avgLogprob'] < -1:
                warnings.append('uncertain-recognition')
            if row['noSpeechProbability'] > .6:
                warnings.append('high-no-speech-prior')
            if reasons:
                excluded.append({'segmentId': row['id'], 'wordIndex': index, 'text': word['text'], 'issues': reasons})
            else:
                words.append({'segmentId': row['id'], 'wordIndex': index, **word,
                              'issues': warnings, 'verified': False})
    return words, excluded


def match_words(canonical, recognized):
    """Global monotonic matching allows split recognitions, never invented timestamps."""
    if len(canonical) > 1000 or len(recognized) > 2500:
        raise ValueError('Lyric proposal exceeds its bounded word count')
    left = [normalized(word['text']) for word in canonical]
    right = [normalized(word['text']) for word in recognized]
    n, m = len(left), len(right)
    scores = [[float('inf')] * (m + 1) for _ in range(n + 1)]
    choices = [[None] * (m + 1) for _ in range(n + 1)]
    scores[0][0] = 0.
    for i in range(n + 1):
        for j in range(m + 1):
            current = scores[i][j]
            candidates = []
            if i < n:
                candidates.append((i + 1, j, current + .85, 'unmatched-canonical', 0.))
            if j < m:
                candidates.append((i, j + 1, current + .65, 'unmatched-recognition', 0.))
            if i < n:
                for count in [1, 2, 3]:
                    if j + count > m:
                        continue
                    group = recognized[j:j + count]
                    if any(after['start'] - before['end'] > .8 for before, after in zip(group, group[1:])):
                        continue
                    similarity = difflib.SequenceMatcher(None, left[i], ''.join(right[j:j + count]), autojunk=False).ratio()
                    if similarity >= .68:
                        candidates.append((i + 1, j + count, current + (1 - similarity) + (count - 1) * .04, 'matched', similarity))
            for ni, nj, cost, kind, similarity in candidates:
                if cost < scores[ni][nj]:
                    scores[ni][nj] = cost
                    choices[ni][nj] = (i, j, kind, similarity)
    matches = [None] * n
    i, j = n, m
    while i or j:
        previous = choices[i][j]
        if previous is None:
            raise ValueError('Chronological proposal trace is incomplete')
        pi, pj, kind, similarity = previous
        if kind == 'matched':
            group = recognized[pj:j]
            matches[pi] = {'startSeconds': group[0]['start'], 'endSeconds': group[-1]['end'],
                           'similarity': similarity, 'recognition': group, 'verified': False}
        i, j = pi, pj
    return matches


def propose(lyrics, segments, duration):
    lines = lyrics.splitlines()
    if not lines or len(lines) > 500 or any(not line.strip() for line in lines):
        raise ValueError('Canonical lyric lines must be nonempty and bounded')
    canonical = [{'lineIndex': index, 'wordIndex': word_index, 'text': word}
                 for index, line in enumerate(lines) for word_index, word in enumerate(line.split())]
    if any('\ufffd' in word['text'] or not normalized(word['text']) for word in canonical):
        raise ValueError('Canonical words contain invalid characters')
    recognized, excluded = recognized_words(segments, duration)
    matches = match_words(canonical, recognized)
    result = []
    offset = 0
    for index, line in enumerate(lines):
        length = len(line.split())
        words = [{'wordIndex': i, 'text': canonical[offset + i]['text'], 'candidate': matches[offset + i]} for i in range(length)]
        matched = [word['candidate'] for word in words if word['candidate']]
        missing = [word['wordIndex'] for word in words if not word['candidate']]
        issues = []
        if missing:
            issues.append('missing-word-observations')
        if any(word['similarity'] < .85 for word in matched):
            issues.append('recognition-spelling-disagreement')
        if any(item['issues'] for word in matched for item in word['recognition']):
            issues.append('uncertain-recognition')
        span = matched[-1]['endSeconds'] - matched[0]['startSeconds'] if matched else None
        if span is not None and span > 20:
            issues.append('excessive-line-span')
        window = None
        if len(matched) >= max(2, math.ceil(length * .6)) and span is not None and span <= 20:
            window = {'startSeconds': max(0., matched[0]['startSeconds'] - 1.5),
                      'endSeconds': min(duration, matched[-1]['endSeconds'] + 1.5)}
        result.append({'lineIndex': index, 'text': line, 'words': words,
                       'matchedWordCount': len(matched), 'missingWordIndices': missing,
                       'alignmentWindowProposal': window, 'issues': issues, 'lyricTimingVerified': False})
        offset += length
    return {'lines': result, 'canonicalWordCount': len(canonical), 'recognizedWordCount': len(recognized),
            'matchedWordCount': sum(row is not None for row in matches), 'excludedRecognition': excluded}


def main():
    if len(sys.argv) != 4:
        raise ValueError('Pass direction-input.json, speech receipt and a new output JSON path')
    packet_path, speech_path, output = map(Path, sys.argv[1:])
    if packet_path.stat().st_size > 2 * 1024 ** 2 or speech_path.stat().st_size > 2 * 1024 ** 2:
        raise ValueError('Lyric inputs exceed their bounded size')
    packet, speech = json.loads(packet_path.read_text()), json.loads(speech_path.read_text())
    brief = packet['brief']
    fingerprint = hashlib.sha256(json.dumps(brief, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()
    request = speech['request']
    if packet.get('schemaVersion') != 2 or fingerprint != packet['briefSha256'] or packet['jobId'] != request['jobId'] or packet['releaseId'] != request['releaseId'] or request['briefSha256'] != fingerprint or request['lyrics'] != brief['lyrics'] or request['language'] != brief['language']:
        raise ValueError('Lyric evidence belongs to a different frozen job or brief')
    if speech.get('model') != MODEL or speech.get('revision') != REVISION or speech.get('source') != {'sha256': brief['audioSha256'], 'bytes': brief['audioBytes']}:
        raise ValueError('Recognition does not bind the pinned model and canonical source')
    if speech.get('status') not in ['recognized-unverified', 'failed'] or not isinstance(speech.get('segments'), list):
        raise ValueError('No bounded raw recognition evidence is available')
    source = Path(packet['source']['path'])
    expected = {'sha256': brief['audioSha256'], 'bytes': brief['audioBytes']}
    if audio.file_receipt(source) != expected or speech['decodedAudio']['samples'] != round(brief['audioDuration'] * 16000):
        raise ValueError('Lyric proposal source differs from the exact master')
    actual = float(json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', str(source)], check=True, capture_output=True, text=True, timeout=60).stdout)['format']['duration'])
    if abs(actual - brief['audioDuration']) > .005:
        raise ValueError('Lyric proposal duration differs from the measured source')
    proposed = propose(brief['lyrics'], speech['segments'], actual)
    result = {'schemaVersion': 1, 'status': 'chronological-timing-proposals-unverified',
              'jobId': packet['jobId'], 'releaseId': packet['releaseId'], 'briefSha256': fingerprint,
              'source': expected, 'durationSeconds': actual, 'language': brief['language'],
              'canonicalLyrics': brief['lyrics'], 'speechEvidence': audio.file_receipt(speech_path),
              'runnerSha256': audio.file_receipt(Path(__file__))['sha256'],
              **proposed, 'suppliedWordsPreserved': True, 'canonicalLyricsChanged': False,
              'lyricTimingVerified': False, 'fullSongHeard': False, 'pilotApproved': False,
              'humanAccepted': False, 'observedAt': time.time()}
    if audio.file_receipt(source) != expected:
        raise ValueError('Canonical source changed during lyric proposal')
    audio.write_new(output, result)
    print(json.dumps({'outputPath': str(output), 'lines': len(proposed['lines']),
                      'matchedWordCount': proposed['matchedWordCount'], 'lyricTimingVerified': False}))


if __name__ == '__main__':
    main()
