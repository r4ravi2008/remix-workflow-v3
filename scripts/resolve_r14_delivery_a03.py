"""Create a native Resolve delivery timeline from the corrected rendered master."""
from pathlib import Path
import json

P=Path('/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/nuvvantene-istam-deep-house/music-video/rebuild-r10-neon-space')
assert project.GetName()=='NUVVANTENE - R10 - ONE ORBIT' and not project.IsRenderingInProgress()
verification=json.loads((P/'records/r14-native/master-technical-a03.json').read_text());assert verification['sample_identical']
master=P/'renders/r14-native/nuvvantene-r14-native-ribbons-master-a03.mov'
pool=project.GetMediaPool();media=pool.ImportMedia([str(master)]);assert len(media)==1
name='R14 - DELIVERY A03 FROM PCM MASTER'
assert not any(project.GetTimelineByIndex(i).GetName()==name for i in range(1,project.GetTimelineCount()+1))
t=pool.CreateEmptyTimeline(name);assert project.SetCurrentTimeline(t);t.SetStartTimecode('00:00:00:00')
items=pool.AppendToTimeline([{'mediaPoolItem':media[0],'startFrame':0,'endFrame':5319,'recordFrame':0}]);assert items
video=t.GetItemListInTrack('video',1);audio=t.GetItemListInTrack('audio',1)
assert len(video)==1 and len(audio)==1 and t.GetEndFrame()==5319
assert video[0].GetDuration()==5319 and audio[0].GetDuration()==5319
readback={'revision':'R14-full-native-a03','timeline':name,'editable_film_timeline':'R14 - NATIVE LIGHT RIBBONS - FULL PROVISIONAL','master':str(master),'master_sha256':verification['sha256'],'frames':t.GetEndFrame(),'fps':t.GetSetting('timelineFrameRate'),'video_items':[{'start':i.GetStart(),'end':i.GetEnd(),'source':i.GetMediaPoolItem().GetClipProperty('File Path'),'properties':i.GetProperty()} for i in video],'audio_items':[{'start':i.GetStart(),'end':i.GetEnd(),'source':i.GetMediaPoolItem().GetClipProperty('File Path'),'properties':i.GetProperty()} for i in audio],'assembly_owner':'Resolve; primary film uses 50 editable native Fusion compositions. This timeline only encodes the rendered PCM master for playback.','watched':False,'heard':False}
(P/'records/r14-native/delivery-wrapper-readback-a03.json').write_text(json.dumps(readback,indent=2)+'\n')
assert resolve.GetProjectManager().SaveProject()
assert project.SetCurrentRenderFormatAndCodec('mp4','H264')
assert project.SetRenderSettings({'TargetDir':str(P/'renders/r14-native'),'CustomName':'nuvvantene-r14-native-ribbons-full-a03','MarkIn':0,'MarkOut':5318,'FormatWidth':1920,'FormatHeight':1080,'FrameRate':24,'ExportVideo':True,'ExportAudio':True,'VideoQuality':20000})
assert project.SetRenderSettings({'AudioCodec':'aac','AudioSampleRate':48000})
j=project.AddRenderJob();assert j
assert project.StartRendering(j)
result={'job':j,'settings':next(x for x in project.GetRenderJobList() if x['JobId']==j),'delivery_timeline':name}
