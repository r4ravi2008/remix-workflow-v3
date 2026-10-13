"""Bounded, blank-aware Telugu alignment; observations never approve lyric timing."""
import hashlib
import importlib.metadata
import importlib.util
import json
import math
from pathlib import Path
import os
import signal
import subprocess
import sys
import time
import uuid

SERVICE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('ctc_canonical_alignment', SERVICE / 'lyric-alignment.py')
canonical = importlib.util.module_from_spec(spec)
spec.loader.exec_module(canonical)
audio = canonical.audio
MODEL = 'OpenVoiceOS/ai4bharat-indicconformer-te-onnx'
REVISION = 'd952dec2a1d256a1569cdfc9a9615cba05a1a2e3'
CACHE = SERVICE / 'director/ctc-model'
WEIGHTS_SHA = 'd615acecbfcffca3fa04ed8bc62284ba30cf48f90f537d4d0040b1b0e75f0b1c'
FRAME_SECONDS = .04


def align_lattice(logprobs, vocab, text, blank):
    """Find a complete CTC path over exact native text and available BPE pieces.

    The export has no SentencePiece tokenizer. Allow all exact piece spellings
    instead of fabricating a tokenizer or transliterating the target.
    """
    words = text.split()
    target = '▁' + '▁'.join(words)
    if not words or len(target) > 1000 or not 1 <= len(logprobs) <= 750:
        raise ValueError('CTC alignment exceeds its bounded native-text or frame range')
    pieces = {index: piece for index, piece in vocab.items() if index != blank and piece and not piece.startswith('<')}
    matches = {position: [(position + len(piece), index) for index, piece in pieces.items()
                          if target.startswith(piece, position)] for position in range(len(target))}
    reachable = {0}
    for position in range(len(target)):
        if position in reachable:
            reachable.update(end for end, index in matches[position])
    if len(target) not in reachable:
        raise ValueError('The pinned native vocabulary cannot represent the exact supplied lyrics')
    states = [(position, blank) for position in sorted(reachable)]
    states += sorted({(end, index) for position in reachable if position < len(target)
                      for end, index in matches[position]})
    lookup = {state: index for index, state in enumerate(states)}
    groups = {position: [index for index, state in enumerate(states) if state[0] == position]
              for position in reachable}
    scores = [-math.inf] * len(states)
    scores[lookup[(0, blank)]] = 0.
    history = []
    for row in logprobs:
        if len(row) != len(vocab) or any(not math.isfinite(float(value)) or float(value) > .001 for value in row):
            raise ValueError('Finite normalized CTC log probabilities are required')
        next_scores = [-math.inf] * len(states)
        parents = [-1] * len(states)
        for position, indices in groups.items():
            ordered = sorted(indices, key=lambda index: scores[index], reverse=True)[:2]
            best = ordered[0]
            destination = lookup[(position, blank)]
            next_scores[destination] = scores[best] + float(row[blank])
            parents[destination] = best
            for index in indices:
                label = states[index][1]
                if label != blank:
                    score = scores[index] + float(row[label])
                    if score > next_scores[index]:
                        next_scores[index] = score
                        parents[index] = index
            if position == len(target):
                continue
            for end, label in matches[position]:
                parent = best if states[best][1] != label else ordered[1] if len(ordered) > 1 else None
                if parent is None:
                    continue
                destination = lookup[(end, label)]
                score = scores[parent] + float(row[label])
                if score > next_scores[destination]:
                    next_scores[destination] = score
                    parents[destination] = parent
        scores = next_scores
        history.append(parents)
    current = max(groups[len(target)], key=lambda index: scores[index])
    if not math.isfinite(scores[current]):
        raise ValueError('No complete CTC path exists for these exact lyrics')
    score = scores[current]
    path = []
    for parents in reversed(history):
        path.append(current)
        current = parents[current]
        if current < 0:
            raise ValueError('CTC path has no source-bound predecessor')
    path.reverse()
    emissions = []
    for frame, state_index in enumerate(path):
        position, label = states[state_index]
        if label == blank:
            continue
        piece = pieces[label]
        if emissions and emissions[-1]['state'] == state_index and emissions[-1]['endFrame'] == frame:
            emissions[-1]['endFrame'] += 1
            emissions[-1]['logprobs'].append(float(logprobs[frame][label]))
        else:
            emissions.append({'state': state_index, 'token': label, 'piece': piece,
                              'startCharacter': position - len(piece), 'endCharacter': position,
                              'startFrame': frame, 'endFrame': frame + 1,
                              'logprobs': [float(logprobs[frame][label])]})
    if ''.join(row['piece'] for row in emissions) != target:
        raise ValueError('CTC traceback changed or repeated the exact native text')
    output, position = [], 0
    for index, word in enumerate(words):
        end = position + len(word) + 1
        tokens = [row for row in emissions if position <= row['startCharacter'] < end]
        probability = min(math.exp(sum(row['logprobs']) / len(row['logprobs'])) for row in tokens)
        output.append({'wordIndex': index, 'text': word, 'startFrame': tokens[0]['startFrame'],
                       'endFrame': tokens[-1]['endFrame'], 'probability': probability})
        position = end
    return output, [{key: value for key, value in row.items() if key not in ['state', 'logprobs']} for row in emissions], score


