#!/usr/bin/env python3
"""Audit recorded reviews; never infer perceptual quality from file integrity."""
import argparse
import hashlib
import json
from pathlib import Path
import sys


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def component_fingerprint(record):
    return fingerprint({k: v for k, v in record.items() if k != "review"})


def file_hash(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rating(value):
    return type(value) is int and 0 <= value <= 4


def valid_ranges(ranges, frame_count):
    return (isinstance(ranges, list) and bool(ranges) and
            all(isinstance(pair, list) and len(pair) == 2 and
                all(type(n) is int for n in pair) and
                0 <= pair[0] < pair[1] <= frame_count for pair in ranges))


def uncovered_ranges(required, observed):
    """Return gaps in half-open frame ranges; overlapping observations count once."""
    gaps = []
    for start, end in required:
        cursor = start
        for lo, hi in sorted(observed):
            if hi <= cursor or lo >= end:
                continue
            if lo > cursor:
                gaps.append([cursor, min(lo, end)])
            cursor = min(end, max(cursor, hi))
        if cursor < end:
            gaps.append([cursor, end])
    return gaps


def require_template_coverage(policy, template):
    """Keep project overrides while requiring all current safety checks."""
    for kind, rule in template['kinds'].items():
        local = policy.get('kinds', {}).get(kind)
        require(isinstance(local, dict), f'Project policy lacks template kind: {kind}')
        for field in ('criteria', 'hard_gates'):
            missing = set(rule[field]) - set(local.get(field, []))
            require(not missing, f'Project policy lacks {kind}.{field}: {sorted(missing)}')
    for kind, rule in template.get('timed_review', {}).items():
        local = policy.get('timed_review', {}).get(kind, {})
        require(local.get('scope') == rule['scope'] and
                set(rule['methods']).issubset(set(local.get('methods', []))),
                f'Project policy lacks current {kind} timed_review requirement')


def audit(policy, manifest, base, template=None):
    if template is not None:
        require_template_coverage(policy, template)
    require(policy['schemaVersion'] == 1 and manifest['schemaVersion'] == 1, 'Unsupported schema')
    minimum = policy['profiles'][policy['profile']]
    require(rating(minimum), 'Invalid profile minimum')
    require(type(policy['max_attempts_per_component']) is int and policy['max_attempts_per_component'] > 0, 'Invalid attempt limit')
    kinds = policy['kinds']
    require(bool(kinds), 'No component rubrics')
    timed_rules = policy.get('timed_review', {})
    require(isinstance(timed_rules, dict), 'Invalid timed_review rules')
    for kind, rule in timed_rules.items():
        require(kind in kinds and rule.get('scope') in ('full', 'declared'), 'Invalid timed review scope')
        methods = rule.get('methods')
        require(isinstance(methods, list) and bool(methods) and
                len(methods) == len(set(methods)) and
                all(m in ('watched_normal_speed', 'heard') for m in methods),
                f'{kind}: invalid timed review methods')
    for kind, rule in kinds.items():
        for field in ('criteria', 'hard_gates'):
            names = rule[field]
            require(isinstance(names, list) and names and all(isinstance(n, str) and n for n in names), f'{kind}: invalid {field}')
            require(len(names) == len(set(names)), f'{kind}: duplicate {field}')
    for kind, overrides in policy.get('overrides', {}).items():
        require(kind in kinds, f'Unknown override kind: {kind}')
        for criterion, value in overrides.items():
            require(criterion in kinds[kind]['criteria'] and rating(value), f'Invalid override: {kind}.{criterion}')
    records = manifest['components']
    require(isinstance(records, list) and records, 'No components')
    index = {}
    for record in records:
        cid = record['id']
        require(isinstance(cid, str) and cid and cid not in index, 'Missing or duplicate ID')
        require(record['kind'] in kinds, f'{cid}: unknown kind')
        require(isinstance(record['revision'], str) and bool(record['revision']), f'{cid}: missing revision')
        require(bool(record.get('intended_use')), f'{cid}: missing intended use')
        require(isinstance(record.get('dependencies'), list), f'{cid}: missing dependency list')
        require(isinstance(record.get('artifacts'), list) and bool(record['artifacts']), f'{cid}: no artifacts')
        index[cid] = record
    targets = manifest['targets']
    require(isinstance(targets, list) and targets and all(t in index for t in targets), 'Missing/unknown targets')
    results, visiting = {}, set()
    policy_hash = fingerprint(policy)

    def inspect(cid):
        if cid in results:
            return results[cid]
        require(cid not in visiting, f'Dependency cycle at {cid}')
        visiting.add(cid)
        record = index[cid]
        issues = []
        def issue(status, message):
            issues.append({'status': status, 'reason': message})
        for artifact in record['artifacts']:
            path = base / artifact['path']
            if not path.is_file():
                issue('stale', f'Missing artifact: {artifact["path"]}')
            elif file_hash(path) != artifact['sha256']:
                issue('stale', f'Artifact changed: {artifact["path"]}')
        review = record.get('review') or {}
        if not review:
            issue('pending', 'No review')
        else:
            if review.get('revision') != record['revision'] or review.get('policy_sha256') != policy_hash:
                issue('stale', 'Review revision or policy changed')
            if review.get('component_sha256') != component_fingerprint(record):
                issue('stale', 'Reviewed component definition changed')
            for field in ('reviewer', 'method', 'scope'):
                if not isinstance(review.get(field), str) or not review[field].strip():
                    issue('pending', f'Missing review {field}')
        def evidence(item):
            return isinstance(item.get('evidence'), str) and bool(item['evidence'].strip())
        rule = kinds[record['kind']]
        timed = timed_rules.get(record['kind'])
        if timed:
            count = record.get('frame_count')
            if type(count) is not int or count <= 0:
                issue('pending', 'Timed review requires positive decoded frame_count')
            else:
                required = ([[0, count]] if timed['scope'] == 'full' else
                            record.get('review_ranges', [[0, count]]))
                if not valid_ranges(required, count):
                    issue('pending', 'Invalid required review_ranges')
                else:
                    sessions = review.get('sessions', [])
                    if not isinstance(sessions, list):
                        sessions = []
                    for method in timed['methods']:
                        observed = []
                        for session in sessions:
                            if not isinstance(session, dict) or session.get('method') != method:
                                continue
                            if evidence(session) and valid_ranges(session.get('ranges'), count):
                                observed.extend(session['ranges'])
                        gaps = uncovered_ranges(required, observed)
                        if gaps:
                            issue('pending', f'{method} coverage missing frames: {gaps}')
        for gate in rule['hard_gates']:
            item = review.get('gates', {}).get(gate, {})
            if item.get('verdict') == 'fail':
                issue('rejected', f'Hard gate failed: {gate}')
            elif item.get('verdict') != 'pass' or not evidence(item):
                issue('pending', f'Hard gate unproven: {gate}')
        for criterion in rule['criteria']:
            item = review.get('criteria', {}).get(criterion, {})
            if item.get('status') == 'not_applicable':
                if not evidence(item):
                    issue('pending', f'Unjustified N/A: {criterion}')
                continue
            score = item.get('score')
            if item.get('status') != 'rated' or not rating(score) or not evidence(item):
                issue('pending', f'Criterion unreviewed: {criterion}')
            else:
                threshold = policy.get('overrides', {}).get(record['kind'], {}).get(criterion, minimum)
                if score < threshold:
                    issue('rejected', f'{criterion}: {score} below {threshold}')
        for dependency in record['dependencies']:
            did = dependency['id']
            require(did in index, f'{cid}: unknown dependency {did}')
            if dependency['revision'] != index[did]['revision']:
                issue('stale', f'Dependency revision changed: {did}')
            outcome = inspect(did)
            if outcome['status'] != 'accepted':
                issue('blocked', f'Dependency {did} is {outcome["status"]}')
        visiting.remove(cid)
        priority = ('stale', 'rejected', 'pending', 'blocked')
        status = next((s for s in priority if any(i['status'] == s for i in issues)), 'accepted')
        results[cid] = {'status': status, 'issues': issues}
        return results[cid]

    for cid in index:
        inspect(cid)
    return {'policy_sha256': policy_hash, 'targets_pass': all(results[t]['status'] == 'accepted' for t in targets), 'components': results}


def main(default_template=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--policy', type=Path)
    parser.add_argument('--manifest', type=Path)
    parser.add_argument('--template', type=Path,
                        default=default_template or Path(__file__).parent.parent / 'assets/quality-policy.json',
                        help='Current category template; defaults to shared video policy')
    parser.add_argument('--fingerprint', action='store_true')
    parser.add_argument('--check-policy', action='store_true', help='Compare a project policy with the current skill template')
    parser.add_argument('--example', action='store_true')
    parser.add_argument('--fingerprint-components', action='store_true')
    args = parser.parse_args()
    if args.example:
        print(json.dumps({'schemaVersion': 1, 'targets': ['frame-01'], 'components': [{
            'id': 'frame-01', 'kind': 'image', 'revision': 'v1', 'intended_use': 'Shot 2 accepted motion anchor',
            'artifacts': [{'path': 'frames/frame-01.png', 'sha256': '<actual file hash>'}],
            'dependencies': [{'id': 'storyboard', 'revision': 'v1'}],
            'review': {'revision': 'v1', 'policy_sha256': '<fingerprint>', 'component_sha256': '<component fingerprint>', 'reviewer': '<reviewer>',
                       'method': '<actual inspection method>', 'scope': '<whole frame and references>',
                       'gates': {'references_compared': {'verdict': 'pass', 'evidence': '<observations and evidence path>'}},
                       'criteria': {'identity': {'status': 'rated', 'score': 3, 'evidence': '<specific comparison>'}}}
        }]}, indent=2))
        print('Example is intentionally incomplete: add the dependency record and every applicable policy check.', file=sys.stderr)
        return 0
    try:
        if args.fingerprint_components:
            require(args.manifest is not None, '--manifest is required')
            records = json.loads(args.manifest.read_text())['components']
            print(json.dumps({r['id']: component_fingerprint(r) for r in records}, indent=2))
            return 0
        require(args.policy is not None, '--policy is required')
        policy = json.loads(args.policy.read_text())
        if args.check_policy:
            template = json.loads(args.template.read_text())
            require_template_coverage(policy, template)
            print(json.dumps({'status': 'current-template-covered', 'policy_sha256': fingerprint(policy)}))
            return 0
        if args.fingerprint:
            print(fingerprint(policy))
            return 0
        require(args.manifest is not None, '--manifest is required')
        template = json.loads(args.template.read_text())
        report = audit(policy, json.loads(args.manifest.read_text()), args.manifest.resolve().parent, template)
        print(json.dumps(report, indent=2))
        return 0 if report['targets_pass'] else 1
    except (ValueError, KeyError, TypeError, AttributeError, OSError) as error:
        print(json.dumps({'error': str(error)}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
