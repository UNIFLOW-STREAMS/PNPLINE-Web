import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from survey import *
s.frame_set(225)
for u in [.25,.28,.33,.77]:
 low,high=.55,1.0
 for i in range(20):
  v=(low+high)/2
  if hit(u,v) is not None:low=v
  else:high=v
 for dv in [.015,.005,.001]:
  p=hit(u,low-dv);print('HORIZON',u,round(low,4),dv,xyz(p))
dg=bpy.context.evaluated_depsgraph_get()
for x in [-92,-89,-86,-83,-80]:
 for y in [5,9,15,22]:
  p=Vector((x,y,(140**2-x*x-y*y)**.5));n=p.normalized()
  ok,_,_,_,ob,_=s.ray_cast(dg,n*165,-n);print('GROUND',x,y,ob.name if ok else '-')
