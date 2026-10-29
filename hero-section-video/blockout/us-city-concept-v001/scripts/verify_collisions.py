"""Evaluated mesh BVH broad/narrow collision audit, separately reports original contacts."""
import bpy,json,sys,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(510);dg=bpy.context.evaluated_depsgraph_get();candidate=Path(bpy.data.filepath)
def shape(objects):
 vs=[];fs=[];names=[]
 for o in objects:
  if o.type not in {'MESH','CURVE'} or o.hide_render:continue
  eo=o.evaluated_get(dg);m=eo.to_mesh()
  if not m:continue
  off=len(vs);vs.extend([eo.matrix_world@v.co for v in m.vertices]);fs.extend([tuple(off+i for i in p.vertices) for p in m.polygons]);names.extend([o.name]*len(m.polygons));eo.to_mesh_clear()
 if not vs:return None
 return {'tree':BVHTree.FromPolygons(vs,fs),'names':names,'lo':Vector(tuple(min(v[i] for v in vs) for i in range(3))),'hi':Vector(tuple(max(v[i] for v in vs) for i in range(3)))}
def overlap(a,b):return all(a['hi'][i]>=b['lo'][i] and b['hi'][i]>=a['lo'][i] for i in range(3))
owned=[o for o in s.objects if o.get('uc_owner')]
zones={z:shape([o for o in owned if o.get('uc_zone')==z]) for z in sorted({o.get('uc_zone') for o in owned})}
root_names=['A02_SHIP','A01_CONTAINER','A03_TRACTOR','A03_TRAILER','A04_PRIMARY','A05_SECONDARY','P02_SPREADER','W01_NEW_PALLET','W01_STORED_PALLET','W02_INBOUND_JACK','W02_STORAGE_JACK','W05_PICK_CART','W09_OUT_CART','W08_LAST_LOAD','W07_OPEN_PACK','W04_PICK_BIN_PRODUCT','CH_PICKER','CH_PACKER','CH_LOADER']
groups={n:[s.objects[n],*s.objects[n].children_recursive] for n in root_names if n in s.objects}
groups['P02_MOVING']=[o for o in s.objects if o.name.startswith('P02_CABLE') or o.name=='P02_TROLLEY']
groups['P02_FIXED']=[o for o in s.objects if o.name.startswith(('P02_LEG','P02_BOOM'))]
groups['WAREHOUSE_FIXED']=[s.objects['E08_WAREHOUSE'],*s.objects['E08_WAREHOUSE'].children_recursive]
hits={};camera_near=[]
frames=sorted(set(range(0,1393))|{b+j/4 for b in [390,421,456,510,532,578,583,600,648,720,776,842,890,900,960,1026,1090,1158,1200,1260] for j in range(-4,5)})
for f in frames:
 s.frame_set(int(f),subframe=f%1);dg=bpy.context.evaluated_depsgraph_get()
 for n,obs in groups.items():
  # Cheap bounds before evaluated-mesh conversion.
  pts=[o.matrix_world@Vector(p) for o in obs if o.type=='MESH' for p in o.bound_box]
  if not pts:continue
  bb={'lo':Vector(tuple(min(v[i] for v in pts) for i in range(3))),'hi':Vector(tuple(max(v[i] for v in pts) for i in range(3)))}
  targets=[(z,st) for z,st in zones.items() if st and overlap(bb,st)]
  if not targets:continue
  dyn=shape(obs)
  if not dyn:continue
  for z,st in targets:
   pairs=dyn['tree'].overlap(st['tree'])
   for a,b in set((dyn['names'][i],st['names'][j]) for i,j in pairs):
    key=a+' | '+b
    if key not in hits:hits[key]={'first':f,'last':f,'samples':0}
    hits[key]['last']=f;hits[key]['samples']+=1
 cam=s.camera.matrix_world.translation
 for z,st in zones.items():
  near=st['tree'].find_nearest(cam) if st else None
  if near and near[0] is not None and near[3]<.35:camera_near.append({'f':f,'zone':z,'distance':near[3]})
 if f%200==0:print('COLLISION_FRAME',f,flush=True)
report={'candidate':str(candidate),'sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'frames':len(frames),'new_mesh_surface_intersections':hits,'camera_near_new_surface':camera_near,'groups':list(groups),'limitations':['Surface BVH detects crossings, not all full containment cases. Broad-phase world bounds precede narrow phase.','No artistic occlusion pass is implied.','Original warehouse contacts are preserved by data/evaluation comparison, separately recorded as baseline defects.']}
(R/'review'/f'{candidate.stem}-collisions.json').write_text(json.dumps(report,indent=2));print('NEW_CONTACT_PAIRS',len(hits),'CAMERA_NEAR',len(camera_near))
assert not hits and not camera_near
