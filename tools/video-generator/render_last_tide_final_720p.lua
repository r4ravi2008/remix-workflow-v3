local r=assert(resolve or (Resolve and Resolve()) or (bmd and bmd.scriptapp and bmd.scriptapp("Resolve")) or (fusion and fusion.GetResolve and fusion:GetResolve()),"Resolve handle unavailable")
local pm=assert(r:GetProjectManager()); local p=assert(pm:GetCurrentProject())
assert(p:GetName()=="THE LAST TIDE - BEAT EDIT V4",p:GetName())
local targetName="THE LAST TIDE - V6 SPARSE CAPTIONED"
local t=nil
for i=1,p:GetTimelineCount() do local tl=p:GetTimelineByIndex(i); if tl and tl:GetName()==targetName then t=tl end end
assert(t,"captioned target timeline missing")
assert(p:SetCurrentTimeline(t))
local logPath="/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/hello-ammai-progressive-deep-house/music-video/resolve/v6-full-film/v6-final-720p-render.log"
local log=assert(io.open(logPath,"w")); local function out(...) local a={...}; local s={}; for i,v in ipairs(a) do s[i]=tostring(v) end; local line=table.concat(s,"\t"); print(line); log:write(line,"\n"); log:flush() end
local v=t:GetItemListInTrack("video",1) or {}; local a=t:GetItemListInTrack("audio",1) or {}; local st=t:GetTrackCount("subtitle"); local si=st>0 and (t:GetItemListInTrack("subtitle",1) or {}) or {}
out("TIMELINE",t:GetName(),"video",#v,"audio",#a,"subtitle_tracks",st,"subtitle_items",#si,"frames",t:GetStartFrame(),t:GetEndFrame())
assert(#v==40,"unexpected video clip count")
if t.SetOutputBlanking then local ok=pcall(function() return t:SetOutputBlanking({Top=138,Bottom=138,Left=0,Right=0}) end); out("BLANKING_SET",ok) end
assert(p:LoadRenderPreset("H.264 Master"))
assert(p:SetCurrentRenderFormatAndCodec("mp4","H264"))
p:SetCurrentRenderMode(1)
local renderDir="/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/hello-ammai-progressive-deep-house/music-video/resolve/v6-full-film/renders"
local settings={SelectAllFrames=true,TargetDir=renderDir,CustomName="the-last-tide-v6-final-720p",ExportVideo=true,ExportAudio=true,FormatWidth=1280,FormatHeight=720,FrameRate=24,VideoQuality=16000,AudioCodec="aac",AudioSampleRate=48000,NetworkOptimization=true,DataBurnIn="None",ExportSubtitle=(#si>0),SubtitleFormat="SRT"}
assert(p:SetRenderSettings(settings))
local job=p:AddRenderJob(); out("JOB",job); assert(job)
assert(p:SaveProject()); assert(p:StartRendering({job})); out("STARTED",job,"target",1280,720,"subtitle_export",#si>0); log:close()
