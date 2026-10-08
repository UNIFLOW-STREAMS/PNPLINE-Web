import sys,unittest,math
from pathlib import Path
from mathutils import Quaternion
sys.path.insert(0,str(Path(__file__).resolve().parent))
from camera_math import orientation_degrees
class OrientationRegression(unittest.TestCase):
 def test_quaternion_sign_is_same_orientation(self):
  q=Quaternion((0,0,1),.3);opposite=q.copy();opposite.negate()
  self.assertAlmostEqual(orientation_degrees(q,opposite),0,places=3)
 def test_right_angle_remains_ninety_degrees(self):
  self.assertAlmostEqual(orientation_degrees(Quaternion((1,0,0,0)),Quaternion((0,0,1),math.pi/2)),90,places=3)
if __name__=='__main__':
 r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(OrientationRegression))
 if not r.wasSuccessful():raise SystemExit(1)
