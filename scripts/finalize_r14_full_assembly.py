"""Finish the existing partial R14 assembly after its coda tool-name check."""
from pathlib import Path
import json

P=Path('/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/nuvvantene-istam-deep-house/music-video/rebuild-r10-neon-space')
assert project.GetName()=='NUVVANTENE - R10 - ONE ORBIT' and not project.IsRenderingInProgress()
t=project.GetCurrentTimeline();assert t.GetName()=='R14 - NATIVE LIGHT RIBBONS - FULL PROVISIONAL'
t.SetCurrentTimecode('00:03:41:14')
source=next(project.GetTimelineByIndex(i) for i in range(1,project.GetTimelineCount()+1) if project.GetTimelineByIndex(i).GetName()=='R13 - TELUGU ORBITAL VOYAGE - FULL')
pool=project.GetMediaPool();carrier=source.GetItemListInTrack('video',1)[0].GetMediaPoolItem()
def inp(n,key):return next(i for i in n.GetInputList().values() if i.GetAttrs().get('INPS_ID')==key)
def add(c,kind,name):
    n=c.AddTool(kind,False);n.SetAttrs({'TOOLS_Name':name});return n
for item in t.GetItemListInTrack('video',2):
    c=item.GetFusionCompByIndex(1)
    if c.GetAttrs().get('COMPB_Locked'):c.Unlock()
    if item.GetStart() in [614,738,808]:
        c.Lock();mask=c.FindTool('MotionMatchedSubjectMatte')
        align=c.FindTool('AlignImportedMatte') or add(c,'TimeStretcher','AlignImportedMatte')
        align.ConnectInput('Input',mask);inp(align,'SourceTime').SetExpression('MotionMatchedSubjectMatte.GlobalIn+time')
        c.FindTool('ProtectSubjectAndRemoveOrbit').ConnectInput('Image2',align);c.Unlock()
    if item.GetStart()==5120:
        c.Lock();motion=c.FindTool('IntentionalFinalPose')
        inp(motion,'SourceTime').SetExpression('MediaIn1.GlobalIn+123')
        loader=add(c,'Loader','ProtectedMotionEnvelope');loader.SetInput('Clip',str(P/'analysis/r14-native/S02-full-motion-envelope-a01.png'));loader.SetInput('Loop',1)
        matte=add(c,'Custom','ProtectFigureAndClearBackground');matte.ConnectInput('Image1',motion);matte.ConnectInput('Image2',loader)
        for key,value in [('RedExpression','r1*r2'),('GreenExpression','g1*r2'),('BlueExpression','b1*r2'),('AlphaExpression','r2')]:matte.SetInput(key,value)
        c.FindTool('MediaOut1').ConnectInput('Input',matte);c.Unlock()
        item.SetFades({'FadeIn':5,'FadeOut':48})
assert not t.GetItemListInTrack('video',3) and not t.GetItemListInTrack('audio',1)
lyrics=[]
for src in source.GetItemListInTrack('video',2):
    a,b=src.GetStart(),src.GetEnd();exported=P/f'resolve/r14-native/full-lyric-{a}.comp'
    assert src.ExportFusionComp(str(exported),1)
    item=pool.AppendToTimeline([{'mediaPoolItem':carrier,'startFrame':0,'endFrame':b-a,'recordFrame':a,'trackIndex':3,'mediaType':1}])[0]
    c=item.ImportFusionComp(str(exported));c.Lock()
    text=next(n for n in c.GetToolList(False).values() if n.GetAttrs().get('TOOLS_RegID')=='TextPlus')
    text.SetInput('Size',.05);text.SetInput('Center',{1:.72,2:.54})
    c.Unlock();item.SetClipColor('Blue')
    lyrics.append({'a':a,'b':b,'text':text.GetInput('StyledText',20),'size':text.GetInput('Size',20)})
audio=source.GetItemListInTrack('audio',1)[0].GetMediaPoolItem()
item=pool.AppendToTimeline([{'mediaPoolItem':audio,'startFrame':0,'endFrame':5319,'recordFrame':0,'trackIndex':1,'mediaType':2}])[0]
assert item.GetDuration()==5319 and t.GetEndFrame()==5319
cards={s['start']:s for s in json.loads((P/'screenplay.json').read_text())['shots']}
body=[]
for item in t.GetItemListInTrack('video',2):
    a,b=item.GetStart(),item.GetEnd();c=item.GetFusionCompByIndex(1);motion=c.FindTool('MotionMap') or c.FindTool('IntentionalFinalPose')
    mask=c.FindTool('ProtectedMotionEnvelope') or c.FindTool('MotionMatchedSubjectMatte')
    body.append({'id':cards[a]['id'],'a':a,'b':b,'source':c.FindTool('MediaIn1').GetAttrs().get('TOOLS_Clip_Path'),'matte':mask.GetAttrs().get('TOOLS_Clip_Path') or mask.GetInput('Clip',0),'source_times':[motion.GetInput('SourceTime',f) for f in [0,b-a-1]],'enabled':item.GetClipEnabled()})
env=t.GetItemListInTrack('video',1)[0];c=env.GetFusionCompByIndex(1);camera=c.FindTool('ForwardCamera')
env.AddMarker(0,'Cyan','R14 NATIVE WORLD','Fixed geometry, forward camera, emission response only. Provisional audiovisual review.',5319,'R14')
assert resolve.GetProjectManager().SaveProject()
assert env.ExportFusionComp(str(P/'resolve/r14-native/full-native-environment-a01.comp'),1)
assert resolve.GetProjectManager().ExportProject(project.GetName(),str(P/'resolve/r14-native/nuvvantene-r14-native-full-a01.drp'))
readback={'revision':'R14-full-native-a01','project':project.GetName(),'timeline':t.GetName(),'frames':5319,'fps':24,'audio_source':audio.GetClipProperty('File Path'),'body':body,'native_environment_gaps':[{'a':i.GetStart(),'b':i.GetEnd(),'replacement':'native 3D corridor'} for i in source.GetItemListInTrack('video',1) if i.GetStart() not in {b['a'] for b in body}],'lyrics':lyrics,'tracks':3,'obsolete_overlays_consumed':False,'camera_samples':[[f,camera.GetInput('Transform3DOp.Translate.Z',f)] for f in [0,614,1366,2752,4152,5318]],'radii':{n:c.FindTool(n).GetInput('KD_InputsTubeCreate3D.Radius',0) for n in ['CyanPath1','CyanPath2','CyanPath3','SelectedAccentTrace']},'review':{'measured':False,'frame_inspected':False,'watched':False,'heard':False,'creative_acceptance':False},'authorization_record':str(P.parent/'rebuild-r08/full-song-a01/full-motion-v02/records/full-film-authorization.json')}
(P/'records/r14-native/full-native-readback-a01.json').write_text(json.dumps(readback,indent=2)+'\n')
result={'timeline':t.GetName(),'frames':5319,'body_clips':len(body),'lyric_cues':len(lyrics),'audio_path':readback['audio_source'],'camera_samples':readback['camera_samples']}
