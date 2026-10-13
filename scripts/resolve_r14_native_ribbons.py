from pathlib import Path
import json
import math

P = Path('/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/nuvvantene-istam-deep-house/music-video/rebuild-r10-neon-space')
controls = json.loads((P/'analysis/r14-native/audio-controls-a01.json').read_text())
assert project.GetName() == 'NUVVANTENE - R10 - ONE ORBIT'
assert not project.IsRenderingInProgress()
claim=json.loads(Path('/tmp/remix-resolve-reservation.json').read_text())
assert claim['owner_thread']=='01a0ff3f-8968-7922-a88b-74ed982185f8' and claim['status']=='active'
source = next(project.GetTimelineByIndex(i) for i in range(1,project.GetTimelineCount()+1) if project.GetTimelineByIndex(i).GetName()=='R13 - TELUGU ORBITAL VOYAGE - FULL')
name = 'R14 - NATIVE LIGHT RIBBONS - PROOF A01'
assert name not in [project.GetTimelineByIndex(i).GetName() for i in range(1,project.GetTimelineCount()+1)]
pool=project.GetMediaPool()
carrier=pool.ImportMedia([str(P/'resolve/native-composition-carrier.mov')])[0]
audio=source.GetItemListInTrack('audio',1)[0].GetMediaPoolItem()
t=pool.CreateEmptyTimeline(name)
t.SetStartTimecode('00:00:00:00')
assert project.SetCurrentTimeline(t)
t.AddTrack('video'); t.AddTrack('video')
t.SetTrackName('video',1,'NATIVE 3D - FIXED LIGHT PATHS')
t.SetTrackName('video',2,'PROTECTED SILHOUETTE')
t.SetTrackName('video',3,'PRESERVED LYRIC CUES')
t.SetTrackName('audio',1,'CANONICAL R05 - SOURCE 614 TO 948')
N=controls['proof_frames']

def tool(c,kind,name):
    v=c.AddTool(kind,False)
    assert v is not None,kind
    v.SetAttrs({'TOOLS_Name':name})
    return v

def input_object(node,key):
    return next(i for i in node.GetInputList().values() if i.GetAttrs().get('INPS_ID')==key)

env=pool.AppendToTimeline([{'mediaPoolItem':carrier,'startFrame':0,'endFrame':N,'recordFrame':0,'trackIndex':1,'mediaType':1}])[0]
c=env.AddFusionComp(); c.Lock()
black=tool(c,'Background','BlackVoid')
black.SetInput('Width',1920);black.SetInput('Height',1080)
for key in ['TopLeftRed','TopLeftGreen','TopLeftBlue']:black.SetInput(key,0)
scene=tool(c,'Merge3D','FixedWorld')
mat=tool(c,'MtlPBRUber','CyanEmission')
mat.SetInput('Base.Base',0)
for key,value in zip(['Red','Green','Blue'],[.018,.58,.72]):
    mat.SetInput('Emission.Color.'+key,value)
mat.AddModifier('Emission.Emission','BezierSpline')
curve=input_object(mat,'Emission.Emission').GetConnectedOutput().GetTool()
curve.SetKeyFrames({i:{1:value,'Flags':{'Linear':True}} for i,value in enumerate(controls['emission'])},True)

def path_geometry(name,offset,index,material,trace=False):
    pipe=tool(c,'KD_TubeCreate3D',name)
    pipe.SetInput('KD_InputsTubeCreate3D.PointCreation',0)
    pipe.SetInput('KD_InputsTubeCreate3D.PointCount',24)
    pipe.SetInput('KD_InputsTubeCreate3D.ProfileSegments',8)
    pipe.SetInput('KD_InputsTubeCreate3D.Radius',.010 if not trace else .012)
    pipe.SetInput('KD_InputsTubeCreate3D.Segments',192)
    pipe.SetInput('KD_InputsTubeCreate3D.PointJitterMultiplier',0)
    for k in range(24):
        z=6-7.5*k
        x=offset[0]+.55*math.sin((-z+6)/52)
        y=offset[1]+.32*math.sin((-z+6)/68)
        for axis,value in zip('XYZ',[x,y,z]):
            pipe.SetInput(f'KD_InputsTubeCreate3D.Point{k+1}{axis}',value)
    pipe.ConnectInput('MaterialInput',material)
    scene.ConnectInput('SceneInput'+str(index),pipe)
    return pipe

offsets=[(-3.5,-1.7),(3.7,-1.15),(-1.8,2.2)]
for k,offset in enumerate(offsets):path_geometry('CyanPath'+str(k+1),offset,k+1,mat)
red=tool(c,'MtlPBRUber','CrimsonTraceEmission');red.SetInput('Base.Base',0)
for key,value in zip(['Red','Green','Blue'],[.9,.012,.055]):red.SetInput('Emission.Color.'+key,value)
accents=controls['selected_accents']
age='time-'+str(accents[-1])
for accent,next_accent in reversed(list(zip(accents[:-1],accents[1:]))):
    age='iif(time<'+str(next_accent)+',time-'+str(accent)+','+age+')'
