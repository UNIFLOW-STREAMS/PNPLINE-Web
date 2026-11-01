import json,hashlib,os,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1]
pointer=R.parent/'latest-lookdev.json'
record=json.loads(pointer.read_text())
master=Path(record['file'])
version=R/'pnpline-white-canopy-v001.blend'
def digest(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
old=record['sha256']
assert old=='e6e08bc82ebfd75c25e241c74f81a8876ae26ba8e5e28748c3da6573ab225ec3' and digest(master)==old
check=json.loads((R/'review/verification.json').read_text())
assert check['pass_all'] and all((R/'review'/(n+'.png')).stat().st_size>20000 for n in ['container-on-ship','waterfront','warehouse-approach'])
backup=R/'source-before-white-canopy.blend'
assert not backup.exists()
shutil.copyfile(master,backup);assert digest(backup)==old
shutil.copyfile(pointer,R/'previous-latest-lookdev.json')
stage=master.with_name('white-canopy-stage.blend')
assert not stage.exists()
shutil.copyfile(version,stage)
new=digest(version);assert digest(stage)==new and digest(master)==old
os.replace(stage,master)
assert digest(master)==new
row=dict(file=str(master),versioned_copy=str(version),sha256=new,source=str(backup),source_sha256=old,previous_lookdev_record=str(R/'previous-latest-lookdev.json'),fps=30,frame_start=0,frame_end=989,review=str(R/'review/waterfront.png'),preservation=str(R/'review/verification.json'),delivery=str(R/'delivery.json'),status='White faceted US and China street planting, light gray working container, white LINE lettering.')
data=json.dumps(row,indent=2);(R/'delivery.json').write_text(data)
tmp=pointer.with_suffix('.canopy.tmp');tmp.write_text(data);os.replace(tmp,pointer)
print(new)
