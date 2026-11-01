"""Promote only a verified copy, if the delivery file is still the previous revision."""
import hashlib,json,os,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1]
archive=R.parent/'container-ship-v001/pnpline-container-ship-v001.blend'
candidate=R/'pnpline-fleet-trucks-v001.blend'
master=R.parent/'hero-material-v001/pnpline-hero-material-v001.blend'
pointer=R.parent/'latest-lookdev.json'
review=R/'review'
def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
a=json.loads((review/'verification.json').read_text())
m=json.loads(pointer.read_text())
assert a['pass'] and a['source_sha256']==m['sha256']==sha(master)==sha(archive)
assert a['result_sha256']==sha(candidate)!=a['source_sha256']
for shot in ('after-tractor-left','after-tractor-right','after-617','after-880','after-dispatch','after-yard','before-yard'):
    assert (review/(shot+'.png')).stat().st_size>20000
prior=R/'previous-latest-lookdev.json'
stage=master.with_name('pnpline-hero-material-v001.fleet-staged.blend')
assert not prior.exists() and not stage.exists()
shutil.copyfile(pointer,prior)
shutil.copyfile(candidate,stage)
assert sha(stage)==a['result_sha256'] and sha(master)==a['source_sha256']
os.replace(stage,master)
assert sha(master)==a['result_sha256']
record=dict(file=str(master),sha256=a['result_sha256'],versioned_copy=str(candidate),
            source=str(archive),source_sha256=a['source_sha256'],review=str(review/'after-tractor-left.png'),
            opposite_side=str(review/'after-tractor-right.png'),dispatch=str(review/'after-dispatch.png'),
            camera_loading=str(review/'after-617.png'),camera_dispatch=str(review/'after-880.png'),
            crane_before=str(review/'before-yard.png'),crane_after=str(review/'after-yard.png'),
            preservation=str(review/'verification.json'),delivery=str(R/'delivery.json'),
            previous_lookdev_record=str(prior),fps=30,frame_start=0,frame_end=989,
            status='Three modeled road trucks with double-sided raised PNPLINE wordmarks; two decorative inland USA cranes removed. Camera and logistics motion verified.')
payload=json.dumps(record,indent=2)
(R/'delivery.json').write_text(payload)
p=pointer.with_suffix('.fleet-staged.tmp')
assert not p.exists()
p.write_text(payload)
os.replace(p,pointer)
print('MASTER',master,a['result_sha256'])
