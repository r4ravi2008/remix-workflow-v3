local r=assert(Resolve(), "Resolve connection unavailable")
local pm=r:GetProjectManager()
local p=assert(pm:GetCurrentProject(), "No current project")
assert(p:GetName()=="THE LAST TIDE - BEAT EDIT V4", "Wrong project")
assert(not p:IsRenderingInProgress(), "Render is active")
local base=nil
local candidate=nil
for i=1,p:GetTimelineCount() do
  local t=p:GetTimelineByIndex(i)
  if t:GetName()=="THE LAST TIDE - V6 PROVISIONAL CONFORM - NO FINISH" then base=t end
  if t:GetName()=="THE LAST TIDE - V6 BEAT TRANSITION CANDIDATE" then candidate=t end
end
assert(base, "Missing provisional conform")
if not candidate then candidate=assert(base:DuplicateTimeline("THE LAST TIDE - V6 BEAT TRANSITION CANDIDATE"), "Duplicate failed") end
assert(p:SetCurrentTimeline(candidate))
local clips=candidate:GetItemListInTrack("video",1)
assert(#clips==40, "Unexpected clip count")
local tr=clips[2]:AddTransition({type="Cross Dissolve",category="simple",position="start",alignment="center",duration=22})
assert(tr, "Cross Dissolve was not created")
assert(tr:GetType()=="transition", "Created item is not a transition")
print("TRANSITION_TEST",tr:GetName(),tr:GetStart(),tr:GetEnd(),tr:GetDuration())
assert(pm:SaveProject(), "Save failed")
