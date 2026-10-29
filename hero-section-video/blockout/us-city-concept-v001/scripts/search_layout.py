"""Read-only broad static-placement search. Frustum is a filter, never art acceptance."""
import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector,Matrix
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(390);U=s.objects['US_FRAME'].matrix_world.copy()
frames=list(range(300,511,3));cams=[]
for f in frames:
 s.frame_set(f);cams.append((f,s.camera.matrix_world.copy(),s.camera.data.lens))
# Cache projection matrix in local US coordinates to evaluate thousands of static placements.
projs=[]
for f,cm,lens in cams:
 s.frame_set(f);p=s.camera.calc_matrix_camera(bpy.context.evaluated_depsgraph_get(),x=960,y=540,scale_x=1,scale_y=1)@cm.normalized().inverted()@U;projs.append((f,p))
def uv(p,v):
 q=p@Vector((*v,1))
 return ((q.x/q.w+1)/2,(q.y/q.w+1)/2,q.w) if q.w>0 else (-9,-9,-1)
def longest(vals):
 best=[];run=[]
 for f,ok in vals:
  if ok:run.append(f)
  else:
   if len(run)>len(best):best=run
   run=[]
 return run if len(run)>len(best) else best
statues=[];height=float(sys.argv[-1]) if '--height' in sys.argv else 10.836
print('PROJECTION_SANITY',list(world_to_camera_view(s,s.camera,U@Vector((-65,9,-10)))),uv(projs[-1][1],(-65,9,-10)))
for x in range(-90,-14,3):
 for y in list(range(-44,-5,3))+list(range(8,48,3)):
  if x>-35 and y>0:continue
  z=math.sqrt(140**2-x*x-y*y)-140
  pts=[(x+dx,y+dy,z+zz) for dx,dy,zz in [(-1.9,0,2.65+height),(1,0,2.65+height*.75),(0,0,2.65),(0,0,.4)]]
  vals=[];sizes=[]
  for f,p in projs:
   v=[uv(p,q) for q in pts];ok=all(.06<a<.94 and .06<b<.94 and c>0 for a,b,c in v);size=max(q[1] for q in v)-min(q[1] for q in v)
   vals.append((f,ok and size>.08));sizes.append(size)
  run=longest(vals)
  if run:statues.append({'position':[x,y,z],'frames':[run[0],run[-1]],'duration':(run[-1]-run[0]+3)/12,'size_mid':sizes[frames.index(run[len(run)//2])]})
statues.sort(key=lambda a:(a['duration'],a['size_mid']),reverse=True)
# Whole-district rotations; constrain building footprint to land behind active port.
district=[];tried=0
for yaw in range(-75,46,15):
 rot=Matrix.Rotation(math.radians(yaw),4,'Z')
 for dx in range(-15,46,5):
  for dy in range(-10,16,5):
   tried+=1;trans=Vector((dx,37+dy,0))-rot@Vector((0,37,0))
   bbox=[rot@Vector((x,y,.7))+trans for x,y in [(-27,24),(22,24),(-27,55),(22,55),(22,34),(35,40),(22,48),(36,48)]]
   valid=all(-31<=v.x<=119 and 22<=v.y<=64 and not (34<v.x<83 and v.y<40) for v in bbox)
   if not valid:continue
   title=[rot@Vector((x,53,z))+trans for x in [-24,22] for z in [1,19]]
   vals=[]
   for f,p in projs:
    ps=[uv(p,v) for v in title];vals.append((f,all(.03<a<.97 and .03<b<.97 and c>0 for a,b,c in ps)))
   run=longest(vals)
   district.append({'yaw':yaw,'translation':list(trans),'duration':(run[-1]-run[0]+3)/12 if run else 0,'frames':[run[0],run[-1]] if run else None})
district.sort(key=lambda a:a['duration'],reverse=True)
report={'body_height':height,'statue_candidates_tested':len(range(-90,-14,3))*(len(range(-44,-5,3))+len(range(8,48,3))),'statue_top':statues[:30],'near_port_candidates':[v for v in statues if v['position'][0]>=-65],'district_candidates_tested':tried,'district_allowed':district,'caveat':'Frustum-only feasibility; full 3D mesh visibility, ground connection and motion review still required. City land bounds conservative around operating warehouse.'}
(R/'review'/f'static-layout-search-{height:.3f}.json').write_text(json.dumps(report,indent=2));print(json.dumps({'statue_top':statues[:5],'near_port_candidates':report['near_port_candidates'][:5],'district_allowed':district[:6]}))
