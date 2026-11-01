import bpy,math
from mathutils import Vector,Matrix
from bpy_extras.object_utils import world_to_camera_view
s=bpy.context.scene;s.frame_set(509);U=s.objects['US_FRAME'].matrix_world.copy();cam=s.camera
names=['UC_LETTER_U','UC_LETTER_S','UC_LETTER_A','UC_GLASS_SPIRE_TOWER','UC_LIBERTY_ISLAND_CAP']
points=[s.objects[n].matrix_world@Vector(v) for n in names for v in s.objects[n].bound_box]
ship=[s.objects['SHIP_HULL'].matrix_world@Vector(v) for v in s.objects['SHIP_HULL'].bound_box]
for eye,aim in [((-78,-40,19),(-1,29,3)),((-77,-38,15),(-1,29,3)),((-78,-40,16),(-1,29,3)),((-80,-40,18),(-1,29,3)),((-78,-40,19),(-4,25,3))]:
 e=Vector(eye);a=Vector(aim);cam.matrix_world=U@Matrix.LocRotScale(e,(a-e).to_track_quat('-Z','Y'),Vector((1,1,1)))
 p=[world_to_camera_view(s,cam,v) for v in points];sp=[world_to_camera_view(s,cam,v) for v in ship]
 print('PROBE',eye,aim,'dist',round((e-a).length,2),'bounds',*[round(val,3) for val in [min(v.x for v in p),max(v.x for v in p),min(v.y for v in p),max(v.y for v in p)]],'shipwidth',round(max(v.x for v in sp)-min(v.x for v in sp),3))
