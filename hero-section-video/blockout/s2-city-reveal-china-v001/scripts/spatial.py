"""Quarter-frame conservative broadphase; BVH closest camera surface and title intersections."""
import bpy,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(0)
meshes=[o for o in s.objects if o.type=='MESH' and not o.hide_render and not o.hide_viewport and not o.hide_get()]
new=[o for o in meshes if o.get('s2_reveal_owner')];old=[o for o in meshes if not o.get('s2_reveal_owner')]
def bounds(o):
 pts=np.array([tuple(o.matrix_world@Vector(c)) for c in o.bound_box]);return pts.min(0),pts.max(0)
def bvh(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons],all_triangles=False)
def distance(p,box):return np.linalg.norm(np.maximum(np.maximum(box[0]-p,p-box[1]),0))
def animated(o):return o.animation_data is not None or (o.parent is not None and animated(o.parent))
static={o.name:(bounds(o),bvh(o)) for o in meshes if not animated(o)}
title_boxes={o.name:bounds(o) for o in new};title_bvh={o.name:bvh(o) for o in new}
hits=[];candidates=[];min_gap=1e9;title_hits=[];support=[]
for f in np.arange(0,1392.001,.25):
 s.frame_set(int(f),subframe=float(f%1));cam=s.camera.matrix_world.translation.copy();cp=np.array(cam)
 # New title vs all original moving meshes; static pairs checked once.
 for o in old:
  if not animated(o) and f!=0:continue
  box=static[o.name][0] if o.name in static else bounds(o)
  for n,tb in title_boxes.items():
   overlap=np.minimum(box[1],tb[1])-np.maximum(box[0],tb[0])
   if np.min(overlap)<=1e-4:continue
   # Planned foundation contact with the terrace is not an obstruction.
   if n.startswith('CHINA_base_') and o.name=='CN_LAND_TERRACE':continue
   tree=static[o.name][1] if o.name in static else bvh(o)
   if title_bvh[n].overlap(tree):title_hits.append([float(f),n,o.name])
 if not 97<=f<=216:continue
 for o in meshes:
  box=static[o.name][0] if o.name in static else bounds(o)
  gap=distance(cp,box)
  if gap>.5:continue
  tree=static[o.name][1] if o.name in static else bvh(o);co,normal,index,dist=tree.find_nearest(cam)
  if co is None:continue
  min_gap=min(min_gap,dist)
  if dist<.12:hits.append([float(f),o.name,dist])
  # Negative normal dot indicates containment for closed outward oriented meshes.
  if (cam-co).dot(normal)<-.001:candidates.append([float(f),o.name,dist])
cn=s.objects['CN_FRAME'].matrix_world;terrain=s.objects['CN_LAND_TERRACE'];inv=terrain.matrix_world.inverted()
for o in new:
 if not o.get('title_foundation'):continue
 errors=[]
 for v in list(o.data.vertices)[:4]:
  wp=o.matrix_world@v.co;origin=inv@(wp+cn.to_3x3()@Vector((0,0,30)));direction=(inv.to_3x3()@(cn.to_3x3()@Vector((0,0,-1)))).normalized();hit,loc,*_=terrain.ray_cast(origin,direction,distance=60)
  errors.append((terrain.matrix_world@loc-wp).length if hit else None)
 support.append({'object':o.name,'corner_surface_errors_m':errors})
result={'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'quarter_samples':5569,'camera_test_frames':[97,216],'camera_surface_hits':hits,'camera_inside_candidates':candidates,'closest_surface_in_broadphase_m':min_gap if min_gap<1e9 else None,'title_original_intersections':title_hits,'foundation_support':support,'method':'world-space mesh BVH; .12m camera clearance, .5m broadphase. 0.25-frame samples; finite-sample test, not continuous proof. Plinth/terrain intended support contact excepted.'}
result['pass_all']=not hits and not candidates and not title_hits and all(e is not None and e<.001 for r in support for e in r['corner_surface_errors_m'])
(R/'review/spatial.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if not result['pass_all']:raise SystemExit(1)
