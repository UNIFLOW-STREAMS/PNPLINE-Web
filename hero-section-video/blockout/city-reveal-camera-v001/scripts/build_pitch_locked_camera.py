"""Fixed world pitch/roll across the city entry; preserve close framing and source actions."""
import bpy,sys,argparse,json,hashlib,math
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(a.output).resolve()
assert out.is_relative_to(R) and not out.exists()
source=R.parent/'curvature-rework-v001/candidate-curvature-v004.blend'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='7fdfe45379eab1e3fc53262610dd7872461983bdb590348c1fe7052407278b1a'
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;U=s.objects['US_FRAME'].matrix_world.copy();names=['CAM_MASTER','CAM_LOOK_TARGET'];records={}
for f in range(440,651):
 s.frame_set(f);records[f]={'lens':s.camera.data.lens,**{n:(s.objects[n].matrix_world.copy(),s.objects[n].parent.matrix_world.copy()) for n in names}}
frames={}
for n in names:
 o=s.objects[n];basis=o.matrix_basis.copy();inverse=o.matrix_parent_inverse.copy();frame=bpy.data.objects.new('CR_REVEAL_'+n,None);s.collection.objects.link(frame);frame.parent=o.parent;frame.rotation_mode='QUATERNION';frame['role']='camera_reveal_correction'
 o.parent=frame;o.matrix_basis=basis;o.matrix_parent_inverse=inverse;frames[n]=frame
def ease(t):
 t=max(0,min(1,t));return t*t*t*(10+t*(-15+6*t))
def attitude(q):
 forward=q@Vector((0,0,-1));right=q@Vector((1,0,0));level_right=forward.cross(Vector((0,0,1))).normalized();level_up=level_right.cross(forward).normalized()
 return math.atan2(forward.y,forward.x),math.asin(max(-1,min(1,forward.z))),math.atan2(right.dot(level_up),right.dot(level_right))
def oriented(yaw,pitch,roll):
 forward=Vector((math.cos(pitch)*math.cos(yaw),math.cos(pitch)*math.sin(yaw),math.sin(pitch)))
 level_right=forward.cross(Vector((0,0,1))).normalized();level_up=level_right.cross(forward).normalized()
 right=level_right*math.cos(roll)+level_up*math.sin(roll);up=level_up*math.cos(roll)-level_right*math.sin(roll)
 return Matrix((right,up,-forward)).transposed().to_quaternion()
def angle_lerp(a,b,t):return a+math.atan2(math.sin(b-a),math.cos(b-a))*t
entry_yaw,locked_pitch,locked_roll=attitude(records[440]['CAM_MASTER'][0].to_quaternion())
def lock_attitude(q):return oriented(attitude(q)[0],locked_pitch,locked_roll)
def hero(f):
 t=ease((f-479)/73);aim=Vector((-1,29,3)).lerp(Vector((0,28,3)),t);eye=Vector((-77,-38,15)).lerp(Vector((-80,-32,15)),t)
 # A lower, more side-on view fits the landmarks without the old long retreat.
 eye=aim+(eye-aim)*(records[f]['lens']/38)
 return U@Matrix.LocRotScale(eye,(aim-eye).to_track_quat('-Z','Y'),Vector((1,1,1))),Matrix.Translation(U@aim)
