import bpy,sys,collections,math
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(225);dg=bpy.context.evaluated_depsgraph_get()
for o in s.objects:
 if not(o.name.startswith('Pacific |') and 'shoreline' in o.name):continue
 hits=collections.Counter()
 for v in list(o.data.vertices)[::3]:
  p=v.co;n=p.normalized();origin=n*170
  for k in range(12):
   ok,hit,_,_,ob,_=s.ray_cast(dg,origin,-n)
   if not ok or ob.name=='EARTH_CONTINUOUS_OCEAN':break
   if not ob.name.startswith('Pacific |') and not ob.hide_render:
    hits[ob.name]+=1;break
   origin=hit-.015*n
 print(o.name,hits.most_common(6))

