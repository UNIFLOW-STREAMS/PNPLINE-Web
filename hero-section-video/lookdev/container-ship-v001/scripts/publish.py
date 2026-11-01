import hashlib, json, os, shutil
from pathlib import Path

root=Path(__file__).resolve().parents[1]
master=root.parent/'hero-material-v001/pnpline-hero-material-v001.blend'
version=root/'pnpline-container-ship-v001.blend'
previous=root.parent/'us-warehouse-curvature-v001/pnpline-us-warehouse-curvature-v001.blend'
pointer=root.parent/'latest-lookdev.json'
review=root/'review'
def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

record=json.loads(pointer.read_text())
audit=json.loads((review/'verification.json').read_text())
old=sha(previous);new=sha(version)
assert audit['pass'] and new==audit['result_sha256'] and old==audit['source_sha256']
assert old==sha(master)==record['sha256'] and new!=old
for name in ('before-sailing','after-sailing','after-berth','after-48','after-375'):
    assert (review/(name+'.png')).stat().st_size>20000

prior=root/'previous-latest-lookdev.json'
shutil.copyfile(pointer,prior)
stage=master.with_name('pnpline-hero-material-v001.ship-staged.blend')
assert not stage.exists()
shutil.copyfile(version,stage)
assert sha(stage)==new and sha(master)==old
os.replace(stage,master)
assert sha(master)==new
updated=dict(file=str(master),sha256=new,versioned_copy=str(version),source=str(previous),source_sha256=old,
             review=str(review/'after-berth.png'),before_view=str(review/'before-sailing.png'),
             sailing_view=str(review/'after-sailing.png'),preservation=str(review/'verification.json'),
             delivery=str(root/'delivery.json'),previous_lookdev_record=str(prior),
             fps=30,frame_start=0,frame_end=989,status='Detailed container vessel with double-sided relief wordmark. Original cargo handoffs and camera verified.')
payload=json.dumps(updated,indent=2)
(root/'delivery.json').write_text(payload)
p=pointer.with_suffix('.ship-staged.tmp')
p.write_text(payload);os.replace(p,pointer)
print('MASTER',master,new)
