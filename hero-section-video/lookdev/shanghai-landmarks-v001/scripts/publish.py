import hashlib,json,os,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];ptr=R.parent/'latest-lookdev.json'
def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
prev=json.loads((R/'previous-latest-lookdev.json').read_text())
master=Path(prev['file']);out=R/'pnpline-shanghai-landmarks-v001.blend'
assert json.loads(ptr.read_text())==prev
assert sha(master)==prev['sha256']==sha(prev['versioned_copy'])
checks=json.loads((R/'review/checks.json').read_text())
images=[R/'review'/f'{label}-{name}.png' for label in ['before','after'] for name in ['skyline','landmarks','camera-0057']]
assert all(p.exists() and p.stat().st_size>10000 for p in images)
result=sha(out)
delivery=dict(file=str(out),sha256=result,source=prev['versioned_copy'],checks=checks,review=[str(p) for p in images],renderer='Cycles / OPTIX, 32 samples, denoised; saved production settings unchanged',changes=['SWFC tapered glass body and integrated small trapezoidal aperture','Jin Mao octagonal setbacks, facade-conforming glazing and layered crown','Oriental Pearl enlarged uniformly 1.35x about existing ground anchor'],preserved='Other 26680 object transforms/data references/render visibility, existing animation actions, camera, timeline, ocean and logistics assets')
(R/'delivery.json').write_text(json.dumps(delivery,indent=2))
record={**prev,'versioned_copy':str(out),'sha256':result,'source':prev['versioned_copy'],'source_sha256':prev['sha256'],'previous_lookdev_record':str(R/'previous-latest-lookdev.json'),'review':str(R/'review/after-skyline.png'),'delivery':str(R/'delivery.json'),'status':'Shanghai SWFC and Jin Mao rebuilt with integrated facades. Oriental Pearl enlarged 35 percent. Reviewed in Cycles, existing camera and animation preserved.'}
stage=master.with_name('.shanghai-landmarks-stage.blend');stageptr=ptr.with_suffix('.shanghai-landmarks-stage.tmp')
assert not stage.exists() and not stageptr.exists()
shutil.copyfile(out,stage);stageptr.write_text(json.dumps(record,indent=2))
assert sha(stage)==result and sha(master)==prev['sha256']
os.replace(stage,master);os.replace(stageptr,ptr)
assert sha(master)==json.loads(ptr.read_text())['sha256']
print('PUBLISHED',master,result)
