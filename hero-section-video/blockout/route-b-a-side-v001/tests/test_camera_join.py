import bpy,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;c=s.camera
points=[];qs=[]
for f in range(450,461):s.frame_set(f);points.append(c.matrix_world.translation.copy());qs.append(c.matrix_world.to_quaternion())
steps=[(b-a).length for a,b in zip(points,points[1:])];angles=[a.rotation_difference(b).angle*57.2957795 for a,b in zip(qs,qs[1:])]
checks={'S4_join_no_position_jump':max(steps)<1.5,'S4_join_no_rotation_jump':max(angles)<3}
tag=sys.argv[sys.argv.index('--')+1]if '--'in sys.argv else 'join'
(R/'review'/f'{tag}.json').write_text(json.dumps({'checks':checks,'position_steps':steps,'rotation_steps_degrees':angles},indent=2));print(checks,steps,angles);assert all(checks.values())
