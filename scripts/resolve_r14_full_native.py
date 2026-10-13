"""Assemble the full provisional R14 film in Resolve from the native proof.

The user authorized full provisional continuation with audiovisual review pending.
R13 and all immutable source assets remain available as predecessors.
"""
from pathlib import Path
import json,math

P=Path('/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/nuvvantene-istam-deep-house/music-video/rebuild-r10-neon-space')
assert project.GetName()=='NUVVANTENE - R10 - ONE ORBIT'
assert not project.IsRenderingInProgress()
claim=json.loads(Path('/tmp/remix-resolve-reservation.json').read_text())
assert claim['status']=='active' and claim['owner_thread']=='01a0ff3f-8968-7922-a88b-74ed982185f8'
auth=json.loads((P.parent/'rebuild-r08/full-song-a01/full-motion-v02/records/full-film-authorization.json').read_text())
assert 'full-song provisional' in auth['scope']
controls=json.loads((P/'analysis/r14-native/full-controls-a01.json').read_text())
screenplay=json.loads((P/'screenplay.json').read_text())
by_start={s['start']:s for s in screenplay['shots']}
source=next(project.GetTimelineByIndex(i) for i in range(1,project.GetTimelineCount()+1) if project.GetTimelineByIndex(i).GetName()=='R13 - TELUGU ORBITAL VOYAGE - FULL')
name='R14 - NATIVE LIGHT RIBBONS - FULL PROVISIONAL'
assert name not in [project.GetTimelineByIndex(i).GetName() for i in range(1,project.GetTimelineCount()+1)]
pool=project.GetMediaPool()
carrier=source.GetItemListInTrack('video',1)[0].GetMediaPoolItem()
audio=source.GetItemListInTrack('audio',1)[0].GetMediaPoolItem()
t=pool.CreateEmptyTimeline(name);t.SetStartTimecode('00:00:00:00')
assert project.SetCurrentTimeline(t)
t.AddTrack('video');t.AddTrack('video')
for index,label in enumerate(['NATIVE 3D WORLD','PROTECTED BHARATANATYAM FIGURE','PRESERVED LYRIC CUES'],1):t.SetTrackName('video',index,label)
t.SetTrackName('audio',1,'CANONICAL R05 - UNCHANGED')

def inp(node,key):return next(i for i in node.GetInputList().values() if i.GetAttrs().get('INPS_ID')==key)
def add(c,kind,name):
    n=c.AddTool(kind,False);assert n is not None,kind
    n.SetAttrs({'TOOLS_Name':name});return n
def append(a,b,track):
    item=pool.AppendToTimeline([{'mediaPoolItem':carrier,'startFrame':0,'endFrame':b-a,'recordFrame':a,'trackIndex':track,'mediaType':1}])[0]
    assert item.GetDuration()==b-a
    return item

env=append(0,5319,1)
t.SetCurrentTimecode('00:03:41:14')
c=env.ImportFusionComp(str(P/'resolve/r14-native/native-ribbon-environment-a03.comp'));c.Lock()
c.SetAttrs({'COMPN_RenderStart':0,'COMPN_RenderEnd':5318,'COMPN_GlobalStart':0,'COMPN_GlobalEnd':5318})
for k in range(1,5):
    n=c.FindTool('CyanPath'+str(k)) if k<4 else c.FindTool('SelectedAccentTrace')
    ox,oy=[(-3.5,-1.7),(3.7,-1.15),(-1.8,2.2),(3.7,-1.15)][k-1]
    for point in range(24):
        z=6-22.5*point
        for axis,value in zip('XYZ',[ox+.55*math.sin((-z+6)/52),oy+.32*math.sin((-z+6)/68),z]):n.SetInput(f'KD_InputsTubeCreate3D.Point{point+1}{axis}',value)
