local r=assert(Resolve(), "Resolve connection unavailable")
local logPath="/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/hello-ammai-progressive-deep-house/music-video/resolve/v6-full-film/transition-api-probe.log"
local log=assert(io.open(logPath,"w"),"Cannot open probe log")
local function out(...)
  local xs={...}; local s={}
  for i,v in ipairs(xs) do s[i]=tostring(v) end
  local line=table.concat(s,"\t")
  print(line); log:write(line,"\n"); log:flush()
end
local pm=r:GetProjectManager()
local p=assert(pm:GetCurrentProject(), "No current project")
assert(p:GetName()=="THE LAST TIDE - BEAT EDIT V4", "Wrong project")
assert(not p:IsRenderingInProgress(), "Render is active")
local base=nil
for i=1,p:GetTimelineCount() do
  local t=p:GetTimelineByIndex(i)
  if t:GetName()=="THE LAST TIDE - V6 PROVISIONAL CONFORM - NO FINISH" then base=t end
end
assert(base, "Missing provisional conform")
local probeName="THE LAST TIDE - V6 TRANSITION API PROBE"
local probe=nil
for i=1,p:GetTimelineCount() do
  local t=p:GetTimelineByIndex(i)
  if t:GetName()==probeName then probe=t end
end
if not probe then probe=assert(base:DuplicateTimeline(probeName), "Duplicate failed") end
assert(p:SetCurrentTimeline(probe))
local clips=probe:GetItemListInTrack("video",1)
assert(#clips==40, "Unexpected clip count")
local attempts={
  {"c1_end_left",1,"end","left",1},
  {"c1_end_center",1,"end","center",1},
  {"c1_end_right",1,"end","right",1},
  {"c2_start_left",2,"start","left",1},
  {"c2_start_center",2,"start","center",1},
  {"c2_start_right",2,"start","right",1},
  {"c3_start_left",3,"start","left",1},
  {"c3_start_center",3,"start","center",1},
  {"c3_start_right",3,"start","right",1},
}
for _,a in ipairs(attempts) do
  local ok, tr=pcall(function()
    return clips[a[2]]:AddTransition({type="Cross Dissolve",category="simple",position=a[3],alignment=a[4],duration=a[5]})
  end)
  if ok and tr then
    out("TRANSITION_PROBE_OK",a[1],tr:GetName(),tr:GetStart(),tr:GetEnd(),tr:GetDuration())
    log:close()
    return
  else
    out("TRANSITION_PROBE_FAIL",a[1],tostring(tr))
  end
end
out("TRANSITION_PROBE_NONE")
log:close()
