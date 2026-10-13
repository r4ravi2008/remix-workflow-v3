local base='/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/urvashi/music-video/hyperreal-story-review-v2'
local f=assert(io.open(base..'/message-assembly.log','w'))
local function log(s) print(s); f:write(tostring(s),'\n'); f:flush() end
local ok,err=pcall(function()
 local pm=resolve:GetProjectManager()
 local p=assert(pm:GetCurrentProject())
 assert(not p:IsRenderingInProgress(),'Wait for picture render')
 local tl=assert(p:GetCurrentTimeline())
 assert(tl:GetName()=='URVASHI STORY CUT v2 - REVIEW CANDIDATE')
 local clips=tl:GetItemListInTrack('video',1)
 local specs={
  {index=14,text='Coffee tomorrow?\nOr a walk at KBR Park?',color={0.11,0.035,0.045},from=8,to=100},
  {index=27,text='Flying out tonight.\nBack Sunday.',color={0.045,0.06,0.08},from=8,to=89},
  {index=31,text='OYO tonight?',color={0.11,0.035,0.045},from=8,to=217},
  {index=31,text='Okay.',color={0.025,0.085,0.08},from=146,to=217,y=0.34}
 }
 local comps={}
 for _,s in ipairs(specs) do
  local comp=comps[s.index]
  if not comp then
   assert(clips[s.index]:GetFusionCompCount()==0,'Existing comp; inspect before reapplying')
   comp=assert(clips[s.index]:AddFusionComp()); comps[s.index]=comp
  end
  local input=assert(comp:FindTool('MediaIn1'))
  local output=assert(comp:FindTool('MediaOut1'))
  local previous=output.Input:GetConnectedOutput()
  local attrs=comp:GetAttrs()
  local start=attrs.COMPN_RenderStart or 0
  log('comp '..s.index..' render start '..start)
  local y=s.y or 0.53
  local mask=assert(comp:AddTool('RectangleMask',-32768,-32768))
  mask.Width=0.34; mask.Height=0.135; mask.Center={0.25,y}; mask.CornerRadius=0.12
  local bg=assert(comp:AddTool('Background',-32768,-32768))
  bg.TopLeftRed=s.color[1]; bg.TopLeftGreen=s.color[2]; bg.TopLeftBlue=s.color[3]; bg.TopLeftAlpha=0.90
  bg.EffectMask=mask.Mask
  local text=assert(comp:AddTool('TextPlus',-32768,-32768))
  text.StyledText=s.text; text.Font='Helvetica'; text.Style='Regular'; text.Size=0.022; text.Center={0.25,y}; text.Red1=0.96; text.Green1=0.96; text.Blue1=0.94
  local card=assert(comp:AddTool('Merge',-32768,-32768))
  card.Background=bg.Output; card.Foreground=text.Output
  local merge=assert(comp:AddTool('Merge',-32768,-32768))
  merge.Background=previous or input.Output; merge.Foreground=card.Output
  merge.Blend:SetExpression('min(max((time-'..(start+s.from)..')/8,0),1)*min(max(('..(start+s.to)..'-time)/8,0),1)')
  output.Input=merge.Output
  log('added '..s.text)
 end
 assert(pm:SaveProject())
 assert(pm:ExportProject(p:GetName(),base..'/urvashi-story-review-v2-messages.drp',true))
 assert(tl:Export(base..'/urvashi-story-review-v2-messages.drt',resolve.EXPORT_DRT))
 assert(p:LoadRenderPreset('H.264 Master'))
 assert(p:SetCurrentRenderMode(1))
 assert(p:SetCurrentRenderFormatAndCodec('mp4','H264'))
 assert(p:SetRenderSettings({SelectAllFrames=true,TargetDir=base,CustomName='urvashi-story-review-v2',ExportVideo=true,ExportAudio=true,FormatWidth=1920,FormatHeight=1080,FrameRate=24,AudioCodec='aac',AudioSampleRate=48000,VideoQuality=18000}))
 local job=assert(p:AddRenderJob()); log('render-job '..job); assert(p:StartRendering({job}))
end)
log(ok and 'SUCCESS' or tostring(err))
f:close()
