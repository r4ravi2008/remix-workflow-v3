"""Offline failure/recovery tests. Fake server responses; no paid GPU or real quality approval."""
import copy
import io
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import unittest
import urllib.error
from unittest.mock import patch

from asset_snapshot import create, verify
from comfy_job import Client, collect, job_directory, reconcile, status, submit
from prepare_h3_job import prepare


class FakeClient:
    url = 'http://127.0.0.1:8189'

    def __init__(self):
        self.queue = {'queue_running': [], 'queue_pending': []}
        self.history = {}
        self.posts = 0
        self.lose_response = False

    def request(self, route, payload=None):
        if route == '/object_info':
            return {'LoadImage': {}, 'SaveVideo': {}}
        if route == '/queue':
            return self.queue
        if route == '/prompt':
            self.posts += 1
            entry = [0, 'prompt-1', payload['prompt'], payload['extra_data'], ['2']]
            self.queue['queue_running'] = [entry]
            if self.lose_response:
                raise TimeoutError('Server queued the prompt; HTTP response was lost')
            return {'prompt_id': 'prompt-1'}
        if route == '/history':
            return self.history
        if route == '/history/prompt-1':
            return self.history
        raise AssertionError(route)


class FootageHelpersTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.inputs = self.root / 'input'
        self.inputs.mkdir()
        (self.inputs / 'anchor.png').write_bytes(b'synthetic anchor for binding tests')
        self.snapshot = create(self.inputs, ['anchor.png'])
        self.workflow = {'1': {'class_type': 'LoadImage', 'inputs': {'image': 'anchor.png'}},
                         '2': {'class_type': 'SaveVideo', 'inputs': {'images': ['1', 0]}}}
        self.bindings = [{'node': '1', 'input': 'image', 'path': 'anchor.png'}]
        self.directory = job_directory(self.root / 'ledger', 'shot-01-r1')
        self.client = FakeClient()

    def submit(self):
        return submit(self.client, self.directory, self.workflow, self.snapshot, self.bindings,
                      self.inputs, time.time() + 600, 120)

    def complete(self, outputs=None):
        entry = self.client.queue['queue_running'][0]
        self.client.queue['queue_running'] = []
        self.client.history = {'prompt-1': {'prompt': entry, 'status': {'status_str': 'success', 'completed': True},
                                          'outputs': outputs or {}}}

    def test_snapshot_copies_between_roots_and_detects_stale_file(self):
        remote = self.root / 'remote'
        shutil.copytree(self.inputs, remote)
        self.assertTrue(verify(remote, self.snapshot)['verified'])
        (remote / 'anchor.png').write_bytes(b'old anchor')
        with self.assertRaisesRegex(ValueError, 'mismatch'):
            verify(remote, self.snapshot)

    def test_snapshot_tampering_and_escape_rejected(self):
        tampered = copy.deepcopy(self.snapshot)
        tampered['files'][0]['bytes'] = 1
        with self.assertRaisesRegex(ValueError, 'definition changed'):
            verify(self.inputs, tampered)
        (self.root / 'outside').write_text('private')
        with self.assertRaisesRegex(ValueError, 'out-of-root'):
            create(self.inputs, ['../outside'])

    def test_stale_input_or_graph_binding_prevents_submission(self):
        self.workflow['1']['inputs']['image'] = 'old.png'
        with self.assertRaisesRegex(ValueError, 'binding'):
            self.submit()
        self.assertEqual(self.client.posts, 0)

    def test_unbound_second_image_rejected(self):
        self.workflow['3'] = {'class_type': 'LoadImage', 'inputs': {'image': 'old.png'}}
        with self.assertRaisesRegex(ValueError, 'Unbound'):
            self.submit()

    def test_lost_response_recovers_without_duplicate_spend(self):
        self.client.lose_response = True
        with self.assertRaises(TimeoutError):
            self.submit()
        self.assertTrue((self.directory / 'intent.json').exists())
        with self.assertRaisesRegex(ValueError, 'already has'):
            self.submit()
        self.assertEqual(reconcile(self.client, self.directory)['state'], 'running')
        self.assertEqual(self.client.posts, 1)

    def test_no_history_match_remains_uncertain(self):
        self.client.lose_response = True
        with self.assertRaises(TimeoutError):
            self.submit()
        self.client.queue['queue_running'] = []
        with self.assertRaisesRegex(ValueError, 'Uncertain'):
            reconcile(self.client, self.directory)
        self.assertEqual(self.client.posts, 1)

    def test_recovery_from_completed_history(self):
        self.client.lose_response = True
        with self.assertRaises(TimeoutError):
            self.submit()
        self.complete()
        self.assertEqual(reconcile(self.client, self.directory)['state'], 'generated-unreviewed')

    def test_changed_graph_cannot_reuse_receipt(self):
        self.submit()
        (self.directory / 'workflow.json').write_text('{}')
        with self.assertRaisesRegex(ValueError, 'workflow changed'):
            status(self.client, self.directory)

    def test_deadline_and_occupied_queue_prevent_submission(self):
        for deadline, reserve in [(float('nan'), 120), (float('inf'), 120), (time.time() + 600, float('nan'))]:
            with self.subTest(deadline=deadline, reserve=reserve):
                with self.assertRaisesRegex(ValueError, 'deadline'):
                    submit(self.client, self.directory, self.workflow, self.snapshot, self.bindings,
                           self.inputs, deadline, reserve)
        with self.assertRaisesRegex(ValueError, 'deadline'):
            submit(self.client, self.directory, self.workflow, self.snapshot, self.bindings,
                   self.inputs, time.time() + 5, 120)
        self.client.queue['queue_pending'] = [[0, 'another-owner']]
        with self.assertRaisesRegex(ValueError, 'occupied'):
            self.submit()
        self.assertEqual(self.client.posts, 0)

    def test_server_validation_error_preserves_diagnostic_and_intent(self):
        original = self.client.request
        def request(route, payload=None):
            if route == '/prompt':
                raise urllib.error.HTTPError(self.client.url + route, 400, 'invalid graph', {},
                    io.BytesIO(b'{"node_errors":{"17":{"error":"invalid codec"}}}'))
            return original(route, payload)
        self.client.request = request
        with self.assertRaisesRegex(ValueError, 'HTTP error'):
            self.submit()
        saved = json.loads((self.directory / 'submission-response.json').read_text())
        self.assertEqual(saved['detail']['node_errors']['17']['error'], 'invalid codec')
        self.assertTrue((self.directory / 'intent.json').exists())
        with self.assertRaisesRegex(ValueError, 'already has'):
            self.submit()

    def test_failed_or_unknown_prompt_is_not_complete(self):
        self.submit()
        self.complete()
        self.client.history['prompt-1']['status'] = {'status_str': 'error', 'completed': False}
        self.assertEqual(status(self.client, self.directory)['state'], 'failed')
        self.client.history = {}
        self.assertEqual(status(self.client, self.directory)['state'], 'unknown-do-not-resubmit')

    def test_output_path_escape_and_partial_file_rejected(self):
        self.submit()
        self.complete({'2': {'video': [{'filename': 'bad.mp4', 'subfolder': '..', 'type': 'output'}]}})
        output = self.root / 'output'
        output.mkdir()
        (self.root / 'bad.mp4').write_bytes(b'invalid')
        with self.assertRaisesRegex(ValueError, 'out-of-root'):
            collect(self.client, self.directory, output, self.root / 'archive')
        self.client.history['prompt-1']['outputs']['2']['video'][0]['subfolder'] = ''
        (output / 'bad.mp4').write_bytes(b'partial MP4')
        with patch('comfy_job.probe_video', side_effect=ValueError('decode failed')):
            with self.assertRaisesRegex(ValueError, 'decode'):
                collect(self.client, self.directory, output, self.root / 'archive')
        self.assertFalse((self.directory / 'result.json').exists())

    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'ffmpeg/ffprobe unavailable')
    def test_real_decode_and_immutable_archive_do_not_claim_creative_approval(self):
        output = self.root / 'output'
        output.mkdir()
        source = output / 'pilot.mp4'
        subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'testsrc2=size=64x48:rate=24',
                        '-t', '0.5', '-c:v', 'mpeg4', str(source)], check=True, capture_output=True)
        self.submit()
        self.complete({'2': {'video': [{'filename': source.name, 'subfolder': '', 'type': 'output'}]}})
        result = collect(self.client, self.directory, output, self.root / 'archive')
        self.assertEqual(result['state'], 'generated-unreviewed')
        self.assertFalse(result['watched_normal_speed'])
        self.assertEqual(int(result['media']['streams'][0]['nb_read_frames']), 12)
        self.assertEqual(collect(self.client, self.directory, output, self.root / 'archive')['sha256'], result['sha256'])
        Path(result['archive']).write_bytes(b'unrelated file')
        with self.assertRaisesRegex(ValueError, 'differs'):
            collect(self.client, self.directory, output, self.root / 'archive')

    def test_embedded_credentials_are_rejected(self):
        with self.assertRaises(ValueError):
            Client('https://user:secret@example.invalid')

    def test_h3_recipe_binds_selected_image_and_retains_single_encode(self):
        graph, bindings = prepare('run/anchor.png', 'A simple visual action.', 1536, 640, 124, 24, 42, 'shot-02-r1')
        self.assertEqual(graph['6']['inputs']['image'], bindings[0]['path'])
        self.assertEqual(graph['8']['inputs']['prompt'], 'A simple visual action.')
        self.assertEqual(graph['8']['inputs']['length'], 124)
        self.assertEqual(graph['16']['inputs']['codec'], 'none')
        self.assertEqual(graph['17']['inputs']['format.codec'], 'h264')
        self.assertNotIn('C007', json.dumps(graph))
        for node in graph.values():
            for value in node['inputs'].values():
                if isinstance(value, list):
                    self.assertIn(value[0], graph)

    def test_h3_recipe_rejects_incompatible_frame_lattice(self):
        with self.assertRaisesRegex(ValueError, 'frame count'):
            prepare('anchor.png', 'Visual action.', 1536, 640, 120, 24, 42, 'shot-02-r1')


if __name__ == '__main__':
    unittest.main()
