import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('speech_evidence',Path(__file__).with_name('speech-evidence.py'))
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SpeechEvidenceTests(unittest.TestCase):
    def row(self):
        return {'id':1,'start':2.,'end':4.,'text':'ప్రతి నిమిషం','avgLogprob':-.1,'noSpeechProbability':.1,
                'words':[{'text':'ప్రతి','start':2.,'end':3.,'probability':.9},{'text':'నిమిషం','start':3.,'end':4.,'probability':.9}]}

    def test_measured_native_words_remain_in_source_ranges(self):
        row=self.row()
        self.assertEqual(module.validate_segments([row],5),[])
        self.assertEqual(row['text'],'ప్రతి నిమిషం')

    def test_outside_or_reversed_word_ranges_cannot_become_evidence(self):
        for start,end in [(1,3),(3,6),(4,3)]:
            row=self.row();row['words'][0]['start']=start;row['words'][0]['end']=end
            with self.assertRaises(ValueError):module.validate_segments([row],5)
        with self.assertRaises(ValueError):module.validate_segments([self.row()],3)

    def test_uncertain_or_zero_length_recognition_is_flagged_without_fake_repair(self):
        row=self.row();row['noSpeechProbability']=.8;row['words'][0]['end']=2.
        issues=module.validate_segments([row],5)
        self.assertEqual({i['code'] for i in issues},{'uncertain-recognition','uncertain-word-timing'})
        self.assertEqual(row['words'][0]['end'],2.)


if __name__=='__main__':unittest.main()
