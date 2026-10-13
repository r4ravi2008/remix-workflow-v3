local base='/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/urvashi/music-video/hyperreal-story-review-v2'
local f=assert(io.open(base..'/resolve-readback.tsv','w'))
local function log(...) local a={...}; for i,v in ipairs(a) do a[i]=tostring(v) end; f:write(table.concat(a,'\t'),'\n'); f:flush(); print(table.concat(a,'\t')) end
local ok,err=pcall(function()
 local pm=resolve:GetProjectManager()
 local p=assert(pm:GetCurrentProject())
 local tl=assert(p:GetCurrentTimeline())
 assert(tl:GetName()=='URVASHI STORY CUT v2 - REVIEW CANDIDATE')
 assert(tl:SetStartTimecode('00:00:00:00'))
 local plan=dofile(base..'/review-plan.lua')
 local items=tl:GetItemListInTrack('video',1)
 assert(#items==#plan.cuts,'Clip count mismatch')
 for i,c in ipairs(plan.cuts) do
  assert(items[i]:GetStart()==c.startFrame and items[i]:GetDuration()==c.durationFrames,'Timing mismatch '..c.cutId)
  tl:AddMarker(c.startFrame,'Blue',c.cutId..' '..c.anchorId,'REVIEW CANDIDATE: '..c.storyBeat,1,c.cutId)
 end
 local a=tl:GetItemListInTrack('audio',1)
 assert(#a==1 and a[1]:GetStart()==0 and a[1]:GetDuration()==plan.totalFrames,'Audio range mismatch')
 assert(tl:GetEndFrame()==plan.totalFrames,'Programme duration mismatch')
 log('timeline',tl:GetName(),tl:GetStartFrame(),tl:GetEndFrame())
 for _,kind in ipairs({'video','audio'}) do
  for track=1,tl:GetTrackCount(kind) do
   for i,item in ipairs(tl:GetItemListInTrack(kind,track)) do
    log(kind,track,i,item:GetName(),item:GetStart(),item:GetEnd(),item:GetDuration())
   end
  end
 end
 assert(pm:SaveProject())
 log('project-export',pm:ExportProject(p:GetName(),base..'/urvashi-story-review-v2.drp',true))
 log('timeline-export',tl:Export(base..'/urvashi-story-review-v2.drt',resolve.EXPORT_DRT))
 tl:SetCurrentTimecode('00:00:00:00')
 assert(p:LoadRenderPreset('H.264 Master'))
 assert(p:SetCurrentRenderMode(1))
 assert(p:SetCurrentRenderFormatAndCodec('mp4','H264'))
 assert(p:SetRenderSettings({SelectAllFrames=true,TargetDir=base,CustomName='urvashi-story-review-v2-picture-only',ExportVideo=true,ExportAudio=true,FormatWidth=1920,FormatHeight=1080,FrameRate=24,AudioCodec='aac',AudioSampleRate=48000,VideoQuality=18000}))
 local job=assert(p:AddRenderJob())
 log('render-job',job)
 assert(p:StartRendering({job}))
end)
log('success',ok,err or '')
f:close()
