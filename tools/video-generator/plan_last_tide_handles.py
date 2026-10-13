"""Reserve monotonic source time through transitions; never freeze or restart a plate."""
import hashlib
import json
from fractions import Fraction
from prepare_last_tide_v6 import OUT

path = OUT / 'full-film-plan.json'
plan = json.loads(path.read_text())
rows = []
for shot in plan['shots']:
    incoming = next((t for t in plan['transitions'] if t['incoming'] == shot['id']), None)
    outgoing = next((t for t in plan['transitions'] if t['outgoing'] == shot['id']), None)
    pre = shot['recordInFrame'] - incoming['startFrame'] if incoming else 0
    post = outgoing['endFrame'] - shot['recordOutFrame'] if outgoing else 0
    assert pre >= 0 and post >= 0
    record_in, record_out = shot['recordInFrame'] - pre, shot['recordOutFrame'] + post
    source_in, source_out = shot['sourceInFrame'], shot['sourceOutFrame']
    status = 'existing_source_window_candidate'
    if shot['sourceId'].startswith('A'):
        record = OUT / (shot['sourceId'] + '-motion-record.json')
        if record.exists():
            measured = json.loads(record.read_text())
            source_in, source_out = 2, int(measured['frames']) - 2
            status = 'downloaded_candidate_endpoints_and_cadence_pending'
        else:
            source_in += 2
            source_out -= 2
            status = 'missing_motion_duration_assumed_not_verified'
    speed = Fraction(source_out-source_in, record_out-record_in)
    assert speed > 0
    cut_in = Fraction(source_in) + pre * speed
    cut_out = Fraction(source_out) - post * speed
    assert source_in <= cut_in < cut_out <= source_out
    rows.append({'shotId':shot['id'], 'sourceId':shot['sourceId'], 'status':status,
                 'extendedRecordFrames':[record_in,record_out], 'cleanRecordFrames':[shot['recordInFrame'],shot['recordOutFrame']],
                 'sourceWindowFrames':[source_in,source_out], 'preHandleTimelineFrames':pre, 'postHandleTimelineFrames':post,
                 'speedRatio':str(speed), 'speedPercent':round(float(speed)*100,3),
                 'sourceAtCleanIn':str(cut_in), 'sourceAtCleanOut':str(cut_out),
                 'mapping':'source = sourceWindowIn + (recordFrame - extendedRecordIn) * speedRatio',
                 'needsCadenceReview':True})
for left,right in zip(rows,rows[1:]):
    assert left['cleanRecordFrames'][1] == right['cleanRecordFrames'][0]
report={'status':'planning_only_not_applied_in_resolve', 'planSha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'fps':24,'shotCount':len(rows),'transitionsPlanned':len(plan['transitions']),
        'rule':'Keep source chronology continuous from first transition visibility through clean shot to final transition visibility. Never restart incoming footage at the nominal cut.',
        'limitation':'Allocates handles inside the selected source window by a slightly slower candidate retime. Does not establish accepted duration or optical-flow quality.',
        'shots':rows}
(OUT/'transition-handle-candidates.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'shotCount':len(rows),'gapCheck':'passed','positiveMonotonicMappings':True,'missingMotion':[r['sourceId'] for r in rows if r['status'].startswith('missing')]},indent=2))
