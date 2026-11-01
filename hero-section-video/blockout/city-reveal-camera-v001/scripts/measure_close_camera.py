"""Measure the delivered projection and motion, independently of the builder."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;file=Path(bpy.data.filepath)
out={'candidate_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'samples':[]};turns=[];distances=[];prev=None
for f in range(440,649):
 s.frame_set(f);c=s.camera;q=c.matrix_world.to_quaternion();distance=(c.matrix_world.translation-s.objects['CAM_LOOK_TARGET'].matrix_world.translation).length
 if 455<=f<=552:distances.append((distance,f))
 if prev is not None:
  angle=math.degrees(q.rotation_difference(prev).angle);turns.append((min(angle,360-angle),f))
 prev=q
 if f in [455,479,509,521,552,576,600,624,648]:
  o=s.objects['SHIP_HULL'];p=[world_to_camera_view(s,c,o.matrix_world@Vector(v)) for v in o.bound_box]
  out['samples'].append({'frame':f,'distance':distance,'ship_screen_width':max(v.x for v in p)-min(v.x for v in p)})
s.frame_set(552);a=s.camera.matrix_world.to_quaternion();s.frame_set(648);b=s.camera.matrix_world.to_quaternion();angle=math.degrees(a.rotation_difference(b).angle)
out.update(max_distance=max(distances),max_rotation_step=max(turns),handoff_angle=min(angle,360-angle))
(R/'review'/f'{file.stem}-measurements.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
