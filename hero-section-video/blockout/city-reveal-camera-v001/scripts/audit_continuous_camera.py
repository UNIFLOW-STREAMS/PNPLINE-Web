"""Measure camera movement at the previously stationary joins and preserve lens data."""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];candidate=Path(bpy.data.filepath)
s=bpy.context.scene;c=s.camera
def lens_keys(camera):
 return [(fc.data_path,fc.array_index,[(list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation) for k in fc.keyframe_points]) for layer in camera.data.animation_data.action.layers for strip in layer.strips for bag in strip.channelbags for fc in bag.fcurves]
keys=lens_keys(c);p={};q={};projection={}
for half in range(814,1396):
 f=half/2;s.frame_set(int(f),subframe=f%1);p[f]=c.matrix_world.translation.copy();q[f]=c.matrix_world.to_quaternion()
 if f<=440 or f>=672:projection[f]=(c.data.lens,c.data.shift_x,c.data.shift_y)
speed={f:(p[f+.5]-p[f]).length*2 for f in p if f+.5 in p}
turns={f:min(math.degrees(q[f].rotation_difference(q[f+.5]).angle),360-math.degrees(q[f].rotation_difference(q[f+.5]).angle))*2 for f in q if f+.5 in q}
joins={str(f):{'speed_before':speed[f-.5],'speed_after':speed[f]} for f in [440,500,596,648,672]}
acc=[((p[f+.5]-2*p[f]+p[f-.5]).length*4,f) for f in p if 438<=f<=674]
result={'candidate_sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'joins_units_per_frame':joins,'minimum_speed_438_672':min((v,f) for f,v in speed.items() if 438<=f<672),'maximum_acceleration_438_674':max(acc),'maximum_turn_degrees_per_frame':max((v,f) for f,v in turns.items() if 438<=f<674)}
bpy.ops.wm.open_mainfile(filepath=str(R.parent/'curvature-rework-v001/candidate-curvature-v004.blend'));s=bpy.context.scene;c=s.camera
result['focal_length_action_unchanged']=keys==lens_keys(c)
errors=[]
for f,values in projection.items():
 s.frame_set(int(f),subframe=f%1);errors.extend(abs(a-b) for a,b in zip(values,(c.data.lens,c.data.shift_x,c.data.shift_y)))
result['projection_error_outside_window']=max(errors)
(R/'review'/f'{candidate.stem}-continuous-audit.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
assert result['minimum_speed_438_672'][0]>.1
assert result['maximum_acceleration_438_674'][0]<.12
assert result['maximum_turn_degrees_per_frame'][0]<2
assert result['focal_length_action_unchanged'] and max(errors)<1e-6
