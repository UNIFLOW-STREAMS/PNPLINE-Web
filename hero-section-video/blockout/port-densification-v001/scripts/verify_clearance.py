"""Triangle intersections against new solid scenery, per output frame; read-only."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];source=Path(bpy.data.filepath);s=bpy.context.scene;s.frame_set(349);I=s.objects['US_FRAME'].matrix_world.inverted()
def owned(o):return o.get('pt_owner')=='port-densification-v001'
solids=[o for o in s.objects if o.type=='MESH' and owned(o) and o.get('pt_role') in ['container','crane','quay_fixture']]
vertices=[];faces=[];names=[]
for o in solids:
 T=I@o.matrix_world;n=len(vertices);vertices.extend(T@v.co for v in o.data.vertices)
 faces.extend(tuple(i+n for i in p.vertices) for p in o.data.polygons);names.extend([o.name]*len(o.data.polygons))
static=BVHTree.FromPolygons(vertices,faces)
roots={'A02_SHIP','A01_CONTAINER','A03_TRACTOR','A03_TRAILER','A04_PRIMARY','A05_SECONDARY','P02_SPREADER','W01_NEW_PALLET','W08_LAST_LOAD'}
def moving_root(o):
 if o.name.startswith('P02_CABLE') or o.name=='P02_TROLLEY':return 'P02_MOVING'
 p=o
 while p:
  if p.name in roots:return p.name
  p=p.parent
 return None
moving=[(o,moving_root(o)) for o in s.objects if o.type=='MESH' and moving_root(o) and not owned(o)]
errors={};queries=0;camera_hits=[]
for f in range(990):
 s.frame_set(f);dep=bpy.context.evaluated_depsgraph_get()
 for o,root in moving:
  ev=o.evaluated_get(dep)
  if ev.hide_render:continue
  T=I@ev.matrix_world;bb=[T@Vector(v) for v in ev.bound_box]
  lo=[min(p[i] for p in bb) for i in range(3)];hi=[max(p[i] for p in bb) for i in range(3)]
  if any(hi[i]<[-27,-7,-6][i] or lo[i]>[24,20,17][i] for i in range(3)):continue
  me=ev.to_mesh();vs=[T@v.co for v in me.vertices];fs=[p.vertices[:] for p in me.polygons]
  if fs:
   tree=BVHTree.FromPolygons(vs,fs);hits=static.overlap(tree);queries+=1
   for left,right in hits:
    key=(o.name,names[left]);errors.setdefault(key,[])
    if not errors[key] or errors[key][-1]!=f:errors[key].append(f)
  ev.to_mesh_clear()
 cam=I@s.camera.matrix_world.translation;near=static.find_nearest(cam)
 if near and near[0] is not None and near[3]<.15:camera_hits.append([f,names[near[2]],near[3]])
 if f%100==0:print('AUDIT',f,'pairs',len(errors),flush=True)
report={'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'frames':990,'moving_mesh_count':len(moving),'new_solid_mesh_count':len(solids),'triangle_queries':queries,
 'intersections':[{'moving':a,'new_scenery':b,'frames':fs} for (a,b),fs in errors.items()], 'camera_surface_proximity_under_0_15':camera_hits,
 'passed':not errors and not camera_hits,'scope':'Triangle-surface intersections at all 990 output frames. Foundations and painted markings are excluded as intended contact surfaces.'}
(R/'review/clearance.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='intersections'},indent=2))
assert report['passed'],'New port scenery intersects moving scene content; see clearance.json'
