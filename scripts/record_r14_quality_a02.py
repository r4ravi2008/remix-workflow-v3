"""Bind candidate dependencies and truthful pending reviews to the exact R14 export."""
from pathlib import Path
import hashlib,json,importlib.util,subprocess

P=Path('/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/nuvvantene-istam-deep-house/music-video/rebuild-r10-neon-space')
ROOT=Path('/Users/aira/projects/remix-gpt-coding-agent')
spec=importlib.util.spec_from_file_location('gate',ROOT/'.agents/skills/video-director/scripts/quality_gate.py')
gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)
policy=json.loads((P/'quality-policy.json').read_text());policy_hash=gate.fingerprint(policy)
readback=json.loads((P/'records/r14-native/full-native-readback-a02.json').read_text())
technical=json.loads((P/'records/r14-native/full-render-technical-a02.json').read_text())
components=[]

def artifact(path):
    path=Path(path);return {'path':str(path.relative_to(P)) if path.is_relative_to(P) else str(path),'sha256':hashlib.file_digest(path.open('rb'),'sha256').hexdigest()}

def component(cid,kind,paths,deps=(),frames=None,passes=None):
    revision='R14-full-native-a02'
    record={'id':cid,'kind':kind,'revision':revision,'intended_use':'Full provisional R14 film under explicit continuation authorization; creative acceptance remains pending.','artifacts':[artifact(path) for path in paths],'dependencies':[{'id':d,'revision':revision} for d in deps]}
    if frames:record.update(frame_count=frames,review_ranges=[[0,frames]])
    review={'revision':revision,'policy_sha256':policy_hash,'reviewer':'Codex','method':'native readback, file measurement and exact-render frame inspection; no normal-speed watched or heard review','scope':'Bound R14 A02 files. Frame samples do not establish timing, motion quality or creative acceptance.','sessions':[],
            'gates':{name:{'verdict':'pending','evidence':'Required perceptual or acceptance evidence remains unavailable.'} for name in policy['kinds'][kind]['hard_gates']},
            'criteria':{name:{'status':'pending','score':None,'evidence':'Unrated; technical integrity and sampled frames do not establish the complete perceptual criterion.'} for name in policy['kinds'][kind]['criteria']}}
    for name,evidence in (passes or {}).items():review['gates'][name]={'verdict':'pass','evidence':evidence}
    review['component_sha256']=gate.component_fingerprint(record);record['review']=review;components.append(record)
    return cid

audio=component('canonical-audio','audio',[P/'resolve/R05-canonical.wav'],frames=5319,passes={'correct_source':'Exact canonical SHA256 9769452de248e4c05029f678fe3eac2d0ae0134161e7636356af641379e9396c.','decodes':'Packed PCM24 stereo, 48000 Hz, 10638000 sample frames.','requested_range_intact':'221.625 seconds, no audio retiming or trims in native readback.'})
audio_map=component('audio-controls','audio_map',[P/'analysis/r14-native/full-controls-a01.json'],[audio],passes={'canonical_audio_bound':'Controls bind the exact canonical hash; beat grid remains explicitly estimated.'})
brief=component('brief','brief',[P/'records/r14-native/brief-a02.json'],[audio_map],passes={'interpretation_evidence_disclosed':'Brief distinguishes measured controls from missing listening and normal-speed creative review.'})
story=component('storyboard','storyboard',[P/'records/r14-native/full-timeline-plan-a02.json',P/'records/r14-native/full-a02-correction-evidence.json'],[brief,audio_map],frames=5319,passes={'scope_respected':'Native Resolve full-song revision; no new paid generation or upload.','audio_map_bound':'Plan binds unchanged canonical audio and provisional timing status.','anchor_plan_complete':'35 contiguous editorial intervals and 90 review anchors at most 2.5 seconds apart.','approval_boundary_met':'Persistent explicit full provisional continuation authorization is recorded; no accepted-film claim.'})
sources=sorted({n['source_path'] for clip in readback['clips'] for n in clip['nodes'] if n.get('source_path','').endswith('.mp4')})
provenance=json.loads((P/'records/r14-native/inherited-source-provenance.json').read_text())
provenance_by_source={row['source']:row for row in provenance}
anchor_paths=sorted({a['path'] for row in provenance for a in row['anchors'] if not a.get('missing')})
anchor_ids={path:component('anchor-'+Path(path).stem,'image',[path],[story],passes={'provenance_recorded':'Exact model-input image compared with inherited source-job input snapshot; recorded in inherited-source-provenance.json.'}) for path in anchor_paths}
motion_ids=[]
for source in sources:
    name=Path(source).stem
    row=provenance_by_source[source]
    upstream=[anchor_ids[a['path']] for a in row['anchors'] if a['path'] in anchor_ids]
    motion_ids.append(component('source-'+name,'motion',[source,row['bindings'],row['inputs']],[story]+upstream,frames=124,passes={'usable_duration_verified':'Source snapshot inventory and native source-time readback bind the 124-frame original.','current_source_snapshot_verified':'Exact consumed source bytes are hashed in this manifest.'}))
