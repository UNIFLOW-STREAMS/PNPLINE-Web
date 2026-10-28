"""Finite-sample conservative collision screening and visible surface samples.
Projected points are not visible area; ray hits and on-screen counts are separate.
"""
import bpy,sys,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(0)
inv=s.objects['CN_FRAME'].matrix_world.inverted()
owned=[o for o in s.objects if o.type=='MESH' and o.get('cn_proxy_owner')]
def bounds(o):
 p=np.array([inv@o.matrix_world@Vector(v) for v in o.bound_box]);return p.min(axis=0),p.max(axis=0)
nb=[bounds(o) for o in owned];low=np.array([b[0] for b in nb]);high=np.array([b[1] for b in nb])
def moving(o):return bool(o.animation_data) or (o.parent is not None and moving(o.parent))
actors=[o for o in s.objects if o.type=='MESH' and (moving(o) or o.name.startswith('P01')) and not o.get('cn_proxy_owner')]
collisions=[];camera_hits=[];min_camera_clearance=1e9;min_actor_clearance=1e9
for f in np.arange(0,1392.001,.25):
 s.frame_set(int(f),subframe=float(f%1));p=np.array(inv@s.camera.matrix_world.translation)
 gaps=np.maximum(np.maximum(low-p,p-high),0);dist=np.linalg.norm(gaps,axis=1);min_camera_clearance=min(min_camera_clearance,float(dist.min()))
 for i in np.flatnonzero(dist<.12):camera_hits.append([float(f),owned[i].name,float(dist[i])])
 for o in actors:
  a,b=bounds(o);gap=np.maximum(np.maximum(low-b,a-high),0);dist=np.linalg.norm(gap,axis=1);min_actor_clearance=min(min_actor_clearance,float(dist.min()))
  for i in np.flatnonzero(np.all(np.minimum(high,b)-np.maximum(low,a)>.001,axis=1)):
   collisions.append([float(f),o.name,owned[i].name])
collision={'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'samples':5569,'frame_step':.25,'camera_clearance_lower_bound':min_camera_clearance,'actor_clearance_lower_bound':min_actor_clearance,'camera_hits':camera_hits,'aabb_overlap_candidates':collisions,'actor_count':len(actors),'method':'CN-space AABB screening of each actual mesh envelope; disjoint envelopes prove separation at sampled poses only. Camera radius .12. No continuous collision claim.'}
(R/'review/collisions.json').write_text(json.dumps(collision,indent=2));print('COLLISION',len(camera_hits),len(collisions),flush=True)
def rendered(o):return not o.hide_render and not o.hide_get() and not any(c.hide_render for c in o.users_collection)
def group(o):
 while o.parent and o.parent.name!='CN_PROXY_ROOT':o=o.parent
 return o.name
sampled={}
frames=sorted(set(range(96,217,2))|{124,148,180,216}|set(range(220,333,4))|{450,456})
for f in frames:
 s.frame_set(f);dg=bpy.context.evaluated_depsgraph_get();verts=[];polys=[];owners=[];samples=[]
 for o in s.objects:
  if o.type!='MESH' or not rendered(o):continue
  eo=o.evaluated_get(dg);m=eo.to_mesh();m.calc_loop_triangles();offset=len(verts);vs=[eo.matrix_world@v.co for v in m.vertices];verts.extend(vs)
  for tri in m.loop_triangles:polys.append(tuple(offset+i for i in tri.vertices));owners.append(o.name)
  if o in owned and not o.get('cn_foundation'):
   # Surface centroid samples, evenly spread across polygons, independent of AABB.
   stride=max(1,len(m.polygons)//14)
   for face in list(m.polygons)[::stride]:samples.append((o.name,group(o),eo.matrix_world@face.center))
  eo.to_mesh_clear()
 tree=BVHTree.FromPolygons(verts,polys,all_triangles=True);row={};origin=s.camera.matrix_world.translation
 for n,g,pt in samples:
  r=row.setdefault(g,{'samples':0,'in_frame':0,'visible':0,'occluders':{}});r['samples']+=1
  p=world_to_camera_view(s,s.camera,pt)
  if p.z<=0 or not(0<=p.x<=1 and 0<=p.y<=1):continue
  r['in_frame']+=1;direction=pt-origin;length=direction.length
  hit,normal,idx,d=tree.ray_cast(origin,direction.normalized(),length+.01)
  if idx is not None and owners[idx]==n:r['visible']+=1
  elif idx is not None:r['occluders'][owners[idx]]=r['occluders'].get(owners[idx],0)+1
 sampled[f]=row
(R/'review/visibility.json').write_text(json.dumps({'sha256':collision['sha256'],'frames':sampled,'method':'Actual visible polygon-centroid ray samples. Counts do not estimate screen area, nor establish aesthetic acceptance.'},indent=2));print('VISIBILITY',len(sampled),flush=True)
if camera_hits or collisions:raise SystemExit(1)
