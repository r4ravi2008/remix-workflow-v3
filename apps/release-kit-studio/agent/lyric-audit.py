"""Compare independently generated native lyric evidence without repairing timestamps."""
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import time

PINS = {
    'whisper': ('Systran/faster-whisper-large-v3', 'edaa852ec7e145841d8ffdb056a99866b5f0a478',
                '69f74147e3334731bc3a76048724833325d2ec74642fb52620eda87352e3d4f1'),
    'ctc': ('OpenVoiceOS/ai4bharat-indicconformer-te-onnx', 'd952dec2a1d256a1569cdfc9a9615cba05a1a2e3',
            'd615acecbfcffca3fa04ed8bc62284ba30cf48f90f537d4d0040b1b0e75f0b1c'),
}


def file_receipt(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for data in iter(lambda: stream.read(1024 * 1024), b''):digest.update(data)
    return {'sha256': digest.hexdigest(), 'bytes': path.stat().st_size}


def fingerprint(brief):
    return hashlib.sha256(json.dumps(brief, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()


def audit(packet, proposals, whisper, ctc):
    brief = packet['brief']
    digest = fingerprint(brief)
    expected = {'sha256': brief['audioSha256'], 'bytes': brief['audioBytes']}
    if packet.get('schemaVersion') != 2 or packet['briefSha256'] != digest:
        raise ValueError('The frozen direction packet changed')
    if any(proposals.get(key) != packet[key] for key in ['jobId', 'releaseId', 'briefSha256']) or proposals.get('source') != expected or proposals.get('canonicalLyrics') != brief['lyrics']:
        raise ValueError('Lyric proposals belong to a different frozen source or brief')
    if proposals.get('lyricTimingVerified') is not False or proposals.get('canonicalLyricsChanged') is not False:
        raise ValueError('Unverified proposals cannot assert timing or change canonical lyrics')
    indices = whisper['request']['lineIndices']
    lines = brief['lyrics'].splitlines()
    if not isinstance(indices, list) or not 1 <= len(indices) <= 8 or indices != sorted(set(indices)) or any(type(index) is not int or not 0 <= index < len(lines) for index in indices):
        raise ValueError('Alignment selects different chronological canonical line instances')
    selected = ' '.join(lines[index] for index in indices)
    for kind, receipt in [('whisper', whisper), ('ctc', ctc)]:
        request = receipt['request']
        model, revision, weights = PINS[kind]
        if (receipt.get('model'), receipt.get('revision'), receipt.get('weights', {}).get('sha256')) != (model, revision, weights):
            raise ValueError('Alignment does not bind the pinned model bytes')
        if receipt.get('status') != 'aligned-unverified' or receipt.get('alignmentComplete') is not True or receipt.get('source') != expected or receipt.get('canonicalText') != selected or request.get('lineIndices') != indices:
            raise ValueError('Alignment does not bind these exact chronological native words')
        for key in ['jobId', 'releaseId', 'briefSha256']:
            if request.get(key) != packet[key]:raise ValueError('Alignment belongs to a different frozen job or brief')
        if request.get('lyrics') != brief['lyrics'] or request.get('language') != brief['language'] or request.get('sourceDuration') != brief['audioDuration'] or request.get('sourceSha256') != expected['sha256'] or request.get('sourceBytes') != expected['bytes']:
            raise ValueError('Alignment source or canonical lyrics changed')
        if not 0 <= request['startSeconds'] < request['endSeconds'] <= brief['audioDuration'] or request['endSeconds'] - request['startSeconds'] > 30:
            raise ValueError('Alignment range exceeds the actual master')
        if any(receipt.get(key) is not False for key in ['lyricTimingVerified', 'canonicalLyricsChanged', 'fullSongHeard', 'pilotApproved', 'humanAccepted']):
            raise ValueError('Model observations cannot certify review or acceptance')
        if [row['text'] for row in receipt['words']] != selected.split():
            raise ValueError('Alignment changed the exact native words')
        previous = request['startSeconds']
        for index, row in enumerate(receipt['words']):
            if row['wordIndex'] != index or row.get('verified') is not False or any(not math.isfinite(row[key]) for key in ['startSeconds', 'endSeconds', 'probability']) or not 0 <= row['probability'] <= 1 or not previous - .02 <= row['startSeconds'] <= row['endSeconds'] <= request['endSeconds'] + .04:
                raise ValueError('Alignment has invalid or asserted word evidence')
            previous = row['endSeconds']
    result, offset = [], 0
    for line_index in indices:
        line = proposals['lines'][line_index]
        if line['lineIndex'] != line_index or line['text'] != lines[line_index]:
            raise ValueError('Proposals changed a repeated canonical line instance')
        for word_index, spelling in enumerate(lines[line_index].split()):
            candidate = line['words'][word_index]
            if candidate['wordIndex'] != word_index or candidate['text'] != spelling:
                raise ValueError('Proposals changed a canonical word')
            left, right = whisper['words'][offset], ctc['words'][offset]
            hints = candidate['candidate']
            issues = []
            for kind, row in [('whisper', left), ('ctc', right)]:
                issues.extend(kind + ':' + issue for issue in row['issues'])
                if row['probability'] < .6:issues.append(kind + ':uncertain-canonical-word')
                if offset == 0 and row['startSeconds'] - (whisper if kind == 'whisper' else ctc)['request']['startSeconds'] <= .02:
                    issues.append(kind + ':crop-boundary-onset-unresolved')
            starts = [left['startSeconds'], right['startSeconds']]
            if hints is None:
                issues.append('recognition:missing-canonical-word')
            else:
                starts.append(hints['startSeconds'])
                if hints.get('verified') is not False or not math.isfinite(hints['startSeconds']) or not math.isfinite(hints['endSeconds']) or not 0 <= hints['startSeconds'] < hints['endSeconds'] <= brief['audioDuration']:
                    raise ValueError('Recognition proposes invalid or asserted source timing')
                if hints['similarity'] < .85:issues.append('recognition:spelling-disagreement')
                if any(row['issues'] for row in hints['recognition']):issues.append('recognition:uncertain-observation')
            spread = max(starts) - min(starts)
            if spread > .15:issues.append('timing-evidence-disagreement')
            result.append({'lineIndex': line_index, 'wordIndex': word_index, 'text': spelling,
                           'recognitionProposal': None if hints is None else {'startSeconds': hints['startSeconds'], 'endSeconds': hints['endSeconds']},
                           'whisperProposal': {key: left[key] for key in ['startSeconds', 'endSeconds', 'probability']},
                           'ctcTokenEmissions': {key: right[key] for key in ['startSeconds', 'endSeconds', 'probability']},
                           'timingSpreadSeconds': spread, 'issues': sorted(set(issues)), 'verified': False})
            offset += 1
    return {'schemaVersion': 1, 'status': 'cross-evidence-audit-unverified',
            **{key: packet[key] for key in ['jobId', 'releaseId', 'briefSha256']}, 'source': expected,
            'lineIndices': indices, 'canonicalLyricsChanged': False, 'suppliedWordsPreserved': True,
            'words': result, 'timingEvidenceConsistent': all(not row['issues'] for row in result),
            'ctcTimingBasis': 'token-emission frames; word onsets and sung dwell are unverified',
            'automaticLyricTimingQualified': False, 'lyricTimingVerified': False,
            'fullSongHeard': False, 'pilotApproved': False, 'humanAccepted': False}


def main():
    if len(sys.argv) != 6:
        raise ValueError('Pass direction packet, lyric proposals, Whisper alignment, CTC alignment and a new audit path')
    packet_path, proposals_path, whisper_path, ctc_path, output = map(Path, sys.argv[1:])
    inputs = [packet_path, proposals_path, whisper_path, ctc_path]
    if any(path.stat().st_size > 2 * 1024 ** 2 for path in inputs) or output.exists():
        raise ValueError('Preserve existing audit evidence and use bounded source receipts')
    packet, proposals, whisper, ctc = [json.loads(path.read_text()) for path in inputs]
    source = Path(packet['source']['path'])
    expected = {'sha256': packet['brief']['audioSha256'], 'bytes': packet['brief']['audioBytes']}
    if file_receipt(source) != expected:raise ValueError('The actual canonical master changed')
    duration = float(json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', str(source)], check=True, capture_output=True, text=True, timeout=60).stdout)['format']['duration'])
    if abs(duration - packet['brief']['audioDuration']) > .005:raise ValueError('The measured master duration changed')
    result = audit(packet, proposals, whisper, ctc)
    result.update({'inputs': {name: file_receipt(path) for name, path in zip(['packet', 'proposals', 'whisper', 'ctc'], inputs)},
                   'runnerSha256': file_receipt(Path(__file__))['sha256'], 'observedAt': time.time()})
    if file_receipt(source) != expected:raise ValueError('The canonical source changed during the audit')
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x') as stream:
        __import__('os').chmod(output, 0o600);json.dump(result, stream, indent=2, ensure_ascii=False);stream.write('\n')
    print(json.dumps({'outputPath': str(output), 'wordsAudited': len(result['words']),
                      'timingEvidenceConsistent': result['timingEvidenceConsistent'], 'lyricTimingVerified': False}))


if __name__ == '__main__':main()
