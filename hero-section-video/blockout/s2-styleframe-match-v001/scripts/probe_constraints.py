"""Read-only evidence for locked animation versus reference semantics."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];s=bpy.context.scene
def uv(p):
 v=world_to_camera_view(s,s.camera,p);return [v.x,1-v.y,v.z]
def frame(f):s.frame_set(int(f),subframe=f%1)
rows=[]
for f in [0,24,48,72,96,144,156,170,180,216,278,330,450,456,510,532,632]:
 frame(f-.25 if f else f);p0=s.objects['A02_SHIP'].matrix_world.translation.copy()
 frame(f+.25);p1=s.objects['A02_SHIP'].matrix_world.translation.copy()
 frame(f);ship=s.objects['A02_SHIP'].matrix_world.copy();velocity=(p1-p0)/(.25 if f==0 else .5)
 posaxis=(ship.to_3x3()@Vector((1,0,0))).normalized()
 rows.append({'frame':f,'velocity_world':list(velocity),'speed_per_frame':velocity.length,'velocity_dot_ship_positive_x':velocity.normalized().dot(posaxis) if velocity.length>1e-6 else None,'plus_x_endpoint_uv':uv(ship@Vector((6.8,0,0))),'minus_x_endpoint_uv':uv(ship@Vector((-6.8,0,0))),'bridge_uv':uv(s.objects['SHIP_BRIDGE'].matrix_world.translation),'trolley_corners_uv':[uv(s.objects['P01_TROLLEY'].matrix_world@Vector(c)) for c in s.objects['P01_TROLLEY'].bound_box],'cable_tops_uv':[uv(s.objects['P01_CABLE_'+str(i)].matrix_world@Vector((0,0,.5))) for i in range(4)]})
(R/'review/protected-constraint-probes.json').write_text(json.dumps({'coordinates':'normalized top-left, x/y, camera depth; no reference image transformed','samples':rows},indent=2))
print(json.dumps([r for r in rows if r['frame'] in [156,170,216,278]],indent=2))
