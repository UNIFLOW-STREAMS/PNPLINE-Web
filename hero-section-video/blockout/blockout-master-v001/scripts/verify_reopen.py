import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
S=bpy.context.scene
assert S.camera.name=='CAM_MASTER'
assert S['master_version']=='v001'
assert S.frame_end==1392
assert not bpy.app.handlers.frame_change_post, 'Motion should need no custom callbacks'
S.render.resolution_x=960;S.render.resolution_y=540
S.frame_set(900)
S.render.filepath=str(ROOT/'review'/'reopen-f0900.png')
bpy.ops.render.render(write_still=True)
print('REOPEN_REPRODUCED_FRAME_900')
