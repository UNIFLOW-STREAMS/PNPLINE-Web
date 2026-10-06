import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];S=bpy.context.scene
S.render.resolution_x=960;S.render.resolution_y=540
evidence=[]
for f in [0,24,48,72,96,97,110,144,159,160,161]:
    S.frame_set(f)
    inv=bpy.data.objects['CN_FRAME'].matrix_world.inverted()
    p=inv@S.camera.matrix_world.translation;t=inv@bpy.data.objects['A01_CONTAINER'].matrix_world.translation
    evidence.append({'frame':f,'camera_cn':list(p),'subject_cn':list(t),'elevation_deg':math.degrees(math.atan2(p.z-t.z,math.hypot(p.x-t.x,p.y-t.y)))})
    S.render.filepath=str(ROOT/'review'/f'camera-f{f:04}.png');bpy.ops.render.render(write_still=True)
(ROOT/'review/camera-states.json').write_text(json.dumps(evidence,indent=2),encoding='utf-8')
