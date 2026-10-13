import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('audio_perception',Path(__file__).with_name('audio-perception.py'))
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class BoundedPerceptionTests(unittest.TestCase):
    def test_invalid_observations_remain_preserved_and_unusable(self):
        row=module.observation_record('Describe only sounds.','A transition occurs at 3:20.')
        self.assertFalse(row['usable'])
        self.assertFalse(row['semanticVerified'])
        self.assertEqual(row['response'],'A transition occurs at 3:20.')
        self.assertEqual(len(row['issues']),1)
    def test_model_timestamps_or_tempo_cannot_replace_measured_timing(self):
        for raw in ['A transition occurs at 3:20.', 'The tempo is 89.55 bpm.', 'A change occurs after 12 seconds.', 'Breathing at intervals (0.32,0.46).', 'Singing at (0.00-2.30).']:
            with self.assertRaises(ValueError):module.validate_observation(raw)
        self.assertEqual(module.validate_observation('Singing continues over a repeated synth pattern.'),'Singing continues over a repeated synth pattern.')
    def test_missing_truncated_or_unexpanded_audio_cannot_count_as_perception(self):
        valid=module.validate_features([1,128,3000],800,200,128000,160)
        self.assertEqual(valid['attendedFrames'],800)
        for shape,frames,tokens in [([],0,1),([1,128,3000],800,1),([1,128,3000],300,75),([1,80,3000],800,200)]:
            with self.assertRaises(ValueError):module.validate_features(shape,frames,tokens,128000,160)

    def test_full_pal_pal_range_has_no_truncation_or_gap(self):
        duration=239.68
        rows=module.windows(duration)
        self.assertEqual(rows[0]['startSeconds'],0)
        self.assertEqual(rows[-1]['endSeconds'],duration)
        self.assertEqual(len(rows),10)
        for row in rows:
            self.assertGreater(row['endSeconds'],row['startSeconds'])
            self.assertLessEqual(row['endSeconds']-row['startSeconds'],30)
        for before,after in zip(rows,rows[1:]):
            self.assertLessEqual(after['startSeconds'],before['endSeconds'])

    def test_invalid_windows_cannot_silently_skip_or_loop(self):
        for duration,length,overlap in [(0,28,2),(float('inf'),28,2),(239.68,31,2),(239.68,28,28)]:
            with self.assertRaises(ValueError):module.windows(duration,length,overlap)

    def test_model_claims_require_the_observation_contract(self):
        raw='```json\n'+__import__('json').dumps({k:'uncertain' for k in ['description','instruments','vocals','mood','rhythm','changes','uncertainty']})+'\n```'
        self.assertEqual(module.parse_findings(raw)['uncertainty'],'uncertain')
        for raw in ['{"approved":true}','[]','{"description":42}']:
            with self.assertRaises(ValueError):module.parse_findings(raw)

    def test_instrument_arrays_normalize_without_accepting_extra_claims(self):
        value={k:'uncertain' for k in ['description','vocals','mood','rhythm','changes','uncertainty']}
        value['instruments']=['bass','drums']
        self.assertEqual(module.parse_findings(__import__('json').dumps(value))['instruments'],'bass, drums')
        self.assertEqual(module.parse_findings(str(value))['instruments'],'bass, drums')
        value['approved']=True
        with self.assertRaises(ValueError):module.parse_findings(__import__('json').dumps(value))
        with self.assertRaises(ValueError):module.parse_findings('__import__("os").getcwd()')

if __name__=='__main__':unittest.main()
