import bpy
from pathlib import Path

root = Path(__file__).resolve().parents[1]
scene = bpy.context.scene
scene.render.engine = 'BLENDER_WORKBENCH'
scene.render.resolution_x = 320
scene.render.resolution_y = 180
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = str(root / 'review' / 'smoke.png')
bpy.ops.wm.save_as_mainfile(filepath=str(root / 'review' / 'smoke.blend'))
bpy.ops.render.render(write_still=True)
print('SMOKE_OK', bpy.app.version_string, bpy.app.binary_path)
