"""Verify diagnostic manifest export from an existing local native kit."""
from contextlib import closing
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import time
import uuid
import zipfile

APP = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('editor_archive_http', APP / 'agent/check-editor.py')
http = importlib.util.module_from_spec(spec)
spec.loader.exec_module(http)
assert http.STUDIO == 'http://localhost:1337' and http.EDITOR == 'http://localhost:1339'
SOURCE = APP / 'docs/editor/frame-diagnostics-runtime-receipt.json'
SOURCE_HASH = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
source = json.loads(SOURCE.read_text())
assert source['passed'] and source['sourceAudioIsSynthetic'] and not source['cloudVerified']
assert source['sourceHashes']['editor/engine/engine.py'] == hashlib.sha256((APP / 'editor/engine/engine.py').read_bytes()).hexdigest()
DATABASE = next((APP / '.alchemy/local/d1/cloudflare-runtime-D1DatabaseObject').glob('*.sqlite'))
ROOT = APP / '.local' / ('editor-diagnostic-archive-' + str(uuid.uuid4()))
ROOT.mkdir(mode=0o700)
SOURCE_FILES = ['editor/archive.ts', 'editor/artifact.ts', 'editor/zip.ts', 'editor/kit-contract.ts', 'agent/editor-cli.ts', 'agent/verify-kit.py', 'agent/check-editor-diagnostic-archive.py']
SOURCE_HASHES = {name: hashlib.sha256((APP / name).read_bytes()).hexdigest() for name in SOURCE_FILES}


def sql(query, values=()):
    with closing(sqlite3.connect(f'file:{DATABASE}?mode=ro', uri=True)) as database:
        database.row_factory = sqlite3.Row
        return [dict(row) for row in database.execute(query, values)]


def holds():
    config = json.loads((APP / '.local/local-worker.json').read_text())
    result, _ = http.request(http.STUDIO, '/api/worker/holds', token=config['token'])
    return sorted([{key: job[key] for key in ('id', 'attempt', 'state')} for job in result['jobs']], key=lambda job: job['id'])


def native_count():
    names = subprocess.check_output(['docker', 'ps', '--format', '{{.Names}}'], text=True).splitlines()
    return len([name for name in names if name.startswith('workerd-release-kit-editor-preview-RenderObject-') and not name.endswith('-proxy')])


def main():
    before_holds = holds()
    job_id = source['editorJobId']
    jobs = sql('SELECT id,tenant_id,release_id,state,receipt_json FROM editor_jobs WHERE id=?', (job_id,))
    assert len(jobs) == 1 and jobs[0]['state'] == 'ready'
    job = jobs[0]
    assert native_count() == 0 and not sql('SELECT job_id FROM editor_capacity')
    before_jobs = sql('SELECT id,state FROM editor_jobs WHERE release_id=? ORDER BY id', (job['release_id'],))
    token = receipt = None
    began = time.monotonic()
    try:
        credential, _ = http.request(http.EDITOR, '/v1/operator/tokens', 'POST', {'tenantId': job['tenant_id']}, token=http.OPERATOR, expected=201)
        token = credential['token']
        path = ROOT / 'diagnostic-kit.zip'
        run = subprocess.run(['bun', 'agent/editor-cli.ts', 'archive', job_id, str(path)], cwd=APP,
                             env={**os.environ, 'EDITOR_URL': http.EDITOR, 'EDITOR_TOKEN': token},
                             check=True, capture_output=True, text=True, timeout=180)
        proof = json.loads(run.stdout)
        (ROOT / 'cli-proof.json').write_text(json.dumps(proof, indent=2) + '\n')
        assert proof['archiveEntriesVerified'] == 8 and proof['downloadedBytesVerified'] is True
        assert proof['sha256'] == hashlib.sha256(path.read_bytes()).hexdigest()
        with zipfile.ZipFile(path) as archive:
            manifest = json.loads(archive.read('manifest.json'))
        expected = {output['id']: output['frameDiagnostics'] for output in source['nativeReceipt']['outputs']}
        findings = {output['id']: output['frameDiagnostics'] for output in manifest['files']}
        assert findings == expected and len(findings) == 6
        assert all(row['semanticReviewed'] is False and row['completeFrameCoverage'] is True for row in findings.values())
        assert findings['short-2']['counts']['nearBlackFrames'] == 48 and findings['short-2']['reviewSuggested'] is True
        assert findings['short-1']['nearStaticRanges'] and findings['short-1']['reviewSuggested'] is True
        assert findings['short-3']['nearStaticRanges'][0]['expected'] is True and findings['short-3']['reviewSuggested'] is False
        assert all(manifest[key] is False for key in ['motionReviewed', 'heard', 'creativelyAccepted'])
        assert holds() == before_holds
        assert sql('SELECT id,state FROM editor_jobs WHERE release_id=? ORDER BY id', (job['release_id'],)) == before_jobs
        assert native_count() == 0 and not sql('SELECT job_id FROM editor_capacity')
        assert SOURCE_HASH == hashlib.sha256(SOURCE.read_bytes()).hexdigest()
        assert SOURCE_HASHES == {name: hashlib.sha256((APP / name).read_bytes()).hexdigest() for name in SOURCE_FILES}
        receipt = {'scope': 'local Workerd/D1/R2 existing-kit diagnostic manifest export only', 'passed': True,
                   'testedAt': time.time(), 'sourceHashes': SOURCE_HASHES,
                   'sourceNativeReceipt': 'frame-diagnostics-runtime-receipt.json', 'sourceNativeReceiptSha256': SOURCE_HASH,
                   'editorJobId': job_id, 'releaseId': job['release_id'], 'archive': proof,
                   'checks': ['real-agent-cli-downloads-and-verifies-eight-existing-entries',
                              'six-output-diagnostics-match-the-source-bound-native-receipt',
                              'blank-freeze-and-declared-hold-findings-preserved',
                              'semantic-motion-listening-and-creative-review-not-invented',
                              'existing-intent-and-both-pal-pal-holds-unchanged',
                              'no-native-container-started-and-capacity-remains-free'],
                   'elapsedSeconds': round(time.monotonic() - began, 3), 'newRenderSubmitted': False,
                   'gpuInferenceSubmitted': False, 'nativeContainersObserved': 0, 'capacitySlotReleased': True,
                   'cloudVerified': False, 'palPalKitCompleted': False, 'motionReviewed': False,
                   'heard': False, 'creativelyAccepted': False}
        receipt['archive'].pop('destination', None)
    finally:
        if token:
            http.request(http.EDITOR, '/v1/operator/tokens/revoke', 'POST', {'targetToken': token}, token=http.OPERATOR)
            assert sql('SELECT enabled FROM editor_tokens WHERE hash=?', (hashlib.sha256(token.encode()).hexdigest(),))[0]['enabled'] == 0
        if receipt:
            receipt['diagnosticTokenRevoked'] = True
            (APP / 'docs/editor/frame-diagnostics-archive-runtime-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return receipt


if __name__ == '__main__':
    result = main()
    print(json.dumps({'passed': result['passed'], 'checks': result['checks'], 'cloudVerified': False}))
