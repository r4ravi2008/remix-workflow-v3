"""Replace the failing long TubeCreate3D paths with native cylinder meshes.

Standard Shape3D geometry was render-tested at a negative camera depth where
TubeCreate3D no longer appeared. The path, palette and fixed widths are retained.
"""
from pathlib import Path
import json,math

P=Path('/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/nuvvantene-istam-deep-house/music-video/rebuild-r10-neon-space')
assert project.GetName()=='NUVVANTENE - R10 - ONE ORBIT' and not project.IsRenderingInProgress()
t=project.GetCurrentTimeline();assert t.GetName()=='R14 - NATIVE LIGHT RIBBONS - FULL PROVISIONAL'
t.SetCurrentTimecode('00:03:41:14')
env=t.GetItemListInTrack('video',1)[0];c=env.GetFusionCompByIndex(1);c.Lock()
scene=c.FindTool('FixedWorld')
for i in scene.GetInputList().values():
    key=i.GetAttrs().get('INPS_ID','')
    if key.startswith('SceneInput'):scene.ConnectInput(key,None)
for name in ['CyanPath1','CyanPath2','CyanPath3','SelectedAccentTrace','NativeCylinderCapabilityProbe']:
    node=c.FindTool(name)
    if node:node.Delete()
scene.ConnectInput('SceneInput1',c.FindTool('ForwardCamera'))

def add_cylinder(name,radius,height,centre,angle_x,angle_y,material,index):
    n=c.AddTool('Shape3D',False);n.SetAttrs({'TOOLS_Name':name});n.SetInput('Shape','SurfaceCylinderInputs')
    for key,value in [('SurfaceCylinderInputs.Radius',radius),('SurfaceCylinderInputs.Height',height),('SurfaceCylinderInputs.SubdivisionLevelBase',12),('SurfaceCylinderInputs.SubdivisionLevelHeight',1),('Transform3DOp.Rotate.X',angle_x),('Transform3DOp.Rotate.Y',angle_y)]:n.SetInput(key,value)
    for axis,value in zip('XYZ',centre):n.SetInput('Transform3DOp.Translate.'+axis,value)
    assert n.ConnectInput('MaterialInput',material)
    assert scene.ConnectInput('SceneInput'+str(index),n)
    return n

index=2;meshes=[]
for rail,(ox,oy) in enumerate([(-3.5,-1.7),(3.7,-1.15),(-1.8,2.2)],1):
    points=[]
    for k in range(24):
        z=6-22.5*k;points.append([ox+.55*math.sin((-z+6)/52),oy+.32*math.sin((-z+6)/68),z])
    for segment,(a,b) in enumerate(zip(points[:-1],points[1:]),1):
        delta=[b[k]-a[k] for k in range(3)];length=math.sqrt(sum(v*v for v in delta))
        centre=[(a[k]+b[k])/2 for k in range(3)]
        name=f'CyanRail{rail}Segment{segment:02}'
        angle_x=math.degrees(math.acos(delta[1]/length));angle_y=math.degrees(math.atan2(delta[0],delta[2]))
        n=add_cylinder(name,.016,length*1.003,centre,angle_x,angle_y,c.FindTool('CyanEmission'),index)
        meshes.append({'name':name,'radius':n.GetInput('SurfaceCylinderInputs.Radius',0),'centre':centre,'height':length*1.003})
        index+=1

trace=add_cylinder('CrimsonTravellingSeam',.026,1.8,[3.7,-1.15,0],90,180,c.FindTool('CrimsonTraceEmission'),index)
controls=json.loads((P/'analysis/r14-native/full-controls-a01.json').read_text())
accents=controls['accents'];age='time-'+str(accents[-1])
for accent,next_accent in reversed(list(zip(accents[:-1],accents[1:]))):age='iif(time<'+str(next_accent)+',time-'+str(accent)+','+age+')'
age='('+age+')';z='('+controls['camera_z']+'-4-70*min(1,max(0,'+age+'/36)))'
for axis,expression in [('Z',z),('X','3.7+.55*sin((6-'+z+')/52)'),('Y','-1.15+.32*sin((6-'+z+')/68)')]:
    next(i for i in trace.GetInputList().values() if i.GetAttrs().get('INPS_ID')=='Transform3DOp.Translate.'+axis).SetExpression(expression)
c.Unlock();assert resolve.GetProjectManager().SaveProject()
assert env.ExportFusionComp(str(P/'resolve/r14-native/full-native-environment-a02.comp'),1)
assert resolve.GetProjectManager().ExportProject(project.GetName(),str(P/'resolve/r14-native/nuvvantene-r14-native-full-a02.drp'))
record={'revision':'R14-full-native-a02','replacement':'Standard native Shape3D cylinder meshes follow the same fixed curved paths. No old overlay tracks consumed.','observed_failure':'TubeCreate3D paths ceased appearing after the camera entered negative Z. Cause is not claimed resolved. Standard cylinder render proved visible at frame 1543 with the original forward camera.','cyan_meshes':meshes,'crimson_trace':{'radius':.026,'length':1.8,'animated_dimensions':False,'position_animated':True},'camera_forward_formula':controls['camera_z'],'width_animation':False,'review':{'rendered':False,'frame_inspected':False,'watched':False,'heard':False,'creative_acceptance':False}}
(P/'records/r14-native/world-mesh-repair-a02.json').write_text(json.dumps(record,indent=2)+'\n')
result={'native_meshes':len(meshes),'crimson_trace':1,'editable_checkpoint':'nuvvantene-r14-native-full-a02.drp'}
