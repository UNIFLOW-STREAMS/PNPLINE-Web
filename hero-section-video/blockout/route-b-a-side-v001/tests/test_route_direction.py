"""Fails for a C-side destination, backwards travel, or non-spherical route."""
import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(144)
cn=s.objects['CN_FRAME'].matrix_world;ci=cn.inverted();ship=s.objects['A02_SHIP']
points=[];alignment=[];radial=[]
for f in range(145,510):
 s.frame_set(f);m=ship.matrix_world.copy();p=m.translation.copy();s.frame_set(f+1);v=ship.matrix_world.translation-p
 points.append(ci@p);radial.append(abs(p.length-140))
 if v.length>.001:alignment.append(m.to_3x3().col[0].normalized().dot(v.normalized()))
s.frame_set(510);us=ci@s.objects['US_FRAME'].matrix_world.translation
checks={'destination_on_A_side':us.x < -80,'route_reaches_A_seaward_gate':any(p.x < -30 and p.y > 8 for p in points),'bow_moves_forward':min(alignment)>.98,'ship_follows_spherical_water':max(radial)<.02}
out={'checks':checks,'destination_CN_local':list(us),'minimum_bow_velocity_dot':min(alignment),'max_radial_error':max(radial)}
tag=sys.argv[sys.argv.index('--')+1]if '--'in sys.argv else 'route'
(R/'review'/f'{tag}-direction.json').write_text(json.dumps(out,indent=2));print(json.dumps(out));assert all(checks.values()),checks
