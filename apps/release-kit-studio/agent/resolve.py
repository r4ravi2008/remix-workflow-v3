"""Local Resolve finishing with isolated projects, native Fusion, guarded render jobs and measured outputs."""
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time

SDK='/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules'
sys.path.insert(0,SDK)
import DaVinciResolveScript as api

LEASE=Path('/tmp/remix-resolve-mac-lease.json')

def digest(path):
    sha=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):sha.update(chunk)
    return sha.hexdigest()

def save(path, value):
    temporary=path.with_suffix(path.suffix+'.tmp')
    temporary.write_text(json.dumps(value,indent=2)+'\n')
    os.replace(temporary,path)

def connect():
    resolve=api.scriptapp('Resolve')
    if not resolve:raise RuntimeError('Local Resolve is not running or external scripting is unavailable')
    return resolve

def checked(value, message):
    if not value:raise RuntimeError(message)
    return value

def set_settings(target, requested):
    actual=target.GetSettings()
    def matches(key,value):
        if key not in actual:return False
        try:return float(actual[key])==float(value)
        except (ValueError,TypeError):return str(actual[key])==str(value)
    if not all(matches(key,value) for key,value in requested.items()):
        target.SetSettings(requested)
        actual=target.GetSettings()
    checked(all(matches(key,value) for key,value in requested.items()),'Native settings readback differs from the requested format')
    return {key:actual[key] for key in requested}

def compose(item, scene, cues, gain, timeline_start, fps, language):
    comp=checked(item.AddFusionComp(),'Could not create native Fusion composition')
    tools=comp.GetToolList()
    mi=next(t for t in tools.values() if t.GetAttrs()['TOOLS_RegID']=='MediaIn')
    mo=next(t for t in tools.values() if t.GetAttrs()['TOOLS_RegID']=='MediaOut')
    attributes=comp.GetAttrs()
    first=int(attributes.get('COMPN_GlobalStart',0))
    frame_count=int(round(item.GetDuration()))
    previous=mi
    comp.SetData('ReleaseKit',{'sceneId':scene['id'],'environmentOnly':True,'humanAccepted':False})
    text_readbacks=[]
    comp.StartUndo('Compose release scene with protected native lyrics')
    try:
        for index,region in enumerate(scene.get('environmentMasks',[])):
            if not region.get('frameInspected') or not region.get('excludesPeopleLyricsAndProps'):
                raise RuntimeError('Environment mask has not been checked against its protected layers')
            mask=comp.AddTool('RectangleMask',False,0,index)
            for field,value in {'Center':{1:region['x'],2:region['y']},'Width':region['width'],'Height':region['height'],'SoftEdge':.008}.items():mask.SetInput(field,value,first)
            glow=comp.AddTool('SoftGlow',False,1,index)
            glow.SetAttrs({'TOOLS_Name':'EnvironmentMusicResponse'+str(index+1)})
            for field,value in {'Threshold':.62,'XGlowSize':7,'YGlowSize':7,'Blend':.45}.items():glow.SetInput(field,value,first)
            checked(glow.ConnectInput('Input',previous),'Glow input connection failed')
            checked(glow.ConnectInput('EffectMask',mask),'Protected environment mask failed')
            spline=comp.BezierSpline();glow.Gain=spline
            spline.SetKeyFrames({first+i:{1:gain[min(timeline_start+i,len(gain)-1)],'Flags':{'Linear':True}} for i in range(frame_count)},True)
            previous=glow
        font={'Telugu':'Kohinoor Telugu','Hindi':'Kohinoor Devanagari','Tamil':'Kohinoor Tamil'}[language]
        for index,cue in enumerate(cues):
            begin=max(0,int(round(cue['start']*fps))-timeline_start)
            end=min(frame_count,int(round(cue['end']*fps))-timeline_start)
            if end<=begin:continue
            for row,line in enumerate(cue.get('lines',[cue['text']])):
                text=comp.AddTool('TextPlus',False,2,index*2+row)
                text.SetAttrs({'TOOLS_Name':f'NativeLyric{index+1}Line{row+1}'})
                y=scene.get('lyricY',[.91,.085])[min(row,1)]
                for field,value in {'StyledText':line,'Font':font,'Style':'Semibold','Size':scene.get('lyricSize',.034),'Center':{1:.5,2:y},'Red1':1,'Green1':.969 if row==0 else .722,'Blue1':.918 if row==0 else .42,'Alpha1':1,'UseLigatures':1}.items():text.SetInput(field,value,first)
                text_readbacks.append((text,line,first))
                merge=comp.AddTool('Merge',False,3,index*2+row)
                checked(merge.ConnectInput('Background',previous),'Lyric background failed')
                checked(merge.ConnectInput('Foreground',text),'Lyric foreground failed')
                visibility=comp.BezierSpline();merge.Blend=visibility
                keys={first:{1:0,'Flags':{'StepIn':True}},first+begin:{1:1,'Flags':{'StepIn':True}},first+end:{1:0,'Flags':{'StepIn':True}}}
                visibility.SetKeyFrames(keys,True)
                previous=merge
        checked(mo.ConnectInput('Input',None),'Could not detach native output for timeline commit')
        checked(mo.ConnectInput('Input',previous),'Could not bind native output to timeline')
        comp.SetData('ReleaseKit',{'sceneId':scene['id'],'environmentOnly':True,'humanAccepted':False})
    finally:
        comp.EndUndo(True)
    for text,line,timecode in text_readbacks:checked(text.GetInput('StyledText',timecode)==line,'Native lyric text readback failed')
    return {'scene':scene['id'],'frames':frame_count,'fusionStart':first,'cueCount':len(cues)}

