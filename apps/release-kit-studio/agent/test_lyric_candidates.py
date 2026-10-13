import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('lyric_candidates',Path(__file__).with_name('lyric-candidates.py'))
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def segment(index,start,text):
    words=text.split()
    return {'id':index,'start':start,'end':start+len(words),'avgLogprob':-.1,'noSpeechProbability':.1,
            'words':[{'text':word,'start':start+i,'end':start+i+1,'probability':.9} for i,word in enumerate(words)]}


class LyricProposalTests(unittest.TestCase):
    def test_repeated_native_lines_keep_distinct_chronological_instances(self):
        lyrics='ప్రతి నిమిషం\nనీ రూపమే\nప్రతి నిమిషం'
        result=module.propose(lyrics,[segment(1,10,'ప్రతి నిమిషం'),segment(2,20,'నీ రూపమే'),segment(3,50,'ప్రతి నిమిషం')],60)
        self.assertEqual([r['text'] for r in result['lines']],lyrics.splitlines())
        self.assertEqual([r['words'][0]['candidate']['startSeconds'] for r in result['lines']],[10,20,50])
        self.assertTrue(all(r['lyricTimingVerified'] is False for r in result['lines']))

    def test_missing_words_have_no_fabricated_times(self):
        result=module.propose('ప్రతి నిమిషం నువ్వు',[segment(1,10,'ప్రతి నిమిషం')],20)
        self.assertIsNone(result['lines'][0]['words'][2]['candidate'])
        self.assertEqual(result['lines'][0]['missingWordIndices'],[2])

    def test_split_recognition_preserves_exact_canonical_word(self):
        result=module.propose('నువ్వ్లేని లోటే',[segment(1,10,'నువ్వ్ లేని లోటే')],20)
        first=result['lines'][0]['words'][0]
        self.assertEqual(first['text'],'నువ్వ్లేని')
        self.assertEqual(len(first['candidate']['recognition']),2)
        self.assertEqual(first['candidate']['startSeconds'],10)
        self.assertEqual(first['candidate']['endSeconds'],12)

    def test_invalid_ranges_are_excluded_and_uncertainty_is_retained(self):
        row=segment(1,10,'ప్రతి నిమిషం');row['noSpeechProbability']=.9;row['words'][1]['end']=13
        result=module.propose('ప్రతి నిమిషం',[row],20)
        self.assertEqual(len(result['excludedRecognition']),1)
        self.assertIn('high-no-speech-prior',result['lines'][0]['words'][0]['candidate']['recognition'][0]['issues'])
        self.assertIsNone(result['lines'][0]['words'][1]['candidate'])


if __name__=='__main__':unittest.main()
