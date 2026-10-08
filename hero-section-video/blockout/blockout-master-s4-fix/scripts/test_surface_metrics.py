"""Behavioral regression for an assembly's occluded internal faces."""
import bpy,sys,unittest
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from s4_metrics import surface
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
S=bpy.context.scene;bpy.ops.object.camera_add(location=(0,-12,0));C=bpy.context.object;S.camera=C
C.rotation_euler=(Vector((0,0,0))-C.location).to_track_quat('-Z','Y').to_euler();C.data.lens=35
for name,p,scale in [('panel-front',(0,-.2,0),(2,.1,1)),('panel-back',(0,.2,0),(2,.1,1))]:
 bpy.ops.mesh.primitive_cube_add(size=2,location=p);o=bpy.context.object;o.name=name;o.scale=scale
bpy.context.view_layer.update()
class SurfaceMetricRegression(unittest.TestCase):
 def test_internal_panels_do_not_count_as_external_obstruction(self):
  self.assertGreater(surface(['panel-front','panel-back'])['visible_fraction'],.95)
 def test_external_crane_obstruction_is_counted(self):
  bpy.ops.mesh.primitive_cube_add(size=2,location=(-.9,-2,0));o=bpy.context.object;o.name='P02_LEG_fixture';o.scale=(.9,.1,2);bpy.context.view_layer.update()
  v=surface(['panel-front','panel-back']);self.assertGreater(v['crane_fraction'],.3);self.assertLess(v['visible_fraction'],.7)
  bpy.data.objects.remove(o,do_unlink=True)
if __name__=='__main__':
 r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(SurfaceMetricRegression))
 if not r.wasSuccessful():raise SystemExit(1)
