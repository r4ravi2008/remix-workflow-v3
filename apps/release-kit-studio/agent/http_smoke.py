"""Exercise native Alchemy dev bindings using the exact Pal Pal audio; never emit credentials."""
import hashlib
import json
from pathlib import Path
import time
import subprocess
import os
import urllib.error
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parent.parent
BASE = 'http://localhost:1337'
OPERATOR = next(line.split('=',1)[1] for line in (ROOT/'.env').read_text().splitlines() if line.startswith('STUDIO_OPERATOR_TOKEN='))
WORKSPACE = Path('/Users/aira/Library/Mobile Documents/com~apple~CloudDocs/ai-music/workspaces/pal-pal-nimisham')

def ensure_service_stopped():
    registered=subprocess.run(['launchctl','print','gui/'+str(os.getuid())+'/com.dabbitech.release-kit-studio.worker'],capture_output=True)
    if registered.returncode==0:
        raise RuntimeError('Stop the owned worker service before integration smoke checks so it cannot claim test jobs.')

def call(path, method='GET', body=None, session=None, worker=None, lease=None, extra=None):
    headers={'Origin':BASE}
    if isinstance(body,dict): body=json.dumps(body).encode();headers['Content-Type']='application/json'
    if session: headers['Cookie']=session
    if worker: headers['Authorization']='Bearer '+worker
    if lease: headers['X-Job-Lease']=lease
    if extra: headers.update(extra)
    request=urllib.request.Request(BASE+path,data=body,method=method,headers=headers)
    try:
        with urllib.request.urlopen(request,timeout=120) as response:
            return response.status,json.load(response),response.headers
    except urllib.error.HTTPError as error:
        return error.code,json.load(error),error.headers

def main():
    ensure_service_stopped()
    results={}
    status,invite,_=call('/api/operator/invites','POST',{'tenantName':'Pal Pal production'},worker=OPERATOR)
    assert status==201,(status,invite)
    status,account,headers=call('/api/auth/exchange','POST',{'token':invite['token']})
    assert status==200,(status,account)
    session=headers['Set-Cookie'].split(';',1)[0]
    assert call('/api/auth/exchange','POST',{'token':invite['token']})[0]==401
    results['oneTimeInvitation']=True
    source=WORKSPACE/'pal-pal-telugu-deep-house-remix.wav'
    audio=source.read_bytes()
    sha=hashlib.sha256(audio).hexdigest()
    assert sha=='a5fa914e8f7cae9c76f7ec309ce3a60194d138baa3d2684477f361feeea5c8b3'
    brief={'title':'Pal Pal Nimisham','lyrics':(WORKSPACE/'pal-pal-nimisham-lyrics.txt').read_text().strip(),'language':'Telugu','audioName':source.name,'audioSha256':sha,'audioBytes':len(audio),'audioDuration':239.68,'profile':{'name':'Dhool','identity':'Neon city, memory and longing. Preserve the pink-haired man and woman from the existing Pal Pal anchors. Native Telugu lyric art and music-responsive environments.','palette':'Midnight city','intensity':'Restrained'}}
    status,release,_=call('/api/releases','POST',{'requestKey':str(uuid.uuid4()),'brief':brief},session=session)
    assert status==201,(status,release)
    rid=release['id']
    assert call('/api/releases/'+rid)[0]==401
    status,second,_=call('/api/operator/invites','POST',{'tenantName':'Isolation test'},worker=OPERATOR)
    assert status==201
    status,_,otherheaders=call('/api/auth/exchange','POST',{'token':second['token']})
    assert status==200
    assert call('/api/releases/'+rid,session=otherheaders['Set-Cookie'].split(';',1)[0])[0]==404
    results['tenantIsolation']=True
    status,upload,_=call('/api/releases/'+rid+'/audio','PUT',audio,session=session,extra={'Content-Type':'application/octet-stream','X-Content-Sha256':sha,'X-Upload-Bytes':str(len(audio))})
    assert status==200,(status,upload)
    results['canonicalAudioStoredAndChecksumVerified']=True
    status,start,_=call('/api/releases/'+rid+'/start','POST',{},session=session)
    assert status==202,(status,start)
    status,device,_=call('/api/operator/devices','POST',{'name':'Mac Resolve + Tailscale GPU'},worker=OPERATOR)
    assert status==201,(status,device)
    credentials={'baseUrl':BASE,'token':device['token'],'releaseId':rid,'session':session,'deviceId':device['id']}
    private=ROOT/'.local/http-smoke-worker.json';private.write_text(json.dumps(credentials));private.chmod(0o600)
    results.update({'releaseId':rid,'audioSha256':sha,'audioBytes':len(audio),'queuedJobId':start['job']['id'],'bindingRuntime':'Alchemy native local D1/R2','testedAt':time.time(),'fullKitRendered':False})
    (ROOT/'docs/local-api-receipt.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps(results))

if __name__=='__main__':main()
