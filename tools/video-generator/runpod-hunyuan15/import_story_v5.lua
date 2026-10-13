local base='/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/urvashi/music-video/hyperreal-story-review-v5'
local report=assert(io.open(base..'/resolve-import-readback.tsv','w'))
local function log(...)
  local values={...}; for i,v in ipairs(values) do values[i]=tostring(v) end
  report:write(table.concat(values,'\t'),'\n'); report:flush()
end
local ok,err=pcall(function()
  local resolve=resolve or (Resolve and Resolve()) or (bmd and bmd.scriptapp('Resolve')) or (fusion and fusion:GetResolve())
  assert(resolve,'Native Resolve handle unavailable')
  local pm=resolve:GetProjectManager()
  local project=assert(pm:GetCurrentProject())
  assert(project:GetName()=='URVASHI HYPERREAL STORY CUT 20260921','Wrong project')
  assert(not project:IsRenderingInProgress(),'Existing render must finish first')
  assert(pm:SaveProject())
  local name='URVASHI STORY CUT v5 - PROVISIONAL ANCHOR REVIEW'
  local timeline=nil
  for i=1,project:GetTimelineCount() do
    local candidate=project:GetTimelineByIndex(i)
    if candidate:GetName()==name then timeline=candidate end
  end
  if not timeline then
    assert(pm:ExportProject(project:GetName(),base..'/pre-v5-import-checkpoint.drp',true))
    timeline=assert(project:GetMediaPool():ImportTimelineFromFile(base..'/story-cut.fcpxml',{importSourceClips=true}))
    assert(timeline:SetName(name))
  end
  assert(project:SetCurrentTimeline(timeline))
  local plan=dofile(base..'/review-plan.lua')
  local clips=timeline:GetItemListInTrack('video',1)
  assert(#clips==#plan.cuts,'Cut count mismatch')
  local start=timeline:GetStartFrame()
  for i,cut in ipairs(plan.cuts) do
    local clip=clips[i]
    local source=assert(clip:GetMediaPoolItem()):GetClipProperty('File Path')
    assert(clip:GetStart()-start==cut.startFrame,'Start mismatch: '..cut.cutId)
    assert(clip:GetDuration()==cut.durationFrames,'Duration mismatch: '..cut.cutId)
    assert(source==base..'/'..cut.sourceFile,'Source mismatch: '..cut.cutId)
    log(cut.cutId,clip:GetStart()-start,clip:GetDuration(),source)
  end
  assert(timeline:GetEndFrame()-start==4482,'Timeline duration mismatch')
  local audio=timeline:GetItemListInTrack('audio',1)
  assert(#audio==1,'Expected one canonical audio clip')
  assert(audio[1]:GetMediaPoolItem():GetClipProperty('File Path')==plan.audio,'Wrong master audio')
  assert(pm:SaveProject())
  assert(timeline:Export(base..'/urvashi-story-review-v5-provisional.drt',resolve.EXPORT_DRT))
  log('VERIFIED',name,4482,#clips,'STILL REVIEW ONLY - MOTION AND OVERLAYS PENDING')
end)
log('success',ok,err or '')
report:close()
assert(ok,err)
