import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(349);U=s.objects['US_FRAME'];I=U.matrix_world.inverted();deps=bpy.context.evaluated_depsgraph_get()
def us(o):
 while o:
  if o.name=='US_FRAME':return True
  o=o.parent
 return False
def mesh(o):
 ev=o.evaluated_get(deps);me=ev.to_mesh();T=I@ev.matrix_world;v=[T@p.co for p in me.vertices];f=[tuple(p.vertices)for p in me.polygons];ev.to_mesh_clear();return v,f
def bounds(v):return([min(p[i]for p in v)for i in range(3)],[max(p[i]for p in v)for i in range(3)])
def overlap(a,b):return all(a[0][i]<=b[1][i]and b[0][i]<=a[1][i]for i in range(3))
letters=[]
for o in s.objects:
 if o.name.startswith('UST_LETTER_'):
  v,f=mesh(o);letters.append((o.name,bounds(v),BVHTree.FromPolygons(v,f)))
hits={};tested=0
for o in s.objects:
 if o.type not in {'MESH','CURVE','FONT'}or o.hide_render or o.name.startswith('UST_')or not us(o):continue
 if o.name in {'US_LAND_TERRACE','CE_NY_CURVED_LAND'}:continue
 box=bounds([I@o.matrix_world@Vector(v)for v in o.bound_box]);possible=[r for r in letters if overlap(r[1],box)]
 if not possible:continue
 v,f=mesh(o)
 if not f:continue
 bvh=BVHTree.FromPolygons(v,f);tested+=1
 for n,b,t in possible:
  pairs=t.overlap(bvh)
  if pairs:
   root=o
   while root.parent and not any(k in root for k in ['cv_anchor','ce_anchor','usd_anchor']):root=root.parent
   touched=set(i for a,b in pairs for i in f[b]);pts=[v[i]for i in touched]
   hits.setdefault(root.name,[]).append({'letter':n,'object':o.name,'face_pairs':len(pairs),'contact_bounds':bounds(pts)})
report={'file':bpy.data.filepath,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'tested_original_meshes':tested,'collision_roots':hits}
(R/'review/layout-collisions.json').write_text(json.dumps(report,indent=2));print('COLLISIONS',json.dumps(hits),flush=True)
