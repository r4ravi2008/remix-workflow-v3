local output = "/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/urvashi/music-video/hyperreal-hybrid-motion-v1/resolve-probe.txt"
local f = assert(io.open(output, "w"))
local function log(k,v) f:write(k,"\t",tostring(v),"\n"); f:flush(); print(k,v) end
local ok,err = pcall(function()
  local pm = resolve:GetProjectManager()
  local old = pm:GetCurrentProject()
  assert(not old or not old:IsRenderingInProgress(), "Existing render in progress")
  if old then assert(pm:SaveProject(), "Could not save outgoing project") end
  local name = "URVASHI HYPERREAL STORY CUT 20260921"
  local project = old and old:GetName() == name and old or pm:CreateProject(name)
  assert(project, "Project exists or creation failed; inspect before retry")
  assert(project:GetTimelineCount() == 0, "Probe already has a timeline; do not duplicate it")
  log("project",project:GetName())
  log("settings-return", project:SetSettings({timelineFrameRate="24",timelinePlaybackFrameRate="24",timelineResolutionWidth="1920",timelineResolutionHeight="1080"}))
  local settings = project:GetSettings()
  assert(tonumber(settings.timelineFrameRate)==24 and tonumber(settings.timelineResolutionWidth)==1920 and tonumber(settings.timelineResolutionHeight)==1080, "Settings readback mismatch")
  local mp = project:GetMediaPool()
  local tl = assert(mp:CreateEmptyTimeline("00 TECHNICAL PROBE - NOT STORY REVIEW"))
  assert(tl:SetStartTimecode("00:00:00:00"))
  local p = "/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/urvashi/music-video/source-of-truth-hyperreal-v1/01-anchor-images/S03-I01__T012760__first-approach__openai-imagegen.png"
  local media = assert(mp:ImportMedia({p}))
  assert(media[1], "PNG import failed")
  local item = mp:AppendToTimeline({{mediaPoolItem=media[1],startFrame=0,endFrame=47,mediaType=1,trackIndex=1,recordFrame=tl:GetStartFrame()}})[1]
  assert(item, "Still append failed")
  log("still-duration",item:GetDuration())
  log("timeline-start",tl:GetStartFrame())
  log("timeline-end",tl:GetEndFrame())
  for k,v in pairs(project:GetRenderFormats()) do log("format "..k,v) end
  for k,v in pairs(project:GetRenderCodecs("mp4")) do log("mp4codec "..k,v) end
  for _,v in pairs(project:GetRenderPresetList()) do log("preset",v) end
  log("saved",pm:SaveProject())
end)
log("success",ok)
if not ok then log("error",err) end
f:close()
