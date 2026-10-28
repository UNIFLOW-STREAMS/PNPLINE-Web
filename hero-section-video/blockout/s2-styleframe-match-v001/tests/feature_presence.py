"""Minimum editable design probes, not aesthetic acceptance.
Detect absent 3D clouds/bridge/water/coast and missing exact hull brand.
Stable names are the new builder contract; geometry, material and parent tests
prevent empties/labels alone from satisfying the presence requirement.
"""
import bpy,unittest,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
class FeatureTests(unittest.TestCase):
 def geometry(self,name):
  root=bpy.data.objects.get(name);self.assertIsNotNone(root,name+' missing')
  meshes=[o for o in [root,*root.children_recursive] if o.type=='MESH' and not o.hide_render]
  self.assertTrue(meshes,name+' has no rendered mesh')
  self.assertTrue(any(len(o.data.vertices)>8 and len(o.data.polygons)>4 for o in meshes),name+' lacks actual form')
  for o in meshes:self.assertFalse(o.constraints,'no camera-follow or pose tricks');self.assertIsNone(o.animation_data)
  return root,meshes
 def test_two_spatial_cloud_sculptures(self):
  a,_=self.geometry('SF_CLOUD_LEFT');b,_=self.geometry('SF_CLOUD_RIGHT')
  self.assertGreater((a.matrix_world.translation-b.matrix_world.translation).length,10)
 def test_interior_water_has_real_surface(self):
  root,meshes=self.geometry('SF_INTERNAL_WATER')
  self.assertTrue(any(o.data.materials for o in meshes))
 def test_bridge_has_open_span(self):
  root,meshes=self.geometry('SF_ARCH_BRIDGE')
  self.assertGreater(len(meshes),1,'separate span/support structure required')
 def test_reference_white_coast_is_3d(self):
  root,meshes=self.geometry('SF_WHITE_COAST')
  self.assertTrue(any(o.dimensions.z>.5 for o in meshes),'flat card is not the coast')
 def test_hull_brand_exact_and_attached_to_same_ship(self):
  o=bpy.data.objects.get('SF_HULL_PNPLINE');self.assertIsNotNone(o,'missing large hull brand')
  self.assertEqual(o.type,'FONT');self.assertEqual(o.data.body,'PNPLINE')
  p=o.parent
  while p and p.name!='A02_SHIP':p=p.parent
  self.assertIsNotNone(p,'brand must follow the same real ship')
if __name__=='__main__':
 r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(FeatureTests))
 (R/'review/feature-red.json').write_text(json.dumps({'tests':r.testsRun,'failures':[(str(t),trace) for t,trace in r.failures],'errors':[(str(t),trace) for t,trace in r.errors]},indent=2))
 if not r.wasSuccessful():raise SystemExit(1)
