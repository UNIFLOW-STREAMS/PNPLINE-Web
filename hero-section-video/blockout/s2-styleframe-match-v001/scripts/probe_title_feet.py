import bpy,sys,json
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(156);inv=s.objects['SF_CN_LAYOUT'].matrix_world.inverted()
def inside(p,poly):
 hit=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a.y>p.y)!=(b.y>p.y)and p.x<(b.x-a.x)*(p.y-a.y)/(b.y-a.y)+a.x:hit=not hit
 return hit
w=s.objects['SF_BASIN_WATER_SURFACE'];ps=[inv@w.matrix_world@v.co for v in w.data.vertices];outer=ps[:96];inner=ps[96:]
for ch in 'CHINA':
 o=s.objects['SF_CHINA_GOLD_'+ch];vs=[inv@o.matrix_world@v.co for v in o.data.vertices];z=min(v.z for v in vs);feet=[v for v in vs if v.z<z+.15]
 flooded=[list(v)for v in feet if inside(v,outer)and not inside(v,inner)]
 print(ch,len(feet),'wet',flooded)
