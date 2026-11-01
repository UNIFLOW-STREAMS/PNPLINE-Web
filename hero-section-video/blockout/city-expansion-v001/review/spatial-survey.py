import bpy,json,math
from mathutils import Vector
from pathlib import Path
s=bpy.context.scene;s.frame_set(700);u=s.objects['US_FRAME'].matrix_world.copy();inv=u.inverted();center=Vector((0,0,-140))
def arc(p):
 n=(p-center).normalized();a=math.acos(max(-1,min(1,n.z)));q=math.hypot(n.x,n.y)
 return [140*a*n.x/q,140*a*n.y/q] if q>1e-8 else [0,0]
def hull(points):
 p=sorted(set(tuple(round(v,3) for v in q) for q in points))
 def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
 low=[]
 for q in p:
  while len(low)>1 and cross(low[-2],low[-1],q)<=0:low.pop()
  low.append(q)
 high=[]
 for q in reversed(p):
  while len(high)>1 and cross(high[-2],high[-1],q)<=0:high.pop()
  high.append(q)
 return low[:-1]+high[:-1]
def row(o,mesh=False):
 m=inv@o.matrix_world;p=m.translation
 r={'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'p':list(p),'arc':arc(p),'props':{k:(v.to_list() if hasattr(v,'to_list') else str(v)) for k,v in o.items()}}
 if mesh and o.type=='MESH':
  points=[m@v.co for v in o.data.vertices];aa=[arc(v) for v in points]
  r['bounds']=[[min(v[k] for v in points) for k in range(3)],[max(v[k] for v in points) for k in range(3)]]
  r['arc_bounds']=[[min(v[k] for v in aa) for k in range(2)],[max(v[k] for v in aa) for k in range(2)]]
  if 'LAND' in o.name or 'ROAD' in o.name or 'ROUTE' in o.name:r['arc_hull']=hull(aa)
 return r
names=['US_LAND_TERRACE','US_QUAY','US_PORT_BACK','US_YARD_ROAD','E07_INBOUND_ROAD','E09_MANEUVER_YARD','E11_ROUTE_1','E11_ROUTE_-1','E08_WAREHOUSE','UC_CITY_DISTRICT','CV_WH_US_FRAME','CV_BRIDGE_US_FRAME','UC_BRIDGE_DECK','UC_PALM_TRUNK_00','UC_PALM_TRUNK_01','UC_PALM_TRUNK_02']
roots=[o for o in s.objects if o.name.startswith('CV_') and (o.name.startswith(('CV_BLOCK','CV_LETTER','CV_CENTRAL','CV_GLASS','CV_CIVIC','CV_BRIDGE','CV_LIBERTY','CV_WH','CV_CRANE','CV_TREE')))]
report={'us_matrix':list(map(list,u)),'count':len(s.objects),'objects':[row(s.objects[n],True) for n in names if n in s.objects],'roots':[row(o) for o in roots],'bridge_objects':[row(o,True) for o in s.objects if o.name.startswith('UC_BRIDGE')],'samples':{}}
for f in [0,75,165,315,375,420,455,467,480,497,504,521,565,600,650,690,750,840,900,989]:
 s.frame_set(f);report['samples'][f]={n:row(s.objects[n]) for n in ['A02_SHIP','A03_TRACTOR','A03_TRAILER','A04_PRIMARY','A05_SECONDARY'] if n in s.objects}
p=Path(__file__).with_name('spatial-survey.json');p.write_text(json.dumps(report,indent=2));print('SURVEY',p);print(json.dumps({k:report[k] for k in ['us_matrix','count','objects']}))