def main():
    audio.managed()
    path = audio.owned_path(sys.argv[1])
    if path.stat().st_size > 65536:
        raise ValueError('Alignment request exceeds 64 KiB')
    request = json.loads(path.read_text())
    text = canonical.validate_request(request)
    if request['device'] != 'cpu' or request['language'] != 'Telugu':
        raise ValueError('This pinned CTC backend supports explicitly selected Telugu CPU execution only')
    source, output = audio.owned_path(request['sourcePath']), audio.owned_path(request['outputPath'])
    expected = {'sha256': request['sourceSha256'], 'bytes': request['sourceBytes']}
    if output.exists() or source == output or audio.file_receipt(source) != expected:
        raise ValueError('Preserve existing evidence and bind the exact frozen source')
    actual = audio.decoded_audio_duration(source)
    if abs(actual - request['sourceDuration']) > .005:
        raise ValueError('CTC source duration differs from its measured binding')
    lease = SERVICE / 'director/.cpu-alignment-lease.json'
    owner = {'service': 'release-kit-studio', 'purpose': 'ctc-lyric-alignment', 'job_id': request['jobId'],
             'owner_id': str(uuid.uuid4()), 'pid': os.getpid(), 'reserved_epoch': time.time()}
    audio.write_new(lease, owner)
    started = time.time()
    receipt = {'schemaVersion': 1, 'status': 'failed', 'request': request, 'source': expected,
               'model': MODEL, 'revision': REVISION, 'runnerSha256': audio.file_receipt(Path(__file__))['sha256'],
               'canonicalText': text, 'alignmentComplete': False, 'alignmentContractPassed': False,
               'runtime': {'device': 'cpu', 'provider': 'CPUExecutionProvider', 'computeType': 'int8', 'cpuThreads': 4},
               'lyricTimingVerified': False, 'canonicalLyricsChanged': False, 'fullSongHeard': False,
               'pilotApproved': False, 'humanAccepted': False}
    try:
        import numpy as np
        import onnxruntime as rt
        from onnx_asr.preprocessors.preprocessor import OnnxPreprocessor
        from importlib.resources import files
        import onnx_asr.preprocessors
        if importlib.metadata.version('onnx-asr') != '0.12.0':
            raise ValueError('Use the pinned isolated ONNX alignment environment')
        receipt['weights'] = audio.file_receipt(CACHE / 'model.int8.onnx')
        if receipt['weights'] != {'sha256': WEIGHTS_SHA, 'bytes': 137677313}:
            raise ValueError('CTC weights differ from the pinned export manifest')
        if json.loads((CACHE / 'config.json').read_text()) != {'model_type': 'nemo-conformer-ctc', 'features_size': 80, 'subsampling_factor': 4, 'max_tokens_per_step': 10}:
            raise ValueError('CTC feature and timing configuration changed')
        vocabulary = {int(index): piece for piece, index in (line.rsplit(' ', 1) for line in (CACHE / 'vocab.txt').read_text().splitlines())}
        if sorted(vocabulary) != list(range(257)) or vocabulary[256] != '<blk>':
            raise ValueError('The pinned Telugu CTC vocabulary changed')
        preprocessor_bytes = files(onnx_asr.preprocessors).joinpath('data/nemo80.onnx').read_bytes()
        receipt['preprocessor'] = {'package': 'onnx-asr', 'version': '0.12.0', 'sha256': hashlib.sha256(preprocessor_bytes).hexdigest(), 'bytes': len(preprocessor_bytes)}
        receipt['vocabulary'] = audio.file_receipt(CACHE / 'vocab.txt')
        if receipt['preprocessor']['sha256'] != '7ab6b0d1f57832e56f59aa7cab4289de50df7f8d5296cdfd281d9c9b7b8d73e0' or receipt['vocabulary'] != {'sha256': 'dc0b7bbb9eca8d3c8aebf1eb86e3144c90d692b4008cf5a32d46437b942b23ac', 'bytes': 2706}:
            raise ValueError('The pinned preprocessing or native vocabulary bytes changed')
        pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(source), '-ss', str(request['startSeconds']),
                              '-t', str(request['endSeconds'] - request['startSeconds']), '-ac', '1', '-ar', '16000',
                              '-f', 'f32le', '-'], check=True, capture_output=True, timeout=90).stdout
        samples = np.frombuffer(pcm, dtype='<f4').copy()
        if abs(len(samples) - round((request['endSeconds'] - request['startSeconds']) * 16000)) > 1 or not np.isfinite(samples).all():
            raise ValueError('CTC audio does not cover its exact source range')
        receipt['decodedAudio'] = {'sampleRate': 16000, 'samples': len(samples), 'sha256': hashlib.sha256(pcm).hexdigest()}
        options = rt.SessionOptions();options.intra_op_num_threads = 4;options.inter_op_num_threads = 1
        settings = {'sess_options': options, 'providers': ['CPUExecutionProvider']}
        features, lengths = OnnxPreprocessor('nemo80', settings)(samples[None], np.array([len(samples)], dtype=np.int64))
        session = rt.InferenceSession(str(CACHE / 'model.int8.onnx'), **settings)
        if session.get_providers() != ['CPUExecutionProvider'] or features.shape[0:2] != (1, 80) or not np.isfinite(features).all():
            raise ValueError('CTC must use its declared CPU provider and real native features')
        (logits,) = session.run(['logprobs'], {'audio_signal': features, 'length': lengths})
        count = int((lengths[0] - 1) // 4 + 1)
        logprobs = logits[0, :count]
        if not 1 <= count <= 750 or logprobs.shape != (count, 257) or not np.isfinite(logprobs).all():
            raise ValueError('CTC outputs differ from the real attended frame range')
        if not np.allclose(np.exp(logprobs).sum(axis=-1), 1., atol=.002):
            raise ValueError('CTC output is not normalized log-probability evidence')
        sidecar = output.with_suffix('.ctc-logprobs.npy')
        with sidecar.open('xb') as stream:
            os.chmod(sidecar, 0o600);np.save(stream, logprobs, allow_pickle=False)
        receipt['emissions'] = {'path': str(sidecar), **audio.file_receipt(sidecar)}
        receipt['modelAudioInput'] = {'featureShape': list(features.shape), 'attendedFrames': int(lengths[0]),
                                      'featureSha256': hashlib.sha256(features.tobytes()).hexdigest(),
                                      'ctcFrames': count, 'frameSeconds': FRAME_SECONDS,
                                      'ctcSha256': hashlib.sha256(logprobs.tobytes()).hexdigest()}
        labels = logprobs.argmax(axis=-1).tolist()
        greedy, previous = [], None
        for label in labels:
            if label != previous and label != 256:greedy.append(vocabulary[label])
            previous = label
        receipt['greedyRecognition'] = ''.join(greedy).replace('▁', ' ').strip()
        words, tokens, score = align_lattice(logprobs, vocabulary, text, 256)
        result, issues = [], []
        for row in words:
            codes = ['uncertain-canonical-word'] if row['probability'] < .6 else []
            start = row['startFrame'] * FRAME_SECONDS
            end = min(row['endFrame'] * FRAME_SECONDS, len(samples) / 16000)
            if start >= end:codes.append('zero-length-word-alignment')
            if row['wordIndex'] == 0 and start <= .02:codes.append('crop-boundary-onset-unresolved')
            if codes:issues.append({'wordIndex': row['wordIndex'], 'text': row['text'], 'issues': codes})
            result.append({**row, 'startSeconds': start + request['startSeconds'],
                           'endSeconds': end + request['startSeconds'], 'issues': codes, 'verified': False})
        if audio.file_receipt(source) != expected:
            raise ValueError('The frozen source changed during CTC alignment')
        receipt.update({'status': 'aligned-unverified', 'alignmentComplete': True,
                        'alignmentContractPassed': not issues, 'words': result, 'tokens': tokens,
                        'issues': issues, 'pathLogProbability': score,
                        'nativeTokenization': 'exact-piece-lattice-without-transliteration'})
    except BaseException as error:
        receipt.update({'errorType': type(error).__name__, 'error': str(error)[:1200]})
        raise
    finally:
        receipt['elapsedSeconds'] = time.time() - started
        audio.write_new(output, receipt)
        if lease.exists() and json.loads(lease.read_text()).get('owner_id') == owner['owner_id']:lease.unlink()
        print(json.dumps({'status': receipt['status'], 'outputPath': str(output), 'alignmentComplete': receipt['alignmentComplete'], 'lyricTimingVerified': False}))


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit(f'CTC alignment interrupted by signal {signum}'))
    main()
