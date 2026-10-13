-- Sparse beat-synced transition pass for Last Tide only.
-- Does not edit Urvashi timelines, bins, or renders.
local logPath = "/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/hello-ammai-progressive-deep-house/music-video/resolve/v6-full-film/v6-sparse-pass.log"
local log = assert(io.open(logPath, "w"))
local function out(...)
  local a = {...}
  local s = {}
  for i, v in ipairs(a) do s[i] = tostring(v) end
  local line = table.concat(s, "\t")
  print(line)
  log:write(line, "\n")
  log:flush()
end

out("START", os.time())
out("ENV", "resolve", tostring(resolve), "Resolve", tostring(Resolve), "bmd", tostring(bmd), "fusion", tostring(fusion))
local r = resolve or _G.__lastTideResolve
if not r and Resolve then
  local ok, got = pcall(Resolve)
  out("RESOLVE_CALL", tostring(ok), tostring(got))
  if ok then r = got end
end
if not r and bmd and bmd.scriptapp then
  local ok, got = pcall(function() return bmd.scriptapp("Resolve") end)
  out("BMD_CALL", tostring(ok), tostring(got))
  if ok then r = got end
end
if not r and fusion and fusion.GetResolve then
  local ok, got = pcall(function() return fusion:GetResolve() end)
  out("FUSION_CALL", tostring(ok), tostring(got))
  if ok then r = got end
end
if not r then
  out("NO_RESOLVE")
  log:close()
  return
end
local pm = r:GetProjectManager()
local p = pm:GetCurrentProject()
if not p then
  out("NO_PROJECT")
  log:close()
  return
end
out("PROJECT", p:GetName())
if p:GetName() ~= "THE LAST TIDE - BEAT EDIT V4" then
  out("WRONG_PROJECT_STOP")
  log:close()
  return
end
if p:IsRenderingInProgress() then
  out("RENDER_ACTIVE_STOP")
  log:close()
  return
end

