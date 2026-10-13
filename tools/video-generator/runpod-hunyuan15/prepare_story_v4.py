"""Build a versioned Resolve musical revision; retain all prior exports."""
import copy, hashlib, json, shutil, subprocess
from pathlib import Path
root=Path('/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/urvashi/music-video')
base=root/'hyperreal-story-review-v4'; old=root/'hyperreal-story-review-v3'
base.mkdir(exist_ok=True); (base/'anchors').mkdir(exist_ok=True)
plan=json.loads((root/'anchor-revisions-v4/candidate-edit-contract.json').read_text())
plan['timelineName']='URVASHI STORY CUT v4 - MUSIC REACTIVE REVIEW'
plan['status']='PROVISIONAL_REVIEW_LISTENING_PENDING'
changes={'C004':13.78,'C010':39.96,'C016':67.75,'C017':73.75,'C018':78.25,'C026':104.04,'C027':111.0,'C030':121.75,'C031':126.08,'C037':157.38,'C038':161.0,'C039':165.5,'C040':171.0}
for c in plan['cuts']:
    if c['cutId'] in changes: c['startFrame']=round(changes[c['cutId']]*24)
    src=Path(c['sourceFile'])
    source=src if src.is_absolute() else old/'anchors'/src.name
    dest=base/'anchors'/src.name
    if not dest.exists(): shutil.copy2(source,dest)
    assert hashlib.sha256(dest.read_bytes()).hexdigest()==c['sha256']
    c['sourceFile']='anchors/'+src.name; c['displayAnchorFile']=c['sourceFile']
bridge=next(c for c in plan['cuts'] if c['cutId']=='C026')
extra=[]
for suffix,t,focus in [('b',104.38,'woman'),('c',104.71,'man'),('d',106.0,'wide')]:
    c=copy.deepcopy(bridge); c.update(cutId='C026'+suffix,startFrame=round(t*24),storyBeat='Same continuous bridge moment; '+focus+' coverage on vocal accent',reviewFraming=focus)
    extra.append(c)
plan['cuts']+=extra; plan['cuts'].sort(key=lambda c:c['startFrame'])
for i,c in enumerate(plan['cuts']):
    end=plan['cuts'][i+1]['startFrame'] if i+1<len(plan['cuts']) else 4482
    c.update(endFrameExclusive=end,durationFrames=end-c['startFrame'],startSeconds=c['startFrame']/24,endSeconds=end/24,endSecondsExclusive=end/24,endTimecodeExclusive=f'{end//86400:02}:{end//1440%60:02}:{end//24%60:02}:{end%24:02}')
    assert c['durationFrames']>0
assert next(c for c in plan['cuts'] if c['cutId']=='C008')['startFrame']==790
assert next(c for c in plan['cuts'] if c['cutId']=='C008')['endFrameExclusive']==898
plan['musicalRevision']={'analysis':'whole-song-analysis.json','boundaryChanges':changes,'bridgeAccents':[104.04,104.38,104.71,106.0],'transitions':{'C013':8,'C019':8,'C041':12},'coverageCaveat':'Bridge singles are native Resolve reframing of S23 for animatic review, not newly generated anchors. Approve framing then create full-resolution singles before motion generation. No animated zoom, reverse or fake slow motion.','outroCorrection':'User clarified C026 near 1:45, not scene28. Departure burst unchanged.'}
(base/'edit-contract.json').write_text(json.dumps(plan,indent=2,ensure_ascii=False))
subprocess.run(['python3',str(Path(__file__).parent/'build_resolve_xml.py'),str(base)],check=True)
script=(old/'assemble-in-resolve.lua').read_text().replace('hyperreal-story-review-v3','hyperreal-story-review-v4').replace('urvashi-story-review-v3','urvashi-story-review-v4').replace('URVASHI STORY CUT v3 - MUSICAL REVIEW',plan['timelineName'])
for oldindex,newindex in [(33,36),(29,32)]: script=script.replace(f'index={oldindex},',f'index={newindex},')
indices={c['cutId']:i+1 for i,c in enumerate(plan['cuts'])}
fx="""
 local clips=tl:GetItemListInTrack('video',1)
 local function reframe(index,cx,cy)
  local comp=assert(clips[index]:AddFusionComp())
  local input=assert(comp:FindTool('MediaIn1')); local output=assert(comp:FindTool('MediaOut1'))
  local trans=assert(comp:AddTool('Transform',-32768,-32768)); trans.Input=input.Output
  trans.Size=2; trans.Center={0.5+(0.5-cx)*2,0.5+(0.5-cy)*2}
  local mask=assert(comp:AddTool('RectangleMask',-32768,-32768)); mask.Width=1; mask.Height=790/1080; mask.Center={0.5,0.5}
  local bg=assert(comp:AddTool('Background',-32768,-32768)); bg.TopLeftRed=0; bg.TopLeftGreen=0; bg.TopLeftBlue=0; bg.TopLeftAlpha=1
  local merge=assert(comp:AddTool('Merge',-32768,-32768)); merge.Background=bg.Output; merge.Foreground=trans.Output; merge.EffectMask=mask.Mask; output.Input=merge.Output
  log('reaction framing '..index)
 end
"""
fx+=f" reframe({indices['C026b']},0.32,0.60)\n reframe({indices['C026c']},0.58,0.65)\n"
for cid,duration in plan['musicalRevision']['transitions'].items():
    index=indices[cid]; prev=base/plan['cuts'][index-2]['sourceFile']
    fx+=f"""
 do
  local comp=assert(clips[{index}]:AddFusionComp())
  local input=assert(comp:FindTool('MediaIn1')); local output=assert(comp:FindTool('MediaOut1'))
  local loader=assert(comp:AddTool('Loader',-32768,-32768)); loader.Clip={json.dumps(str(prev))}
  local merge=assert(comp:AddTool('Merge',-32768,-32768)); merge.Background=loader.Output; merge.Foreground=input.Output
  local start=comp:GetAttrs().COMPN_RenderStart or 0
  merge.Blend:SetExpression('min(max((time-'..start..')/{duration},0),1)'); output.Input=merge.Output
  log('dissolve {cid} {duration} frames')
 end
"""
needle=" assert(pm:SaveProject())\n assert(pm:ExportProject"
assert script.count(needle)==1
script=script.replace(needle,fx+needle)
script=script.replace("local t=assert(p:GetMediaPool()", "assert(pm:ExportProject(p:GetName(),'"+str(base)+"/pre-v4-checkpoint.drp',true)); local t=assert(p:GetMediaPool()")
(base/'assemble-in-resolve.lua').write_text(script)
print(base/'assemble-in-resolve.lua')
