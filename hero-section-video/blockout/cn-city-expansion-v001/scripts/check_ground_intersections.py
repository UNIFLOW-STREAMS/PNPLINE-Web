import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'pnpline-cn-city-expansion-v001.blend'));s=bpy.context.scene;s.frame_set(0);I=s.objects['SF_CN_LAYOUT'].matrix_world.inverted()
def tree(o):
 M=I@o.matrix_world;return BVHTree.FromPolygons([M@v.co for v in o.data.vertices],[tuple(p.vertices)for p in o.data.polygons])
t=tree(s.objects['CNX_CURVED_DISTRICT_LAND']);old=tree(s.objects['SF_FRONT_LAND']);rows=[]
for name in ['SF_CHINA_GOLD_H','SF_CHINA_GOLD_I','CN_QUAY']:
 o=s.objects[name];M=I@o.matrix_world;hits=[]
 for edge in o.data.edges:
  a,b=[M@o.data.vertices[i].co for i in edge.vertices];delta=b-a;length=delta.length
  if length<1e-8:continue
  for start,d in [(a,delta.normalized()),(b,-delta.normalized())]:
   hit,normal,face,dist=t.ray_cast(start,d,length)
   if hit is not None:
    sourcehit=old.ray_cast(Vector((hit.x,hit.y,100)),Vector((0,0,-1)))[0]
    hits.append({'point':list(hit),'old_land_z':sourcehit.z if sourcehit else None})
 rows.append({'name':name,'hit_count':len(hits),'hit_z_range':[min(h['point'][2]for h in hits),max(h['point'][2]for h in hits)]if hits else None,'hits':hits})
(ROOT/'review/ground-intersections.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print(json.dumps([{k:v for k,v in r.items()if k!='hits'}for r in rows]),flush=True)
