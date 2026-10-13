"""A real render can be technically valid while coverage and craft reviews are absent."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from finish_review import check, empty_review, inventory, required_frames, CHECKS


class FinishReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        self.plan = base / 'timeline.json'
        self.render = base / 'render.mp4'
        self.plan.write_text(json.dumps({'timeline': 'Synthetic', 'frames': 12,
            'shots': [{'id': 'wide', 'recordStart': 0, 'recordEnd': 6},
                      {'id': 'close', 'recordStart': 6, 'recordEnd': 12}],
            'overlays': [{'id': 'L01', 'start': 3, 'end': 9}]}))
        self.render.write_bytes(b'synthetic export fixture')
        self.review = empty_review(self.plan, self.render)

    def fill(self):
        for kind, entries in inventory(json.loads(self.plan.read_text())).items():
            for item_id, rng in entries.items():
                row = self.review[kind][item_id]
                row['verdict'] = 'pass'
                row['inspected_frames'] = sorted(required_frames(rng))
                row['checks'] = {name: {'verdict': 'pass', 'evidence': f'{name} observed in fixture'}
                                 for name in CHECKS[kind]}
                if kind == 'joins':
                    row['intended_method'] = row['rendered_method'] = 'action cut'

    def test_unreviewed_render_and_missing_event_are_not_passed(self):
        result = check(self.plan, self.render, self.review)
        self.assertEqual(result['counts'], {'shots': 2, 'lyrics': 1, 'joins': 1})
        self.assertEqual(result['status'], 'pending_or_failed')
        self.fill()
        del self.review['joins']['wide__close']
        self.assertIn('joins: missing', ' '.join(check(self.plan, self.render, self.review)['issues']))

    def test_pass_requires_every_event_and_exact_render_revision(self):
        self.fill()
        self.assertEqual(check(self.plan, self.render, self.review)['status'], 'pass')
        self.render.write_bytes(b'a different render')
        self.assertIn('render bytes changed', ' '.join(check(self.plan, self.render, self.review)['issues']))

    def test_uncorrected_cropped_subject_and_unrealized_transition_block(self):
        self.fill()
        self.review['shots']['close']['checks']['composition'] = {
            'verdict': 'fail', 'evidence': 'Lead head leaves frame at midpoint'}
        join = self.review['joins']['wide__close']
        join['intended_method'] = 'motion match'
        join['rendered_method'] = 'plain cut'
        issues = ' '.join(check(self.plan, self.render, self.review)['issues'])
        self.assertIn('shots.close.composition', issues)
        self.assertIn('method changed without a reviewed reason', issues)

    def test_no_lyric_project_and_gapped_timeline(self):
        plan = json.loads(self.plan.read_text())
        plan.pop('overlays')
        self.assertEqual(inventory(plan)['lyrics'], {})
        plan['shots'][1]['recordStart'] = 7
        with self.assertRaisesRegex(ValueError, 'without gaps'):
            inventory(plan)


if __name__ == '__main__':
    unittest.main()
