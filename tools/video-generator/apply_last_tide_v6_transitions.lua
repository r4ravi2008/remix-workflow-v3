-- Last Tide V6 transition pass. Safe guard: never edits Urvashi or the clean conform.
local r=assert(resolve,"Resolve handle unavailable")
local pm=r:GetProjectManager(); local p=assert(pm:GetCurrentProject(),"No current project")
assert(p:GetName()=="THE LAST TIDE - BEAT EDIT V4","Wrong project: "..p:GetName())
assert(not p:IsRenderingInProgress(),"Render is active")
local base=nil; local final=nil
for i=1,p:GetTimelineCount() do
  local t=p:GetTimelineByIndex(i)
  if t:GetName()=="THE LAST TIDE - V6 PROVISIONAL CONFORM - NO FINISH" then base=t end
  if t:GetName()=="THE LAST TIDE - V6 BEAT TRANSITIONS - NO LYRICS" then final=t end
end
assert(base,"Missing clean provisional conform")
if not final then final=assert(base:DuplicateTimeline("THE LAST TIDE - V6 BEAT TRANSITIONS - NO LYRICS"),"Duplicate failed") end
assert(p:SetCurrentTimeline(final))
local clips=final:GetItemListInTrack("video",1); assert(#clips==40,"Unexpected clip count: "..tostring(#clips))
local logPath="/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/hello-ammai-progressive-deep-house/music-video/resolve/v6-full-film/v6-transition-application.log"
local log=assert(io.open(logPath,"w"))
local function out(...) local a={...}; local s={}; for i,v in ipairs(a) do s[i]=tostring(v) end; local line=table.concat(s,"\t"); print(line); log:write(line,"\n"); log:flush() end
out("START",final:GetName(),#clips)
-- Incoming shot index, planned semantic family, beat-synced duration.
local events={
 {3,"reflection_dissolve",22,"Cross Dissolve"},
 {5,"silk_occlusion",11,"Push"},
 {6,"trapezoid_reveal",8,"Edge Wipe"},
 {10,"shadow_reveal",11,"Dip To Color Dissolve"},
 {12,"reflection_dissolve",22,"Cross Dissolve"},
 {14,"masked_scale_reveal",8,"Slide"},
 {17,"shadow_reveal",11,"Dip To Color Dissolve"},
 {22,"reflection_dissolve",22,"Cross Dissolve"},
 {23,"trapezoid_reveal",8,"Center Wipe"},
 {26,"shadow_reveal",11,"Dip To Color Dissolve"},
 {27,"reflection_dissolve",22,"Cross Dissolve"},
 {29,"silk_occlusion",11,"Push"},
 {31,"reflection_dissolve",22,"Cross Dissolve"},
 {34,"trapezoid_reveal",8,"Edge Wipe"},
 {36,"masked_scale_reveal",8,"Slide"},
 {38,"reflection_dissolve",22,"Cross Dissolve"},
}
local applied=0; local fallback=0
for _,e in ipairs(events) do
  local clipIndex, family, dur, typ=e[1],e[2],e[3],e[4]
  local ok,tr=pcall(function() return clips[clipIndex]:AddTransition({type=typ,category="simple",position="end",alignment="center",duration=dur}) end)
  if not (ok and tr) then
    ok,tr=pcall(function() return clips[clipIndex]:AddTransition({type=typ,category="simple",position="end",alignment="left",duration=dur}) end)
    if ok and tr then fallback=fallback+1 end
  end
  if ok and tr then
    applied=applied+1
    out("APPLIED",clipIndex,family,typ,dur,tr:GetStart(),tr:GetEnd(),tr:GetDuration())
  else
    out("SKIPPED",clipIndex,family,typ,dur,tostring(tr))
  end
end
assert(pm:SaveProject(),"Save failed")
out("SUMMARY",applied,"fallback",fallback,"planned",#events)
log:close()
