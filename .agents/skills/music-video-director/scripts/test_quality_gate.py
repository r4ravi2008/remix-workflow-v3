"""Synthetic acceptance-record tests; these do not assert real media quality."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from quality_gate import audit, component_fingerprint, file_hash, fingerprint, require_template_coverage


class QualityGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.policy = json.loads((Path(__file__).parent.parent / 'assets/quality-policy.json').read_text())
        self.manifest = {'schemaVersion': 1, 'targets': ['motion'], 'components': []}
        for cid, kind, deps in [('image', 'image', []), ('motion', 'motion', [{'id': 'image', 'revision': 'v1'}])]:
            path = self.base / (cid + '.txt')
            path.write_text('Synthetic fixture, not media quality evidence.')
            record = {'id': cid, 'kind': kind, 'revision': 'v1', 'intended_use': 'Synthetic test',
                      'artifacts': [{'path': path.name, 'sha256': file_hash(path)}], 'dependencies': deps}
            if kind == 'motion':
                record['frame_count'] = 48
            rule = self.policy['kinds'][kind]
            record['review'] = {'revision': 'v1', 'component_sha256': component_fingerprint(record),
                               'policy_sha256': fingerprint(self.policy), 'reviewer': 'test',
                               'method': 'synthetic', 'scope': 'fixture only',
                               'gates': {g: {'verdict': 'pass', 'evidence': 'synthetic observation'} for g in rule['hard_gates']},
                               'criteria': {c: {'status': 'rated', 'score': 3, 'evidence': 'synthetic observation'} for c in rule['criteria']}}
            if kind == 'motion':
                record['review']['sessions'] = [{'method': 'watched_normal_speed', 'ranges': [[0, 48]],
                                                'evidence': 'Synthetic coverage; not a real playback claim.'}]
            self.manifest['components'].append(record)

    def run_audit(self):
        return audit(self.policy, self.manifest, self.base)

    def test_accepted_chain(self):
        self.assertTrue(self.run_audit()['targets_pass'])

    def test_low_identity_blocks_motion(self):
        self.manifest['components'][0]['review']['criteria']['identity']['score'] = 2
        result = self.run_audit()
        self.assertEqual(result['components']['image']['status'], 'rejected')
        self.assertEqual(result['components']['motion']['status'], 'blocked')
        self.assertFalse(result['targets_pass'])

    def test_hard_failure_cannot_be_averaged_away(self):
        self.manifest['components'][1]['review']['gates']['lip_sync_policy_met']['verdict'] = 'fail'
        self.assertEqual(self.run_audit()['components']['motion']['status'], 'rejected')

    def test_missing_evidence_is_pending(self):
        del self.manifest['components'][1]['review']['criteria']['motion_quality']['evidence']
        self.assertEqual(self.run_audit()['components']['motion']['status'], 'pending')

    def test_changed_file_is_stale(self):
        (self.base / 'image.txt').write_text('new revision')
        self.assertEqual(self.run_audit()['components']['image']['status'], 'stale')

    def test_updating_manifest_hash_does_not_reapprove_old_review(self):
        (self.base / 'image.txt').write_text('new revision')
        self.manifest['components'][0]['artifacts'][0]['sha256'] = file_hash(self.base / 'image.txt')
        self.assertEqual(self.run_audit()['components']['image']['status'], 'stale')

    def test_policy_change_requires_new_review(self):
        self.policy['profile'] = 'meticulous'
        self.assertEqual(self.run_audit()['components']['image']['status'], 'stale')

    def test_per_criterion_override(self):
        self.policy['overrides'] = {'image': {'identity': 4}}
        for record in self.manifest['components']:
            record['review']['policy_sha256'] = fingerprint(self.policy)
        self.assertEqual(self.run_audit()['components']['image']['status'], 'rejected')

    def test_unexplained_na_is_pending(self):
        self.manifest['components'][0]['review']['criteria']['identity'] = {'status': 'not_applicable'}
        self.assertEqual(self.run_audit()['components']['image']['status'], 'pending')

    def test_dependency_revision_invalidation(self):
        image = self.manifest['components'][0]
        image['revision'] = 'v2'
        image['review']['revision'] = 'v2'
        image['review']['component_sha256'] = component_fingerprint(image)
        self.assertEqual(self.run_audit()['components']['motion']['status'], 'stale')

    def test_cycles_are_invalid(self):
        self.manifest['components'][0]['dependencies'] = [{'id': 'motion', 'revision': 'v1'}]
        with self.assertRaisesRegex(ValueError, 'cycle'):
            self.run_audit()

    def test_missing_dependency_is_invalid(self):
        self.manifest['components'][1]['dependencies'][0]['id'] = 'missing'
        with self.assertRaisesRegex(ValueError, 'unknown dependency'):
            self.run_audit()

    def test_unused_rejected_asset_does_not_block_target(self):
        unused = copy.deepcopy(self.manifest['components'][0])
        unused['id'] = 'unused'
        unused['review']['component_sha256'] = component_fingerprint(unused)
        unused['review']['criteria']['identity']['score'] = 0
        self.manifest['components'].append(unused)
        self.assertTrue(self.run_audit()['targets_pass'])

    def test_sampled_frames_cannot_satisfy_playback(self):
        self.manifest['components'][1]['review']['sessions'][0]['method'] = 'frame_inspected'
        self.assertEqual(self.run_audit()['components']['motion']['status'], 'pending')

    def test_overlapping_sessions_do_not_hide_gap(self):
        self.manifest['components'][1]['review']['sessions'] = [
            {'method': 'watched_normal_speed', 'ranges': [[0, 24], [12, 36]], 'evidence': 'Synthetic'}]
        result = self.run_audit()['components']['motion']
        self.assertEqual(result['status'], 'pending')
        self.assertTrue(any('[36, 48]' in i['reason'] for i in result['issues']))

    def test_contiguous_sessions_cover_range(self):
        self.manifest['components'][1]['review']['sessions'][0]['ranges'] = [[24, 48], [0, 24]]
        self.assertTrue(self.run_audit()['targets_pass'])

    def test_export_requires_full_video_and_audio_review(self):
        record = self.manifest['components'][1]
        record['kind'] = 'export'
        record['review_ranges'] = [[0, 10]]
        rule = self.policy['kinds']['export']
        record['review']['gates'] = {g: {'verdict': 'pass', 'evidence': 'Synthetic'} for g in rule['hard_gates']}
        record['review']['criteria'] = {c: {'status': 'rated', 'score': 3, 'evidence': 'Synthetic'} for c in rule['criteria']}
        record['review']['component_sha256'] = component_fingerprint(record)
        record['review']['sessions'] = [{'method': 'watched_normal_speed', 'ranges': [[0, 10]], 'evidence': 'Synthetic'}]
        self.assertFalse(self.run_audit()['targets_pass'])
        record['review']['sessions'][0]['ranges'] = [[0, 48]]
        self.assertFalse(self.run_audit()['targets_pass'])
        record['review']['sessions'].append({'method': 'heard', 'ranges': [[0, 48]], 'evidence': 'Synthetic'})
        self.assertTrue(self.run_audit()['targets_pass'])

    def test_changed_usable_range_invalidates_review(self):
        self.manifest['components'][1]['review_ranges'] = [[0, 24]]
        self.assertEqual(self.run_audit()['components']['motion']['status'], 'stale')

    def test_invalid_or_unevidenced_playback_is_pending(self):
        session = self.manifest['components'][1]['review']['sessions'][0]
        for ranges in ([[0, 49]], [[True, 48]], [[48, 0]], []):
            session['ranges'] = ranges
            self.assertEqual(self.run_audit()['components']['motion']['status'], 'pending')
        session['ranges'] = [[0, 48]]
        session['evidence'] = ''
        self.assertEqual(self.run_audit()['components']['motion']['status'], 'pending')

    def test_stale_project_policy_cannot_omit_new_review_gates(self):
        old = copy.deepcopy(self.policy)
        old['profile'] = 'meticulous'
        old['kinds']['lyrics']['hard_gates'].remove('rendered_font_and_bounds_verified')
        old.pop('timed_review')
        with self.assertRaisesRegex(ValueError, 'lyrics.hard_gates'):
            require_template_coverage(old, self.policy)
        old['kinds']['lyrics']['hard_gates'].append('rendered_font_and_bounds_verified')
        with self.assertRaisesRegex(ValueError, 'timed_review'):
            require_template_coverage(old, self.policy)
        old['timed_review'] = copy.deepcopy(self.policy['timed_review'])
        require_template_coverage(old, self.policy)


if __name__ == '__main__':
    unittest.main()
