import bpy,ast,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(156);D=s.objects['SF_CN_LAYOUT'];DM=D.matrix_world.copy();DI=DM.inverted()
t=ast.parse((R/'scripts/build_layout_proposal.py').read_text());exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef)and n.name in {'uvpoint','topheight'}],type_ignores=[]),'h','exec'))
def proj(p):
 q=world_to_camera_view(s,s.camera,DM@Vector(p));return [q.x*2048,(1-q.y)*1156]
data={'reference_screen_at_z':{str(z):{str(p):list(uvpoint(*p,z))for p in [(1240,600),(1460,653),(1340,562),(1280,774),(1355,754)]}for z in [1.25,6.5,8.5,9.5]},'existing_mechanics':{str(p):proj(p)for p in [(-.75,1.25,11.8),(-.8,1.25,8.99),(-.8,1.25,7.64),(-.8,1.25,3.99),(2,5,1.25),(2,5,9.5),(-3.5,5,1.25)]}}
(R/'review/crane-fit-probe.json').write_text(json.dumps(data,indent=2));print(json.dumps(data))
