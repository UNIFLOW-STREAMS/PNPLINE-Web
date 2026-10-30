"""Verify a roll-only edit against the accepted v008 camera at half-frame samples."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];candidate=Path(bpy.data.filepath)
def capture():
    s=bpy.context.scene;c=s.camera;out={}
    for f in sorted(set([0,408,439,439.5,649,900,1392]+[n/2 for n in range(880,1298)])):
        s.frame_set(int(f),subframe=f%1)
        q=c.matrix_world.to_quaternion()
        center=(q@Vector((c.data.shift_x*c.data.sensor_width/c.data.lens,c.data.shift_y*c.data.sensor_width/c.data.lens,-1))).normalized()
        out[f]={'eye':list(c.matrix_world.translation),'front':list(q@Vector((0,0,-1))),'center':list(center),'target':list(s.objects['CAM_LOOK_TARGET'].matrix_world.translation),'lens':[c.data.lens],'matrix':[v for row in c.matrix_world for v in row],'shift':[c.data.shift_x,c.data.shift_y]}
    s.frame_set(497)
    def line_angle(points):
        a,b=[world_to_camera_view(s,c,p) for p in points]
        angle=math.degrees(math.atan2((b.y-a.y)*s.render.resolution_y,(b.x-a.x)*s.render.resolution_x))
        return (angle+90)%180-90
    U=s.objects['US_FRAME'].matrix_world;ship=s.objects['A02_SHIP'].matrix_world
    measures={'quay_screen_angle_497':line_angle([U@Vector(p) for p in [(-10,4,.4),(10,4,.4)]]),'ship_screen_angle_497':line_angle([ship@Vector(p) for p in [(-6,-2.6,0),(6,-2.6,0)]])}
    return out,measures
after,new=capture()
bpy.ops.wm.open_mainfile(filepath=str(R/'candidate-city-reveal-v008.blend'))
before,old=capture()
worst={k:max((abs(a-b),f,i) for f in before for i,(a,b) in enumerate(zip(after[f][k],before[f][k]))) for k in ['eye','front','center','target','lens']}
errors={k:v[0] for k,v in worst.items()}
outside={k:max(abs(a-b) for f in before if f<=440 or f>=648 for a,b in zip(after[f][k],before[f][k])) for k in ['matrix','shift']}
result={'candidate_sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'max_component_errors_vs_v008':errors,'worst_error_samples':worst,'max_errors_outside_roll_window':outside,'before':old,'after':new}
(R/'review'/f'{candidate.stem}-roll-audit.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
assert max(errors.values())<1e-4,errors
assert max(outside.values())<1e-4,outside
assert abs(new['quay_screen_angle_497'])<.1 and abs(new['ship_screen_angle_497'])<5
