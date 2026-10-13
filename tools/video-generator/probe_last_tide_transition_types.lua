local logPath="/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/hello-ammai-progressive-deep-house/music-video/resolve/v6-full-film/transition-type-probe.log"
local log=assert(io.open(logPath,"w"))
log:write("START\n"); log:flush()
local r=assert(Resolve(), "Resolve connection unavailable")
local pm=r:GetProjectManager(); local p=assert(pm:GetCurrentProject(), "No current project")
assert(p:GetName()=="THE LAST TIDE - BEAT EDIT V4", "Wrong project")
assert(not p:IsRenderingInProgress(), "Render is active")
local base=nil
for i=1,p:GetTimelineCount() do local t=p:GetTimelineByIndex(i); if t:GetName()=="THE LAST TIDE - V6 PROVISIONAL CONFORM - NO FINISH" then base=t end end
assert(base, "Missing provisional conform")
local name="THE LAST TIDE - V6 TRANSITION TYPE PROBE"
local t=nil
for i=1,p:GetTimelineCount() do local x=p:GetTimelineByIndex(i); if x:GetName()==name then t=x end end
if not t then t=assert(base:DuplicateTimeline(name),"Duplicate failed") end
assert(p:SetCurrentTimeline(t))
local clips=t:GetItemListInTrack("video",1); assert(#clips==40,"Unexpected clip count")
local function out(...) local a={...}; local s={}; for i,v in ipairs(a) do s[i]=tostring(v) end; local line=table.concat(s,"\t"); print(line); log:write(line,"\n"); log:flush() end
local types={
 {"Cross Dissolve",1}, {"Dip To Color Dissolve",3}, {"Fade to Color",5},
 {"Wipe",6}, {"Push",8}, {"Slide",9}, {"Iris",10}, {"Zoom",12},
 {"Cross Iris",14}, {"Center Wipe",15}, {"Edge Wipe",17}, {"Clock Wipe",18},
}
for _,a in ipairs(types) do
 local ok,tr=pcall(function() return clips[a[2]]:AddTransition({type=a[1],category="simple",position="end",alignment="left",duration=1}) end)
 if ok and tr then out("TRANSITION_TYPE_OK",a[1],tr:GetName(),tr:GetStart(),tr:GetEnd(),tr:GetDuration()) else out("TRANSITION_TYPE_FAIL",a[1],tostring(tr)) end
end
log:close()
