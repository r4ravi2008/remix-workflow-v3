"""Audit downloaded v5 footage against the fixed cut contract, without editing Resolve."""
import hashlib
import json
import subprocess
from pathlib import Path
from prepare_motion_v5 import OUT

plan = json.loads((OUT / 'job-preflight.json').read_text())
dispositions_path = OUT / 'motion-dispositions.json'
dispositions = json.loads(dispositions_path.read_text()) if dispositions_path.exists() else {}
selections_path = OUT / 'motion-selections.json'
selections = json.loads(selections_path.read_text()) if selections_path.exists() else {}
records = {}
pilot = OUT / 'C007-v5-pilot_00001_.mp4'
if pilot.exists():
    records['C007'] = {'path': str(pilot), 'sha256': '0bc00f0e5ea311ed02097a4f41ce970dbdd319b3bb7ca7da2906ff5bbd1fce82',
                       'reviewStatus':'USER_APPROVED_QUALITY_LEVEL'}
for report_path in sorted([*OUT.glob('batch-*/*.result.json'), *OUT.glob('retry-*/*.result.json')]):
    report = json.loads(report_path.read_text())
    assert report['localSHA256Verified'] is True
    key = report['jobId']
    assert key not in records, 'Duplicate generation requires explicit selection: ' + key
    records[key] = {'path':report['localOriginal'], 'sha256':report['media']['sha256'],
                    'reviewStatus':'GENERATED_UNREVIEWED','result':str(report_path)}
    if key in dispositions:
        disposition = dispositions[key]
        assert disposition['sha256'] == records[key]['sha256'], 'Stale motion disposition'
        records[key]['reviewStatus'] = disposition['status']
        records[key]['reviewEvidence'] = disposition
placements = []
missing = []
for group in plan['generationGroups']:
    key = group['generationId']
    selection = selections.get(key)
    asset_key = selection['assetId'] if selection else key
    if asset_key not in records or records[asset_key]['reviewStatus'] == 'REJECTED':
        missing.append(key)
        continue
    asset = records[asset_key]
    if selection:
        assert selection['sha256'] == asset['sha256'], 'Stale motion selection'
        assert selection['reviewEvidence'], 'Replacement selection requires evidence'
    media = Path(asset['path'])
    assert hashlib.sha256(media.read_bytes()).hexdigest() == asset['sha256']
    probe = json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-select_streams','v:0',
               '-show_entries','stream=width,height,r_frame_rate,nb_read_frames','-of','json',str(media)]))['streams'][0]
    assert (probe['width'], probe['height'], probe['r_frame_rate']) == (1536,640,'24/1')
    frames = int(probe['nb_read_frames'])
    assert frames >= group['nativeFrames']
    asset['frames'] = frames
    for slot in group['placements']:
        cut = next(j for j in plan['jobs'] if j['jobId'] == slot['cutId'])
        assert slot['sourceOutFrameExclusive'] <= frames
        placements.append({**slot,'generationId':key,'assetId':asset_key,'timelineInFrame':cut['timelineInFrame'],
                           'timelineOutFrameExclusive':cut['timelineOutFrameExclusive'],
                           'reviewStatus':asset['reviewStatus']})
remaining = missing
report = {'status':'PARTIAL_GENERATION' if remaining else 'ALL_GENERATED_REVIEW_AND_RESOLVE_PENDING',
          'downloadedGenerations':sum(g['generationId'] in records for g in plan['generationGroups']),
          'downloadedOriginals':len(records),'requiredGenerations':len(plan['generationGroups']),
          'rejectedGenerations':[key for key, value in records.items() if value['reviewStatus'] == 'REJECTED'],
          'technicallyCoveredFrames':sum(p['timelineOutFrameExclusive']-p['timelineInFrame'] for p in placements),
          'requiredTimelineFrames':4482,'assets':records,'placements':placements,'remainingGenerations':remaining,
          'resolvePolicy':'Do not use Resolve until all videos are generated. This audit does not edit or approve the final film.'}
(OUT / 'downloaded-inventory.json').write_text(json.dumps(report, indent=2))
print(json.dumps({k:report[k] for k in ('status','downloadedGenerations','requiredGenerations','technicallyCoveredFrames','remainingGenerations')}))