age='('+age+')'
red_expression='iif(time<'+str(accents[0])+',0,1.3*max(0,1-'+age+'/36))'
input_object(red,'Emission.Emission').SetExpression(red_expression)
trace=path_geometry('SelectedAccentTrace',offsets[1],4,red,True)
input_object(trace,'KD_InputsTubeCreate3D.RangeStart').SetExpression('min(0.98,max(0,'+age+'/36))')
input_object(trace,'KD_InputsTubeCreate3D.RangeEnd').SetExpression('min(1,0.035+min(0.98,max(0,'+age+'/36)))')
camera=tool(c,'Camera3D','ForwardCamera')
input_object(camera,'Transform3DOp.Translate.Z').SetExpression(controls['camera']['formula_z'])
camera.SetInput('FLength',24);camera.SetInput('PerspFarClip',300)
scene.ConnectInput('SceneInput5',camera)
renderer=tool(c,'Renderer3D','Native3DRenderer')
renderer.ConnectInput('SceneInput',scene)
renderer.SetInput('RendererType','RendererOpenGL')
renderer.SetInput('Width',1920);renderer.SetInput('Height',1080)
renderer.SetInput('RendererOpenGL.LightingEnabled',1)
glow=tool(c,'SoftGlow','RestrainedNeonBloom');glow.ConnectInput('Input',renderer)
glow.SetInput('Gain',.28);glow.SetInput('Threshold',.12);glow.SetInput('XGlowSize',7);glow.SetInput('YGlowSize',7);glow.SetInput('Blend',.3)
merge=tool(c,'Merge','GeometryInVoid');merge.ConnectInput('Background',black);merge.ConnectInput('Foreground',glow)
c.FindTool('MediaOut1').ConnectInput('Input',merge)
c.Unlock(); env.LoadFusionCompByName(env.GetFusionCompNameList()[0])
env.SetClipColor('Cyan')
env.AddMarker(0,'Cyan','NATIVE GEOMETRY','Fixed radii; uninterrupted forward travel; amplitude changes emission only',N,'R14 native proof')
body=[]
for src,mask_name in zip(source.GetItemListInTrack('video',1)[3:6],['S01','S03','S04']):
    a,b=src.GetStart(),src.GetEnd()
    export=P/f'resolve/r14-native/source-{mask_name}.comp'
    assert src.ExportFusionComp(str(export),1)
    it=pool.AppendToTimeline([{'mediaPoolItem':carrier,'startFrame':0,'endFrame':b-a,'recordFrame':a-614,'trackIndex':2,'mediaType':1}])[0]
    cc=it.ImportFusionComp(str(export)); cc.Lock()
    output=cc.FindTool('MediaOut1')
    original=input_object(output,'Input').GetConnectedOutput().GetTool()
    loader=tool(cc,'Loader','SubjectMatte');loader.SetInput('Clip',str(P/f'analysis/r14-native/{mask_name}-subject-matte-a01.png'))
    matte=tool(cc,'Custom','ProtectSubjectAndRemoveOrbit');matte.ConnectInput('Image1',original);matte.ConnectInput('Image2',loader)
    matte.SetInput('RedExpression','r1*r2');matte.SetInput('GreenExpression','g1*r2');matte.SetInput('BlueExpression','b1*r2');matte.SetInput('AlphaExpression','r2')
    output.ConnectInput('Input',matte)
    cc.Unlock(); it.LoadFusionCompByName(it.GetFusionCompNameList()[0]);it.SetFades({'FadeIn':5,'FadeOut':5})
    body.append({'start':it.GetStart(),'end':it.GetEnd(),'mask':mask_name})
lyrics=[]
for src in source.GetItemListInTrack('video',2)[:3]:
    a,b=src.GetStart(),src.GetEnd()
    export=P/f'resolve/r14-native/source-lyric-{a}.comp'
    assert src.ExportFusionComp(str(export),1)
    it=pool.AppendToTimeline([{'mediaPoolItem':carrier,'startFrame':0,'endFrame':b-a,'recordFrame':a-614,'trackIndex':3,'mediaType':1}])[0]
    cc=it.ImportFusionComp(str(export))
    text=next(n for n in cc.GetToolList(False).values() if n.GetAttrs().get('TOOLS_RegID')=='TextPlus')
    lyrics.append({'start':it.GetStart(),'end':it.GetEnd(),'text':text.GetInput('StyledText',0)})
audio_item=pool.AppendToTimeline([{'mediaPoolItem':audio,'startFrame':614,'endFrame':948,'recordFrame':0,'trackIndex':1,'mediaType':2}])[0]
assert audio_item.GetDuration()==N and t.GetEndFrame()==N
assert resolve.GetProjectManager().SaveProject()
assert env.ExportFusionComp(str(P/'resolve/r14-native/native-ribbon-environment-a01.comp'),1)
readback={'project':project.GetName(),'timeline':t.GetName(),'frames':N,'audio_source_frames':[614,948],'audio_source':audio.GetClipProperty('File Path'),'body':body,'lyrics':lyrics,'native_geometry':[n.GetAttrs().get('TOOLS_RegID') for n in c.GetToolList(False).values()],'renderer_type':renderer.GetInput('RendererType',0),'emission_samples':[[i,mat.GetInput('Emission.Emission',i)] for i in [0,50,100,200,333]],'camera_samples':[[i,camera.GetInput('Transform3DOp.Translate.Z',i)] for i in [0,50,100,200,333]],'render_formats':project.GetRenderFormats(),'mp4_codecs':project.GetRenderCodecs('mp4')}
(P/'records/r14-native/native-readback-a01.json').write_text(json.dumps(readback,indent=2)+'\n')
result=readback
