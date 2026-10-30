"""Arrive at the ship side before504, then use a direct path to the truck rear."""
import argparse,hashlib,json,math,sys
from pathlib import Path
import bpy
from mathutils import Matrix,Vector

R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(a.output).resolve()
assert out.is_relative_to(R) and not out.exists()
source=R.parent/'curvature-rework-v001/candidate-curvature-v004.blend'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='7fdfe45379eab1e3fc53262610dd7872461983bdb590348c1fe7052407278b1a'
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
U=s.objects['US_FRAME'].matrix_world.copy();I=U.inverted();names=['CAM_MASTER','CAM_LOOK_TARGET'];records={}
for f in range(440,649):
 s.frame_set(f)
 records[f]={'lens':s.camera.data.lens,**{n:(s.objects[n].matrix_world.copy(),s.objects[n].parent.matrix_world.copy()) for n in names}}

def ease(t):
 t=max(0,min(1,t));return t*t*t*(10+t*(-15+6*t))
def travel_ease(t):
 # A lower peak speed prevents the perspective yaw from accelerating at mid-path.
 t=max(0,min(1,t));return t*t*(3-2*t)
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
end_eye=I@records[648]['CAM_MASTER'][0].translation
end_aim=I@records[648]['CAM_LOOK_TARGET'][0].translation
side_eye=Vector((-10,-32,11));side_aim=Vector((0,1,5))
rear_eye=Vector((-24,13,11));rear_aim=Vector((0,9,5.8))
start_angles=attitude(records[440]['CAM_MASTER'][0].to_quaternion())
end_angles=attitude(records[648]['CAM_MASTER'][0].to_quaternion())

def pose(f):
 if f<=500:
  eye=start_eye.lerp(side_eye,ease((f-440)/60))
  aim=start_aim.lerp(side_aim,ease((f-456)/44))
 elif f<=504:eye=side_eye;aim=side_aim
 elif f<=596:
  w=travel_ease((f-504)/92);eye=side_eye.lerp(rear_eye,w);aim=side_aim.lerp(rear_aim,w)
 else:
  w=ease((f-596)/52);eye=rear_eye.lerp(end_eye,w);aim=rear_aim.lerp(end_aim,w)
 eye=U@eye;aim=U@aim;direction=aim-eye
 yaw=math.atan2(direction.y,direction.x);w=ease((f-504)/144)
 q=oriented(yaw,angle_lerp(start_angles[1],end_angles[1],w),angle_lerp(start_angles[2],end_angles[2],w))
 local=q.inverted()@(aim-eye);factor=records[f]['lens']/s.camera.data.sensor_width/(-local.z)
 headroom=.04*ease((f-440)/16)*(1-ease((f-456)/44))
 shift=(local.x*factor,local.y*factor+headroom*s.render.resolution_y/s.render.resolution_x)
 return eye,aim,q,shift

frames={}
for n in names:
 o=s.objects[n];basis=o.matrix_basis.copy();inverse=o.matrix_parent_inverse.copy()
 layer=bpy.data.objects.new('CR_REVEAL_'+n,None);s.collection.objects.link(layer)
 layer.parent=o.parent;layer.rotation_mode='QUATERNION';layer['role']='camera_reveal_correction'
 o.parent=layer;o.matrix_basis=basis;o.matrix_parent_inverse=inverse;frames[n]=layer
last={}
for f in [0,439,*range(440,649),649,1392]:
 shift=(0.0,0.0)
 if 440<f<648:eye,aim,q,shift=pose(f)
 for n,layer in frames.items():
  correction=Matrix.Identity(4)
  if 440<f<648:
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
s.frame_set(500);s['city_reveal_camera']='v008: direct ship-side arrival500, rear approach504-596, rear tracking596-648; no orbit'
bpy.ops.wm.save_as_mainfile(filepath=str(out))
info={'source':str(source),'candidate':str(out),'candidate_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'affected_frames':[440,648],'ship_side_by':500,'rear_approach_starts':504,'rear_view_by':596,'pitch_roll_locked':[440,504],'fps':s.render.fps,'eye_path':'three straight segments with eased time, no orbit'}
(R/'review'/f'{out.stem}-build.json').write_text(json.dumps(info,indent=2));print(json.dumps(info,indent=2))
