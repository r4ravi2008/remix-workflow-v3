"""Re-align the final chorus in a bounded audio window; never infer word durations."""
import importlib.util
import json
import subprocess
from prepare_last_tide_v6 import OUT, ROOT, MASTER, EXPECTED, save

start, end = 192.0, 211.0
audio = OUT / 'final-chorus-alignment-window.wav'
if not audio.exists():
    subprocess.run(['ffmpeg','-v','error','-ss',str(start),'-i',str(MASTER),'-t',str(end-start),
                    '-ac','1','-ar','16000','-c:a','pcm_s16le',str(audio)],check=True)
data=json.loads((OUT/'lyrics-alignment-candidate.json').read_text())
assert data['audioSha256']==EXPECTED
tail=data['lyrics'][-4:]
spec=importlib.util.spec_from_file_location('alignment',ROOT/'tools/acapella-extractor/align_lyrics.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
texts=[x['text'] for x in tail]
import ctc_forced_aligner as cfa
import onnxruntime as ort
model=ROOT/'tools/acapella-extractor/models/ctc_forced_aligner.onnx'
options=ort.SessionOptions()
options.intra_op_num_threads=4
session=ort.InferenceSession(str(model),sess_options=options,providers=['CPUExecutionProvider'])
waveform=cfa.load_audio(str(audio),ret_type='np')
emissions,stride=cfa.generate_emissions(session,waveform,window_length=30,context_length=2,batch_size=1)
tokens,text=cfa.preprocess_text('\n'.join(texts),romanize=True,language='tel',split_size='word',star_frequency='segment')
segments,scores,blank=cfa.get_alignments(emissions,tokens,cfa.Tokenizer())
spans=cfa.get_spans(tokens,segments,blank)
# The library pads the last word with the complete trailing blank segment.
# Use observed nonblank token boundaries rather than displaying a word to EOF.
trimmed=[]
for span in spans:
    left,right=0,len(span)
    while left<right and span[left].label==blank: left+=1
    while right>left and span[right-1].label==blank: right-=1
    trimmed.append(span[left:right] if left<right else span)
words=cfa.postprocess_results(text,trimmed,stride,scores)
grouped=module.group_words_to_lines(words,[{'name':'Final chorus','lines':texts}],texts)
for old,new in zip(tail,grouped):
    new['start_time']=round(new['start_time']+start,3)
    new['end_time']=round(new['end_time']+start,3)
    for w in new['words']:
        w['start_time']=round(w['start_time']+start,3)
        w['end_time']=round(w['end_time']+start,3)
    old.update(start_time=new['start_time'],end_time=new['end_time'],words=new['words'],
               reviewFlags=['bounded_realign_requires_listening'],
               repairEvidence={'window':[start,end],'priorFailure':'full-song aligner assigned final word to long outro',
                               'method':'fresh CTC on exact canonical excerpt; first/last nonblank token boundaries, excluding library-added trailing silence; no interpolated word timings'})
save('lyrics-alignment-v2-candidate.json',data)
print(json.dumps(tail,ensure_ascii=False,indent=2))
