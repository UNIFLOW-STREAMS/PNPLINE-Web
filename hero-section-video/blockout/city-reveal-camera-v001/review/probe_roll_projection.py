import bpy
from mathutils import Vector
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1]
for version in ['v010','v008']:
 bpy.ops.wm.open_mainfile(filepath=str(R/f'candidate-city-reveal-{version}.blend'))
 s=bpy.context.scene;c=s.camera
 print('VERSION',version,'SENSOR',c.data.sensor_fit,c.data.sensor_width)
 print('DRIVERS',[(d.data_path,d.driver.expression,[(v.name,v.targets[0].id.name,v.targets[0].data_path) for v in d.driver.variables]) for d in c.data.animation_data.drivers])
 for f in [497,528,552,600]:
  s.frame_set(f)
  print('FRAME',f,'SHIFT',c.data.shift_x,c.data.shift_y,'EYE',list(c.matrix_world.translation),'TARGET_SCREEN',list(world_to_camera_view(s,c,s.objects['CAM_LOOK_TARGET'].matrix_world.translation)))
  if version=='v010':print('ROLLPROPS',s.objects['CR_ROLL_LEVEL_CAMERA']['lens_shift_x'],s.objects['CR_ROLL_LEVEL_CAMERA']['lens_shift_y'])
