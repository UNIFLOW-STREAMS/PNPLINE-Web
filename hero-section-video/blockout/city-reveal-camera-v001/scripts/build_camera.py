"""Camera-only continuous reveal layer. Preserve every source scene action and lens key."""
import bpy,sys,argparse,json,hashlib
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
def hero(f):
 t=ease((f-479)/73);aim=Vector((18,29,9)).lerp(Vector((16,29,9)),t);eye=Vector((-68,-92,50)).lerp(Vector((-58,-89,47)),t)
 eye=aim+(eye-aim)*(.9*records[f]['lens']/32)
 return U@Matrix.LocRotScale(eye,(aim-eye).to_track_quat('-Z','Y'),Vector((1,1,1))),Matrix.Translation(U@aim)
last={}
for f in [0,439,*range(440,649),649,1392]:
 weight=ease((f-440)/39) if f<=552 else 1
 for n,frame in frames.items():
  correction=Matrix.Identity(4)
  if weight>0 and f<648:
   original,P=records[f][n]
   if f<=552:
    desired=hero(f)[names.index(n)];loc=original.translation.lerp(desired.translation,weight);q=original.to_quaternion().slerp(desired.to_quaternion(),weight)
   else:
    # A fixed endpoint avoids inheriting the old orbit/180-degree slerp branch jump.
    start_cam,start_target=hero(552);end_cam=records[648]['CAM_MASTER'][0];end_target=records[648]['CAM_LOOK_TARGET'][0];t=(f-552)/96;w=ease(t)
    aim=start_target.translation.lerp(end_target.translation,w)
    camera_q=start_cam.to_quaternion().slerp(end_cam.to_quaternion(),w)
    distance=(start_cam.translation-start_target.translation).length*(1-w)+(end_cam.translation-end_target.translation).length*w
    # Move on the interpolated viewing axis so rotation never drifts off the subject.
    loc=aim+camera_q@Vector((0,0,distance)) if n=='CAM_MASTER' else aim
    q=camera_q if n=='CAM_MASTER' else start_target.to_quaternion().slerp(end_target.to_quaternion(),w)
   final=Matrix.LocRotScale(loc,q,original.to_scale());correction=P.inverted()@final@original.inverted()@P
  frame.location=correction.translation;frame.rotation_quaternion=correction.to_quaternion()
  if n in last and frame.rotation_quaternion.dot(last[n])<0:frame.rotation_quaternion.negate()
  last[n]=frame.rotation_quaternion.copy();frame.keyframe_insert('location',frame=f);frame.keyframe_insert('rotation_quaternion',frame=f)
for frame in frames.values():
 for l in frame.animation_data.action.layers:
  for st in l.strips:
   for bag in st.channelbags:
    for fc in bag.fcurves:
     for k in fc.keyframe_points:k.interpolation='LINEAR'
s.frame_set(509);s['city_reveal_camera']='v003: city hold479-552, subject-centered handoff440-648; source fps retained'
bpy.ops.wm.save_as_mainfile(filepath=str(out))
(R/'review'/f'{out.stem}-build.json').write_text(json.dumps({'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'candidate':str(out),'candidate_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'changed_original_objects':names,'new_objects':[o.name for o in frames.values()],'affected_frames':[440,648],'city_hold':[479,552],'fps':s.render.fps},indent=2));print('SAVED',out)
