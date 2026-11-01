import hashlib,json,os,shutil
from pathlib import Path
r=Path(__file__).resolve().parents[1];ptr=r.parent/'latest-lookdev.json'
def digest(p):
 with open(p,'rb') as fp:return hashlib.file_digest(fp,'sha256').hexdigest()
prev=json.loads((r/'previous-latest-lookdev.json').read_text())
master=Path(prev['file']);out=r/'pnpline-ocean-foam-v001.blend'
assert prev==json.loads(ptr.read_text()) and digest(master)==prev['sha256']==digest(prev['versioned_copy'])
checks=json.loads((r/'review/checks.json').read_text())
files=[r/'review'/f'ocean-{k}.png' for k in [201,225,245]]+[r/'review/crossing-30fps.mp4']
assert checks['packed_maps']==4 and all(p.stat().st_size>20000 and p.stat().st_mtime>=out.stat().st_mtime for p in files)
result=digest(out)
record={**prev,'sha256':result,'versioned_copy':str(out),'source':prev['versioned_copy'],'source_sha256':prev['sha256'],'previous_lookdev_record':str(r/'previous-latest-lookdev.json'),'review':str(files[1]),'delivery':str(r/'delivery.json'),'status':'Stylized Pacific water with island shelves, travelling ripples, speed-driven foam and a continuous grazing-angle sky reflection.'}
(r/'delivery.json').write_text(json.dumps(dict(output=str(out),sha256=result,checks=checks,review=[str(p) for p in files],maps=[p.name for p in (r/'resources').iterdir()],coordinates='Spherical metre chart. Linear packed data textures; no external runtime dependencies for the new material.',wake='R aerated water, G foam lace, B crest height. Track EXR encodes stern distance, lateral coordinate and steering. Baked progress keys must be regenerated if vessel motion changes.'),indent=2))
stage=master.with_name('.sea-foam-stage.blend');newptr=ptr.with_suffix('.sea-foam-stage.tmp')
assert not stage.exists() and not newptr.exists()
shutil.copyfile(out,stage);newptr.write_text(json.dumps(record,indent=2))
assert digest(stage)==result and digest(master)==prev['sha256'] and json.loads(ptr.read_text())==prev
os.replace(stage,master);os.replace(newptr,ptr)
assert digest(master)==json.loads(ptr.read_text())['sha256']
print('PUBLISHED',master,result)

