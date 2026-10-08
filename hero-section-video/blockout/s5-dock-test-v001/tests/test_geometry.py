import unittest,sys,importlib.util
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
class Geometry(unittest.TestCase):
 def test_boxes_separate_touch_penetrate(self):
  self.assertIsNotNone(importlib.util.find_spec('geometry'),'Missing collision contract')
  from geometry import overlap
  from mathutils import Vector
  def box(x):return [Vector((x+a,b,c)) for a in [-1,1] for b in [-1,1] for c in [-1,1]]
  axes=[Vector((1,0,0)),Vector((0,1,0)),Vector((0,0,1))]
  self.assertEqual(overlap(box(0),axes,box(3),axes),0)
  self.assertEqual(overlap(box(0),axes,box(2),axes),0)
  self.assertAlmostEqual(overlap(box(0),axes,box(1.5),axes),.5)
if __name__=='__main__':
 r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Geometry));assert r.wasSuccessful()
