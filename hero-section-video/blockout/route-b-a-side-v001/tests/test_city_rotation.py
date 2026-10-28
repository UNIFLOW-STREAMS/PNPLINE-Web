"""Catch wrong-side exit, lost S1 suspension alignment and return to old crane."""
import bpy,json,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(144);ship=s.objects['A02_SHIP'];si=ship.matrix_world.inverted()
a=si@s.objects['SF_CHINA_A'].matrix_world.translation;c=si@s.objects['SF_CHINA_C'].matrix_world.translation
gaps=[];rope=[]
for f in range(73):
 s.frame_set(f);sp=s.objects['P01_SPREADER'].matrix_world.translation;head=s.objects['CR_SUSPENSION_HEAD'].matrix_world.translation;up=ship.matrix_world.to_3x3().col[2];d=head-sp;gaps.append((d-up*d.dot(up)).length);rope.append(d.dot(up))
checks={'A_ahead_of_C_along_existing_bow':a.x>c.x,'S1_suspension_stays_over_spreader':max(gaps)<.001,'S1_ropes_positive':min(rope)>.1}
tag=sys.argv[sys.argv.index('--')+1]if '--'in sys.argv else 'city'
(R/'review'/f'{tag}.json').write_text(json.dumps({'checks':checks,'A_local':list(a),'C_local':list(c),'max_suspension_horizontal_error':max(gaps),'min_rope_height':min(rope)},indent=2));print(checks);assert all(checks.values())
