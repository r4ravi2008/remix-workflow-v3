"""Update current consumers only after the complete native exports are verified."""
from pathlib import Path
import json,datetime,shutil,html

P=Path('/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/nuvvantene-istam-deep-house/music-video/rebuild-r10-neon-space')
W=P.parents[1];R=P/'records/r14-native'
technical=json.loads((R/'full-render-technical-a03.json').read_text())
master=json.loads((R/'master-technical-a03.json').read_text())
inspection=json.loads((R/'full-frame-inspection-a03.json').read_text())
readback=json.loads((R/'full-native-readback-a03.json').read_text())
assert technical['full_decode_exit']==0 and master['sample_identical']
assert inspection['observed_defects_remaining']==[]
assert readback['frames']==5319 and readback['video_tracks']==3
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
backup=R/'superseded-root-consumers';backup.mkdir(exist_ok=True)
for filename in ['screenplay.json','effects-config.json','BRIEF.md']:
    path=P/filename
    if path.is_file() and not (backup/filename).exists():shutil.copy2(path,backup/filename)
plan=json.loads((R/'full-timeline-plan-a03.json').read_text())
screen={'revision':'R14-full-native-a03','canonical_frames':5319,'fps':24,'status':'full provisional rendered, measured and sampled-frame inspected; audiovisual and creative review pending','heard':False,'watched':False,'review_anchors':plan['review_anchors'],'native_timeline':readback['timeline'],'shots':[{**s,'start':s['recordStart'],'end':s['recordEnd']} for s in plan['shots']],'lyric_events':plan['lyric_events']}
(P/'screenplay.json').write_text(json.dumps(screen,indent=2)+'\n')
effects={'schema_version':1,'revision':'R14-full-native-a03','direction':'Minimal black space with an Indian Bharatanatyam silhouette, cyan 3D light rails and crimson garment/seam accents.','framing':{'canvas':[1920,1080],'fps':24,'camera':'Forward-only native perspective camera; source figure framing preserved.'},'native_world':{'owner':'Resolve Fusion','renderer':'OpenGL Renderer3D','geometry':'69 fixed Shape3D cylinder segments forming three curved rails','cyan_radius':.016,'crimson_radius':.026,'crimson_length':1.8,'animated_dimensions':False},'response':{'owner':'Native OpenPBR emission with baked BezierSpline','source':'Signed packed PCM24 canonical amplitude','attack_ms':100,'release_ms':400,'scope':'Environment emission only; figure and text excluded','beat_grid':'127.011 BPM estimate; downbeat phase and felt sync remain unverified','false_native_audio_binding_claim':False},'lyrics':{'owner':'Native TextPlus','words_and_cues':'Existing explicitly selected Latin transliteration preserved','size':.05,'centre':[.72,.54],'timing_status':'Listening pending'},'transitions':{'owner':'Resolve','source_fades_frames':5,'final_hold_fade_frames':48,'environment':'Continuous native world across all shot joins'},'review':{'measured':True,'frame_inspected':True,'watched':False,'heard':False,'creative_accepted':False,'exact_render_matrix':'records/r14-native/finish-review-a03.json'},'predecessor':'R13 source timeline retained; full A01 export rejected for disappearing environment and clipped body.'}
(P/'effects-config.json').write_text(json.dumps(effects,indent=2)+'\n')
mp4=Path(technical['render']);mov=Path(master['master']);drp=P/'resolve/r14-native/nuvvantene-r14-native-full-a03.drp'
receipt={'revision':'R14-full-native-a03','status':'full_provisional_rendered_measured_sampled_frame_inspected_review_pending','project':readback['project'],'timeline':readback['timeline'],'duration_seconds':221.625,'frames':5319,'fps':24,'playback':str(mp4),'playback_sha256':technical['sha256'],'pcm_master':str(mov),'master_sha256':master['sha256'],'pcm_sample_identical':True,'canonical_audio_sha256':master['canonical_sha256'],'editable_project':str(drp),'shots':35,'foreground_clips':27,'lyric_cues':22,'review_anchors':90,'review_interval_seconds_max':2.5,'sampled_frames':len(technical['sampled_frames']),'measured':True,'frame_inspected':True,'watched':False,'heard':False,'creative_acceptance':False,'quality_gate_pass':False,'quality_gate_report':str(R/'quality-gate-report-a03.json'),'finish_review_report':str(R/'finish-review-report-a03.json'),'updated_at':now}
(R/'delivery-receipt-a03.json').write_text(json.dumps(receipt,indent=2)+'\n')
old_receipt=P/'records/delivery-receipt.json'
if old_receipt.is_file() and not (backup/'delivery-receipt.json').exists():shutil.copy2(old_receipt,backup/'delivery-receipt.json')
old_receipt.write_text(json.dumps(receipt,indent=2)+'\n')
brief=f"# R14 native light ribbons\n\nFull provisional film: 221.625 seconds, 1920×1080, 24 fps.\n\nA Bharatanatyam silhouette guides cyan light through reaching, ankle accents and hand gestures. The red pleated fan returns before a held closing pose dissolves. Three fixed 3D rails establish depth under a continuous forward camera. Restrained amplitude response changes environment emission, never geometry size.\n\nNative Resolve project: {readback['project']}\n\nTimeline: {readback['timeline']}\n\nThe prior ball and texture overlay tracks are omitted. Canonical audio samples remain identical in the PCM master. Existing lyric words and timings are preserved.\n\nFull decode and sampled-frame inspection are recorded. Normal-speed watching, listening, felt beat sync and creative acceptance remain pending. The quality gate remains pending; this is a review candidate under the user's persistent full-film provisional authorization.\n\nPlayback: {mp4}\n\nEditable project: {drp}\n"
(P/'BRIEF.md').write_text(brief)
(P/'R14-IMPLEMENTATION.md').write_text(brief+f"\nEvidence: {R/'delivery-receipt-a03.json'}\n\nFull A01 was rejected for late world disappearance and mask clipping. Standard Shape3D meshes replaced the disappearing path plugin. A non-numbered still filename and explicit source hold prevent stale mask sequence selection. The repaired figure is checked in the exact full A03 export.\n")
page=f'''<!doctype html><meta charset="utf-8"><title>Nuvvantene R14 review</title><style>body{{background:#080a0b;color:#d9e8eb;font:17px system-ui;margin:36px auto;max-width:1200px}}video{{width:100%}}a{{color:#00d9ef}}p{{line-height:1.6}}</style><h1>Nuvvantene · R14 native light ribbons</h1><p>Full provisional Resolve film · 3:41.625 · 1080p / 24 fps</p><video controls src="{html.escape(str(mp4))}"></video><p>Three fixed cyan rails, crimson accents, Bharatanatyam silhouette and preserved lyrics. Canonical PCM samples match exactly in the master.</p><p>Measured and sampled-frame inspected. Normal-speed audiovisual review and creative acceptance remain pending.</p><p><a href="{html.escape(str(drp))}">Editable Resolve project</a> · <a href="{html.escape(str(mov))}">PCM master</a> · <a href="{html.escape(str(R/'delivery-receipt-a03.json'))}">Verification record</a></p>'''
(P/'R14-FULL-FILM-REVIEW.html').write_text(page)
mfile=W/'meta.json';m=json.loads(mfile.read_text());v=m['music_video']
v.update(stage='r14_full_provisional_rendered_review_pending',r14_status=receipt['status'],r14_native=receipt,current_storyboard=str(P/'screenplay.json'),current_storyboard_review=str(R/'full-frame-inspection-a03.json'),current_review_page=str(P/'R14-FULL-FILM-REVIEW.html'),current_playback=str(mp4),current_pcm_master=str(mov),current_editable_project=str(drp),resolve_project=readback['project'],resolve_timeline=readback['timeline'],measured=True,frame_inspected=True,watched=False,heard=False,creative_acceptance=False)
v['active_revision']='R14-full-native-a03'
v['current_delivery_receipt']=str(R/'delivery-receipt-a03.json')
if 'r10_neon_space' in v:
    v['r10_neon_space']['status']='superseded_by_r14_native'
    v['r10_neon_space']['superseded_by']='R14-full-native-a03'
mfile.write_text(json.dumps(m,indent=2)+'\n')
print({'playback':str(mp4),'master':str(mov),'editable':str(drp),'current_consumers_updated':True,'watched':False,'heard':False,'creative_acceptance':False})
