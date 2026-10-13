WIDTH, HEIGHT, FPS = 32, 18, 24
PIXELS = WIDTH * HEIGHT
LIMIT = 256
THRESHOLDS = {'blackMeanLuma': 3, 'blackPeakLuma': 6, 'flatLumaSpread': 2,
              'staticMeanAbsoluteDelta': .2, 'staticMinimumFrames': 12,
              'abruptMeanAbsoluteDelta': 60}


def covered(start, end, intervals):
    cursor = start
    for left, right in sorted(intervals):
        if left <= cursor < right:
            cursor = right
        if cursor >= end:
            return True
    return False


def analyze_frames(data, project, comp):
    count = comp['frames']
    if type(count) is not int or not 1 <= count <= 21600 or len(data) != count * PIXELS:
        raise ValueError('Diagnostic decode differs from the exact frame count.')
    image = comp['id'] in {'thumbnail', 'artwork'}
    assets = {asset['id']: asset for asset in project['assets']}
    holds, fades, joins = [], [], set()
    for clip in comp['clips']:
        start, end = clip['at'], clip['at'] + clip['frames']
        if assets[clip['assetId']]['kind'] == 'image':
            holds.append((start, end))
        if clip['fadeIn']:
            fades.append((start, start + clip['fadeIn']))
        if clip['fadeOut']:
            fades.append((end - clip['fadeOut'], end))
        if start:
            joins.add(start)
    black, flat, static, abrupt, seams = [], [], [], [], []
    counters = {'nearBlackFrames': 0, 'flatFrames': 0, 'nearStaticFrames': 0,
                'nearBlackRanges': 0, 'flatRanges': 0, 'nearStaticRanges': 0,
                'abruptChanges': 0, 'unplannedFindingRanges': 0}
    omitted = {'nearBlackRanges': 0, 'flatRanges': 0, 'nearStaticRanges': 0, 'abruptChanges': 0}
    active = {}

    def finish(name, end):
        row = active.pop(name, None)
        if row is None or name == 'nearStaticRanges' and end - row['startFrame'] < THRESHOLDS['staticMinimumFrames']:
            return
        start = row['startFrame']
        expected_fade = covered(start, end, fades)
        expected_hold = name == 'nearStaticRanges' and covered(start, end, holds)
        row.update({'endFrame': end, 'expected': expected_fade or expected_hold,
                    'context': 'declared-image-hold' if expected_hold else 'planned-fade' if expected_fade else 'no-declared-exemption'})
        counters[name] += 1
        if name == 'nearStaticRanges':
            counters['nearStaticFrames'] += end - start
        if not row['expected']:
            counters['unplannedFindingRanges'] += 1
        target = {'nearBlackRanges': black, 'flatRanges': flat, 'nearStaticRanges': static}[name]
        if len(target) < LIMIT:
            target.append(row)
        else:
            omitted[name] += 1

    def collect(name, frame, condition, metrics, include_previous=False):
        if not condition:
            finish(name, frame)
            return
        if name not in active:
            active[name] = {'startFrame': frame - int(include_previous), **metrics}
        else:
            for key, value in metrics.items():
                active[name][key] = max(active[name][key], value)

    previous = None
    for frame in range(count):
        pixels = data[frame * PIXELS:(frame + 1) * PIXELS]
        mean, peak, spread = sum(pixels) / PIXELS, max(pixels), max(pixels) - min(pixels)
        is_black = mean <= THRESHOLDS['blackMeanLuma'] and peak <= THRESHOLDS['blackPeakLuma']
        is_flat = spread <= THRESHOLDS['flatLumaSpread']
        counters['nearBlackFrames'] += int(is_black)
        counters['flatFrames'] += int(is_flat)
        collect('nearBlackRanges', frame, is_black, {'maximumMeanLuma': mean, 'maximumPeakLuma': peak})
        collect('flatRanges', frame, is_flat, {'maximumLumaSpread': spread})
        if previous is not None:
            deltas = [abs(left - right) for left, right in zip(previous, pixels)]
            mean_delta = sum(deltas) / PIXELS
            if not image:
                collect('nearStaticRanges', frame, mean_delta <= THRESHOLDS['staticMeanAbsoluteDelta'],
                        {'maximumMeanAbsoluteDelta': mean_delta}, include_previous=True)
            if frame in joins or mean_delta >= THRESHOLDS['abruptMeanAbsoluteDelta']:
                row = {'atFrame': frame, 'meanAbsoluteDelta': mean_delta, 'maximumPixelDelta': max(deltas), 'plannedCut': frame in joins}
                if frame in joins:
                    seams.append(row)
                if mean_delta >= THRESHOLDS['abruptMeanAbsoluteDelta']:
                    counters['abruptChanges'] += 1
                    counters['unplannedFindingRanges'] += int(frame not in joins)
                    if len(abrupt) < LIMIT:
                        abrupt.append(row)
                    else:
                        omitted['abruptChanges'] += 1
        previous = pixels
    for name in list(active):
        finish(name, count)
    return {'schemaVersion': 1, 'method': 'all-frame-reduced-rgb-luma/v1', 'width': WIDTH, 'height': HEIGHT,
            'timebaseFps': FPS, 'sampledFrames': count, 'completeFrameCoverage': True, 'motionExpected': not image,
            'thresholds': THRESHOLDS.copy(), 'counts': counters, 'omittedFindings': omitted,
            'nearBlackRanges': black, 'flatRanges': flat, 'nearStaticRanges': static,
            'abruptChanges': abrupt, 'joinMeasurements': seams,
            'reviewSuggested': counters['unplannedFindingRanges'] > 0, 'semanticReviewed': False}
