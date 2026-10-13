local base='/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/urvashi/music-video/hyperreal-story-review-v4'
local f=assert(io.open(base..'/finish.log','w'))
local function log(s) f:write(tostring(s),'\n'); f:flush(); print(s) end
local ok,err=pcall(function()
 local pm=resolve:GetProjectManager(); local p=assert(pm:GetCurrentProject()); assert(not p:IsRenderingInProgress())
 local tl=assert(p:GetCurrentTimeline()); assert(tl:GetName()=='URVASHI STORY CUT v4 - MUSIC REACTIVE REVIEW')
 local clips=tl:GetItemListInTrack('video',1); assert(#clips==46)
 local plan=dofile(base..'/review-plan.lua')
 for i,c in ipairs(plan.cuts) do assert(clips[i]:GetStart()==c.startFrame and clips[i]:GetDuration()==c.durationFrames) end
 for _,s in ipairs({{15,8,'N08C-I01__T041417__restrained-response__openai-imagegen.png'},{21,8,'S11-I01__T053760__reflection-distance__openai-imagegen.png'},{46,12,'S35-I01__T174760__unresolved-ending__openai-imagegen.png'}}) do
  local comp=clips[s[1]]:GetFusionCompByIndex(1) or assert(clips[s[1]]:AddFusionComp())
  comp:Lock()
  local loader=comp:FindTool('Loader1') or assert(comp:AddTool('Loader',-32768,-32768))
  loader.Clip=base..'/anchors/'..s[3]
  local merge=comp:FindTool('Merge1') or assert(comp:AddTool('Merge',-32768,-32768))
  merge.Background=loader.Output; merge.Foreground=comp:FindTool('MediaIn1').Output
  local start=comp:GetAttrs().COMPN_RenderStart or 0
  merge.Blend:SetExpression('min(max((time-'..start..')/'..s[2]..',0),1)')
  comp:FindTool('MediaOut1').Input=merge.Output; comp:Unlock()
  log('transition '..s[1]..' frames '..s[2])
 end
 assert(pm:SaveProject())
 assert(pm:ExportProject(p:GetName(),base..'/urvashi-story-review-v4-messages.drp',true))
 assert(tl:Export(base..'/urvashi-story-review-v4-messages.drt',resolve.EXPORT_DRT))
 assert(p:LoadRenderPreset('H.264 Master')); assert(p:SetCurrentRenderMode(1)); assert(p:SetCurrentRenderFormatAndCodec('mp4','H264'))
 assert(p:SetRenderSettings({SelectAllFrames=true,TargetDir=base,CustomName='urvashi-story-review-v4',ExportVideo=true,ExportAudio=true,FormatWidth=1920,FormatHeight=1080,FrameRate=24,AudioCodec='aac',AudioSampleRate=48000,VideoQuality=18000}))
 local job=assert(p:AddRenderJob()); log('render-job '..job); assert(p:StartRendering({job}))
end)
log(ok and 'SUCCESS' or tostring(err)); f:close()
