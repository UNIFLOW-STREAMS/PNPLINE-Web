"""Continuous-velocity joins on the accepted ship-side / rear route, with port leveling."""
import argparse,hashlib,json,math,sys
from pathlib import Path
import bpy
from mathutils import Matrix,Vector,Quaternion

R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(a.output).resolve()
assert out.is_relative_to(R) and not out.exists()
source=R.parent/'curvature-rework-v001/candidate-curvature-v004.blend'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='7fdfe45379eab1e3fc53262610dd7872461983bdb590348c1fe7052407278b1a'
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
U=s.objects['US_FRAME'].matrix_world.copy();I=U.inverted();names=['CAM_MASTER','CAM_LOOK_TARGET'];records={}
for tick in range(1756,2697):
 f=tick/4;s.frame_set(int(f),subframe=f%1)
 records[f]={'lens':s.camera.data.lens,**{n:(s.objects[n].matrix_world.copy(),s.objects[n].parent.matrix_world.copy()) for n in names}}

def ease(t):
 t=max(0,min(1,t));return t*t*t*(10+t*(-15+6*t))
def attitude(q):
 front=q@Vector((0,0,-1));right=q@Vector((1,0,0))
 lr=front.cross(Vector((0,0,1))).normalized();lu=lr.cross(front).normalized()
 return math.atan2(front.y,front.x),math.asin(max(-1,min(1,front.z))),math.atan2(right.dot(lu),right.dot(lr))
def oriented(yaw,pitch,roll):
 front=Vector((math.cos(pitch)*math.cos(yaw),math.cos(pitch)*math.sin(yaw),math.sin(pitch)))
 lr=front.cross(Vector((0,0,1))).normalized();lu=lr.cross(front).normalized()
 right=lr*math.cos(roll)+lu*math.sin(roll);up=lu*math.cos(roll)-lr*math.sin(roll)
 return Matrix((right,up,-front)).transposed().to_quaternion()
def angle_lerp(a,b,t):return a+math.atan2(math.sin(b-a),math.cos(b-a))*t

start_eye=I@records[440]['CAM_MASTER'][0].translation
start_aim=I@records[440]['CAM_LOOK_TARGET'][0].translation
end_eye=I@records[672]['CAM_MASTER'][0].translation
end_aim=I@records[672]['CAM_LOOK_TARGET'][0].translation
side_eye=Vector((-10,-32,11));side_aim=Vector((0,1,5))
rear_eye=Vector((-24,13,11));rear_aim=Vector((0,9,5.8))
start_angles=attitude(records[440]['CAM_MASTER'][0].to_quaternion())
end_angles=attitude(records[648]['CAM_MASTER'][0].to_quaternion())

def local_at(n,f):return I@records[f][n][0].translation
def velocity(n,f):return (local_at(n,f+.25)-local_at(n,f-.25))/.5
times=[440,500,596,648,672]
eyes=[start_eye,side_eye,rear_eye,local_at('CAM_MASTER',648),end_eye]
# Keep a small trailing offset while the truck starts moving, instead of
# catching its rear mount too early and braking again before the handoff.
eyes[3].x-=1.0
aims=[start_aim,side_aim,rear_aim,local_at('CAM_LOOK_TARGET',648),end_aim]
def bisect_velocity(a,b,c,speed):
 return ((b-a).normalized()+(c-b).normalized()).normalized()*speed
eye_v=[velocity('CAM_MASTER',440),bisect_velocity(*eyes[:3],.32),bisect_velocity(*eyes[1:4],.20),bisect_velocity(*eyes[2:5],.17),velocity('CAM_MASTER',672)]
aim_v=[velocity('CAM_LOOK_TARGET',440),Vector((0,0,0)),Vector((.08,.06,0)),Vector((.13,.025,-.02)),velocity('CAM_LOOK_TARGET',672)]
def curve(f,points,velocities):
 i=next((i for i in range(len(times)-1) if f<=times[i+1]),len(times)-2)
 dt=times[i+1]-times[i];t=(f-times[i])/dt
 return (2*t**3-3*t*t+1)*points[i]+(t**3-2*t*t+t)*dt*velocities[i]+(-2*t**3+3*t*t)*points[i+1]+(t**3-t*t)*dt*velocities[i+1]
quay=[U@Vector(p) for p in [(-10,4,.4),(10,4,.4)]]
port_up=(U.to_quaternion()@Vector((0,0,1))).normalized()

