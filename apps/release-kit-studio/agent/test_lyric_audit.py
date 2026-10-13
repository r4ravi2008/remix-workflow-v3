import copy
import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('lyric_audit',Path(__file__).with_name('lyric-audit.py'))
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def fixture():
    brief={'audioSha256':'a'*64,'audioBytes':10,'audioDuration':10,'language':'Telugu','lyrics':'ప్రతి నిమిషం\nప్రతి నిమిషం'}
    packet={'schemaVersion':2,'brief':brief,'briefSha256':module.fingerprint(brief),'jobId':'job','releaseId':'release'}
    expected={'sha256':brief['audioSha256'],'bytes':brief['audioBytes']}
    lines=[]
    for index in range(2):
        lines.append({'lineIndex':index,'text':'ప్రతి నిమిషం','words':[
            {'wordIndex':0,'text':'ప్రతి','candidate':{'startSeconds':1.25,'endSeconds':1.8,'similarity':1.,'recognition':[{'issues':[]}],'verified':False}},
            {'wordIndex':1,'text':'నిమిషం','candidate':{'startSeconds':2.25,'endSeconds':2.8,'similarity':1.,'recognition':[{'issues':[]}],'verified':False}},
        ]})
    proposals={**{key:packet[key] for key in ['jobId','releaseId','briefSha256']},'source':expected,
               'canonicalLyrics':brief['lyrics'],'lyricTimingVerified':False,'canonicalLyricsChanged':False,'lines':lines}
    receipts=[]
    for kind in ['whisper','ctc']:
        model,revision,weights=module.PINS[kind]
        request={**{key:packet[key] for key in ['jobId','releaseId','briefSha256']},'lineIndices':[1],
                 'lyrics':brief['lyrics'],'language':brief['language'],'sourceDuration':10,'sourceSha256':expected['sha256'],
                 'sourceBytes':expected['bytes'],'startSeconds':1.,'endSeconds':5.}
        receipts.append({'model':model,'revision':revision,'weights':{'sha256':weights},'status':'aligned-unverified',
                         'alignmentComplete':True,'alignmentContractPassed':True,'source':expected,'canonicalText':'ప్రతి నిమిషం','request':request,
                         'words':[{'wordIndex':index,'text':word,'startSeconds':1.2+index,'endSeconds':1.8+index,'probability':.9,'issues':[],'verified':False} for index,word in enumerate(['ప్రతి','నిమిషం'])],
                         **{key:False for key in ['lyricTimingVerified','canonicalLyricsChanged','fullSongHeard','pilotApproved','humanAccepted']}})
    return packet,proposals,*receipts


class IndependentLyricEvidenceTests(unittest.TestCase):
    def test_old_high_probability_crop_edge_pass_is_rejected_without_repairing_raw_times(self):
        values=fixture();values[2]['words'][0]['startSeconds']=1.
        before=copy.deepcopy(values[2])
        result=module.audit(*values)
        self.assertFalse(result['timingEvidenceConsistent'])
        self.assertIn('whisper:crop-boundary-onset-unresolved',result['words'][0]['issues'])
        self.assertIn('timing-evidence-disagreement',result['words'][0]['issues'])
        self.assertEqual(values[2],before)

    def test_missing_observations_remain_missing_with_exact_native_spelling(self):
        values=fixture();values[1]['lines'][1]['words'][0]['candidate']=None
        result=module.audit(*values)
        self.assertIsNone(result['words'][0]['recognitionProposal'])
        self.assertEqual(result['words'][0]['text'],'ప్రతి')
        self.assertIn('recognition:missing-canonical-word',result['words'][0]['issues'])

    def test_foreign_brief_or_same_text_from_another_repeated_line_is_rejected(self):
        values=fixture();values[3]['request']['lineIndices']=[0]
        with self.assertRaisesRegex(ValueError,'chronological'):module.audit(*values)
        values=fixture();values[3]['request']['briefSha256']='b'*64
        with self.assertRaisesRegex(ValueError,'frozen job or brief'):module.audit(*values)

    def test_agreement_is_not_listening_or_verified_lyric_timing(self):
        result=module.audit(*fixture())
        self.assertTrue(result['timingEvidenceConsistent'])
        self.assertFalse(result['lyricTimingVerified'])
        self.assertFalse(result['automaticLyricTimingQualified'])
        self.assertFalse(result['fullSongHeard'])
        values=fixture();values[2]['words'][0]['verified']=True
        with self.assertRaisesRegex(ValueError,'asserted word evidence'):module.audit(*values)


if __name__=='__main__':unittest.main()
