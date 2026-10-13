import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('lyric_alignment',Path(__file__).with_name('lyric-alignment.py'))
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CanonicalAlignmentTests(unittest.TestCase):
    def row(self,text,start,end,probability=.9):
        return {'text':text,'startSeconds':start,'endSeconds':end,'probability':probability,'tokens':[1]}

    def test_punctuation_groups_without_replacing_supplied_words_or_times(self):
        rows=[self.row(' The',.1,.2),self.row(' train',.2,.6),self.row('.',.6,.6)]
        words,issues=module.group_words(rows,'The train.',1)
        self.assertEqual([r['text'] for r in words],['The','train.'])
        self.assertEqual(words[-1]['endSeconds'],.6)
        self.assertEqual(issues,[])

    def test_exact_native_text_is_required_without_romanization_or_asr_replacement(self):
        words,_=module.group_words([self.row(' ప్రతి',0,1),self.row(' నిమిషం',1,2)],'ప్రతి నిమిషం',3)
        self.assertEqual([r['text'] for r in words],['ప్రతి','నిమిషం'])
        with self.assertRaisesRegex(ValueError,'canonical words'):
            module.group_words([self.row(' ప్రతీ',0,1),self.row(' నిమిషం',1,2)],'ప్రతి నిమిషం',3)

    def test_outside_reversed_or_non_finite_alignments_fail(self):
        for start,end in [(-1,1),(1,4),(2,1),(float('nan'),1)]:
            with self.assertRaises(ValueError):module.group_words([self.row(' ప్రతి',start,end)],'ప్రతి',3)

    def test_low_probability_and_zero_length_words_remain_unverified(self):
        words,issues=module.group_words([self.row(' ప్రతి',0,0,.1)],'ప్రతి',3)
        self.assertEqual(set(issues[0]['issues']),{'crop-boundary-onset-unresolved','zero-length-word-alignment','uncertain-canonical-word'})
        self.assertFalse(words[0]['verified'])
        self.assertEqual(words[0]['startSeconds'],words[0]['endSeconds'])

    def test_high_probability_at_crop_edge_does_not_certify_the_first_onset(self):
        words,issues=module.group_words([self.row(' ప్రతి',0,2.62,.92),self.row(' నిమిషం',2.62,3.02,.8)],'ప్రతి నిమిషం',7.5)
        self.assertEqual(issues,[{'wordIndex':0,'text':'ప్రతి','issues':['crop-boundary-onset-unresolved']}])
        self.assertEqual(words[0]['startSeconds'],0)
        self.assertEqual(words[0]['endSeconds'],2.62)
        self.assertFalse(words[0]['verified'])

    def test_only_selected_chronological_canonical_lines_enter_alignment(self):
        value={'schemaVersion':1,'jobId':'8f55a7a3-e2df-4239-ab5f-603ad55d070b','releaseId':'92a6e687-e9ec-4325-a767-f44a56c73d84',
               'briefSha256':'a'*64,'sourcePath':'unused','sourceSha256':'b'*64,'sourceBytes':10,'sourceDuration':60,
               'language':'Telugu','lyrics':'ప్రతి నిమిషం\nనీ రూపమే\nప్రతి నిమిషం','startSeconds':20,'endSeconds':28,
               'lineIndices':[1,2],'device':'cuda','outputPath':'unused'}
        self.assertEqual(module.validate_request(value),'నీ రూపమే ప్రతి నిమిషం')
        for indices in [[2,1],[0,0],[3],[],[.5]]:
            with self.assertRaises(ValueError):module.validate_request({**value,'lineIndices':indices})
        with self.assertRaises(ValueError):module.validate_request({**value,'endSeconds':55})


if __name__=='__main__':unittest.main()
