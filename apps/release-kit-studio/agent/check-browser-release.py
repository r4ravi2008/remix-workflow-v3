"""Read back the exact browser release and its independently hashed worker source."""
import hashlib
import json
from pathlib import Path
import sys
import time
import urllib.request
import uuid

APP = Path(__file__).resolve().parent.parent
WORKSPACE = Path('/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/pal-pal-nimisham')


def checksum(path):
    digest = hashlib.sha256()
    with path.open('rb') as source:
        while block := source.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def check(release_id):
    assert str(uuid.UUID(release_id)) == release_id
    config = json.loads((APP / '.local/local-worker.json').read_text())
    assert config['baseUrl'] == 'http://localhost:1337'

    def request(path, worker=False):
        headers = {'Authorization': 'Bearer ' + config['token']} if worker else {'Cookie': config['session']}
        with urllib.request.urlopen(urllib.request.Request(config['baseUrl'] + path, headers=headers), timeout=20) as response:
            assert response.status == 200
            return json.load(response)

    release = request('/api/releases/' + release_id)
    held = next(job for job in request('/api/worker/holds', True)['jobs'] if job['releaseId'] == release_id)
    assert release['state'] == held['state'] == 'waiting-for-direction'
    assert release['job']['id'] == held['id'] and release['job']['attempt'] == held['attempt'] == 1
    brief = held['brief']
    assert release['brief'] == brief
    selected = WORKSPACE / 'pal-pal-telugu-deep-house-remix.wav'
    assert brief['audioSha256'] == checksum(selected) == 'a5fa914e8f7cae9c76f7ec309ce3a60194d138baa3d2684477f361feeea5c8b3'
    assert brief['audioDuration'] == 239.68 and brief['audioBytes'] == selected.stat().st_size == 46018732
    assert brief['lyrics'] == (WORKSPACE / 'pal-pal-nimisham-lyrics.txt').read_text().strip()
    artist = request('/api/artist-profile')['artist']
    assert artist['profile'] == brief['profile'] and artist['profile']['name'] == 'Dhool'
    directory = Path(config['localState']) / held['id']
    assert checksum(directory / 'canonical-audio') == brief['audioSha256']
    assert (directory / 'canonical-audio').stat().st_size == brief['audioBytes']
    source = json.loads((directory / 'source-receipt.json').read_text())
    fingerprint = hashlib.sha256(json.dumps(brief, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    assert source['briefSha256'] == fingerprint and source['releaseId'] == release_id and source['attempt'] == 1
    status = json.loads((Path(config['localState']) / 'service-status.json').read_text())
    assert status['state'] == 'idle' and any(job['id'] == held['id'] for job in status['held'])
    library = request('/api/releases')['releases']
    assert {item['id'] for item in library} == {release_id, config['releaseId']}
    assert release['assets'] == []
    receipt = {
        'verifiedAt': time.time(), 'runtime': 'Alchemy native local D1/R2 plus the installed launchd service',
        'releaseId': release_id, 'jobId': held['id'], 'attempt': held['attempt'], 'state': held['state'],
        'audioSha256': brief['audioSha256'], 'audioBytes': brief['audioBytes'], 'audioDuration': brief['audioDuration'],
        'nativeLyricsMatch': True, 'artistSnapshotMatchesSavedStudioIdentity': True,
        'tenantReleaseReadbackMatchesSubmittedBrief': True,
        'briefSha256': fingerprint, 'workerSourceIndependentlyHashed': True,
        'sameReleaseAfterBrowserRetry': True, 'readyOutputs': 0, 'servicePid': status['pid'],
        'laterServicePoll': status['observedAt'], 'heldWithoutReclaim': True,
        'gpuProvider': source['gpuProvider'], 'finishing': source['finishing'],
        'newInferenceSubmitted': False, 'resolveMutated': False, 'hostedEndToEndVerified': False, 'fullKitComplete': False,
    }
    (APP / 'docs/browser-worker-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Pass the exact browser-created release ID.')
    check(sys.argv[1])
