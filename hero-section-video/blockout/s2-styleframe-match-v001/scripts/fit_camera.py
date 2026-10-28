"""Read-only static viewpoint study fitting existing ship and live trolley.
Reference correspondences are approximate; no synthetic match score is AC.
"""
import bpy,json,math,random
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(156);cam=s.camera;cn=s.objects['CN_FRAME'].matrix_world;ship=s.objects['A02_SHIP'].matrix_world
points=[(ship@Vector((6.8,0,.75)),(.488,.805)),(ship@Vector((-6.8,0,.75)),(.750,.764)),(ship@Vector((0,2.6,0)),(.615,.839)),(cn@Vector((.75,-1.25,11.8)),(.654,.554))]
def calc(v,record=False):
 px,py,pz,tx,ty=v
 if not(-30<px<50 and 2<py<90 and 10<pz<100 and -30<tx<30 and -50<ty<20):return 1e6
 p=Vector((px,py,pz));t=Vector((tx,ty,3))
 cam.location=cn@p;cam.rotation_quaternion=cn.to_quaternion()@(t-p).to_track_quat('-Z','Y');bpy.context.view_layer.update()
 out=[];err=0
 for world,goal in points:
  q=world_to_camera_view(s,cam,world);got=(q.x,1-q.y);err+=sum((got[i]-goal[i])**2 for i in range(2));out.append({'target':goal,'actual':got})
 return out if record else err
trials=[]
for initial in [[22,47,32,4,-12],[12,27,50,4,-12],[5,38,55,2,-10]]:
 v=initial.copy();best=calc(v)
 for step in [8,4,2,1,.5,.2,.08,.03]:
  for _ in range(120):
   improved=False
   for i in range(5):
    for sign in [-1,1]:
     test=v.copy();test[i]+=sign*step;value=calc(test)
     if value<best:v,best=test,value;improved=True
   if not improved:break
 trials.append({'initial':initial,'position':v[:3],'target':v[3:]+[3],'diagnostic_squared_error':best,'points':calc(v,True)})
(R/'review/camera-fit.json').write_text(json.dumps(trials,indent=2));print(json.dumps(trials,indent=2))
