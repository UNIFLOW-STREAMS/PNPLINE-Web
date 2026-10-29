"""Catch a civic dome placed behind the skyline in the arrival shot."""
import bpy,unittest
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
s=bpy.context.scene
class CivicReadability(unittest.TestCase):
 def test_dome_and_lantern_have_unobstructed_arrival_silhouette(self):
  for f in [432,450,468]:
   s.frame_set(f);dg=bpy.context.evaluated_depsgraph_get()
   for name in ['UC_CIVIC_DOME','UC_CIVIC_LANTERN']:
    o=s.objects[name];p=o.matrix_world@(sum((Vector(v) for v in o.bound_box),Vector())/8)
    screen=world_to_camera_view(s,s.camera,p)
    self.assertTrue(.03<screen.x<.97 and .03<screen.y<.97 and screen.z>0,(f,name,list(screen)))
    origin=s.camera.matrix_world.translation;d=p-origin
    hit,loc,n,i,ob,m=s.ray_cast(dg,origin,d.normalized(),distance=d.length+.1)
    self.assertTrue(hit and ob.name.startswith('UC_CIVIC'),(f,name,ob.name if hit else 'miss'))
r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(CivicReadability))
if not r.wasSuccessful():raise SystemExit(1)
