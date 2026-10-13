"""Verify the native PCM export against the canonical packed 24-bit samples."""
from pathlib import Path
import hashlib,json,subprocess,wave
import numpy as np

P=Path('/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/nuvvantene-istam-deep-house/music-video/rebuild-r10-neon-space')
master=P/'renders/r14-native/nuvvantene-r14-native-ribbons-master-a03.mov'
canonical=P/'resolve/R05-canonical.wav'
with wave.open(str(canonical)) as wav:
    expected=wav.readframes(wav.getnframes());configuration=[wav.getnchannels(),wav.getsampwidth(),wav.getframerate(),wav.getnframes()]
actual=subprocess.run(['/opt/homebrew/bin/ffmpeg','-v','error','-i',str(master),'-map','0:a:0','-f','s24le','-acodec','pcm_s24le','-'],capture_output=True,check=True).stdout
equal=actual==expected
probe=json.loads(subprocess.run(['/opt/homebrew/bin/ffprobe','-v','error','-show_streams','-show_format','-of','json',str(master)],capture_output=True,text=True,check=True).stdout)
video=next(s for s in probe['streams'] if s['codec_type']=='video');audio=next(s for s in probe['streams'] if s['codec_type']=='audio')
assert (video['width'],video['height'],video['r_frame_rate'],int(video['nb_frames']))==(1920,1080,'24/1',5319)
assert audio['codec_name']=='pcm_s24le' and audio['sample_rate']=='48000'
decode=subprocess.run(['/opt/homebrew/bin/ffmpeg','-v','error','-i',str(master),'-f','null','-'],capture_output=True,text=True)
assert decode.returncode==0,decode.stderr
record={'master':str(master),'sha256':hashlib.file_digest(master.open('rb'),'sha256').hexdigest(),'canonical_audio':str(canonical),'canonical_sha256':hashlib.file_digest(canonical.open('rb'),'sha256').hexdigest(),'audio_configuration':configuration,'canonical_pcm_sha256':hashlib.sha256(expected).hexdigest(),'rendered_pcm_sha256':hashlib.sha256(actual).hexdigest(),'rendered_pcm_bytes':len(actual),'sample_identical':equal,'probe':probe,'decode_exit':decode.returncode,'heard':False}
(P/'records/r14-native/master-technical-a03.json').write_text(json.dumps(record,indent=2)+'\n')
assert equal,'Native export PCM differs from canonical samples; inspect before delivery.'
print({'sample_identical':equal,'pcm_sample_frames':len(actual)//6,'master_bytes':master.stat().st_size,'sha256':record['sha256']})
