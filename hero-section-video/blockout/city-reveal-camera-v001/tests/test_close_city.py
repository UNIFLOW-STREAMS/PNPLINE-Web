"""Regression: excessive pullback makes the ship tiny and the following turn too large."""
import bpy,unittest,math
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
s=bpy.context.scene
class CloseCity(unittest.TestCase):
 def test_camera_stays_close_through_city_reveal(self):
  distances=[]
  for f in range(455,553):
   s.frame_set(f);distances.append(((s.camera.matrix_world.translation-s.objects['CAM_LOOK_TARGET'].matrix_world.translation).length,f))
  self.assertLess(max(distances)[0],115,str(max(distances)))
 def test_ship_remains_readable_at_end_of_arrival(self):
  widths=[]
  for f in [479,490,509,521,540,552]:
   s.frame_set(f);o=s.objects['SHIP_HULL'];p=[world_to_camera_view(s,s.camera,o.matrix_world@Vector(v)) for v in o.bound_box]
   widths.append((max(v.x for v in p)-min(v.x for v in p),f))
  self.assertGreater(min(widths)[0],.13,str(min(widths)))
 def test_handoff_uses_a_smaller_turn(self):
  s.frame_set(552);a=s.camera.matrix_world.to_quaternion();s.frame_set(648);b=s.camera.matrix_world.to_quaternion();angle=math.degrees(a.rotation_difference(b).angle)
  self.assertLess(min(angle,360-angle),50)
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(CloseCity))
 if not result.wasSuccessful():raise AssertionError('Close-city camera regression')
