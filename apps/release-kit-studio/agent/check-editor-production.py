import hashlib
import importlib
import json
import sqlite3
import subprocess
import sys
import time
import urllib.parse
import uuid
from pathlib import Path

http = importlib.import_module('check-editor')
APP, FIXTURE, OPERATOR, STUDIO, request = http.APP, http.FIXTURE, http.OPERATOR, http.STUDIO, http.request


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'))


def verify_existing(release_id):
    if urllib.parse.urlparse(STUDIO).hostname not in {'localhost', '127.0.0.1'}:
        raise AssertionError('Existing synthetic canaries are only read from local Workerd.')
    uuid.UUID(release_id)
    rows = []
    for path in (APP / '.alchemy/local/d1/cloudflare-runtime-D1DatabaseObject').glob('*.sqlite'):
        if path.name == 'metadata.sqlite':
            continue
        with sqlite3.connect(path) as database:
            database.row_factory = sqlite3.Row
            row = database.execute('SELECT releases.tenant_id,releases.brief_json,jobs.id,jobs.state,jobs.receipt_json FROM releases JOIN jobs ON jobs.release_id=releases.id WHERE releases.id=?', (release_id,)).fetchone()
            if row:
                rows.append(dict(row))
    if len(rows) != 1:
        raise AssertionError('Exactly one stored canary is required.')
    row = rows[0]
    if json.loads(row['brief_json'])['title'] != 'Production adapter synthetic canary' or row['state'] != 'review':
        raise AssertionError('Only a completed synthetic adapter canary can be verified.')
    completion = json.loads(row['receipt_json'])
    native = completion['receipt']
    if completion['finishing'] != 'cloudflare-editor' or not all(native[key] is True for key in ['measured', 'storedByteReadback', 'receiptStored']) or len(native['outputs']) != 6:
        raise AssertionError('A complete stored native receipt is required.')
    session = device = None
    checks = ['prior-native-kit-and-atomic-promotion-read-back-without-rerender']
    private = APP / '.local/editor-production-private'
    try:
        invite, _ = request(STUDIO, f'/api/operator/tenants/{row["tenant_id"]}/invites', 'POST', token=OPERATOR, expected=201)
        _, headers = request(STUDIO, '/api/auth/exchange', 'POST', {'token': invite['token']})
        session = headers['Set-Cookie'].split(';', 1)[0]
        status, _ = request(STUDIO, f'/api/releases/{release_id}', session=session)
        if status['state'] != 'review' or len(status['assets']) != 6 or not all(asset['verified'] for asset in status['assets']):
            raise AssertionError('Tenant review ledger must contain all six verified outputs.')
        checks.append('tenant-review-ledger-six-verified-outputs')
        receipts = []
        for asset in status['assets']:
            content, headers = request(STUDIO, f'/api/assets/{asset["id"]}', session=session, raw=True)
            expected = next(output for output in native['outputs'] if output['id'] == asset['outputId'])
            if len(content) != asset['bytes'] or hashlib.sha256(content).hexdigest() != asset['sha256'] or asset['sha256'] != expected['sha256'] or 'Content-Range' in headers:
                raise AssertionError('Full download must return complete immutable bytes with HTTP 200.')
            segment, range_headers = request(STUDIO, f'/api/assets/{asset["id"]}', session=session, raw=True, extra={'Range': 'bytes=0-31'}, expected=206)
            if segment != content[:32] or range_headers['Content-Range'] != f'bytes 0-31/{len(content)}' or range_headers['Content-Length'] != '32':
                raise AssertionError('Partial download must bind the exact requested byte range.')
            extension = 'jpg' if asset['outputId'] in {'thumbnail', 'artwork'} else 'mp4'
            destination = private / f'{release_id}-{asset["outputId"]}.{extension}'
            destination.write_bytes(content)
            subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-i', str(destination), '-f', 'null', '-'], check=True, capture_output=True)
            receipts.append({'outputId': asset['outputId'], 'sha256': asset['sha256'], 'bytes': asset['bytes'], 'completeDownloadedDecode': True})
        checks += ['six-tenant-full-downloads-http-200-and-checksum-match', 'six-exact-byte-range-downloads-http-206', 'six-downloaded-artifacts-completely-decode']
        device, _ = request(STUDIO, '/api/operator/devices', 'POST', {'name': 'Stored kit verification canary'}, token=OPERATOR, expected=201)
        request(STUDIO, f'/api/worker/jobs/{row["id"]}/editor/promote', 'POST', {'editorJobId': completion['editorJobId']}, token=device['token'], extra={'X-Job-Lease': 'expired-attempt'}, expected=409)
        checks.append('completed-attempt-cannot-repromote')
        receipt = {'scope': 'local-workerd-production-adapter-six-output-synthetic-canary', 'testedAt': time.time(), 'passed': True,
                   'resumedStoredKitVerification': True, 'checks': checks, 'releaseId': release_id, 'jobId': row['id'], 'editorJobId': completion['editorJobId'],
                   'receiptSha256': completion['receiptSha256'], 'nativeReceipt': native, 'outputs': receipts, 'cloudVerified': False,
                   'palPalKitCompleted': False, 'motionReviewed': False, 'heard': False, 'creativelyAccepted': False}
    finally:
        if device:
            request(STUDIO, f'/api/operator/devices/{device["id"]}/revoke', 'POST', token=OPERATOR)
        if session:
            request(STUDIO, '/api/auth/logout', 'POST', session=session)
    checks.append('diagnostic-device-revoked-and-session-logged-out')
    receipt['diagnosticCredentialsRevoked'] = True
    (APP / 'docs/editor/production-runtime-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'ok': True, 'scope': receipt['scope'], 'checks': checks}))


def main(generated=False):
    if urllib.parse.urlparse(STUDIO).hostname not in {'localhost', '127.0.0.1'}:
        raise AssertionError('The seeded production canary only supports local Workerd.')
    checks = []
    private = APP / '.local/editor-production-private'
    private.mkdir(mode=0o700, exist_ok=True)
    input_path = private / 'input.json'
    device = session = None
    job_id = receipt = None
    candidates = []
    try:
        invite, _ = request(STUDIO, '/api/operator/invites', 'POST', {'tenantName': 'Production adapter canary ' + str(uuid.uuid4())}, token=OPERATOR, expected=201)
        _, headers = request(STUDIO, '/api/auth/exchange', 'POST', {'token': invite['token']})
        session = headers['Set-Cookie'].split(';', 1)[0]
        device, _ = request(STUDIO, '/api/operator/devices', 'POST', {'name': 'Isolated production adapter canary'}, token=OPERATOR, expected=201)
        project = json.loads((FIXTURE / 'project.json').read_text())
        audio = next(asset for asset in project['assets'] if asset['kind'] == 'audio')
        brief = {'title': 'Production adapter synthetic canary', 'lyrics': project['lyrics'], 'language': project['language'], 'audioName': 'canary.wav', 'audioSha256': audio['sha256'], 'audioBytes': audio['bytes'], 'audioDuration': audio['duration'],
                 'profile': {'name': 'Canary', 'identity': 'Synthetic technical test. No creative acceptance.', 'palette': 'Midnight city', 'intensity': 'Restrained'}}
        release, _ = request(STUDIO, '/api/releases', 'POST', {'requestKey': str(uuid.uuid4()), 'brief': brief}, session=session, expected=201)
        release_id = release['id']
        job_id, lease = str(uuid.uuid4()), str(uuid.uuid4())
        candidates = []
        for path in (APP / '.alchemy/local/d1/cloudflare-runtime-D1DatabaseObject').glob('*.sqlite'):
            if path.name == 'metadata.sqlite':
                continue
            with sqlite3.connect(path) as database:
                if database.execute('SELECT id FROM releases WHERE id=?', (release_id,)).fetchone():
                    candidates.append(path)
        if len(candidates) != 1:
            raise AssertionError('The canary release must bind exactly one local D1 database.')
        with sqlite3.connect(candidates[0]) as database:
            database.execute('PRAGMA foreign_keys=ON')
            database.execute("INSERT INTO jobs(id,release_id,state,device_id,lease_hash,lease_until,attempt,created_at,updated_at) VALUES(?,?,'running',?,?,?,1,?,?)",
                             (job_id, release_id, device['id'], hashlib.sha256(lease.encode()).hexdigest(), int(time.time()) + 900, int(time.time()), int(time.time())))
            database.execute("UPDATE releases SET state='running' WHERE id=?", (release_id,))
        checks.append('isolated-test-lease-without-queued-work-or-other-consumer-interruption')
        root = f'/api/worker/jobs/{job_id}/editor'
        headers = {'X-Job-Lease': lease}
        request(STUDIO, root + '/tools/project.inspect', 'POST', {'projectId': 'missing', 'revision': None}, expected=401, extra=headers)
        request(STUDIO, root + '/tools/project.inspect', 'POST', {'projectId': 'missing', 'revision': None}, token=device['token'], expected=409)
        request(STUDIO, root + '/operator/tokens', 'POST', {'tenantId': 'foreign'}, token=device['token'], extra=headers, expected=404)
        request(STUDIO, root + '/tools/media.inspect', 'POST', {'assetId': 'foreign-media'}, token=device['token'], extra=headers, expected=404)
        checks += ['worker-device-and-exact-lease-required', 'operator-route-and-foreign-media-rejected']
        project['releaseId'] = release_id
        project['briefSha256'] = hashlib.sha256(canonical(brief).encode()).hexdigest()
        prefix = f'p_{release_id}_'
        inputs = []
        recipe_inputs = []
        collected_shots = []
        planned_shots = []
        for asset in project['assets']:
            original = asset['id']
            asset['id'] = prefix + original
            binding = {'assetId': asset['id'], 'kind': 'canonical-audio'} if asset['kind'] == 'audio' else {'assetId': asset['id'], 'kind': 'file', 'path': str(FIXTURE / 'assets' / original)}
            if generated and asset['kind'] == 'video':
                shot_id = 'synthetic-collected-' + original
                collected_shots.append({'id': shot_id, 'path': str(FIXTURE / 'assets' / original)})
                planned_shots.append({'id': shot_id, **{field: 'synthetic-unsubmitted-' + field for field in ['ledger', 'workflow', 'inputs', 'bindings', 'inputRoot', 'outputRoot', 'archive', 'outputNode']}})
                binding = {'assetId': asset['id'], 'kind': 'shot', 'shotId': shot_id}
            inputs.append(binding)
            recipe_inputs.append({'mediaKind': asset['kind'], 'source': binding})
        for composition in project['compositions']:
            if composition['audio']:
                composition['audio']['assetId'] = prefix + composition['audio']['assetId']
            for clip in composition['clips']:
                clip['assetId'] = prefix + clip['assetId']
                if clip['reactive']:
                    clip['reactive']['maskAssetId'] = prefix + clip['reactive']['maskAssetId']
        project_path = private / f'{release_id}.json'
        project_path.write_text(canonical(project))
        plan = {'schemaVersion': 2, 'releaseId': release_id, 'briefSha256': project['briefSha256'], 'audioSha256': project['audioSha256'], 'approvedForBulk': False,
                'reviewEvidence': 'Synthetic integration diagnostic only.', 'shots': [], 'editor': {'projectId': 'production-' + release_id, 'expectedRevision': 0, 'projectPath': str(project_path), 'assets': inputs}}
        if generated:
            recipe = {key: project[key] for key in ['schemaVersion', 'releaseId', 'briefSha256', 'audioSha256', 'language', 'lyrics', 'fps', 'compositions']}
            recipe['inputs'] = recipe_inputs
            recipe_path = private / f'{release_id}-recipe.json'
            recipe_path.write_text(canonical(recipe))
            plan = {**plan, 'schemaVersion': 3, 'shots': planned_shots, 'editor': {'projectId': 'production-' + release_id, 'expectedRevision': 0, 'recipePath': str(recipe_path)}}
            checks.append('generated-media-recipe-has-no-predicted-shot-hash')
        source = str(FIXTURE / 'assets' / audio['id'].removeprefix(prefix))
        input_path.write_text(json.dumps({'config': {'baseUrl': STUDIO, 'token': device['token'], 'workstationConfig': 'unused-by-native-editor', 'localState': str(private), 'planRegistry': str(private)},
                                         'job': {'id': job_id, 'releaseId': release_id, 'attempt': 1, 'lease': lease, 'brief': brief}, 'plan': plan, 'source': source, 'collectedShots': collected_shots}))
        input_path.chmod(0o600)
        result = subprocess.run(['bun', 'agent/check-editor-production.ts', str(input_path)], cwd=APP, capture_output=True, text=True, timeout=600)
        if result.returncode:
            raise AssertionError('Production adapter failed: ' + result.stderr[:2000])
        outcome = json.loads(result.stdout)
        if outcome['state'] != 'review' or outcome['outputCount'] != 6 or outcome['humanAccepted'] is not False:
            raise AssertionError('The native adapter did not reach six-output review.')
        checks += ['real-production-adapter-source-and-file-bindings', 'immutable-media-upload-through-studio-editor-binding', 'six-output-native-render-and-independent-verification', 'private-r2-promotion-without-download-and-reupload']
        if generated:
            checks.append('collected-shot-measured-and-materialized-before-immutable-commit')
        status, _ = request(STUDIO, f'/api/worker/jobs/{job_id}', token=device['token'])
        if status['state'] != 'review' or len(status['assets']) != 6 or not all(asset['verified'] for asset in status['assets']):
            raise AssertionError('Outer production ledger differs from adapter outcome.')
        download_receipts = []
        for asset in status['assets']:
            content, download_headers = request(STUDIO, f'/api/assets/{asset["id"]}', session=session, raw=True)
            if len(content) != asset['bytes'] or hashlib.sha256(content).hexdigest() != asset['sha256']:
                raise AssertionError('Tenant private download differs from promoted output.')
            if 'Content-Range' in download_headers:
                raise AssertionError('A complete download must return HTTP 200 without Content-Range.')
            segment, range_headers = request(STUDIO, f'/api/assets/{asset["id"]}', session=session, raw=True, extra={'Range': 'bytes=0-31'}, expected=206)
            if segment != content[:32] or range_headers['Content-Range'] != f'bytes 0-31/{len(content)}':
                raise AssertionError('Partial download must return the exact byte range.')
            extension = 'jpg' if asset['outputId'] in {'thumbnail', 'artwork'} else 'mp4'
            destination = private / f'{release_id}-{asset["outputId"]}.{extension}'
            destination.write_bytes(content)
            subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-i', str(destination), '-f', 'null', '-'], check=True, capture_output=True)
            download_receipts.append({'outputId': asset['outputId'], 'sha256': asset['sha256'], 'bytes': asset['bytes'], 'completeDownloadedDecode': True})
        checks += ['outer-review-ledger-six-verified-outputs', 'tenant-private-downloads-match-immutable-output-hashes', 'six-exact-byte-range-downloads-http-206', 'six-downloaded-artifacts-completely-decode']
        request(STUDIO, root + '/promote', 'POST', {'editorJobId': outcome['editorJobId']}, token=device['token'], extra=headers, expected=409)
        checks.append('completed-attempt-cannot-repromote-or-downgrade-ready-assets')
        receipt = {'scope': 'local-workerd-production-adapter-six-output-synthetic-canary', 'testedAt': time.time(), 'passed': True, 'checks': checks,
                   'planSchemaVersion': plan['schemaVersion'], 'gpuInferenceSubmitted': False,
                   'releaseId': release_id, 'jobId': job_id, 'editorJobId': outcome['editorJobId'], 'outputs': download_receipts, 'cloudVerified': False,
                   'palPalKitCompleted': False, 'motionReviewed': False, 'heard': False, 'creativelyAccepted': False}
    finally:
        input_path.unlink(missing_ok=True)
        if job_id and device and len(candidates) == 1:
            with sqlite3.connect(candidates[0]) as database:
                database.execute("UPDATE releases SET state='needs-reconciliation' WHERE id IN (SELECT release_id FROM jobs WHERE id=? AND device_id=? AND state='running')", (job_id, device['id']))
                database.execute("UPDATE jobs SET state='needs-reconciliation',phase='Synthetic canary stopped',lease_hash=NULL,lease_until=NULL,updated_at=? WHERE id=? AND device_id=? AND state='running'", (int(time.time()), job_id, device['id']))
        if device:
            request(STUDIO, f'/api/operator/devices/{device["id"]}/revoke', 'POST', token=OPERATOR)
        if session:
            request(STUDIO, '/api/auth/logout', 'POST', session=session)
    if receipt:
        checks.append('diagnostic-device-revoked-and-session-logged-out')
        receipt['diagnosticCredentialsRevoked'] = True
        receipt_name = 'generated-production-runtime-receipt.json' if generated else 'production-runtime-receipt.json'
        (APP / 'docs/editor' / receipt_name).write_text(json.dumps(receipt, indent=2) + '\n')
        print(json.dumps({'ok': True, 'scope': receipt['scope'], 'checks': checks}))


if __name__ == '__main__':
    try:
        if len(sys.argv) == 3 and sys.argv[1] == 'verify':
            verify_existing(sys.argv[2])
        elif sys.argv[1:] == ['generated']:
            main(generated=True)
        elif not sys.argv[1:]:
            main()
        else:
            raise AssertionError('Use no arguments, generated, or verify RELEASE_ID.')
    except Exception as error:
        print(json.dumps({'ok': False, 'error': str(error)}), file=sys.stderr)
        sys.exit(1)
