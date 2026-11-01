import hashlib,json,os,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1]
master=R.parent/'hero-material-v001/pnpline-hero-material-v001.blend'
version=R/'pnpline-us-warehouse-curvature-v001.blend'
before=R/'before.blend';review=R/'review';pointer=R.parent/'latest-lookdev.json'
def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
original=sha(before);new=sha(version)
assert sha(master)==original and original!=new,'Master changed since the source was captured'
verified=json.loads((review/'verification.json').read_text())
tires=json.loads((review/'tire-contact.json').read_text())
assert verified['pass'] and all(max(map(abs,data['result_range']))<.02 for data in tires.values())
assert all((review/f'{when}-{view}.png').stat().st_size>10000 for when in ('before','after') for view in ('side','frontage','outlet','880','989'))
previous=R/'previous-latest-lookdev.json'
shutil.copyfile(pointer,previous)
staged=master.with_name('pnpline-hero-material-v001.warehouse-curvature-staged.blend')
assert not staged.exists()
shutil.copyfile(version,staged)
assert sha(staged)==new and sha(master)==original
os.replace(staged,master)
assert sha(master)==new
record=dict(file=str(master),sha256=new,versioned_copy=str(version),source=str(before),source_sha256=original,
            review=str(review/'after-frontage.png'),before_view=str(review/'before-frontage.png'),preservation=str(review/'verification.json'),
            wheel_contacts=str(review/'tire-contact.json'),delivery=str(R/'delivery.json'),previous_lookdev_record=str(previous),
            fps=30,frame_start=0,frame_end=989,status='US warehouse, approach, dispatch and rear city seated on spherical grade. Native camera and original actions verified.')
(R/'delivery.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
p=pointer.with_suffix('.warehouse-curvature.tmp')
p.write_text(json.dumps(record,indent=2),encoding='utf-8');os.replace(p,pointer)
print(master,new)
