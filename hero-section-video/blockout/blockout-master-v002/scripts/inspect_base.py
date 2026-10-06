import bpy,json
from mathutils import Vector
S=bpy.context.scene
print('INSPECT',json.dumps({'current_frame':S.frame_current,'start':S.frame_start,'end':S.frame_end,'markers':[(m.name,m.frame) for m in S.timeline_markers]},ensure_ascii=False))
for f in [0,1,50,80,84,96,110,160]:
 S.frame_set(f); inv=bpy.data.objects['CN_FRAME'].matrix_world.inverted(); c=S.camera
 print('CAM',f,json.dumps({'p':list(inv@c.matrix_world.translation),'q':list((inv@c.matrix_world).to_quaternion()),'lens':c.data.lens,'target':list(inv@bpy.data.objects['CAM_LOOK_TARGET'].matrix_world.translation),'container':list(inv@bpy.data.objects['A01_CONTAINER'].matrix_world.translation)}))
