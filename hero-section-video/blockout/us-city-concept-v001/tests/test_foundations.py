import bpy,math,unittest
from mathutils import Vector
s=bpy.context.scene;s.frame_set(510);I=s.objects['US_FRAME'].matrix_world.inverted()
class FoundationTests(unittest.TestCase):
 def test_bridge_piers_extend_into_spherical_seabed(self):
  for o in s.objects:
   if not o.name.startswith(('UC_BRIDGE_PIER','UC_BRIDGE_ABUTMENT','UC_SHORE_HILL')):continue
   pts=[I@o.matrix_world@Vector(v) for v in o.bound_box]
   sea=min(math.sqrt(140**2-p.x*p.x-p.y*p.y)-140 for p in pts)
   self.assertLessEqual(min(p.z for p in pts),sea-.1,o.name+' floats above spherical water')
r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(FoundationTests))
if not r.wasSuccessful():raise AssertionError('Unanchored foundation')
