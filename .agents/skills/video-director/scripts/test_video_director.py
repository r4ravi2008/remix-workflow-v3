"""Shared text review and factual dependency checks using synthetic fixtures only."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from finish_review import CHECKS, check, empty_review, inventory, required_frames
from quality_gate import audit, component_fingerprint, file_hash, fingerprint


SKILL = Path(__file__).resolve().parent.parent
MUSIC = SKILL.parent / 'music-video-director'


class TextReviewTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.base = Path(tmp.name)
        self.plan_path = self.base / 'timeline.json'
        self.render = self.base / 'synthetic.bin'
        self.render.write_bytes(b'synthetic fixture, not actual video')
        self.plan = {'timeline': 'Synthetic', 'frames': 24,
                     'shots': [{'id': 'S01', 'recordStart': 0, 'recordEnd': 24}],
                     'text_events': [
                         {'id': 'C01', 'role': 'captions', 'start': 0, 'end': 12},
                         {'id': 'SRC01', 'role': 'source', 'start': 0, 'end': 24},
                         {'id': 'AI01', 'role': 'label', 'start': 12, 'end': 24}]}
        self.plan_path.write_text(json.dumps(self.plan))

    def complete_review(self):
        review = empty_review(self.plan_path, self.render)
        for kind, items in inventory(self.plan).items():
            for item_id, frames in items.items():
                row = review[kind][item_id]
                row.update(verdict='pass', inspected_frames=sorted(required_frames(frames)))
                row['checks'] = {name: {'verdict': 'pass', 'evidence': 'Synthetic test observation'}
                                 for name in CHECKS[kind]}
        return review

    def test_all_text_roles_need_current_render_evidence(self):
        review = self.complete_review()
        self.assertEqual(check(self.plan_path, self.render, review)['status'], 'pass')
        del review['text']['AI01']
        self.assertIn('text: missing', ' '.join(check(self.plan_path, self.render, review)['issues']))

    def test_readable_but_inaccurate_caption_fails(self):
        review = self.complete_review()
        review['text']['C01']['checks']['content_accuracy'] = {
            'verdict': 'fail', 'evidence': 'Synthetic caption changes a qualifier'}
        self.assertIn('text.C01.content_accuracy',
                      ' '.join(check(self.plan_path, self.render, review)['issues']))

    def test_legacy_lyric_id_does_not_override_explicit_source_role(self):
        self.plan.pop('text_events')
        self.plan['overlays'] = [{'id': 'L01', 'role': 'source', 'start': 0, 'end': 24},
                                 {'id': 'L02', 'start': 0, 'end': 24}]
        result = inventory(self.plan)
        self.assertEqual(set(result['lyrics']), {'L02'})
        self.assertEqual(set(result['text']), {'L01'})

    def test_changed_text_definition_invalidates_review(self):
        review = self.complete_review()
        self.plan['text_events'][0]['claimIds'] = ['a-different-claim']
        self.plan_path.write_text(json.dumps(self.plan))
        self.assertIn('Plan or render bytes changed',
                      ' '.join(check(self.plan_path, self.render, review)['issues']))

    def test_invalid_or_duplicate_text_ranges_are_rejected(self):
        self.plan['text_events'][0]['end'] = 25
        with self.assertRaises(ValueError):
            inventory(self.plan)
        self.plan['text_events'][0]['end'] = 12
        self.plan['text_events'][1]['id'] = 'C01'
        with self.assertRaisesRegex(ValueError, 'unique'):
            inventory(self.plan)


class NewsQualityTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.base = Path(tmp.name)
        self.policy = json.loads((SKILL / 'assets/news-quality-policy.json').read_text())
        self.manifest = {'schemaVersion': 1, 'targets': ['export'], 'components': []}
        previous = None
        for kind in ('claims', 'script', 'narration', 'captions', 'export'):
            path = self.base / f'{kind}.bin'
            path.write_bytes(f'Synthetic {kind}'.encode())
            record = {'id': kind, 'kind': kind, 'revision': 'v1', 'intended_use': 'Synthetic check',
                      'artifacts': [{'path': path.name, 'sha256': file_hash(path)}],
                      'dependencies': [{'id': previous, 'revision': 'v1'}] if previous else []}
            rule = self.policy['kinds'][kind]
            review = {'revision': 'v1', 'policy_sha256': fingerprint(self.policy),
                      'reviewer': 'Synthetic test', 'method': 'Fixture', 'scope': 'Synthetic only',
                      'gates': {g: {'verdict': 'pass', 'evidence': 'Synthetic fixture'}
                                for g in rule['hard_gates']},
                      'criteria': {c: {'status': 'rated', 'score': 4, 'evidence': 'Synthetic fixture'}
                                   for c in rule['criteria']}}
            timed = self.policy['timed_review'].get(kind)
            if timed:
                record['frame_count'] = 24
                review['sessions'] = [{'method': m, 'ranges': [[0, 24]], 'evidence': 'Synthetic fixture'}
                                      for m in timed['methods']]
            review['component_sha256'] = component_fingerprint(record)
            record['review'] = review
            self.manifest['components'].append(record)
            previous = kind

    def test_unverified_fact_blocks_every_consumer_despite_high_ratings(self):
        self.assertTrue(audit(self.policy, self.manifest, self.base, self.policy)['targets_pass'])
        self.manifest['components'][0]['review']['gates']['material_claims_checked']['verdict'] = 'fail'
        report = audit(self.policy, self.manifest, self.base, self.policy)
        self.assertEqual(report['components']['claims']['status'], 'rejected')
        for kind in ('script', 'narration', 'captions', 'export'):
            self.assertEqual(report['components'][kind]['status'], 'blocked')

    def test_changed_source_fact_cannot_keep_an_old_script_acceptance(self):
        claim = self.manifest['components'][0]
        path = self.base / claim['artifacts'][0]['path']
        path.write_bytes(b'Changed synthetic claim')
        claim['artifacts'][0]['sha256'] = file_hash(path)
        report = audit(self.policy, self.manifest, self.base, self.policy)
        self.assertEqual(report['components']['claims']['status'], 'stale')
        self.assertEqual(report['components']['export']['status'], 'blocked')

    def test_narration_requires_full_heard_take(self):
        voice = self.manifest['components'][2]
        voice['review_ranges'] = [[0, 12]]
        voice['review']['component_sha256'] = component_fingerprint(voice)
        voice['review']['sessions'][0]['ranges'] = [[0, 12]]
        report = audit(self.policy, self.manifest, self.base, self.policy)
        self.assertEqual(report['components']['narration']['status'], 'pending')
        self.assertFalse(report['targets_pass'])

    def test_category_template_cli_and_music_default_remain_distinct(self):
        def run(script, *args):
            return subprocess.run([sys.executable, str(script), *map(str, args)],
                                  capture_output=True, text=True)
        music = run(MUSIC / 'scripts/quality_gate.py', '--policy',
                    MUSIC / 'assets/quality-policy.json', '--check-policy')
        self.assertEqual(music.returncode, 0, music.stderr)
        news = run(SKILL / 'scripts/quality_gate.py', '--policy',
                   SKILL / 'assets/news-quality-policy.json', '--template',
                   SKILL / 'assets/news-quality-policy.json', '--check-policy')
        self.assertEqual(news.returncode, 0, news.stderr)
        missing_factual_gates = run(SKILL / 'scripts/quality_gate.py', '--policy',
                                   SKILL / 'assets/quality-policy.json', '--template',
                                   SKILL / 'assets/news-quality-policy.json', '--check-policy')
        self.assertEqual(missing_factual_gates.returncode, 2)
        self.assertIn('Project policy lacks', missing_factual_gates.stderr)


if __name__ == '__main__':
    unittest.main()
