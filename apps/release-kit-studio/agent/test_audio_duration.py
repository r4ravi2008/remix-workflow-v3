import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


APP = Path(__file__).resolve().parent.parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


audio = load('duration_audio', APP / 'agent/audio-perception.py')
engine = load('duration_engine', APP / 'editor/engine/engine.py')


class DecodedAudioDurationTests(unittest.TestCase):
    def test_compressed_padding_does_not_change_source_duration_or_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            wav, mp3 = root / 'source.wav', root / 'source.mp3'
            subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i',
                            'sine=frequency=440:sample_rate=48000:duration=2', '-ac', '2',
                            '-c:a', 'pcm_s16le', str(wav)], check=True, timeout=30)
            subprocess.run(['ffmpeg', '-v', 'error', '-i', str(wav), '-c:a', 'libmp3lame',
                            '-b:a', '192k', str(mp3)], check=True, timeout=30)
            before = audio.file_receipt(mp3)
            metadata = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_format',
                                '-of', 'json', str(mp3)], check=True, capture_output=True,
                                text=True, timeout=30).stdout)
            self.assertGreaterEqual(float(metadata['format']['duration']), 2)
            for path in [wav, mp3]:
                self.assertEqual(audio.decoded_audio_duration(path), 2)
                self.assertEqual(engine.decoded_audio_duration(path), 2)
            self.assertEqual(audio.file_receipt(mp3), before)

            assets = root / 'assets'
            assets.mkdir()
            source = assets / 'master'
            source.write_bytes(mp3.read_bytes())
            asset = {'id': 'master', 'kind': 'audio', 'duration': 2, **before}
            padded = engine.probe(source)
            padded['format']['duration'] = '2.045714'
            with patch.object(engine, 'probe', return_value=padded):
                measured = engine.inspect_sources({'assets': [asset]}, root)
                self.assertEqual(measured['master']['duration'], 2)
                with self.assertRaisesRegex(ValueError, 'duration'):
                    engine.inspect_sources({'assets': [{**asset, 'duration': 2.2}]}, root)

    def test_unreadable_input_is_not_replaced_with_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'invalid.wav'
            path.write_bytes(b'not audio')
            with self.assertRaises(subprocess.CalledProcessError):
                audio.decoded_audio_duration(path)
            with self.assertRaises(ValueError):
                engine.decoded_audio_duration(path)


if __name__ == '__main__':
    unittest.main()
