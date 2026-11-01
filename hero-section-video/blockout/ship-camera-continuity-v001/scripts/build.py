"""Ship-relative arrival camera: no independent lead, dwell, or catch-up."""
import bpy, hashlib, json, math
from pathlib import Path
from mathutils import Matrix, Vector

R=Path(__file__).resolve().parents[1];cfg=json.loads((R/'config.json').read_text())
source=(R/cfg['source']).resolve();out=R/cfg['output']
assert hashlib.sha256(source.read_bytes()).hexdigest()==cfg['source_sha256']
assert not out.exists()
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;cam=s.camera;ship=s.objects['A02_SHIP'];parent=cam.parent

def ease(t):
 t=max(0,min(1,t));return t*t*t*(10+t*(-15+6*t))

def pose(f,old,M):
 # One authored mount in the moving ship frame. Its longitudinal offset never
 # passes the ship; the camera continues advancing while the city is revealed.
 # Leave the sine parameter unclamped: clamping it at f220 would introduce
 # a velocity corner while the entry blend already has nonzero weight.
 t=(f-220)/130
 offset=Vector((-25-5*math.sin(math.pi*t)+16*ease((f-295)/55),
                -29-4*ease((f-260)/70),31-20*ease((f-225)/110)))
 reveal=ease((f-225)/30)*(1-ease((f-285)/35))
 offset*=1+.10*reveal
 eye=M@offset;up=(M.to_quaternion()@Vector((0,0,1))).normalized()
 target=M.translation+up*(cfg['look_height']+3*reveal);front=(target-eye).normalized()
 right=front.cross(up).normalized();up=right.cross(front).normalized()
 q=Matrix((right,up,-front)).transposed().to_quaternion()
 a,b=cfg['window'];c,d=cfg['full_weight'];w=ease((f-a)/(c-a))*(1-ease((f-d)/(b-d)))
 return Matrix.LocRotScale(old.translation.lerp(eye,w),old.to_quaternion().slerp(q,w),old.to_scale())

a,b=cfg['window'];ticks=[i/8 for i in range(a*8,b*8+1)];records={}
for f in ticks:
 s.frame_set(int(f),subframe=f%1)
 records[f]=(cam.matrix_world.copy(),parent.matrix_world.copy(),ship.matrix_world.copy())
basis=cam.matrix_basis.copy();inverse=cam.matrix_parent_inverse.copy()
layer=bpy.data.objects.new('S3_SHIP_FOLLOW_CAMERA',None);s.collection.objects.link(layer)
layer.parent=parent;layer.rotation_mode='QUATERNION';layer['role']='continuous_ship_relative_city_arrival'
cam.parent=layer;cam.matrix_basis=basis;cam.matrix_parent_inverse=inverse;previous=None
for f in [0,a-1,*ticks,b+1,989]:
 C=Matrix.Identity(4)
 if a<f<b:
  old,P,M=records[f];desired=pose(f,old,M);C=P.inverted()@desired@old.inverted()@P
 layer.location=C.translation;layer.rotation_quaternion=C.to_quaternion()
 if previous and layer.rotation_quaternion.dot(previous)<0:layer.rotation_quaternion.negate()
 previous=layer.rotation_quaternion.copy()
 layer.keyframe_insert('location',frame=f);layer.keyframe_insert('rotation_quaternion',frame=f)
for l in layer.animation_data.action.layers:
 for st in l.strips:
  for bag in st.channelbags:
   for fc in bag.fcurves:
    for k in fc.keyframe_points:k.interpolation='LINEAR'
s['ship_camera_revision']='v001: continuous ship-relative mount; no advance-and-wait reveal'
s.frame_set(280);bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(R/'review/build.json').write_text(json.dumps({'source_sha256':cfg['source_sha256'],'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'window':[a,b],'new_object':layer.name,'camera_only':True,'fps':s.render.fps,'frame_end':s.frame_end},indent=2))
