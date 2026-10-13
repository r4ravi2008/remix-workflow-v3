import importlib.util
import math
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('ctc_alignment',Path(__file__).with_name('ctc-alignment.py'))
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class BlankAwareNativeAlignmentTests(unittest.TestCase):
    def frame(self, label, size=4):
        return [math.log(.97 if index==label else .03/(size-1)) for index in range(size)]

    def test_blank_pre_roll_does_not_become_the_first_native_word(self):
        vocab={0:'▁అ',1:'మ్మ',2:'▁న',3:'<blk>'}
        rows=[self.frame(index) for index in [3,3,3,0,0,3,1,3,2,3]]
        words,tokens,score=module.align_lattice(rows,vocab,'అమ్మ న',3)
        self.assertEqual([row['text'] for row in words],['అమ్మ','న'])
        self.assertEqual(words[0]['startFrame'],3)
        self.assertEqual(words[0]['endFrame'],7)
        self.assertEqual(words[1]['startFrame'],8)
        self.assertEqual(''.join(row['piece'] for row in tokens),'▁అమ్మ▁న')
        self.assertTrue(math.isfinite(score))

    def test_duplicate_native_labels_require_a_blank_between_emissions(self):
        vocab={0:'▁',1:'అ',2:'న',3:'<blk>'}
        rows=[self.frame(index) for index in [0,1,3,1,3]]
        words,tokens,_=module.align_lattice(rows,vocab,'అఅ',3)
        self.assertEqual(words[0]['text'],'అఅ')
        self.assertEqual([row['token'] for row in tokens],[0,1,1])
        with self.assertRaisesRegex(ValueError,'complete CTC path'):
            module.align_lattice([self.frame(index) for index in [0,1,1]],vocab,'అఅ',3)

    def test_unsupported_native_text_is_not_romanized_or_invented(self):
        vocab={0:'▁అ',1:'మ్మ',2:'▁న',3:'<blk>'}
        with self.assertRaisesRegex(ValueError,'represent the exact'):
            module.align_lattice([self.frame(3)],vocab,'నువ్వు',3)

    def test_silence_keeps_low_evidence_for_forced_canonical_words(self):
        vocab={0:'▁అ',1:'మ్మ',2:'▁న',3:'<blk>'}
        words,_,_=module.align_lattice([self.frame(3)]*10,vocab,'అమ్మ న',3)
        self.assertTrue(all(row['probability']<.6 for row in words))


if __name__=='__main__':unittest.main()