mat=c.FindTool('CyanEmission');curve=inp(mat,'Emission.Emission').GetConnectedOutput().GetTool()
curve.SetKeyFrames({i:{1:v,'Flags':{'Linear':True}} for i,v in enumerate(controls['emission'])},True)
camera=c.FindTool('ForwardCamera')
inp(camera,'Transform3DOp.Translate.Z').SetExpression(controls['camera_z'])
inp(camera,'Transform3DOp.Translate.X').SetExpression('.55*sin((6-('+controls['camera_z']+'))/52)')
inp(camera,'Transform3DOp.Translate.Y').SetExpression('.32*sin((6-('+controls['camera_z']+'))/68)')
camera.SetInput('PerspFarClip',400)
renderer=c.FindTool('Native3DRenderer');renderer.SetInput('CameraSelector','ForwardCamera')
accents=controls['accents'];age='time-'+str(accents[-1])
for accent,next_accent in reversed(list(zip(accents[:-1],accents[1:]))):age='iif(time<'+str(next_accent)+',time-'+str(accent)+','+age+')'
age='('+age+')'
inp(c.FindTool('CrimsonTraceEmission'),'Emission.Emission').SetExpression('iif(time<'+str(accents[0])+',0,1.3*max(0,1-'+age+'/36))')
trace=c.FindTool('SelectedAccentTrace')
start='min(.98,max(0,(6-('+controls['camera_z']+')+2)/517.5+'+age+'/36*.18))'
inp(trace,'KD_InputsTubeCreate3D.RangeStart').SetExpression(start)
inp(trace,'KD_InputsTubeCreate3D.RangeEnd').SetExpression('min(1,'+start+'+.012)')
inp(c.FindTool('GeometryInVoid'),'Blend').SetExpression('min(1,time/48)*min(1,(5318-time)/64)')
c.Unlock()
body=[];gaps=[]
proof_exports={614:1,738:2,808:3}
for src in source.GetItemListInTrack('video',1):
    a,b=src.GetStart(),src.GetEnd();card=by_start.get(a)
    source_comp=src.GetFusionCompByIndex(1);media=source_comp.FindTool('MediaIn1')
    source_path=media.GetAttrs().get('TOOLS_Clip_Path','')
    if not source_path.endswith('.mp4'):
        gaps.append({'a':a,'b':b,'replacement':'continuous native 3D corridor; old point/sphere graphics omitted'})
        continue
    item=append(a,b,2)
    if a in proof_exports:
        cc=item.ImportFusionComp(str(P/f'resolve/r14-native/protected-subject-a03-{proof_exports[a]}.comp'))
        cc.Lock()
        mask=cc.FindTool('MotionMatchedSubjectMatte')
        align=add(cc,'TimeStretcher','AlignImportedMatte')
        align.ConnectInput('Input',mask)
        inp(align,'SourceTime').SetExpression('MotionMatchedSubjectMatte.GlobalIn+time')
        cc.FindTool('ProtectSubjectAndRemoveOrbit').ConnectInput('Image2',align)
        cc.Unlock()
        matte_path='motion-matched proof sequence'
    else:
        exported=P/f'resolve/r14-native/full-source-{a}.comp';assert src.ExportFusionComp(str(exported),1)
        cc=item.ImportFusionComp(str(exported));cc.Lock()
        motion=cc.FindTool('MotionMap') or cc.FindTool('IntentionalFinalPose')
        expression=inp(motion,'SourceTime').GetExpression()
        if not expression and a==5120:expression=str(motion.GetInput('SourceTime',0))
        assert expression, {'source':source_path,'start':a}
        inp(motion,'SourceTime').SetExpression('MediaIn1.GlobalIn+('+expression+')')
        anchor=card['anchor'].split('-')[0]
        matte_path=str(P/f'analysis/r14-native/{anchor}-full-motion-envelope-a01.png')
        loader=add(cc,'Loader','ProtectedMotionEnvelope');loader.SetInput('Clip',matte_path);loader.SetInput('Loop',1)
        matte=add(cc,'Custom','ProtectFigureAndClearBackground')
        matte.ConnectInput('Image1',motion);matte.ConnectInput('Image2',loader)
        for key,value in [('RedExpression','r1*r2'),('GreenExpression','g1*r2'),('BlueExpression','b1*r2'),('AlphaExpression','r2')]:matte.SetInput(key,value)
        cc.FindTool('MediaOut1').ConnectInput('Input',matte)
        cc.Unlock()
    cc.SetAttrs({'COMPN_RenderStart':0,'COMPN_RenderEnd':b-a-1,'COMPN_GlobalStart':0,'COMPN_GlobalEnd':5318})
    item.SetFades({'FadeIn':5,'FadeOut':48 if a==5120 else 5});item.SetClipColor('Cyan')
    motion=cc.FindTool('MotionMap') or cc.FindTool('IntentionalFinalPose')
    body.append({'id':card['id'] if card else str(a),'a':a,'b':b,'source':source_path,'matte':matte_path,'source_times':[motion.GetInput('SourceTime',f) for f in [0,b-a-1]]})
