"""Catch raised letters with no actual 3D support under their lowest point."""
import bpy,unittest
from mathutils import Vector
s=bpy.context.scene;s.frame_set(450);u=s.objects['US_FRAME'].matrix_world;inv=u.inverted();up=u.to_3x3()@Vector((0,0,1))
class SupportTests(unittest.TestCase):
 def test_raised_letters_are_supported(self):
  dg=bpy.context.evaluated_depsgraph_get()
  for ch in 'USA':
   o=s.objects['UC_LETTER_'+ch];pts=[o.matrix_world@v.co for v in o.data.vertices];p=min(pts,key=lambda p:(inv@p).z)
   hit,loc,normal,index,obj,matrix=s.ray_cast(dg,p-up*.005,-up,distance=.3)
   self.assertTrue(hit,(ch,'floating letter'))
 def test_front_street_buildings_have_real_ground_support(self):
  dg=bpy.context.evaluated_depsgraph_get()
  for i in range(7):
   o=s.objects[f'UC_BLOCK_00_{i:02}'];pts=[o.matrix_world@v.co for v in o.data.vertices];p=min(pts,key=lambda p:(inv@p).z)
   hit,loc,normal,index,obj,matrix=s.ray_cast(dg,p-up*.005,-up,distance=.3)
   self.assertTrue(hit,(o.name,'floating waterfront building'))
r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(SupportTests))
if not r.wasSuccessful():raise SystemExit(1)
