"""Read-only camera and subject measurements for the closer-city revision."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
s=bpy.context.scene; I=s.objects['US_FRAME'].matrix_world.inverted()
names=['UC_LETTER_U','UC_LETTER_S','UC_LETTER_A','UC_CENTRAL_TOWER','UC_GLASS_SPIRE_TOWER','UC_LIBERTY_ISLAND_CAP']
names=[n for n in names if n in s.objects]
ship=[o.name for o in s.objects if 'HULL' in o.name.upper()]
print('SHIP_NAMES',ship)
out={'source':bpy.data.filepath,'samples':[]}
for f in [440,455,479,509,521,552,576,600,624,648]:
 s.frame_set(f); c=s.camera; target=s.objects['CAM_LOOK_TARGET']; pts=[world_to_camera_view(s,c,s.objects[n].matrix_world@Vector(v)) for n in names for v in s.objects[n].bound_box]
 out['samples'].append({'frame':f,'eye':list(I@c.matrix_world.translation),'aim':list(I@target.matrix_world.translation),'distance':(c.matrix_world.translation-target.matrix_world.translation).length,'lens':c.data.lens,'bounds':[min(p.x for p in pts),max(p.x for p in pts),min(p.y for p in pts),max(p.y for p in pts)]})
print(json.dumps(out,indent=2))
s.frame_set(509)
for n in names+ship:
 o=s.objects[n];pts=[I@o.matrix_world@Vector(v) for v in o.bound_box];print('SUBJECT',n,[(min(p[i] for p in pts),max(p[i] for p in pts)) for i in range(3)])
