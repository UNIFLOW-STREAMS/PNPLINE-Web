import bpy,json,ast
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(156)
D=s.objects['SF_CN_LAYOUT'];DM=D.matrix_world.copy();DI=DM.inverted()
t=ast.parse((R/'scripts/build_layout_proposal.py').read_text());exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name in {'uvpoint','pxwidth'}],type_ignores=[]),'helpers','exec'))
data={}
for o in s.objects:
 if o.name in ['SF_HISTORIC_2','SF_HISTORIC_3','SF_CHINA_N','SF_CHINA_A','SF_SMALL_VEHICLE_2'] or o.name.startswith('SF_CRANE_BASE'):
  p=DI@o.matrix_world.translation
  data[o.name]={'pos':list(p),'mesh_bounds':[list(DI@o.matrix_world@Vector(c))for c in o.bound_box] if o.type=='MESH' else None}
data['samples']={f'{x},{y}':list(uvpoint(x,y))for x in [1000,1150,1300,1450,1550,1650]for y in [630,680,730,780,820]}
(R/'review/na-probe.json').write_text(json.dumps(data,indent=2))
print(json.dumps(data))
