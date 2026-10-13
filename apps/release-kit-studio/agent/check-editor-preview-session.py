"""Verify stored review previews through the Studio's authenticated service binding."""
from contextlib import closing
import hashlib
import importlib.util
import json
from pathlib import Path
import sqlite3
import subprocess
import time


APP = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('preview_session_http', APP / 'agent/check-editor.py')
http = importlib.util.module_from_spec(spec)
spec.loader.exec_module(http)
SOURCE = APP / 'docs/editor/review-preview-runtime-receipt.json'
SOURCE_HASH = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
proof = json.loads(SOURCE.read_text())
assert proof['passed'] and not proof['cloudVerified']
bundle = proof['bundle']
DATABASE = next((APP / '.alchemy/local/d1/cloudflare-runtime-D1DatabaseObject').glob('*.sqlite'))


def sql(query, values=()):
    with closing(sqlite3.connect(f'file:{DATABASE}?mode=ro', uri=True)) as database:
        database.row_factory = sqlite3.Row
        return [dict(row) for row in database.execute(query, values)]


def idle():
    names = subprocess.check_output(['docker', 'ps', '--format', '{{.Names}}'], text=True).splitlines()
    assert not any(name.startswith('workerd-release-kit-editor-preview-RenderObject-') and not name.endswith('-proxy') for name in names)
    assert not sql('SELECT job_id,purpose FROM editor_capacity')


def main():
    idle()
    job = sql('SELECT tenant_id,state,receipt_json FROM editor_jobs WHERE id=?', (bundle['jobId'],))[0]
    session = foreign_session = foreign_token = None
    result = None
    try:
        invitation, _ = http.request(http.STUDIO, f'/api/operator/tenants/{job["tenant_id"]}/invites',
                                     'POST', {}, token=http.OPERATOR, expected=201)
        _, headers = http.request(http.STUDIO, '/api/auth/exchange', 'POST', {'token': invitation['token']})
        session = headers['Set-Cookie'].split(';', 1)[0]
        request = {key: bundle[key] for key in ['jobId', 'outputId', 'startFrame', 'frames', 'sampleFrames']}
        replay, _ = http.request(http.STUDIO, '/api/editor/tools/artifact.preview', 'POST', request, session=session)
        assert replay['reused'] is True and replay['bundle'] == bundle
        idle()
        http.request(http.STUDIO, '/api/editor/tools/artifact.preview', 'POST', request, session=session,
                     extra={'Origin': 'https://foreign.example'}, expected=403)
        base = f'/api/editor/jobs/{bundle["jobId"]}/previews/{bundle["bundleId"]}/preview.mp4'
        media, headers = http.request(http.STUDIO, base, session=session, raw=True)
        file = bundle['files'][0]
        assert len(media) == file['bytes'] and hashlib.sha256(media).hexdigest() == file['sha256']
        assert headers['X-Source-Sha256'] == bundle['source']['sha256']
        part, ranged = http.request(http.STUDIO, base, session=session, raw=True, expected=206,
                                    extra={'Range': 'bytes=11-47'})
        assert part == media[11:48] and ranged['Content-Range'] == f'bytes 11-47/{len(media)}'
        _, head = http.request(http.STUDIO, base, method='HEAD', session=session, raw=True)
        assert head['Content-Length'] == str(len(media))
        http.request(http.STUDIO, base, raw=True, expected=401)
        foreign_session, foreign_token = http.principal()
        http.request(http.STUDIO, base, session=foreign_session, raw=True, expected=404)
        idle()
        assert job == sql('SELECT tenant_id,state,receipt_json FROM editor_jobs WHERE id=?', (bundle['jobId'],))[0]
        assert SOURCE_HASH == hashlib.sha256(SOURCE.read_bytes()).hexdigest()
        result = {'scope': 'local Studio session and Editor service-binding preview verification only',
                  'passed': True, 'testedAt': time.time(), 'sourcePreviewReceipt': SOURCE.name,
                  'sourcePreviewReceiptSha256': SOURCE_HASH,
                  'sourceHashes': {'src/worker.ts': hashlib.sha256((APP / 'src/worker.ts').read_bytes()).hexdigest(),
                                   'agent/check-editor-preview-session.py': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
                  'checks': ['studio-cookie-session-replays-identical-cached-preview',
                             'private-studio-full-range-and-head-responses-match-native-receipt',
                             'foreign-origin-cookie-mutation-rejected',
                             'missing-and-foreign-tenant-sessions-rejected',
                             'source-job-unchanged-no-native-render-or-gpu-inference'],
                  'cloudVerified': False, 'nativeComputeSubmitted': False, 'gpuInferenceSubmitted': False,
                  'palPalKitCompleted': False, 'motionReviewed': False, 'heard': False, 'creativelyAccepted': False}
    finally:
        if foreign_token:
            http.request(http.EDITOR, '/v1/operator/tokens/revoke', 'POST', {'targetToken': foreign_token}, token=http.OPERATOR)
            assert sql('SELECT enabled FROM editor_tokens WHERE hash=?', (hashlib.sha256(foreign_token.encode()).hexdigest(),))[0]['enabled'] == 0
        for cookie in [session, foreign_session]:
            if cookie: http.request(http.STUDIO, '/api/auth/logout', 'POST', {}, session=cookie)
        if result:
            result['diagnosticSessionsLoggedOut'] = True
            result['diagnosticTokenRevoked'] = True
            (APP / 'docs/editor/review-preview-session-runtime-receipt.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


if __name__ == '__main__':
    result = main()
    print(json.dumps({'passed': result['passed'], 'checks': result['checks'], 'cloudVerified': False}))
