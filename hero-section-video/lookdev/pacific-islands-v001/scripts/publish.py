import hashlib,json,os,shutil
from pathlib import Path
r=Path(__file__).resolve().parents[1];ptr=r.parent/'latest-lookdev.json'
def digest(p):
 with open(p,'rb') as fp:return hashlib.file_digest(fp,'sha256').hexdigest()
prev=json.loads((r/'previous-latest-lookdev.json').read_text())
master=Path(prev['file']);out=r/'pnpline-pacific-islands-v001.blend'
assert prev==json.loads(ptr.read_text()) and digest(master)==prev['sha256']==digest(prev['versioned_copy'])
checks=json.loads((r/'review/checks.json').read_text())
shots=[r/'review'/f'crossing-{k}.png' for k in [201,225,245]]
assert checks['terrain_count']==7 and checks['minimum_clearance_lower_bound']>0 and all(p.stat().st_size>50000 and p.stat().st_mtime>=out.stat().st_mtime for p in shots)
result=digest(out)
record={**prev,'sha256':result,'versioned_copy':str(out),'source':prev['versioned_copy'],'source_sha256':prev['sha256'],'previous_lookdev_record':str(r/'previous-latest-lookdev.json'),'review':str(shots[1]),'delivery':str(r/'delivery.json'),'status':'Seven curved Pacific islands and skerries in the China to USA camera crossing; gold SHIP_ROUTE removed.'}
(r/'delivery.json').write_text(json.dumps(dict(output=str(out),sha256=result,checks=checks,frames=[str(p) for p in shots]),indent=2))
stage=master.with_name('.pacific-stage.blend');newptr=ptr.with_suffix('.pacific-stage.tmp')
assert not stage.exists() and not newptr.exists()
shutil.copyfile(out,stage);newptr.write_text(json.dumps(record,indent=2))
assert digest(stage)==result and digest(master)==prev['sha256'] and json.loads(ptr.read_text())==prev
os.replace(stage,master);os.replace(newptr,ptr)
assert digest(master)==json.loads(ptr.read_text())['sha256']
print('PUBLISHED',master,result)

