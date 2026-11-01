import hashlib,json,os,shutil
from pathlib import Path
r=Path(__file__).resolve().parents[1];ptr=r.parent/'latest-lookdev.json'
def digest(p):
 with open(p,'rb') as fp:return hashlib.file_digest(fp,'sha256').hexdigest()
prev=json.loads((r/'previous-latest-lookdev.json').read_text())
master=Path(prev['file']);out=r/'pnpline-liberty-patina-v001.blend'
assert prev==json.loads(ptr.read_text()) and digest(master)==prev['sha256']==digest(prev['versioned_copy'])
checks=json.loads((r/'review/checks.json').read_text())
assert checks['base_objects']==20 and checks['packed_texture'] and all((r/'review'/n).stat().st_mtime>=out.stat().st_mtime for n in ['front.png','quarter.png','checks.json'])
result=digest(out)
record={**prev,'sha256':result,'versioned_copy':str(out),'source':prev['versioned_copy'],'source_sha256':prev['sha256'],'previous_lookdev_record':str(r/'previous-latest-lookdev.json'),'review':str(r/'review/front.png'),'delivery':str(r/'delivery.json'),'status':'Sculpted Liberty in lithographic verdigris. Original pedestal and island retained.'}
(r/'delivery.json').write_text(json.dumps({'output':str(out),'sha256':result,'reference':'User-supplied New York travel poster; the isolated statue ink colours are packed in the scene. Side and rear are reconstructed.','checks':checks,'renders':['review/front.png','review/quarter.png']},indent=2))
stage=master.with_name('.liberty-patina-stage.blend');newptr=ptr.with_suffix('.liberty-stage.tmp')
assert not stage.exists() and not newptr.exists()
shutil.copyfile(out,stage);newptr.write_text(json.dumps(record,indent=2))
assert digest(stage)==result and digest(master)==prev['sha256'] and json.loads(ptr.read_text())==prev
os.replace(stage,master);os.replace(newptr,ptr)
assert digest(master)==json.loads(ptr.read_text())['sha256']
print('PUBLISHED',master,result)
