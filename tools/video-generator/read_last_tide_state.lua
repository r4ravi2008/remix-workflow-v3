local r=assert(resolve or (Resolve and Resolve()) or (bmd and bmd.scriptapp and bmd.scriptapp("Resolve")) or (fusion and fusion.GetResolve and fusion:GetResolve()),"Resolve handle unavailable")
local pm=r:GetProjectManager()
local p=pm:GetCurrentProject()
local t=p and p:GetCurrentTimeline()
local f=assert(io.open("/tmp/last-tide-state.txt","w"))
f:write("project=", tostring(p and p:GetName() or "nil"), "\n")
f:write("timeline=", tostring(t and t:GetName() or "nil"), "\n")
if t then
  f:write("video_tracks=", tostring(t:GetTrackCount("video")), " audio_tracks=", tostring(t:GetTrackCount("audio")), " subtitle_tracks=", tostring(t:GetTrackCount("subtitle")), "\n")
  f:write("start_frame=", tostring(t:GetStartFrame()), " end_frame=", tostring(t:GetEndFrame()), "\n")
  local okb, blank=pcall(function() return t:GetOutputBlanking() end)
  f:write("blanking_ok=", tostring(okb), " blanking=", tostring(blank), "\n")
  for _,kind in ipairs({"video","audio","subtitle"}) do
    local n=t:GetTrackCount(kind)
    for tr=1,n do
      local items=t:GetItemListInTrack(kind,tr) or {}
      f:write(kind,"_track_",tr,"_items=",tostring(#items),"\n")
      for i,it in ipairs(items) do
        local okm,mp=pcall(function() return it:GetMediaPoolItem() end)
        local nm=""
        if okm and mp then nm=mp:GetName() or "" end
        f:write(kind,"_",tr,"_",i," start=",tostring(it:GetStart())," end=",tostring(it:GetEnd())," dur=",tostring(it:GetDuration())," media_ok=",tostring(okm)," media=",nm,"\n")
      end
    end
  end
end
f:close()