lyrics=[]
for src in source.GetItemListInTrack('video',2):
    a,b=src.GetStart(),src.GetEnd();exported=P/f'resolve/r14-native/full-lyric-{a}.comp'
    assert src.ExportFusionComp(str(exported),1)
    item=append(a,b,3);cc=item.ImportFusionComp(str(exported));cc.Lock()
    text=next(n for n in cc.GetToolList(False).values() if n.GetAttrs().get('TOOLS_RegID')=='TextPlus')
    text.SetInput('Size',.05);text.SetInput('Center',{1:.72,2:.54})
    cc.Unlock();item.SetClipColor('Blue')
    lyrics.append({'a':a,'b':b,'text':text.GetInput('StyledText',20),'size':text.GetInput('Size',20)})
item=pool.AppendToTimeline([{'mediaPoolItem':audio,'startFrame':0,'endFrame':5319,'recordFrame':0,'trackIndex':1,'mediaType':2}])[0]
assert item.GetDuration()==5319 and t.GetEndFrame()==5319
env.AddMarker(0,'Cyan','R14 NATIVE WORLD','Fixed geometry, forward camera, emission response only. Provisional audiovisual review.',5319,'R14')
assert resolve.GetProjectManager().SaveProject()
assert env.ExportFusionComp(str(P/'resolve/r14-native/full-native-environment-a01.comp'),1)
assert resolve.GetProjectManager().ExportProject(project.GetName(),str(P/'resolve/r14-native/nuvvantene-r14-native-full-a01.drp'))
readback={'revision':'R14-full-native-a01','project':project.GetName(),'timeline':t.GetName(),'frames':5319,'fps':24,'audio_source':audio.GetClipProperty('File Path'),'body':body,'native_environment_gaps':gaps,'lyrics':lyrics,'tracks':3,'obsolete_overlays_consumed':False,'camera_samples':[[f,camera.GetInput('Transform3DOp.Translate.Z',f)] for f in [0,614,1366,2752,4152,5318]],'radii':{n:c.FindTool(n).GetInput('KD_InputsTubeCreate3D.Radius',0) for n in ['CyanPath1','CyanPath2','CyanPath3','SelectedAccentTrace']},'review':{'measured':False,'frame_inspected':False,'watched':False,'heard':False,'creative_acceptance':False},'authorization_record':str(P.parent/'rebuild-r08/full-song-a01/full-motion-v02/records/full-film-authorization.json')}
(P/'records/r14-native/full-native-readback-a01.json').write_text(json.dumps(readback,indent=2)+'\n')
result={'timeline':t.GetName(),'frames':5319,'body_clips':len(body),'lyric_cues':len(lyrics),'native_environment_gaps':len(gaps),'camera_samples':readback['camera_samples']}