local base = nil
local targetName = "THE LAST TIDE - V6 SPARSE BEAT PASS"
local target = nil
local names = {}
for i = 1, p:GetTimelineCount() do
  local t = p:GetTimelineByIndex(i)
  local name = t:GetName()
  names[#names + 1] = name
  if string.find(name, "URVASHI", 1, true) or string.find(name, "Urvashi", 1, true) then
    out("FORBIDDEN_TIMELINE_PRESENT_NOT_TOUCHED", name)
  end
  if name == "THE LAST TIDE - V6 PROVISIONAL CONFORM - NO FINISH" then base = t end
  if name == targetName then target = t end
end
out("TIMELINES", table.concat(names, " | "))
if not base then
  out("MISSING_CLEAN_CONFORM")
  log:close()
  return
end
local baseClips = base:GetItemListInTrack("video", 1)
out("CLEAN_CONFORM", base:GetName(), baseClips and #baseClips or 0, base:GetStartFrame(), base:GetEndFrame())
if not target then
  target = base:DuplicateTimeline(targetName)
end
if not target then
  out("DUPLICATE_FAILED")
  log:close()
  return
end
assert(p:SetCurrentTimeline(target))
out("TARGET", target:GetName(), target:GetStartFrame(), target:GetEndFrame())

local clips = target:GetItemListInTrack("video", 1)
out("TARGET_CLIPS", clips and #clips or 0)
if not clips or #clips ~= 40 then
  out("UNEXPECTED_CLIP_COUNT_STOP")
  log:close()
  return
end

local function tryTransition(clip, typ, dur, alignment)
  local ok, tr = pcall(function()
    return clip:AddTransition({type = typ, category = "simple", position = "end", alignment = alignment, duration = dur})
  end)
  if ok and tr then return tr end
  return nil
end

-- Outgoing clip index, family, preferred frames, verified Resolve type.
-- Graphic matches stay hard cuts. Durations are beat-relative candidates at 24 fps.
local events = {
  {3, "reflection_dissolve", 16, "Cross Dissolve"},
  {5, "silk_occlusion", 12, "Cross Dissolve"},
  {6, "trapezoid_reveal", 8, "Edge Wipe"},
  {10, "shadow_reveal", 12, "Dip To Color Dissolve"},
  {12, "reflection_dissolve", 16, "Cross Dissolve"},
  {14, "masked_scale_reveal", 8, "Cross Dissolve"},
  {17, "shadow_reveal", 12, "Dip To Color Dissolve"},
  {22, "reflection_dissolve", 16, "Cross Dissolve"},
  {23, "trapezoid_reveal", 8, "Edge Wipe"},
  {26, "shadow_reveal", 12, "Dip To Color Dissolve"},
  {27, "reflection_dissolve", 16, "Cross Dissolve"},
  {29, "silk_occlusion", 12, "Cross Dissolve"},
  {31, "reflection_dissolve", 16, "Cross Dissolve"},
  {34, "trapezoid_reveal", 8, "Center Wipe"},
  {36, "masked_scale_reveal", 8, "Cross Dissolve"},
  {38, "reflection_dissolve", 16, "Cross Dissolve"},
}

local applied = 0
for _, e in ipairs(events) do
  local index, family, dur, typ = e[1], e[2], e[3], e[4]
  local clip = clips[index]
  local tr = nil
  local used = dur
  for _, candidate in ipairs({dur, 8, 4, 1}) do
    tr = tryTransition(clip, typ, candidate, "center")
    if not tr then tr = tryTransition(clip, typ, candidate, "left") end
    if tr then
      used = candidate
      break
    end
  end
  if tr then
    applied = applied + 1
    out("APPLIED", index, family, typ, used, tr:GetName(), tr:GetStart(), tr:GetEnd(), tr:GetDuration())
  else
    out("SKIPPED", index, family, typ, dur)
  end
end
out("TRANSITION_SUMMARY", applied, #events)

local srt = "/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/hello-ammai-progressive-deep-house/music-video/resolve/v6-full-film/the-last-tide-transliterated-PROVISIONAL.srt"
local pool = p:GetMediaPool()
local imported = nil
local okImport, importResult = pcall(function() return pool:ImportMedia({srt}) end)
out("SRT_IMPORT_CALL", tostring(okImport), tostring(importResult))
if okImport and importResult and #importResult > 0 then
  imported = importResult[1]
  local okAppend, appended = pcall(function() return pool:AppendToTimeline({imported}) end)
  out("SRT_APPEND", tostring(okAppend), tostring(appended))
else
  out("SRT_IMPORT_FAILED")
end
local subCount = 0
pcall(function() subCount = target:GetTrackCount("subtitle") end)
out("SUBTITLE_TRACKS", tostring(subCount))
local subItems = target:GetItemListInTrack("subtitle", 1)
out("SUBTITLE_ITEMS", subItems and #subItems or 0)

local saved = pm:SaveProject()
out("SAVED", tostring(saved))

local renderDir = "/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/hello-ammai-progressive-deep-house/music-video/resolve/v6-full-film/renders"
local presetOk = p:LoadRenderPreset("H.264 Master")
out("RENDER_PRESET", tostring(presetOk))
local formatOk = p:SetCurrentRenderFormatAndCodec("mp4", "H264")
out("RENDER_FORMAT", tostring(formatOk))
p:SetCurrentRenderMode(1)
local settingsOk = p:SetRenderSettings({
  SelectAllFrames = true,
  TargetDir = renderDir,
  CustomName = "the-last-tide-v6-sparse-beat-pass-review",
  ExportVideo = true,
  ExportAudio = true,
  FormatWidth = 1920,
  FormatHeight = 1080,
  FrameRate = 24,
  VideoQuality = 25000,
  AudioCodec = "aac",
  AudioSampleRate = 48000,
  NetworkOptimization = true,
  DataBurnIn = "None",
  ExportSubtitle = false,
})
out("RENDER_SETTINGS", tostring(settingsOk))
local job = p:AddRenderJob()
out("RENDER_JOB", tostring(job))
if job then
  local started = p:StartRendering({job})
  out("RENDER_STARTED", tostring(started), target:GetName(), target:GetStartFrame(), target:GetEndFrame(), target:GetEndFrame() - target:GetStartFrame())
else
  out("RENDER_NOT_STARTED")
end
out("DONE")
log:close()
