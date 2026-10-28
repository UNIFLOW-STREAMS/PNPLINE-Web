import bpy,json,ast,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(156);D=s.objects['SF_CN_LAYOUT'];DM=D.matrix_world;DI=DM.inverted()
tree=ast.parse((R/'scripts/build_layout_proposal.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='uvpoint'],type_ignores=[]),'<uv>','exec'))
tree=ast.parse((R/'scripts/verify_title_water.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='inside'],type_ignores=[]),'<inside>','exec'))
w=s.objects['SF_BASIN_WATER_SURFACE'];ring=[v.co.copy()for v in list(w.data.vertices)[:len(w.data.vertices)//2]]
print([(px,py,inside(uvpoint(px,py),ring))for px in [650,665,680,700]for py in [720,730,740,750,760]])
a=uvpoint(486,689);b=uvpoint(665,720);u=(b-a).normalized()
for d in [0,.5,1,1.5,2,2.5,3]:
 p=b+u*d;q=world_to_camera_view(s,s.camera,DM@p);print('extension',d,'water',inside(p,ring),'uv',q.x*2048,(1-q.y)*1156)
