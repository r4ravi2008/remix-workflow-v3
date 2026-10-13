local r=assert(resolve or (Resolve and Resolve()) or (bmd and bmd.scriptapp and bmd.scriptapp("Resolve")) or (fusion and fusion.GetResolve and fusion:GetResolve()),"Resolve handle unavailable")
local pm=assert(r:GetProjectManager()); local p=assert(pm:GetCurrentProject())
assert(p:GetName()=="THE LAST TIDE - BEAT EDIT V4",p:GetName())
local pool=p:GetMediaPool(); local targetName="THE LAST TIDE - V6 SPARSE CAPTIONED"
local target=nil
for i=1,p:GetTimelineCount() do local tl=p:GetTimelineByIndex(i); if tl and tl:GetName()==targetName then target=tl end end
if not target then
  for i=1,p:GetTimelineCount() do local tl=p:GetTimelineByIndex(i); if tl and tl:GetName()=="THE LAST TIDE - V6 SPARSE BEAT PASS" then target=tl:DuplicateTimeline(targetName); break end end
end
assert(target,"sparse timeline missing"); assert(p:SetCurrentTimeline(target))
local f=assert(io.open("/tmp/last-tide-srt-import.txt","w"))
local existing=target:GetTrackCount("subtitle")
f:write("before_subtitle_tracks=",tostring(existing),"\n")
if existing==0 then local ok=target:AddTrack("subtitle"); f:write("add_track=",tostring(ok),"\n") end
local srt="/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/hello-ammai-progressive-deep-house/music-video/resolve/v6-full-film/the-last-tide-transliterated-PROVISIONAL.srt"
local imported=nil
local folder=pool:GetCurrentFolder()
for _,mi in ipairs(folder:GetClipList() or {}) do local ok,n=pcall(function() return mi:GetName() end); if ok and n and string.find(n,"the-last-tide-transliterated-PROVISIONAL",1,true) then imported=mi end end
if not imported then
  local ok,res=pcall(function() return pool:ImportMedia({{FilePath=srt}}) end)
  f:write("import_call=",tostring(ok)," result=",tostring(res),"\n")
  if ok and res and #res>0 then imported=res[1] end
else f:write("using_existing=true name=",tostring(imported:GetName()),"\n") end
assert(imported,"SRT import unavailable")
local okA,app=pcall(function() return pool:AppendToTimeline({{mediaPoolItem=imported,recordFrame=0}}) end)
f:write("append_call=",tostring(okA)," result=",tostring(app),"\n")
local n=target:GetTrackCount("subtitle"); f:write("after_subtitle_tracks=",tostring(n),"\n")
for tr=1,n do local items=target:GetItemListInTrack("subtitle",tr) or {}; f:write("track=",tr," items=",tostring(#items),"\n"); for i,it in ipairs(items) do f:write(i," name=",tostring(it:GetName())," start=",tostring(it:GetStart())," end=",tostring(it:GetEnd())," dur=",tostring(it:GetDuration()),"\n") end end
f:close(); pm:SaveProject()
