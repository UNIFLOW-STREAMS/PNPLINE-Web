import bpy,json,hashlib,numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1];B=R.parents[1]/'blockout/full-layout-master-v001';src=R/'master/source-current.blend';prop=R/'layout-proposal-v001/s4-s5-layout-proposal-v001.blend';dst=B/'master-full-layout-v001.blend';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def get(path,frames,names,space):
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;out=[]
 for f in frames:
  s.frame_set(int(f),subframe=float(f%1));I=s.objects['US_FRAME'].matrix_world.inverted() if space=='US' else None
  out.append([list(map(list,I@s.objects[n].matrix_world if I else s.objects[n].matrix_world)) for n in names]+[[[s.camera.data.lens,0,0,0]]*4])
 return np.array(out,dtype=np.float32)
bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene
protected={'CN_FRAME','EARTH_CONTINUOUS_OCEAN','CAM_MASTER','CAM_LOOK_TARGET'}
for n in ['CN_FRAME','P01_SPREADER','A02_SHIP','A01_CONTAINER','W01_NEW_PALLET']:
 protected.add(n);protected.update(o.name for o in s.objects[n].children_recursive)
protected.update(n for n in s.objects.keys() if n.startswith('P01_CABLE_'));protected=sorted(protected)
early=np.arange(0,216.01,.25);a=get(src,early,protected,'world');b=get(dst,early,protected,'world');earlyerr=float(np.max(np.abs(a-b)));assert earlyerr<.0002,('CN opening changed',earlyerr)
rec=json.loads((R/'layout-proposal-v001/build-record.json').read_text());names=set(rec['flattened_environment']+rec['animated_roots']+['CAM_MASTER','CAM_LOOK_TARGET']);s=bpy.context.scene
for n in rec['animated_roots']:names.update(o.name for o in s.objects[n].children_recursive)
names=sorted(names);middle=np.arange(552,948.01,.25);a=get(prop,middle,names,'US');b=get(dst,middle,names,'US');miderr=float(np.max(np.abs(a-b)));assert miderr<.0003,('Approved proposal changed locally',miderr)
def meshes(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;out={}
 for n in ['A03_TRACTOR','A03_TRAILER','A01_CONTAINER']:
  for o in s.objects[n].children_recursive:
   if o.type=='MESH':out[o.name]=sha_mesh(o)
 return out
def sha_mesh(o):return hashlib.sha256(repr(([tuple(v.co) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])).encode()).hexdigest()
assert meshes(src)==meshes(dst),'Vehicle/container geometry modified'
original=R.parents[1]/'blockout/s5-integration-v001/master-s5-integration-v001.blend';assert sha(original)==sha(src)=='8c76f0e184bc742309cf66dcf9f3f5fa7072e02b54b58e6985a91ff1ae57b665'
out={'pass':True,'master_sha256':sha(dst),'source_sha256':sha(src),'proposal_sha256':sha(prop),'opening_preservation':{'range':[0,216],'step':.25,'objects':len(protected),'matrix_lens_max_error':earlyerr},'adopted_proposal_preservation':{'range':[552,948],'step':.25,'objects':len(names),'space':'US_FRAME local, allowing the common spherical geographic placement','matrix_lens_max_error':miderr},'vehicle_container_meshes_equal':True,'original_file_unchanged':True}
(B/'review/preservation.json').write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out))
