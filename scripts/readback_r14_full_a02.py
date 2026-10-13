"""Record the actual native timeline and save its editable compositions."""
from pathlib import Path
import json

P=Path('/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/nuvvantene-istam-deep-house/music-video/rebuild-r10-neon-space')
assert project.GetName()=='NUVVANTENE - R10 - ONE ORBIT' and not project.IsRenderingInProgress()
t=project.GetCurrentTimeline();assert t.GetName()=='R14 - NATIVE LIGHT RIBBONS - FULL PROVISIONAL'
out=P/'resolve/r14-native/full-a02-compositions';out.mkdir(exist_ok=True)
inventory=[]
for track in range(1,4):
    for item in t.GetItemListInTrack('video',track):
        c=item.GetFusionCompByIndex(1);nodes=[]
        for n in c.GetToolList(False).values():
            attrs=n.GetAttrs();node={'name':attrs.get('TOOLS_Name'),'type':attrs.get('TOOLS_RegID')}
            if attrs.get('TOOLS_Clip_Path'):node['source_path']=attrs['TOOLS_Clip_Path']
            for key in ['Clip','GlobalIn','GlobalOut','StyledText','Size','Center','AlphaExpression','SurfaceCylinderInputs.Radius','SurfaceCylinderInputs.Height']:
                value=n.GetInput(key,0)
                if value is not None:node[key]=value
            if node['name'] in ['MotionMap','IntentionalFinalPose','ForwardCamera','CrimsonTravellingSeam']:
                node['source_times']=[n.GetInput('SourceTime',f) for f in [0,item.GetDuration()-1]]
                node['camera_z']=[n.GetInput('Transform3DOp.Translate.Z',f) for f in [0,614,1366,2752,4152,5318]]
            nodes.append(node)
        comp_path=out/f'V{track}-{item.GetStart():05}.comp'
        assert item.ExportFusionComp(str(comp_path),1)
        inventory.append({'track':track,'start':item.GetStart(),'end':item.GetEnd(),'duration':item.GetDuration(),'fades':item.GetFades(),'composition':str(comp_path),'nodes':nodes})
audio=[{'start':i.GetStart(),'end':i.GetEnd(),'source':i.GetMediaPoolItem().GetClipProperty('File Path'),'properties':i.GetProperty()} for i in t.GetItemListInTrack('audio',1)]
assert len(audio)==1 and (audio[0]['start'],audio[0]['end'])==(0,5319)
assert resolve.GetProjectManager().SaveProject()
assert resolve.GetProjectManager().ExportProject(project.GetName(),str(P/'resolve/r14-native/nuvvantene-r14-native-full-a02.drp'))
readback={'revision':'R14-full-native-a02','project':project.GetName(),'timeline':t.GetName(),'frames':t.GetEndFrame(),'fps':t.GetSetting('timelineFrameRate'),'video_tracks':t.GetTrackCount('video'),'audio':audio,'clips':inventory,'watched':False,'heard':False,'creative_acceptance':False}
(P/'records/r14-native/full-native-readback-a02.json').write_text(json.dumps(readback,indent=2)+'\n')
result={'timeline':t.GetName(),'frames':t.GetEndFrame(),'native_compositions':len(inventory),'audio':audio,'saved_project':str(P/'resolve/r14-native/nuvvantene-r14-native-full-a02.drp')}
