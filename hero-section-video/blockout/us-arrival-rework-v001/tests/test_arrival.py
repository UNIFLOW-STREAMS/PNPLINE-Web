"""Catch flat USA arrangement and a side/overhead camera masquerading as stern follow."""
import bpy,unittest,math
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
s=bpy.context.scene
class ArrivalTests(unittest.TestCase):
 def test_letters_curve_in_world_and_keep_ten_stars(self):
  inv=s.objects['US_FRAME'].matrix_world.inverted()
  ps=[inv@s.objects['UC_LETTER_'+c].matrix_world.translation for c in 'USA']
  for p in ps:p.z=0
  self.assertGreater((ps[1]-ps[0]).cross(ps[2]-ps[0]).length,5)
  self.assertEqual(sum(o.get('uc_role')=='star' for o in s.objects),10)
 def test_landmarks_frame_during_arrival(self):
  for f in [432,450,468]:
   s.frame_set(f)
   for name in ['UC_LETTER_U','UC_LETTER_S','UC_LETTER_A','UC_LIBERTY_FLAME','UC_LIBERTY_CROWN','UC_LIBERTY_ROBE']:
    o=s.objects[name]
    pts=[world_to_camera_view(s,s.camera,o.matrix_world@Vector(v)) for v in o.bound_box]
    self.assertTrue(all(.025<p.x<.975 and .025<p.y<.975 and p.z>0 for p in pts),(f,name,[(round(p.x,2),round(p.y,2)) for p in pts]))
 def test_camera_stern_and_low(self):
  for f in [432,450,468]:
   s.frame_set(f);ship=s.objects['A02_SHIP'];p=ship.matrix_world.inverted()@s.camera.matrix_world.translation
   self.assertLess(p.x,-10,(f,list(p)))
   up=s.camera.matrix_world.translation.normalized();height=s.camera.matrix_world.translation.length-140
   self.assertGreater(height,2);self.assertLess(height,15)
   forward=-s.camera.matrix_world.to_3x3().col[2]
   self.assertLess(abs(math.degrees(math.asin(max(-1,min(1,forward.dot(up)))))),22)
r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ArrivalTests))
if not r.wasSuccessful():raise SystemExit(1)