last={}
for f in [0,439,*range(440,649),649,1392]:
 weight=ease((f-440)/39) if f<=552 else 1
 projection=(0.0,0.0)
 for n,frame in frames.items():
  correction=Matrix.Identity(4)
  if weight>0 and f<648:
   original,P=records[f][n]
   if f<=552:
    desired_cam,desired_target=hero(f)
    source_cam=records[f]['CAM_MASTER'][0];source_target=records[f]['CAM_LOOK_TARGET'][0]
    aim=source_target.translation.lerp(desired_target.translation,weight)
    camera_q=source_cam.to_quaternion().slerp(desired_cam.to_quaternion(),weight)
    distance=(source_cam.translation-source_target.translation).length*(1-weight)+(desired_cam.translation-desired_target.translation).length*weight
    loc=aim+camera_q@Vector((0,0,distance)) if n=='CAM_MASTER' else aim
    q=camera_q if n=='CAM_MASTER' else original.to_quaternion().slerp(desired_target.to_quaternion(),weight)
   else:
    # A fixed endpoint avoids inheriting the old orbit/180-degree slerp branch jump.
    start_cam,start_target=hero(552);end_cam=records[648]['CAM_MASTER'][0];end_target=records[648]['CAM_LOOK_TARGET'][0];t=(f-552)/96;w=ease(t)
    aim=start_target.translation.lerp(end_target.translation,w)
    camera_q=start_cam.to_quaternion().slerp(end_cam.to_quaternion(),w)
    distance=(start_cam.translation-start_target.translation).length*(1-w)+(end_cam.translation-end_target.translation).length*w
    # Move on the interpolated viewing axis so rotation never drifts off the subject.
    loc=aim+camera_q@Vector((0,0,distance)) if n=='CAM_MASTER' else aim
    q=camera_q if n=='CAM_MASTER' else start_target.to_quaternion().slerp(end_target.to_quaternion(),w)
   if n=='CAM_MASTER':
    if f<=552:q=lock_attitude(q);headroom=weight
    else:
     start_angles=attitude(lock_attitude(hero(552)[0].to_quaternion()));end_angles=attitude(end_cam.to_quaternion())
     q=oriented(*(angle_lerp(a,b,w) for a,b in zip(start_angles,end_angles)));headroom=1-w
    # Preserve the v004 eye path. Optical shift centers the subject without tilting
    # the camera or lowering it behind the foreground globe curvature.
    local_target=q.inverted()@(aim-loc);factor=records[f]['lens']/s.camera.data.sensor_width/(-local_target.z)
    projection=(local_target.x*factor,local_target.y*factor+.04*headroom*s.render.resolution_y/s.render.resolution_x)
   final=Matrix.LocRotScale(loc,q,original.to_scale());correction=P.inverted()@final@original.inverted()@P
  frame.location=correction.translation;frame.rotation_quaternion=correction.to_quaternion()
  if n in last and frame.rotation_quaternion.dot(last[n])<0:frame.rotation_quaternion.negate()
  last[n]=frame.rotation_quaternion.copy();frame.keyframe_insert('location',frame=f);frame.keyframe_insert('rotation_quaternion',frame=f)
 for axis,value in zip(('x','y'),projection):
  frame=frames['CAM_MASTER'];frame['lens_shift_'+axis]=value;frame.keyframe_insert('['+json.dumps('lens_shift_'+axis)+']',frame=f)
for axis in ('x','y'):
 driver=s.camera.data.driver_add('shift_'+axis).driver;driver.type='SCRIPTED';driver.expression='offset';var=driver.variables.new();var.name='offset';var.type='SINGLE_PROP';var.targets[0].id=frames['CAM_MASTER'];var.targets[0].data_path='['+json.dumps('lens_shift_'+axis)+']'
for frame in frames.values():
 for l in frame.animation_data.action.layers:
  for st in l.strips:
   for bag in st.channelbags:
    for fc in bag.fcurves:
     for k in fc.keyframe_points:k.interpolation='LINEAR'
s.frame_set(455);s['city_reveal_camera']='v006: fixed world pitch/roll440-552, v004 eye path, optical shift, smooth handoff552-648; original focal length and fps retained'
bpy.ops.wm.save_as_mainfile(filepath=str(out))
(R/'review'/f'{out.stem}-build.json').write_text(json.dumps({'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'candidate':str(out),'candidate_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'changed_original_objects':names,'new_objects':[o.name for o in frames.values()],'affected_frames':[440,648],'city_hold':[479,552],'fps':s.render.fps},indent=2));print('SAVED',out)
