import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[1];S=bpy.context.scene;cam=S.camera
rows=[]
for f in range(1393):
 S.frame_set(f);rows.append({'frame':f,'matrix':[list(r) for r in cam.matrix_world],'target':list(bpy.data.objects['CAM_LOOK_TARGET'].matrix_world.translation),'lens':cam.data.lens})
S.frame_set(0)
p=[world_to_camera_view(S,cam,bpy.data.objects['A01_CONTAINER'].matrix_world@Vector((x,y,z))) for x in [-1.6,1.6] for y in [-.8,.8] for z in [-.75,.75]]
(ROOT/'inputs/base-camera.json').write_text(json.dumps({'frames':rows,'frame0_bounds':{'bottom':min(v.y for v in p),'top':max(v.y for v in p)}},separators=(',',':')),encoding='utf-8')
print('BASE_CAPTURED',{'bottom':min(v.y for v in p),'top':max(v.y for v in p)})
