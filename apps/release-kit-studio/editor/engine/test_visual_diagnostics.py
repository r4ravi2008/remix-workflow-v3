import importlib.util
from pathlib import Path
import unittest


spec = importlib.util.spec_from_file_location('visual_test', Path(__file__).with_name('visual_diagnostics.py'))
visual = importlib.util.module_from_spec(spec)
spec.loader.exec_module(visual)
PATTERN = bytes([40, 180] * (visual.PIXELS // 2))


class FrameDiagnosticTests(unittest.TestCase):
    def fixture(self, frames, kind='video', fade=0, splits=()):
        starts = [0, *splits, frames]
        clips = [{'assetId': 'scene', 'at': start, 'frames': end - start,
                  'fadeIn': fade if start == 0 else 0, 'fadeOut': 0}
                 for start, end in zip(starts, starts[1:])]
        return {'assets': [{'id': 'scene', 'kind': kind}]}, {'id': 'film', 'frames': frames, 'clips': clips}

    def test_full_terminal_freeze_is_reported_but_declared_image_hold_is_expected(self):
        for kind, expected in [('video', False), ('image', True)]:
            project, comp = self.fixture(24, kind)
            result = visual.analyze_frames(PATTERN * 24, project, comp)
            self.assertEqual(result['nearStaticRanges'][0]['startFrame'], 0)
            self.assertEqual(result['nearStaticRanges'][0]['endFrame'], 24)
            self.assertEqual(result['nearStaticRanges'][0]['expected'], expected)
            self.assertEqual(result['reviewSuggested'], not expected)
            self.assertFalse(result['semanticReviewed'])

    def test_only_declared_fade_exempts_a_black_range(self):
        moving = b''.join(bytes([30 + index, 60 + index] * (visual.PIXELS // 2)) for index in range(12))
        for fade, expected in [(0, False), (12, True)]:
            project, comp = self.fixture(24, fade=fade)
            result = visual.analyze_frames(bytes(visual.PIXELS * 12) + moving, project, comp)
            black = result['nearBlackRanges'][0]
            self.assertEqual((black['startFrame'], black['endFrame']), (0, 12))
            self.assertEqual(black['expected'], expected)
            self.assertEqual(result['reviewSuggested'], not expected)

    def test_one_black_frame_in_the_middle_is_not_hidden_by_a_head_fade(self):
        project, comp = self.fixture(25, 'image', fade=3)
        result = visual.analyze_frames(PATTERN * 12 + bytes(visual.PIXELS) + PATTERN * 12, project, comp)
        row = result['nearBlackRanges'][0]
        self.assertEqual((row['startFrame'], row['endFrame'], row['expected']), (12, 13, False))
        self.assertTrue(result['reviewSuggested'])

    def test_every_planned_join_is_measured_and_an_internal_jump_remains_distinct(self):
        project, comp = self.fixture(24, splits=[12])
        result = visual.analyze_frames(bytes([40]) * visual.PIXELS * 12 + bytes([200]) * visual.PIXELS * 12, project, comp)
        self.assertEqual(result['joinMeasurements'][0]['atFrame'], 12)
        self.assertEqual(result['joinMeasurements'][0]['meanAbsoluteDelta'], 160)
        self.assertTrue(result['abruptChanges'][0]['plannedCut'])
        project, comp = self.fixture(24)
        result = visual.analyze_frames(bytes([40]) * visual.PIXELS * 12 + bytes([200]) * visual.PIXELS * 12, project, comp)
        self.assertFalse(result['abruptChanges'][0]['plannedCut'])

    def test_findings_are_bounded_without_omitting_coverage_or_total_counts(self):
        project, comp = self.fixture(600)
        result = visual.analyze_frames((bytes(visual.PIXELS) + PATTERN) * 300, project, comp)
        self.assertEqual(result['sampledFrames'], 600)
        self.assertTrue(result['completeFrameCoverage'])
        self.assertEqual(result['counts']['nearBlackRanges'], 300)
        self.assertEqual(len(result['nearBlackRanges']), 256)
        self.assertEqual(result['omittedFindings']['nearBlackRanges'], 44)
        self.assertTrue(result['reviewSuggested'])

    def test_short_or_extra_decode_cannot_claim_complete_coverage(self):
        project, comp = self.fixture(24)
        for data in [PATTERN * 23, PATTERN * 25, PATTERN * 24 + b'x']:
            with self.assertRaisesRegex(ValueError, 'exact frame count'):
                visual.analyze_frames(data, project, comp)


if __name__ == '__main__':
    unittest.main()