matte_paths=sorted({path for clip in readback['clips'] for n in clip['nodes'] for path in [n.get('Clip'),n.get('source_path')] if isinstance(path,str) and path.endswith('.png')})
matte_artifacts=set()
for path in matte_paths:
    path=Path(path)
    if 'matte-sequence' in str(path):matte_artifacts.update(path.parent.glob('*.png'))
    else:matte_artifacts.add(path)
matte_id=component('foreground-mattes','image',sorted(matte_artifacts),[story],passes={'production_canvas_verified':'All consumed prepared matte images are 1920 by 1080.','intended_use_feasible':'Native Fusion Custom plus explicit source-time alignment was demonstrated in exact Resolve diagnostics.'})
lyrics=component('preserved-lyrics','lyrics',[P/'records/r14-native/full-native-readback-a02.json',P/'records/r14-native/full-timeline-plan-a02.json'],[audio,story],frames=5319)
world=component('native-world','story_graphic',[P/'resolve/r14-native/full-a02-compositions/V1-00000.comp',P/'analysis/r14-native/full-controls-a01.json',P/'records/r14-native/world-mesh-repair-a02.json'],[audio_map,story],frames=5319)
edit_paths=[P/'resolve/r14-native/nuvvantene-r14-native-full-a02.drp',P/'records/r14-native/full-native-readback-a02.json']+sorted((P/'resolve/r14-native/full-a02-compositions').glob('*.comp'))
edit=component('native-edit','edit',edit_paths,[audio,brief,story,matte_id,lyrics,world]+motion_ids,frames=5319,passes={'coverage_complete':'Native world covers frames 0 through 5318; figure and lyric tracks match the full plan.','audio_preserved':'One canonical audio item spans [0,5319) with no retiming.','render_state_verified':'Exact native project, timeline and exported checkpoint read back.','event_order_monotonic':'Native chronological intervals and forward source-time expressions are preserved.'})
export=component('full-review-export','export',[P/'renders/r14-native/nuvvantene-r14-native-ribbons-full-a02.mp4',P/'records/r14-native/full-render-technical-a02.json'],[edit],frames=5319,passes={'correct_render_bound':f"Exact inspected export SHA256 {technical['sha256']}.",'technical_checks_pass':'Full decode exit 0; 1920x1080, 24 fps, 5319 video frames.'})
manifest={'schemaVersion':1,'targets':[export],'components':components,'authorization':'Full provisional continuation despite disclosed perception limits. This manifest never promotes missing evidence to acceptance.','upstream_generation_acceptance':'Existing source and anchor acceptance is not grandfathered; source motion gates remain pending. Prior provenance references are retained in the workspace.'}
(P/'r14-quality-manifest-a02.json').write_text(json.dumps(manifest,indent=2)+'\n')
report=gate.audit(policy,manifest,P,json.loads((ROOT/'.agents/skills/music-video-director/assets/quality-policy.json').read_text()))
(P/'records/r14-native/quality-gate-report-a02.json').write_text(json.dumps(report,indent=2)+'\n')
print({'components':len(components),'sources':len(sources),'matte_artifacts':len(matte_artifacts),'targets_pass':report['targets_pass'],'review':'pending normal-speed audiovisual and creative acceptance'})
