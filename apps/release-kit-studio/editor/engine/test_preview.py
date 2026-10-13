import hashlib
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(filename))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


engine = module('preview_test_engine', 'engine.py')
preview = module('preview_test_native', 'preview.py')


class PreviewColorTests(unittest.TestCase):
    def test_single_pass_preserves_distinct_out_of_order_requested_source_frames(self):
        def ffmpeg(*args):
            return subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-nostdin', *args],
                                  capture_output=True, check=True, timeout=60).stdout

        with tempfile.TemporaryDirectory() as temporary, patch.dict(sys.modules, {'engine': engine}):
            root = Path(temporary)
            source = root / 'moving.mp4'
            ffmpeg('-f', 'lavfi', '-i', 'testsrc2=size=320x180:rate=24:duration=1',
                   '-f', 'lavfi', '-i', 'sine=frequency=440:sample_rate=48000:duration=1',
                   '-c:v', 'libx264', '-threads', '2', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-ac', '2',
                   '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', str(source))
            receipt = preview.make_preview(source, {'id': 'film', 'width': 320, 'height': 180, 'frames': 24},
                                           {'bundleId': 'c' * 64, 'sourceSha256': engine.hash_file(source),
                                            'startFrame': 3, 'frames': 20, 'sampleFrames': [22, 3, 17]}, root)
            self.assertEqual(receipt['sampleFrames'], [3, 17, 22])
            self.assertEqual(len(set(file['sha256'] for file in receipt['files'][1:])), 3)
            self.assertFalse(list((root / 'previews' / ('c' * 64)).glob('selected-*.jpg')))
            for file in receipt['files'][1:]:
                with self.subTest(source_frame=file['sourceFrame']):
                    reference = ffmpeg('-ss', str(file['sourceFrame'] / 24 - .00001), '-i', str(source),
                                       '-frames:v', '1', '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-')
                    image = ffmpeg('-i', str(root / 'previews' / ('c' * 64) / file['name']),
                                   '-frames:v', '1', '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-')
                    self.assertEqual(len(image), 320 * 180 * 3)
                    self.assertLess(sum(abs(a - b) for a, b in zip(reference, image)) / len(reference), 3)

    def test_bt709_video_and_jpeg_review_frames_preserve_decoded_colors(self):
        def ffmpeg(*args):
            return subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-nostdin', *args],
                                  capture_output=True, check=True, timeout=60).stdout

        def rgb(path, seek=None):
            return ffmpeg(*(['-ss', str(seek)] if seek is not None else []),
                          '-i', str(path), '-frames:v', '1', '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-')

        with tempfile.TemporaryDirectory() as temporary, patch.dict(sys.modules, {'engine': engine}):
            root = Path(temporary)
            source = root / 'source.mp4'
            ffmpeg('-f', 'lavfi', '-i', 'smptebars=size=320x180:rate=24:duration=1',
                   '-f', 'lavfi', '-i', 'sine=frequency=440:sample_rate=48000:duration=1',
                   '-c:v', 'libx264', '-threads', '2', '-pix_fmt', 'yuv420p',
                   '-c:a', 'aac', '-ac', '2', '-color_primaries', 'bt709',
                   '-color_trc', 'bt709', '-colorspace', 'bt709', str(source))
            original_hash = hashlib.sha256(source.read_bytes()).hexdigest()
            receipt = preview.make_preview(source, {'id': 'film', 'width': 320, 'height': 180, 'frames': 24},
                                           {'bundleId': 'a' * 64, 'sourceSha256': original_hash,
                                            'startFrame': 6, 'frames': 12, 'sampleFrames': [6, 17]}, root)
            self.assertEqual(receipt['files'][0]['frames'], 12)
            self.assertTrue(receipt['files'][0]['audioComparison']['passed'])
            for file in receipt['files'][1:]:
                with self.subTest(source_frame=file['sourceFrame']):
                    image = root / 'previews' / ('a' * 64) / file['name']
                    reference = rgb(source, file['sourceFrame'] / 24 - .00001)
                    derived = rgb(image)
                    self.assertEqual(len(derived), 320 * 180 * 3)
                    self.assertLess(sum(abs(a - b) for a, b in zip(reference, derived)) / len(reference), 3)
            image = root / 'previews' / ('a' * 64) / receipt['files'][1]['name']
            still = preview.make_preview(image, {'id': 'thumbnail', 'width': 320, 'height': 180, 'frames': 1},
                                         {'bundleId': 'b' * 64, 'sourceSha256': engine.hash_file(image),
                                          'startFrame': 0, 'frames': 1, 'sampleFrames': [0]}, root)
            self.assertEqual(len(still['files']), 2)
            self.assertTrue(all(file['audioComparison'] is None for file in still['files']))
            self.assertEqual(engine.hash_file(source), original_hash)


if __name__ == '__main__':
    unittest.main()
