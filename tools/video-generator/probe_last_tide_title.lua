local r=assert(resolve or (Resolve and Resolve()) or (bmd and bmd.scriptapp and bmd.scriptapp("Resolve")) or (fusion and fusion.GetResolve and fusion:GetResolve()),"Resolve handle unavailable")
local pm=r:GetProjectManager(); local p=assert(pm:GetCurrentProject())
assert(p:GetName()=="THE LAST TIDE - BEAT EDIT V4",p:GetName())
local mp=p:GetMediaPool(); local base=nil
for _,tl in ipairs(mp:GetCurrentFolder():GetClipList() or {}) do end
for _,name in ipairs(mp:GetCurrentFolder():GetClipList() or {}) do end
for _,name in ipairs({"THE LAST TIDE - V6 SPARSE BEAT PASS"}) do
  for _,tl in ipairs(p:GetTimelineCount() and {} or {}) do end
end
local target=nil
for i=1,p:GetTimelineCount() do local tl=p:GetTimelineByIndex(i); if tl and tl:GetName()=="THE LAST TIDE - V6 SPARSE CAPTION TEST" then target=tl end end
if not target then
  for i=1,p:GetTimelineCount() do local tl=p:GetTimelineByIndex(i); if tl and tl:GetName()=="THE LAST TIDE - V6 SPARSE BEAT PASS" then target=tl:DuplicateTimeline("THE LAST TIDE - V6 SPARSE CAPTION TEST"); break end end
end
assert(target,"sparse timeline missing"); p:SetCurrentTimeline(target); target:SetCurrentTimecode("00:00:00:00")
local f=assert(io.open("/tmp/last-tide-title-probe.txt","w"))
for _,preset in ipairs({"Text+","Text"}) do
  local ok,it=pcall(function() return target:InsertTitleIntoTimeline(preset) end)
  f:write("preset=",preset," ok=",tostring(ok)," item=",tostring(it),"\n")
  if ok and it then
    f:write("type=",tostring(it:GetType())," name=",tostring(it:GetName())," start=",tostring(it:GetStart())," end=",tostring(it:GetEnd()),"\n")
    local okp,props=pcall(function() return it:GetProperties() end); f:write("props_ok=",tostring(okp),"\n")
    if okp and props then for k,v in pairs(props) do f:write(tostring(k),"=",tostring(v),"\n") end end
  end
end
f:close(); p:SaveProject()
