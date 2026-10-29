import bpy,unittest,math
s=bpy.context.scene
class MotionTest(unittest.TestCase):
 def test_exit_does_not_accelerate_into_a_whip_pan(self):
  previous=None;peak_turn=0;peak_speed=0
  for i in range(468*4,529*4+1):
   s.frame_set(i//4,subframe=(i%4)/4);m=s.camera.matrix_world.copy();q=m.to_quaternion()
   if previous:
    p0,q0=previous;peak_speed=max(peak_speed,(m.translation-p0).length*48)
    peak_turn=max(peak_turn,math.degrees(q.rotation_difference(q0).angle)*48)
   previous=(m.translation.copy(),q)
  self.assertLess(peak_speed,23,('speed',peak_speed));self.assertLess(peak_turn,42,('turn',peak_turn))
r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(MotionTest))
if not r.wasSuccessful():raise SystemExit(1)
