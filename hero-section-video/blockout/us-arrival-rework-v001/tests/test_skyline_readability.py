"""Catch civic mass hiding the signature stepped tower's body in actual arrival."""
import bpy,unittest
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
s=bpy.context.scene
class SkylineReadability(unittest.TestCase):
 def test_signature_tower_body_reads_above_foreground(self):
  o=next(o for o in s.objects if o.name.startswith('UC_CENTRAL_TOWER_TIER') and max(v.co.z for v in o.data.vertices)-min(v.co.z for v in o.data.vertices)>7)
  vs=[v.co for v in o.data.vertices];x=(min(v.x for v in vs)+max(v.x for v in vs))/2;y=min(v.y for v in vs);lo=min(v.z for v in vs);hi=max(v.z for v in vs)
  for f in [440,455,471]:
   s.frame_set(f);dg=bpy.context.evaluated_depsgraph_get();visible=0;occluders=[]
   for t in [.2,.4,.6,.8]:
    p=o.matrix_world@Vector((x,y,lo+(hi-lo)*t));screen=world_to_camera_view(s,s.camera,p);d=p-s.camera.matrix_world.translation
    hit,loc,n,i,ob,m=s.ray_cast(dg,s.camera.matrix_world.translation,d.normalized(),distance=d.length+.15)
    ok=hit and ob.name.startswith('UC_CENTRAL_TOWER') and .03<screen.x<.97 and .03<screen.y<.97
    visible+=ok;occluders.append(ob.name if hit else 'miss')
   self.assertGreaterEqual(visible,3,(f,visible,occluders))
r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(SkylineReadability))
if not r.wasSuccessful():raise SystemExit(1)
