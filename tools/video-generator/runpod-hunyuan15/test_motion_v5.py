import unittest
import json
from prepare_motion_v5 import build, BASE


class MotionPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = build()

    def test_exact_coverage(self):
        self.assertEqual(sum(j['requiredUsableFrames'] for j in self.plan['jobs']), 4482)
        self.assertTrue(all(j['requiredUsableFrames'] <= 192 for j in self.plan['jobs']))

    def test_group_coverage_and_forward_source_time(self):
        consumed = []
        for group in self.plan['generationGroups']:
            self.assertEqual((group['nativeFrames'] - 5) % 17, 0)
            self.assertLessEqual(group['nativeFrames'], 192)
            previous_end = 0
            for shot in group['placements']:
                self.assertGreaterEqual(shot['sourceInFrame'], previous_end)
                self.assertLessEqual(shot['sourceOutFrameExclusive'], group['nativeFrames'])
                previous_end = shot['sourceOutFrameExclusive']
                consumed.append(shot['cutId'])
        self.assertCountEqual(consumed, [j['jobId'] for j in self.plan['jobs']])

    def test_no_unreviewed_auto_submission(self):
        self.assertTrue(all(not j['submissionAllowed'] for j in self.plan['jobs']))
        self.assertFalse(self.plan['topUpAllowed'])

    def test_anchor_metadata_matches_actual_single_image(self):
        contract = json.loads((BASE / 'edit-contract.json').read_text())
        for cut in contract['cuts']:
            self.assertEqual(cut['motionAnchorIds'], [cut['anchorId']])

    def test_corrected_held_jobs_and_independent_bookends(self):
        jobs = {j['jobId']: j for j in self.plan['jobs']}
        self.assertEqual(jobs['C001']['anchorId'], 'S01-I04')
        self.assertEqual(jobs['C039']['anchorId'], 'S34-I02')
        self.assertEqual(jobs['C041']['anchorId'], 'S01-I04')
        self.assertNotEqual(jobs['C001']['generationId'], jobs['C041']['generationId'])


if __name__ == '__main__':
    unittest.main()
