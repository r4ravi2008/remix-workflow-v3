"""Reuse verified Resolve assembly routines with version-bound arguments."""
import json
import subprocess
from pathlib import Path

here=Path(__file__).parent
base=Path('/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/urvashi/music-video/hyperreal-story-review-v3')
plan=json.loads((base/'edit-contract.json').read_text())
subprocess.run(['python3',str(here/'build_resolve_xml.py'),str(base)],check=True)
verify=(here/'verify_story_cut.lua').read_text().replace('hyperreal-story-review-v2','hyperreal-story-review-v3').replace('URVASHI STORY CUT v2 - REVIEW CANDIDATE',plan['timelineName']).replace('urvashi-story-review-v2','urvashi-story-review-v3')
verify=verify[:verify.index(" assert(p:LoadRenderPreset")]+"\nend)\nlog('success',ok,err or '')\nf:close()\nassert(ok,err)\n"
intro="local pm=resolve:GetProjectManager(); local p=assert(pm:GetCurrentProject()); assert(p:GetName()=='URVASHI HYPERREAL STORY CUT 20260921'); assert(not p:IsRenderingInProgress()); assert(pm:SaveProject()); local t=assert(p:GetMediaPool():ImportTimelineFromFile('"+str(base)+"/story-cut.fcpxml',{importSourceClips=true})); assert(p:SetCurrentTimeline(t)); t:SetName('"+plan['timelineName']+"')\n"
messages=(here/'story_messages.lua').read_text().replace('hyperreal-story-review-v2','hyperreal-story-review-v3').replace('URVASHI STORY CUT v2 - REVIEW CANDIDATE',plan['timelineName']).replace('urvashi-story-review-v2','urvashi-story-review-v3')
indices={c['cutId']:i+1 for i,c in enumerate(plan['cuts'])}
for old,cid in [(14,'C014'),(27,'C027'),(31,'C031')]: messages=messages.replace(f'index={old},',f'index={indices[cid]},')
messages=messages.replace("text='Coffee tomorrow?", "text='COLLEAGUE / INCOMING\\nCoffee tomorrow?").replace("text='Flying out tonight.","text='BOYFRIEND / INCOMING\\nFlying out tonight.").replace("text='OYO tonight?'","text='COLLEAGUE / INCOMING\\nOYO tonight?'").replace("text='Okay.'","text='YOU / SENT\\nOkay.'").replace('mask.Height=0.135','mask.Height=0.17')
(base/'assemble-in-resolve.lua').write_text(intro+verify+messages)
print(base/'assemble-in-resolve.lua')
