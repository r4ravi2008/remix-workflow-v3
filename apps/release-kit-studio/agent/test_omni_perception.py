import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('omni_perception', Path(__file__).with_name('omni-perception.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class OmniAudioCoverageTests(unittest.TestCase):
    def test_discarded_talker_weights_cannot_hide_missing_or_random_thinker_weights(self):
        valid={'missing_keys': [], 'mismatched_keys': [], 'unexpected_keys': ['talker.model.weight', 'token2wav.weight'], 'error_msgs': []}
        self.assertEqual(module.validate_loaded_weights(valid)['discardedAudioGenerationKeys'], 2)
        for change in [{'missing_keys': ['model.layers.0.weight']}, {'mismatched_keys': ['audio_tower.weight']},
                       {'unexpected_keys': ['thinker.audio_tower.weight']}, {'error_msgs': ['bad weights']}]:
            with self.assertRaises(ValueError): module.validate_loaded_weights({**valid, **change})
    def test_odd_feature_lengths_use_the_pinned_encoder_pooling(self):
        for frames, tokens in [(800, 200), (801, 200), (802, 200), (803, 201)]:
            result = module.validate_features([1, 128, 30000], frames, tokens, frames * 160, 160)
            self.assertEqual(result['audioTokens'], tokens)
        with self.assertRaises(ValueError):
            module.validate_features([1, 128, 30000], 801, 201, 801 * 160, 160)

    def test_missing_truncated_or_unexpanded_audio_is_rejected(self):
        for shape, frames, tokens in [([], 0, 1), ([1, 128, 800], 800, 200),
                                     ([1, 128, 30000], 800, 1), ([1, 128, 30000], 300, 75),
                                     ([1, 80, 30000], 800, 200), ([2, 128, 30000], 800, 200),
                                     ([1, 128, 3000], 800, 200)]:
            with self.assertRaises(ValueError):
                module.validate_features(shape, frames, tokens, 128000, 160)


if __name__ == '__main__':
    unittest.main()
