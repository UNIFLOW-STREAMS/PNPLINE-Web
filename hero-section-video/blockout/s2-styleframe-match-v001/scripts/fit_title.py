"""One shared circle; fit projected landmarks, not independent letter depths."""
import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector,Matrix
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));import camera_proposal
camera_proposal.apply();s=bpy.context.scene;s.frame_set(156);dm=s.objects['CN_FRAME'].matrix_world@Matrix.Rotation(math.pi,4,'Z')
cfg=json.loads((R/'title-arc-config.json').read_text());widths=cfg['widths'];total=sum(widths)+cfg['gap']*4;centres=[];cursor=-total/2
for w in widths:centres.append(cursor+w/2);cursor+=w+cfg['gap']
targets=[(525,580,225),(788,615,174),(1010,620,168),(1230,630,187),(1475,650,292)]
def calc(v,record=False):
 mx,my,r,yaw,h,scale=v
 if not(-30<mx<30 and 5<my<70 and 22<r<100 and -65<yaw<45 and 8<h<50 and .65<scale<2.5):return 1e6
 a=math.radians(yaw);err=0;points=[]
 for centre,(x,y,top)in zip(centres,targets):
  angle=centre*scale/r;xx=r*math.sin(angle);yy=r*(math.cos(angle)-1)
  pos=Vector((mx+math.cos(a)*xx-math.sin(a)*yy,my+math.sin(a)*xx+math.cos(a)*yy,1.25))
  q=world_to_camera_view(s,s.camera,dm@pos);qt=world_to_camera_view(s,s.camera,dm@(pos+Vector((0,0,h))))
  actual=[q.x,1-q.y,1-qt.y];goal=[x/2048,y/1156,top/1156]
  err+=sum((a-b)**2*w for a,b,w in zip(actual,goal,[1,.5,1]));points.append({'actual':actual,'target':goal})
 return points if record else err
v=[-5,25,38,-18,25,1.1];best=calc(v)
for steps in [[4,4,8,8,4,.2],[2,2,4,4,2,.1],[.5,.5,1,1,.5,.03],[.1,.1,.2,.2,.1,.008]]:
 for _ in range(100):
  changed=False
  for i in range(6):
   for sign in [-1,1]:
    t=v.copy();t[i]+=steps[i]*sign;e=calc(t)
    if e<best:v,best=t,e;changed=True
  if not changed:break
result={'values':v,'diagnostic_error_not_acceptance':best,'points':calc(v,True)}
(R/'review/title-fit.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
cfg.update({'midpoint':v[:2],'radius':v[2],'yaw_degrees':v[3],'height':v[4],'widths':[w*v[5]for w in widths],'gap':cfg['gap']*v[5]})
(R/'title-arc-config.json').write_text(json.dumps(cfg,indent=2))