def probe_output(path, image=False):
    result=subprocess.run(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=width,height,nb_read_frames:format=duration','-of','json',str(path)],check=True,capture_output=True,text=True,timeout=120)
    data=json.loads(result.stdout);stream=data['streams'][0]
    subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(path),'-f','null','-'],check=True,capture_output=True,timeout=600)
    return {'width':int(stream['width']),'height':int(stream['height']),'duration':0 if image else float(data['format']['duration']),'decoded':True,'sha256':digest(path),'bytes':path.stat().st_size,'frames':int(stream['nb_read_frames'])}

def finish(plan_path):
    plan=json.loads(plan_path.read_text())
    diagnostic=plan.get('scope')=='integration-diagnostic' and plan['duration']<=4 and plan.get('allowProvisionalDiagnostic')
    checked(diagnostic or (plan.get('approvedForFinishing') and plan.get('reviewEvidence')),'Finishing plan requires reviewed footage ranges and lyric placement')
    audio=Path(plan['audio']);checked(digest(audio)==plan['audioSha256'],'Canonical audio hash differs from the finishing plan')
    fps=plan['fps'];checked(fps==24,'This finishing recipe requires 24 fps')
    frames=math.ceil(plan['duration']*fps)
    expected={'film','short-1','short-2','short-3','thumbnail','artwork'}
    checked({output['id'] for output in plan['outputs']}==expected and len(plan['outputs'])==6,'Plan must contain exactly six distinct outputs')
    output_root=Path(plan['outputRoot']);output_root.mkdir(parents=True,exist_ok=True)
    state_path=output_root/'resolve-state.json'
    plan_sha=digest(plan_path)
    if state_path.exists():
        saved=json.loads(state_path.read_text())
        checked(saved['planSha256']==plan_sha,'Resolve plan changed after creation; make an isolated new revision')
        if saved.get('terminal') and saved.get('outputs'):
            for item in saved['outputs']:checked(digest(item['path'])==item['sha256'],'Saved output changed after verification')
            return {'outputs':saved['outputs'],'receipt':saved}
        raise RuntimeError('Previous Resolve attempt is incomplete. Reconcile its saved project and render IDs before creating another revision')
    resolve=connect();manager=resolve.GetProjectManager();outgoing=manager.GetCurrentProject()
    checked(not outgoing or not outgoing.IsRenderingInProgress(),'Another Resolve render is active')
    checked(not outgoing or outgoing.GetUniqueId() in plan['allowedOutgoingProjectIds'],'The active Resolve project is outside this worker ownership boundary')
    owner={'service':'release-kit-studio','productionId':plan['productionId'],'pid':os.getpid(),'reservedEpoch':time.time()}
    with LEASE.open('x') as stream:json.dump(owner,stream)
    terminal=False;project=None
    try:
        if outgoing:checked(manager.SaveProject(),'Could not save outgoing project')
        if outgoing and outgoing.GetUniqueId()==plan.get('recoverEmptyProjectId') and outgoing.GetName()=='RELEASE KIT - '+plan['productionId'] and outgoing.GetTimelineCount()==0:
            project=outgoing
        else:project=checked(manager.CreateProject('RELEASE KIT - '+plan['productionId']),'Project name already exists; reconcile it before proceeding')
        set_settings(project,{'timelineFrameRate':'24','timelinePlaybackFrameRate':'24','timelineResolutionWidth':'1920','timelineResolutionHeight':'1080'})
        pool=project.GetMediaPool()
        resolve.OpenPage('edit')
        prepared_timelines={}
        for output in plan['outputs']:
            ident=output['id'];width=1080 if ident.startswith('short-') else 1920;height=1920 if ident.startswith('short-') or ident=='artwork' else 1080
            timeline=checked(pool.CreateEmptyTimeline(ident),'Could not create isolated output timeline')
            checked(project.SetCurrentTimeline(timeline),'Could not select output timeline')
            set_settings(timeline,{'useCustomSettings':'1','timelineResolutionWidth':str(width),'timelineResolutionHeight':str(height),'timelineFrameRate':'24'})
            timeline.SetStartTimecode('00:00:00:00')
            checked(timeline.GetStartTimecode()=='00:00:00:00','Could not set timeline origin')
            prepared_timelines[ident]=timeline
        imported={}
        paths={str(audio)} | {str(Path(scene['path'])) for output in plan['outputs'] for scene in output['scenes']}
        for source in sorted(paths):
            media=checked(pool.ImportMedia([source]),'Media import failed: '+source)
            imported[source]=media[0]
        envelope=json.loads(Path(plan['envelope']).read_text())
        checked(envelope['sourceSha256']==plan['audioSha256'],'Music envelope differs from canonical audio')
        compositions=[];timelines=[]
        for output in plan['outputs']:
            ident=output['id'];is_image=ident in ('thumbnail','artwork')
            width=1080 if ident.startswith('short-') else 1920
            height=1920 if ident.startswith('short-') or ident=='artwork' else 1080
            timeline=prepared_timelines[ident]
            checked(project.SetCurrentTimeline(timeline),'Could not select output timeline')
            duration_frames=1 if is_image else frames if ident=='film' else math.ceil(output['duration']*fps)
            coverage=0
            for scene in output['scenes']:
                start=scene['recordFrame'];length=scene['frames'];checked(start==coverage and length>0,'Output scene coverage has a gap or overlap')
                source=Path(scene['path']);checked(digest(source)==scene['sha256'],'Scene bytes differ from its accepted range')
                item=checked(pool.AppendToTimeline([{'mediaPoolItem':imported[str(source)],'startFrame':scene['sourceStartFrame'],'endFrame':scene['sourceStartFrame']+length,'mediaType':1,'trackIndex':1,'recordFrame':start}]),'Could not append scene')[0]
                checked(item.GetDuration()==length,'Resolve source end-frame semantics differ from the plan')
                if 'transform' in scene:
                    checked(item.SetProperty(scene['transform']),'Independent portrait framing could not be applied')
                source_start=round(output.get('sourceStart',0)*fps)
                cues=output.get('cues',[])
                gain=envelope['environmentGain'][source_start:source_start+duration_frames]
                compositions.append(compose(item,scene,cues,gain,start,fps,plan['language']))
                coverage+=length
            checked(coverage==duration_frames,'Output does not cover its complete requested duration')
            if not is_image:
                source_start=round(output.get('sourceStart',0)*fps)
                items=checked(pool.AppendToTimeline([{'mediaPoolItem':imported[str(audio)],'startFrame':source_start,'endFrame':source_start+duration_frames,'mediaType':2,'trackIndex':1,'recordFrame':0}]),'Canonical audio append failed')
                checked(abs(items[0].GetDuration()-duration_frames)<=1,'Canonical audio coverage differs from video')
            checked(timeline.GetEndFrame()-timeline.GetStartFrame()==duration_frames,'Timeline frame coverage readback failed')
            timelines.append({'id':ident,'timelineId':timeline.GetUniqueId(),'frames':duration_frames,'width':width,'height':height,'composition':output['composition']})
        checked(manager.SaveProject(),'Could not save native compositions')
        project_id=project.GetUniqueId();name=project.GetName()
        checked(manager.ExportProject(name,str(output_root/'editable.drp')),'Editable project export failed')
        checked(manager.CloseProject(project),'Could not close own project for composition commit')
        project=checked(manager.LoadProject(name),'Could not reload committed native compositions')
        jobs=[]
        for index,output in enumerate(plan['outputs'],1):
            metadata=timelines[index-1];checked(project.SetCurrentTimeline(project.GetTimelineByIndex(index)),'Output timeline selection failed')
            image=output['id'] in ('thumbnail','artwork')
            if not image:checked(project.LoadRenderPreset('H.264 Master'),'H.264 preset unavailable')
            checked(project.SetCurrentRenderFormatAndCodec('jpg' if image else 'mp4','YUV444_8' if image else 'H264'),'Required render codec unavailable')
            checked(project.SetCurrentRenderMode(1),'Could not select single-clip rendering')
            settings={'SelectAllFrames':True,'MarkIn':0,'MarkOut':metadata['frames']-1,'TargetDir':str(output_root),'CustomName':output['id'],'UseUniqueFilenames':False,'ExportVideo':True,'ExportAudio':not image,'FormatWidth':metadata['width'],'FormatHeight':metadata['height'],'FrameRate':24.0}
            if not image:settings.update({'VideoQuality':16000,'AudioCodec':'aac','AudioSampleRate':48000,'NetworkOptimization':True})
            checked(project.SetRenderSettings(settings),'Resolve rejected render settings')
            jobs.append(checked(project.AddRenderJob(),'Could not create own render job'))
        state={'productionId':plan['productionId'],'scope':plan.get('scope','full-release-kit'),'projectId':project_id,'projectName':name,'planSha256':plan_sha,'canonicalAudioSha256':plan['audioSha256'],'jobIds':jobs,'timelines':timelines,'compositions':compositions,'terminal':False,'humanAccepted':False}
        save(state_path,state)
        checked(project.StartRendering(jobs,False),'Could not start own render jobs')
        deadline=time.time()+5400
        while project.IsRenderingInProgress() and time.time()<deadline:time.sleep(5)
        checked(not project.IsRenderingInProgress(),'Render observation deadline reached; keep ownership and reconcile known jobs')
        statuses=[project.GetRenderJobStatus(job) for job in jobs]
        state['renderStatuses']=statuses;save(state_path,state)
        checked(all(status['JobStatus']=='Complete' for status in statuses),'A native render failed; inspect saved job readbacks')
        terminal=True;result=[]
        for output,metadata in zip(plan['outputs'],timelines):
            ident=output['id'];image=ident in ('thumbnail','artwork')
            candidates=list(output_root.glob(ident+'*.jpg')) if image else [output_root/(ident+'.mp4')]
            checked(len(candidates)==1 and candidates[0].is_file(),'Rendered output name is missing or ambiguous')
            measured=probe_output(candidates[0],image)
            checked(measured['width']==metadata['width'] and measured['height']==metadata['height'],'Rendered dimensions differ from the output contract')
            checked(image or abs(measured['duration']-metadata['frames']/fps)<.05,'Rendered duration differs from timeline coverage')
            result.append({'id':ident,'path':str(candidates[0]),'composition':metadata['composition'],**measured})
        state.update({'outputs':result,'terminal':True,'fullFilmWatched':False,'fullFilmHeard':False,'humanAccepted':False})
        save(state_path,state)
        return {'outputs':result,'receipt':state}
    finally:
        if LEASE.exists() and json.loads(LEASE.read_text())==owner and (terminal or not project or not project.IsRenderingInProgress()):
            save(output_root/'resolve-reservation-released.json',{**owner,'releasedEpoch':time.time()})
            LEASE.unlink()

if __name__=='__main__':
    if sys.argv[1]=='probe':
        r=connect();p=r.GetProjectManager().GetCurrentProject()
        print(json.dumps({'version':r.GetVersionString(),'projectId':p.GetUniqueId() if p else None,'projectName':p.GetName() if p else None,'rendering':p.IsRenderingInProgress() if p else False,'leaseExists':LEASE.exists()}))
    elif sys.argv[1]=='finish':print(json.dumps(finish(Path(sys.argv[2]))))
    else:raise ValueError('Use probe or finish with a trusted plan path')
