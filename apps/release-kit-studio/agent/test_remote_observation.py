import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('remote_observation',Path(__file__).with_name('remote_observation.py'))
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ModelOperationFenceTests(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root=Path(self.temporary.name).resolve()
        for target in [module, module.audio]:
            name='SERVICE' if target is module else 'RUN'
            guard=patch.object(target,name,self.root);guard.start();self.addCleanup(guard.stop)
        for name,value in [('managed',lambda:None),('idle_queue',lambda:None),('LEASE',self.root/'lease.json')]:
            guard=patch.object(module.audio,name,value);guard.start();self.addCleanup(guard.stop)
        (self.root/'requests').mkdir()
        (self.root/'audio-perception.py').write_text('fixed runner')
        environment=self.root/'director/venv/bin';environment.mkdir(parents=True)
        (environment/'python').write_text('owned interpreter')
        self.intent={'schemaVersion':1,'id':'a'*64,'kind':'audio-window','jobId':'8f55a7a3-e2df-4239-ab5f-603ad55d070b',
            'releaseId':'92a6e687-e9ec-4325-a767-f44a56c73d84','briefSha256':'b'*64,'sourceSha256':__import__('hashlib').sha256(b'source').hexdigest(),
            'sourceBytes':6,'sourceDuration':239.68,'language':'Telugu','lyrics':'ప్రతి నిమిషం','startSeconds':60,'endSeconds':68}

    def request(self,body=b'source'):
        path=self.root/'requests'/(__import__('uuid').uuid4().__str__()+'.audio');path.write_bytes(body)
        return {'intent':self.intent.copy(),'stagedSource':str(path)}

    def finish(self,args,**kwargs):
        request=json.loads(Path(args[-1]).read_text())
        module.audio.write_new(Path(request['outputPath']),{'status':'observed','request':request,
            'source':{'sha256':request['sourceSha256'],'bytes':request['sourceBytes']}})

    def test_terminal_replay_reads_same_bytes_without_repeating_inference(self):
        with patch.object(module.subprocess,'run',side_effect=self.finish) as inference:
            first=module.run(self.request());second=module.run(self.request())
            self.assertEqual(inference.call_count,1)
        self.assertTrue(first['inferenceSubmitted']);self.assertFalse(second['inferenceSubmitted'])
        self.assertEqual(first['receipt'],second['receipt'])
        self.assertEqual(Path(first['receipt']['path']).stat().st_mode&0o777,0o600)

    def test_unknown_inference_keeps_its_fence_and_does_not_retry(self):
        with patch.object(module.subprocess,'run',return_value=None) as inference:
            with self.assertRaisesRegex(RuntimeError,'no terminal receipt'):module.run(self.request())
            with self.assertRaisesRegex(RuntimeError,'uncertain'):module.run(self.request())
            self.assertEqual(inference.call_count,1)
        self.assertTrue((self.root/'director/operations'/self.intent['id']/'inference-intent.json').exists())

    def test_foreign_brief_or_runner_cannot_reuse_the_same_operation(self):
        with patch.object(module.subprocess,'run',side_effect=self.finish) as inference:
            module.run(self.request())
            foreign=self.request();foreign['intent']['briefSha256']='c'*64
            with self.assertRaisesRegex(ValueError,'different inputs'):module.run(foreign)
            (self.root/'audio-perception.py').write_text('different runner')
            with self.assertRaisesRegex(ValueError,'runner bytes'):module.run(self.request())
            self.assertEqual(inference.call_count,1)

    def test_corrupt_staging_and_unbounded_ranges_never_submit(self):
        with patch.object(module.subprocess,'run') as inference:
            with self.assertRaisesRegex(ValueError,'frozen source'):module.run(self.request(b'other'))
            invalid=self.request();invalid['intent']['endSeconds']=100
            with self.assertRaisesRegex(ValueError,'30 seconds'):module.run(invalid)
            inference.assert_not_called()

    def test_fixed_omni_backend_replays_and_binds_both_runner_files(self):
        runner=self.root/'omni-perception.py';runner.write_text('fixed omni runner')
        self.intent['audioBackend']='qwen2.5-omni'
        with patch.object(module.subprocess,'run',side_effect=self.finish) as inference:
            first=module.run(self.request());second=module.run(self.request())
            self.assertEqual(inference.call_args.args[0][1:3],[str(runner),'inspect'])
            self.assertEqual(inference.call_count,1)
            self.assertTrue(first['inferenceSubmitted']);self.assertFalse(second['inferenceSubmitted'])
            self.assertEqual(first['receipt'],second['receipt'])
            runner.write_text('changed omni runner')
            with self.assertRaisesRegex(ValueError,'runner bytes'):module.run(self.request())
            self.assertEqual(inference.call_count,1)

    def test_audio_backend_cannot_select_arbitrary_commands_or_speech_alignment(self):
        for kind,backend in [('audio-window','arbitrary-command'),('speech','qwen2.5-omni'),('lyric-alignment','qwen2-audio')]:
            intent=self.intent.copy();intent.update({'kind':kind,'audioBackend':backend,'startSeconds':0,'endSeconds':28,'sourceDuration':28})
            with self.assertRaisesRegex(ValueError,'fixed audio backend'):module.validate_intent(intent)

    def cpu_request(self):
        (self.root/'lyric-alignment.py').write_text('fixed alignment runner')
        environment=self.root/'director/asr-venv/bin';environment.mkdir(parents=True)
        (environment/'python').write_text('owned alignment interpreter')
        request=self.request()
        request['intent'].update({'kind':'lyric-alignment','lineIndices':[0],'alignmentDevice':'cpu'})
        return request

    def test_cpu_alignment_busy_lease_defers_before_inference_fence(self):
        request=self.cpu_request()
        (self.root/'director/.cpu-alignment-lease.json').write_text('{"owner_id":"another-owner"}')
        with patch.object(module.subprocess,'run') as inference:
            with self.assertRaisesRegex(RuntimeError,'CPU alignment lease'):module.run(request)
            inference.assert_not_called()
        self.assertFalse((self.root/'director/operations'/self.intent['id']/'inference-intent.json').exists())

    def test_explicit_cpu_alignment_preserves_an_occupied_gpu_lease(self):
        request=self.cpu_request()
        module.audio.LEASE.write_text('{"owner_id":"another-gpu-owner"}')
        with patch.object(module.subprocess,'run',side_effect=self.finish) as inference,patch.object(module.audio,'idle_queue') as queue:
            result=module.run(request)
            self.assertTrue(result['inferenceSubmitted'])
            inference.assert_called_once();queue.assert_not_called()
        self.assertEqual(module.audio.LEASE.read_text(),'{"owner_id":"another-gpu-owner"}')


if __name__=='__main__':unittest.main()
