"""Promote reviewed v6 anchors without changing timing or submitted job evidence."""
import copy
import json
import shutil
from prepare_motion_v5 import ROOT, BASE, OUT, build, sha


def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


revision_path = ROOT / 'anchor-revisions-v6/revision.json'
revision = json.loads(revision_path.read_text())
assert not revision['canonicalConsumersUpdated'], 'Already promoted; do not replay'
contract_path = BASE / 'edit-contract.json'
catalog_path = BASE / 'source-catalog.json'
contract = json.loads(contract_path.read_text())
catalog = json.loads(catalog_path.read_text())
before = copy.deepcopy(contract)
old_hash = sha(contract_path)
backup = ROOT / 'anchor-revisions-v6/pre-promotion'
backup.mkdir(exist_ok=True)
for path in (contract_path, catalog_path, OUT / 'job-preflight.json'):
    assert not (backup / path.name).exists(), 'Existing checkpoint needs inspection'
    shutil.copy2(path, backup / path.name)

for record in revision['records']:
    source = revision_path.parent / record['normalized']
    assert sha(source) == record['normalizedSHA256']
    target = BASE / 'anchors' / source.name
    assert not target.exists() or sha(target) == sha(source)
    shutil.copy2(source, target)
    relative = str(target.relative_to(BASE))
    for cut in contract['cuts']:
        if cut['cutId'] not in record['affectedCuts']:
            continue
        assert cut['anchorId'] == record['replacesAnchorId']
        cut.update(anchorId=record['anchorId'], sourceFile=relative,
                   displayAnchorFile=relative, motionAnchorIds=[record['anchorId']],
                   sha256=record['normalizedSHA256'])
    for asset in catalog['assets']:
        if asset['cutId'] in record['affectedCuts']:
            asset['supersedes'] = copy.deepcopy(asset)
            asset.update(anchorId=record['anchorId'], path=relative,
                         sha256=record['normalizedSHA256'],
                         revisionManifest=str(revision_path))
    record['status'] = 'REVIEWED_FOR_GENERATION'
    record['canonicalPath'] = str(target)

# Legacy motionAnchorIds were inherited from older still edits. Bind every
# single-anchor placement to the same identity as its actual current pixels.
metadata_repairs = []
for cut in contract['cuts']:
    if cut['motionAnchorIds'] != [cut['anchorId']]:
        metadata_repairs.append({'cutId': cut['cutId'], 'previous': cut['motionAnchorIds'],
                                 'current': [cut['anchorId']]})
        cut['motionAnchorIds'] = [cut['anchorId']]
for old, new in zip(before['cuts'], contract['cuts']):
    for key in ('cutId', 'startFrame', 'endFrameExclusive', 'durationFrames'):
        assert old[key] == new[key]
    if old['cutId'] not in ('C001', 'C039', 'C041'):
        assert old['sha256'] == new['sha256']
save(contract_path, contract)
catalog['latestRevision'] = str(revision_path)
save(catalog_path, catalog)
plan = build()
assert len(plan['generationGroups']) == 46
save(OUT / 'job-preflight.json', plan)

# Preserve submitted plans byte-for-byte. Unsubmitted plans get a separate
# reconciliation record; exact hashes and locked placements prove continued use.
for batch in sorted(OUT.glob('batch-*/plan.json')):
    staged = json.loads(batch.read_text())
    for job in staged['jobs']:
        current = next(j for j in plan['jobs'] if j['jobId'] == job['jobId'])
        for key in ('anchorSha256', 'timelineInFrame', 'timelineOutFrameExclusive'):
            assert job[key] == current[key], (batch, job['jobId'], key)
    save(batch.parent / 'contract-reconciliation-v6.json', {
        'status': 'UNCHANGED_JOB_INPUTS_AND_TIMING_VERIFIED',
        'originalPlanSHA256': sha(batch), 'originalContractSHA256': staged['contractSha256'],
        'currentContractSHA256': plan['contractSha256'],
        'verifiedJobs': [j['jobId'] for j in staged['jobs']],
        'budgetObservation': 'Historical only; live balance required before paid startup'})

revision.update(status='CANONICAL_ANCHORS_PROMOTED_RESOLVE_NOT_MODIFIED',
                canonicalConsumersUpdated=True, priorContractSHA256=old_hash,
                currentContractSHA256=plan['contractSha256'], metadataRepairs=metadata_repairs,
                neighborReview='C038 bag and badges set down; revised C039 has neither and maintains separation. C040/C040b matching cream top and charcoal jacket, no bag, progress to joined hands and shoulder rest. Full-size neighboring images inspected. City bookends retain matched skyline and separate generation intent.')
save(revision_path, revision)
print(json.dumps({'promotedCuts': ['C001', 'C039', 'C041'], 'timingChanged': False,
                  'metadataRepairs': metadata_repairs, 'contractSHA256': plan['contractSha256']}))
