#!/usr/bin/env python3
"""Create/check a per-shot, text/lyric, and join review bound to a video render.

The tool checks coverage and evidence shape. It cannot see or hear the film.
The plan must be exported/read back from the actual edited timeline.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys


CHECKS = {
    'shots': ('composition', 'critical_content', 'focus', 'motion'),
    'lyrics': ('legibility', 'visual_integration', 'subject_clearance', 'timing'),
    'text': ('legibility', 'visual_integration', 'subject_clearance', 'timing', 'content_accuracy'),
    'joins': ('visual_motivation', 'rendered_execution', 'edges', 'playback'),
}


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def frame_range(item, start_key, end_key, total):
    start, end = item[start_key], item[end_key]
    if type(start) is not int or type(end) is not int or not 0 <= start < end <= total:
        raise ValueError(f'Invalid frame range: {item.get("id")}')
    return start, end


def inventory(plan):
    total = plan['frames']
    if type(total) is not int or total <= 0 or not isinstance(plan.get('shots'), list) or not plan['shots']:
        raise ValueError('Expected a positive frame count and nonempty shot list')
    shots, lyrics, joins = {}, {}, {}
    cursor = 0
    for shot in plan['shots']:
        sid = shot['id']
        start, end = frame_range(shot, 'recordStart', 'recordEnd', total)
        if not isinstance(sid, str) or not sid or sid in shots or start != cursor:
            raise ValueError('Shot IDs must be unique and ranges must cover the timeline without gaps')
        shots[sid] = [start, end]
        cursor = end
    if cursor != total:
        raise ValueError('Last shot does not cover the render tail')
    previous = None
    for sid in shots:
        if previous is not None:
            joins[f'{previous}__{sid}'] = [shots[previous][1] - 1, shots[sid][0]]
        previous = sid
    events = plan.get('lyric_events')
    if events is None:
        events = [x for x in plan.get('overlays', [])
                  if x.get('role') == 'lyrics' or (not x.get('role') and isinstance(x.get('id'), str) and
                                                 x['id'].startswith('L') and x['id'][1:].isdigit())]
    for item in events:
        lid = item['id']
        if not isinstance(lid, str) or not lid or lid in lyrics:
            raise ValueError('Lyric event IDs must be unique')
        lyrics[lid] = list(frame_range(item, 'start', 'end', total))
    result = {'shots': shots, 'lyrics': lyrics, 'joins': joins}
    text_events = plan.get('text_events')
    if text_events is None:
        text_events = [x for x in plan.get('overlays', [])
                       if x.get('role') and x['role'] != 'lyrics']
    if text_events or 'text_events' in plan:
        text = {}
        for item in text_events:
            tid, role = item['id'], item.get('role')
            if not isinstance(tid, str) or not tid or tid in text or tid in lyrics:
                raise ValueError('Text event IDs must be unique across text and lyrics')
            if not isinstance(role, str) or not role.strip() or role == 'lyrics':
                raise ValueError('Text events require an explicit non-lyric role')
            text[tid] = list(frame_range(item, 'start', 'end', total))
        result['text'] = text
    return result


def required_frames(ranges):
    start, end = ranges
    return {start, (start + end - 1) // 2, end - 1}


def empty_review(plan_path, render_path):
    plan = json.loads(plan_path.read_text())
    items = inventory(plan)
    review = {'schema_version': 1, 'timeline': plan.get('timeline'), 'plan_sha256': digest(plan_path),
              'render_sha256': digest(render_path), 'render': str(render_path.resolve()),
              'note': 'Fill only after inspecting these events in this exact render; pending is not approval.'}
    for kind, expected in items.items():
        review[kind] = {}
        for item_id in expected:
            row = {'verdict': 'pending', 'inspected_frames': [],
                   'checks': {name: {'verdict': 'pending', 'evidence': ''} for name in CHECKS[kind]}}
            if kind == 'joins':
                row.update(intended_method='', rendered_method='', deviation_evidence='')
            review[kind][item_id] = row
    return review


def check(plan_path, render_path, review):
    plan = json.loads(plan_path.read_text())
    expected = inventory(plan)
    issues = []
    if review.get('schema_version') != 1 or review.get('timeline') != plan.get('timeline'):
        issues.append('Review schema or timeline differs')
    if review.get('plan_sha256') != digest(plan_path) or review.get('render_sha256') != digest(render_path):
        issues.append('Plan or render bytes changed after review')
    for kind, entries in expected.items():
        rows = review.get(kind, {})
        if not isinstance(rows, dict):
            issues.append(f'{kind}: missing review map')
            continue
        if set(rows) != set(entries):
            issues.append(f'{kind}: missing {sorted(set(entries)-set(rows))}; extra {sorted(set(rows)-set(entries))}')
        for item_id, rng in entries.items():
            row = rows.get(item_id)
            if not isinstance(row, dict):
                continue
            if row.get('verdict') != 'pass':
                issues.append(f'{kind}.{item_id}: {row.get("verdict", "unreviewed")}')
            observed = row.get('inspected_frames', [])
            if not isinstance(observed, list) or not all(type(n) is int for n in observed) or not required_frames(rng).issubset(set(observed)):
                issues.append(f'{kind}.{item_id}: inspect opening, middle and closing frames')
            for name in CHECKS[kind]:
                item = row.get('checks', {}).get(name, {})
                if item.get('verdict') != 'pass' or not isinstance(item.get('evidence'), str) or not item['evidence'].strip():
                    issues.append(f'{kind}.{item_id}.{name}: no passing observation')
            if kind == 'joins':
                before = row.get('intended_method', '').strip()
                after = row.get('rendered_method', '').strip()
                if not before or not after:
                    issues.append(f'{kind}.{item_id}: intended/rendered method missing')
                elif before != after and not row.get('deviation_evidence', '').strip():
                    issues.append(f'{kind}.{item_id}: method changed without a reviewed reason')
    return {'status': 'pass' if not issues else 'pending_or_failed',
            'counts': {kind: len(entries) for kind, entries in expected.items()}, 'issues': issues}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', required=True, type=Path, help='Plan reconciled with actual editor timeline readback')
    parser.add_argument('--render', required=True, type=Path, help='Exact final exported file')
    parser.add_argument('--review', required=True, type=Path)
    parser.add_argument('command', choices=('init', 'check'))
    args = parser.parse_args()
    try:
        if args.command == 'init':
            blank = empty_review(args.plan, args.render)
            with args.review.open('x') as stream:
                json.dump(blank, stream, indent=2)
                stream.write('\n')
            print(json.dumps({'status': 'pending', 'review': str(args.review)}))
            return 0
        result = check(args.plan, args.render, json.loads(args.review.read_text()))
        print(json.dumps({**result, 'issue_count': len(result['issues']),
                          'issues': result['issues'][:50]}, indent=2))
        return 0 if result['status'] == 'pass' else 1
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        print(json.dumps({'error': str(error)}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
