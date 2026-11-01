import bpy,sys,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
s=bpy.context.scene
s.frame_set(150)
ship=s.objects['A02_SHIP'];inv=ship.matrix_world.inverted()
def bounds(o,inv):
    m=inv@o.matrix_world
    ps=[m@Vector(p) for p in o.bound_box]
    return [[round(f(p[i] for p in ps),4) for i in range(3)] for f in (min,max)]
for group in ('A02_SHIP','A01_CONTAINER','P01_SPREADER'):
    parent=s.objects[group]
    print('GROUP',group,'origin scale',list(parent.matrix_world.to_scale()),len(parent.children_recursive))
    for o in sorted(parent.children_recursive,key=lambda q:q.name):
        if group=='A01_CONTAINER' and o.parent!=parent:continue
        print(o.name,'parent',o.parent.name,'v/r',o.hide_viewport,o.hide_render,'bbox',bounds(o,inv),'mats',[m.name for m in o.data.materials if m] if o.type in ('MESH','FONT','CURVE') else [])
print('markers',[(m.name,m.frame) for m in s.timeline_markers])
for f in (0,18,42,60,80,100,120,135,154,170,200,244,285,330,360,380,400,430,450,485):
    s.frame_set(f);mi=ship.matrix_world.inverted()
    print('frame',f,'camera',list(round(v,2) for v in mi@s.camera.matrix_world.translation),'container',list(round(v,2) for v in mi@s.objects['A01_CONTAINER'].matrix_world.translation),'spreader',list(round(v,2) for v in mi@s.objects['P01_SPREADER'].matrix_world.translation))