def pose(f):
 eye=curve(f,eyes,eye_v);aim=curve(f,aims,aim_v)
 eye=U@eye;aim=U@aim;direction=aim-eye
 yaw=math.atan2(direction.y,direction.x);w=ease((f-504)/144)
 q=oriented(yaw,angle_lerp(start_angles[1],end_angles[1],w),angle_lerp(start_angles[2],end_angles[2],w))
 if f>648:
  source_angles=attitude(records[f]['CAM_MASTER'][0].to_quaternion())
  q=oriented(yaw,source_angles[1],source_angles[2])
 local=q.inverted()@(aim-eye);factor=records[f]['lens']/s.camera.data.sensor_width/(-local.z)
 headroom=.04*ease((f-440)/16)*(1-ease((f-456)/44))
 shift=(local.x*factor,local.y*factor+headroom*s.render.resolution_y/s.render.resolution_x)
 weight=ease((f-440)/39)*(1-ease((f-600)/48))
 if weight>0:
  pa,pb=[q.inverted()@(point-eye) for point in quay]
  dx=pb.x/-pb.z-pa.x/-pa.z;dy=pb.y/-pb.z-pa.y/-pa.z
  quay_angle=(math.atan2(dy,dx)+math.pi/2)%math.pi-math.pi/2
  up_angle=-math.atan2(port_up.dot(q@Vector((1,0,0))),port_up.dot(q@Vector((0,1,0))))
  blend=ease((f-512)/40)
  angle=(quay_angle if f<=512 else (quay_angle+(up_angle-quay_angle)*blend if f<552 else up_angle))*weight
  q=q@Quaternion((0,0,1),angle)
  x,y=shift;co,si=math.cos(angle),math.sin(angle);shift=(co*x+si*y,-si*x+co*y)
 return eye,aim,q,shift

frames={}
for n in names:
 o=s.objects[n];basis=o.matrix_basis.copy();inverse=o.matrix_parent_inverse.copy()
 layer=bpy.data.objects.new('CR_REVEAL_'+n,None);s.collection.objects.link(layer)
 layer.parent=o.parent;layer.rotation_mode='QUATERNION';layer['role']='camera_reveal_correction'
 o.parent=layer;o.matrix_basis=basis;o.matrix_parent_inverse=inverse;frames[n]=layer
last={}
for f in [0,439,*[i/4 for i in range(1760,2689)],673,1392]:
 shift=(0.0,0.0)
 if 440<f<672:eye,aim,q,shift=pose(f)
 for n,layer in frames.items():
  correction=Matrix.Identity(4)
  if 440<f<672:
   original,P=records[f][n]
   final=Matrix.LocRotScale(eye if n=='CAM_MASTER' else aim,q if n=='CAM_MASTER' else original.to_quaternion(),original.to_scale())
   correction=P.inverted()@final@original.inverted()@P
  layer.location=correction.translation;layer.rotation_quaternion=correction.to_quaternion()
  if n in last and layer.rotation_quaternion.dot(last[n])<0:layer.rotation_quaternion.negate()
  last[n]=layer.rotation_quaternion.copy()
  layer.keyframe_insert('location',frame=f);layer.keyframe_insert('rotation_quaternion',frame=f)
 for axis,value in zip(('x','y'),shift):
  layer=frames['CAM_MASTER'];layer['lens_shift_'+axis]=value;layer.keyframe_insert('['+json.dumps('lens_shift_'+axis)+']',frame=f)
for axis in ('x','y'):
 driver=s.camera.data.driver_add('shift_'+axis).driver;driver.type='SCRIPTED';driver.expression='offset'
 var=driver.variables.new();var.name='offset';var.type='SINGLE_PROP';var.targets[0].id=frames['CAM_MASTER'];var.targets[0].data_path='['+json.dumps('lens_shift_'+axis)+']'
for layer in frames.values():
 for l in layer.animation_data.action.layers:
  for st in l.strips:
   for bag in st.channelbags:
    for fc in bag.fcurves:
     for key in fc.keyframe_points:key.interpolation='LINEAR'
s.frame_set(497);s['city_reveal_camera']='v013: continuous-velocity joins440/500/596/648/672, port-level roll, no hold or wide orbit'
bpy.ops.wm.save_as_mainfile(filepath=str(out))
info={'source':str(source),'candidate':str(out),'candidate_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'affected_frames':[440,672],'ship_side_by':500,'rear_view_by':596,'pitch_locked':[440,504],'fps':s.render.fps,'eye_path':'short Hermite joins with shared nonzero endpoint velocities; no dwell; original tracking restored672'}
(R/'review'/f'{out.stem}-build.json').write_text(json.dumps(info,indent=2));print(json.dumps(info,indent=2))
