"""Apply inspected full-body coverage and transparent black in native Fusion."""
from pathlib import Path
import json

P=Path('/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/nuvvantene-istam-deep-house/music-video/rebuild-r10-neon-space')
assert project.GetName()=='NUVVANTENE - R10 - ONE ORBIT' and not project.IsRenderingInProgress()
t=project.GetCurrentTimeline();assert t.GetName()=='R14 - NATIVE LIGHT RIBBONS - FULL PROVISIONAL'
t.SetCurrentTimecode('00:03:41:14')
record=[]
for item in t.GetItemListInTrack('video',2):
    c=item.GetFusionCompByIndex(1);c.Lock()
    old=c.FindTool('ProtectedMotionEnvelope')
    coverage=c.FindTool('FullFigureCoverageA02')
    matte=c.FindTool('ProtectFigureAndClearBackground') or c.FindTool('ProtectSubjectAndRemoveOrbit')
    if coverage or (old and 'S02-full-motion' in old.GetInput('Clip',0)):
        n=coverage or c.AddTool('Loader',False);n.SetAttrs({'TOOLS_Name':'FullFigureCoverageA02'})
        n.SetInput('Clip',str(P/'analysis/r14-native/S02-full-figure-coverage.png'))
        hold=c.FindTool('HoldStaticCoverage') or c.AddTool('TimeStretcher',False)
        hold.SetAttrs({'TOOLS_Name':'HoldStaticCoverage'});hold.ConnectInput('Input',n);hold.SetInput('SourceTime',0)
        assert matte.ConnectInput('Image2',hold)
        if old:old.Delete()
    elif old:
        hold=c.FindTool('HoldStaticCoverage') or c.AddTool('TimeStretcher',False)
        hold.SetAttrs({'TOOLS_Name':'HoldStaticCoverage'});hold.ConnectInput('Input',old)
        hold.SetInput('SourceTime',old.GetInput('GlobalIn',0));assert matte.ConnectInput('Image2',hold)
    if matte:
        for k,v in [('RedExpression','r1*r2'),('GreenExpression','g1*r2'),('BlueExpression','b1*r2')]:matte.SetInput(k,v)
        matte.SetInput('AlphaExpression','min(1,max(r1,max(g1,b1))*8)*r2')
        c.FindTool('MediaOut1').ConnectInput('Input',matte)
    c.Unlock()
    record.append({'start':item.GetStart(),'end':item.GetEnd(),'alpha_expression':matte.GetInput('AlphaExpression',0) if matte else None,'coverage_repaired':c.FindTool('FullFigureCoverageA02') is not None})
assert resolve.GetProjectManager().SaveProject()
assert resolve.GetProjectManager().ExportProject(project.GetName(),str(P/'resolve/r14-native/nuvvantene-r14-native-full-a02.drp'))
(P/'records/r14-native/full-coverage-repair-a02.json').write_text(json.dumps(record,indent=2)+'\n')
result={'clips':len(record),'full_body_coverage_repaired':sum(r['coverage_repaired'] for r in record),'black_background_alpha':'transparent; no new visual animation','sequence_filename_fix':'Non-numeric still filename and explicit source hold prevent the old a01 matte from joining a01/a02 into a sequence.'}
