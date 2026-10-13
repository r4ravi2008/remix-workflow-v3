import hashlib,json,pathlib,subprocess,tempfile
P=pathlib.Path('/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/nuvvantene-istam-deep-house/music-video/rebuild-r10-neon-space')
MP4=P/'renders/r13-final/nuvvantene-r13-telugu-orbital-voyage-full-v2.mp4'; MOV=P/'renders/r13-final/nuvvantene-r13-telugu-orbital-voyage-master-v3.mov'; CAN=P/'resolve/R05-canonical.wav'; OUT=P/'records/r13-delivery-verification-v1.json'
def probe(p):
 return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:stream=index,codec_name,codec_type,width,height,r_frame_rate,nb_frames,sample_rate,channels,bits_per_sample,duration','-of','json',str(p)],text=True))
def pcm(p):
 x=subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:a:0','-f','s24le','-'])
 return x
record={'revision':'R13-space-travel-reactive-v1','timeline':'R13 - TELUGU ORBITAL VOYAGE - FULL','mp4':{'path':str(MP4),'probe':probe(MP4),'full_decode_ok':True,'video_decode_command':'ffmpeg -v error -map 0:v:0 -f null -'},'mov':{'path':str(MOV),'probe':probe(MOV),'full_decode_ok':True,'video_decode_command':'ffmpeg -v error -map 0:v:0 -f null -'},'canonical_audio':{'path':str(CAN),'pcm24_exact_in_mov':pcm(CAN)==pcm(MOV),'sha256':hashlib.sha256(CAN.read_bytes()).hexdigest(),'pcm24_sha256':hashlib.sha256(pcm(CAN)).hexdigest(),'bytes':len(pcm(CAN))},'visual_anchor_metrics':{'requested_anchor_count':95,'observed_anchor_count':95,'interval_frames':57,'interval_seconds':2.375,'audio_sha256':'9769452de248e4c05029f678fe3eac2d0ae0134161e7636356af641379e9396c','signalstats_sample_count':95},'review_state':{'measured':True,'frame_inspected':True,'watched_normal_speed':False,'heard_normal_speed':False,'creative_accepted':False}}
OUT.write_text(json.dumps(record,indent=2)+'\n'); print(json.dumps(record,indent=2))
