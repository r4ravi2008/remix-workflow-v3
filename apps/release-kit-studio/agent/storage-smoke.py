"""Real multipart upload, corruption guard and private storage readback; short footage cannot complete the full release."""
import hashlib
import json
from pathlib import Path
import time
import urllib.request
from http_smoke import call, ROOT, BASE, ensure_service_stopped

def main():
    ensure_service_stopped()
    credentials=json.loads((ROOT/'.local/http-smoke-worker.json').read_text())
    worker=credentials['token']
    status,claim,_=call('/api/worker/claim','POST',{},worker=worker)
    assert status==200 and claim['job'], 'Wait for the earlier local smoke lease to expire before reconciling this job'
    job=claim['job'];jid=job['id'];lease=job['lease']
    source=ROOT/'.local/gpu/P01-a02.mp4';data=source.read_bytes();sha=hashlib.sha256(data).hexdigest()
    status,upload,_=call('/api/worker/jobs/'+jid+'/uploads','POST',{'outputId':'film','bytes':len(data),'sha256':sha,'contentType':'video/mp4'},worker=worker,lease=lease)
    assert status==201,(status,upload)
    aid=upload['assetId'];extra={'X-Job-Id':jid,'X-Upload-Bytes':str(len(data)),'X-Content-Sha256':'0'*64}
    assert call('/api/worker/assets/'+aid+'/parts/1','PUT',data,worker=worker,lease=lease,extra=extra)[0]==409
    extra['X-Content-Sha256']=sha
    status,part,_=call('/api/worker/assets/'+aid+'/parts/1','PUT',data,worker=worker,lease=lease,extra=extra)
    assert status==200,(status,part)
    status,result,_=call('/api/worker/assets/'+aid+'/complete','POST',{},worker=worker,lease=lease,extra={'X-Job-Id':jid})
    assert status==200,(status,result)
    request=urllib.request.Request(BASE+'/api/worker/assets/'+aid,headers={'Authorization':'Bearer '+worker,'X-Job-Lease':lease,'X-Job-Id':jid})
    with urllib.request.urlopen(request,timeout=120) as response:stored=response.read()
    assert hashlib.sha256(stored).hexdigest()==sha and len(stored)==len(data)
    measurement={'width':1024,'height':576,'duration':4.041667,'decoded':True,'sha256':sha,'storageSha256':sha,'composition':'GPU original storage diagnostic; full-release film pending'}
    status,rejection,_=call('/api/worker/jobs/'+jid+'/complete','POST',{'outputs':[{'assetId':aid,'measurement':measurement}],'receipt':{'scope':'storage-smoke'}},worker=worker,lease=lease)
    assert status==409 and 'full song' in rejection['error'],(status,rejection)
    status,hidden,_=call('/api/assets/'+aid,session=credentials['session'])
    assert status==409,(status,hidden)
    claimfile=ROOT/'.local/storage-smoke-claim.json';claimfile.write_text(json.dumps(job));claimfile.chmod(0o600)
    receipt={'runtime':'Alchemy native local R2/D1','jobId':jid,'attempt':job['attempt'],'assetId':aid,'bytes':len(stored),'sha256':sha,'corruptedPartRejected':True,'multipartReadbackVerified':True,'shortFilmRejectedAsFullRelease':True,'unfinishedAssetHiddenFromCustomer':True,'fullKitComplete':False,'testedAt':time.time()}
    (ROOT/'docs/storage-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))

if __name__=='__main__':main()
