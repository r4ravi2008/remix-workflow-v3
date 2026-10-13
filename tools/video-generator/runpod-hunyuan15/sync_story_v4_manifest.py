import json, hashlib
from pathlib import Path
root=Path('/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/urvashi')
base=root/'music-video/hyperreal-story-review-v4'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=json.loads((base/'edit-contract.json').read_text())
revisions=[plan['anchorRevision'],json.loads((root/'music-video/anchor-revisions-v4/revision.json').read_text()),json.loads((root/'music-video/anchor-revisions-v4/S07-revision.json').read_text())]
assets={}
for c in plan['cuts']:
    p=base/c['sourceFile']; assert sha(p)==c['sha256']
    if c['anchorId'] not in assets:
        assets[c['anchorId']]={'anchorId':c['anchorId'],'path':str(p),'sha256':c['sha256'],'status':'CURRENT_REVIEW_CANDIDATE','placements':[]}
    assets[c['anchorId']]['placements'].append({'cutId':c['cutId'],'startFrame':c['startFrame'],'endFrameExclusive':c['endFrameExclusive'],'framing':c.get('reviewFraming','wide')})
for r in revisions: assets[r['anchorId']]['generationLineage']=r
catalog={'schemaVersion':1,'status':'CURRENT_REVIEW_ONLY_NOT_MOTION_APPROVED','timeline':plan['timelineName'],'inheritedCatalog':plan.get('inheritedCatalog',plan['sourceCatalog']),'assets':list(assets.values()),'supersededForCurrentEdit':[{'anchorId':r['replaces'],'replacement':r['anchorId'],'preservedInPriorVersions':True} for r in revisions],'generationGate':'No GPU generation. Bridge reaction singles require full-resolution anchors after edit approval.'}
(base/'source-catalog.json').write_text(json.dumps(catalog,indent=2,ensure_ascii=False))
plan['inheritedCatalog']=catalog['inheritedCatalog']; plan['sourceCatalog']=str(base/'source-catalog.json'); plan['catalogSha256']=sha(base/'source-catalog.json')
plan['anchorRevisions']=revisions
(base/'edit-contract.json').write_text(json.dumps(plan,indent=2,ensure_ascii=False))
meta_path=root/'meta.json'; meta=json.loads(meta_path.read_text())
done=(base/'render-qc.json').exists()
meta['hyperreal_story_review_v4']={'status':'RENDERED_TECHNICAL_QC_PASS_CREATIVE_REVIEW_PENDING' if done else 'APPLIED_IN_RESOLVE_EXPORT_PENDING','timeline':plan['timelineName'],'editContract':'music-video/hyperreal-story-review-v4/edit-contract.json','sourceCatalog':'music-video/hyperreal-story-review-v4/source-catalog.json','musicalAnalysis':'music-video/hyperreal-story-review-v4/whole-song-analysis.json','review':'music-video/hyperreal-story-review-v4/urvashi-story-review-v4.mp4' if done else None,'resolveProject':'music-video/hyperreal-story-review-v4/urvashi-story-review-v4-messages.drp' if done else None,'cuts':len(plan['cuts']),'frames':4482,'fps':24,'replacedAnchors':['S05-I02','S07-I02','S08-I02'],'motionGenerationGate':'WAIT_FOR_USER_APPROVAL_NO_RENTED_GPU','normalSpeedWatched':'PENDING','heard':'PENDING'}
meta['pending_anchor_revision_v4']['resolveUpdate']='APPLIED in v4; v3 remains unchanged for comparison'
meta['pending_anchor_revision_v4']['status']='APPLIED_IN_REVIEW_TIMELINE'
meta['current_story_review']='hyperreal_story_review_v4'
meta_path.write_text(json.dumps(meta,indent=2,ensure_ascii=False)+'\n')
rp=root/'music-video/anchor-revisions-v4/revision.json'; r=json.loads(rp.read_text()); r['resolveUpdate']='APPLIED: C008 S08-I02 in URVASHI STORY CUT v4 - MUSIC REACTIVE REVIEW; frames790-898 verified by native readback'; rp.write_text(json.dumps(r,indent=2)+'\n')
print('Updated current review catalog, edit contract and meta; export complete:',done)
