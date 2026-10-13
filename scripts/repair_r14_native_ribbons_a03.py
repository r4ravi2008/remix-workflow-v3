"""Repair the bound native R14 proof without changing R13."""
from pathlib import Path
import json

P=Path('/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/nuvvantene-istam-deep-house/music-video/rebuild-r10-neon-space')
assert project.GetName()=='NUVVANTENE - R10 - ONE ORBIT'
assert not project.IsRenderingInProgress()
claim=json.loads(Path('/tmp/remix-resolve-reservation.json').read_text())
assert claim['status']=='active' and claim['owner_thread']=='01a0ff3f-8968-7922-a88b-74ed982185f8'
t=project.GetCurrentTimeline()
assert t.GetName()=='R14 - NATIVE LIGHT RIBBONS - PROOF A01'
t.SetCurrentTimecode('00:00:13:21')
matte_records=json.loads((P/'analysis/r14-native/motion-mattes-a03.json').read_text())
readback=[]
for item,record in zip(t.GetItemListInTrack('video',2),matte_records):
    c=item.GetFusionCompByIndex(1);c.Lock()
    old=c.FindTool('SubjectMatte')
    fresh=c.FindTool('MotionMatchedSubjectMatte') or c.AddTool('Loader',False)
    fresh.SetAttrs({'TOOLS_Name':'MotionMatchedSubjectMatte'})
    fresh.SetInput('Clip',record['first_matte'])
    fresh.SetInput('Loop',0)
    fresh.SetInput('GlobalIn',0)
    fresh.SetInput('GlobalOut',record['frames']-1)
    fresh.SetInput('ClipTimeStart',0)
    fresh.SetInput('ClipTimeEnd',record['frames']-1)
    fresh.SetInput('HoldLastFrame',1)
    matte=c.FindTool('ProtectSubjectAndRemoveOrbit')
    matte.ConnectInput('Image2',fresh)
    if old:old.Delete()
    motion=c.FindTool('MotionMap')
    original=next(i for i in motion.GetInputList().values() if i.GetAttrs().get('INPS_ID')=='SourceTime')
    expression=original.GetExpression()
    # MediaIn's bound source begins at Fusion time 2 in this Resolve version.
    if expression and not expression.startswith('MediaIn1.GlobalIn+'):
        original.SetExpression('MediaIn1.GlobalIn+('+expression+')')
    c.Unlock()
    readback.append({'shot':record['shot'],'start':item.GetStart(),'end':item.GetEnd(),'loader':{k:fresh.GetInput(k,0) for k in ['Clip','GlobalIn','GlobalOut','ClipTimeStart','ClipTimeEnd','Loop']},'source_time_samples':[motion.GetInput('SourceTime',q) for q in [0,item.GetDuration()-1]]})
env=t.GetItemListInTrack('video',1)[0]
c=env.GetFusionCompByIndex(1);c.Lock()
c.FindTool('Native3DRenderer').SetInput('CameraSelector','ForwardCamera')
c.FindTool('Native3DRenderer').SetInput('RendererType','RendererOpenGL')
c.FindTool('Native3DRenderer').SetInput('RendererOpenGL.LightingEnabled',1)
for k in range(1,4):c.FindTool('CyanPath'+str(k)).SetInput('KD_InputsTubeCreate3D.Radius',.016)
mat=c.FindTool('CyanEmission')
for key,value in zip(['Red','Green','Blue'],[.02,.75,.95]):mat.SetInput('Emission.Color.'+key,value)
probe=c.FindTool('TemporaryGeometryProbeShape')
if probe:probe.Delete()
c.Unlock()
assert resolve.GetProjectManager().SaveProject()
for index,item in enumerate(t.GetItemListInTrack('video',2)):
    assert item.ExportFusionComp(str(P/f'resolve/r14-native/protected-subject-a03-{index+1}.comp'),1)
assert env.ExportFusionComp(str(P/'resolve/r14-native/native-ribbon-environment-a03.comp'),1)
(P/'records/r14-native/matte-integration-a03.json').write_text(json.dumps(readback,indent=2)+'\n')
result=readback
