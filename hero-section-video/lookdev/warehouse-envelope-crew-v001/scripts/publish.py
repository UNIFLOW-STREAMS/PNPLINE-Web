"""Promote a verified scene only if the project pointer and original archive still agree."""
import json,os,shutil,hashlib
from pathlib import Path
r=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text())
def digest(p):
 with open(p,'rb') as fp:return hashlib.file_digest(fp,'sha256').hexdigest()
ptr=r.parent/'latest-lookdev.json';prev=read(r/'previous-latest-lookdev.json');rep=read(r/'review/build.json')
v=read(r/'review/verification.json');master=Path(prev['file']);out=Path(rep['output'])
assert read(ptr)==prev and digest(master)==prev['sha256']==rep['sha_source']==digest(prev['versioned_copy'])
assert digest(out)==rep['sha_result'] and v['checked_sha256']==rep['sha_result']
assert v['maximum_glove_endpoint_error']<.002 and v['max_world_matrix_difference']==0 and v['all_original_actions_match'] and v['camera_optics_equal'] and v['markers_equal'] and all(x['unexpected']==0 for x in v['envelope'].values())
shots=['exterior.png','receiving.png','crew-maquettes.png','cam-760.png','cam-801.png','cam-841.png']
for n in shots:
 p=r/'review'/n
 assert p.stat().st_size>20000 and p.stat().st_mtime>=out.stat().st_mtime
d=dict(version='warehouse-envelope-crew-v001',source=prev['versioned_copy'],source_sha256=rep['sha_source'],output=str(out),sha256=rep['sha_result'],render_proofs=shots,verification=v,people=['Picking: RF scanner','Packing: tape dispenser','Loading: animated carrier contact'],envelope='Radially fit standing seam panels, two sealed daylight bands, graphite cladding, continuous low-iron viewing wall and open receiving / dispatch doorways.')
(r/'delivery.json').write_text(json.dumps(d,indent=2))
upd={**prev,'versioned_copy':str(out),'source':prev['versioned_copy'],'source_sha256':rep['sha_source'],'sha256':rep['sha_result'],'previous_lookdev_record':str(r/'previous-latest-lookdev.json'),'delivery':str(r/'delivery.json'),'review':str(r/'review/exterior.png'),'status':'US warehouse fully roofed and enclosed except for both loading portals. All three worker proxies replaced by PNPLINE scale figures.'}
stage=master.with_name('.warehouse-crew-stage.blend');tp=ptr.with_suffix('.warehouse-crew-stage.tmp')
assert not stage.exists() and not tp.exists()
shutil.copyfile(out,stage);tp.write_text(json.dumps(upd,indent=2))
assert digest(stage)==rep['sha_result'] and digest(master)==prev['sha256'] and read(ptr)==prev
os.replace(stage,master);os.replace(tp,ptr)
assert digest(master)==read(ptr)['sha256']
print('PUBLISHED',master,upd['sha256'])

