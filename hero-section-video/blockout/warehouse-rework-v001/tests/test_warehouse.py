"""Scene behavior tests: missing physical shell/belt and wrong branding must fail."""
import bpy,unittest,sys
from mathutils import Vector
S=bpy.context.scene;S.frame_set(1075);U=S.objects['US_FRAME'].matrix_world
def cast(p,d,distance=30):
 return S.ray_cast(bpy.context.evaluated_depsgraph_get(),U@Vector(p),U.to_3x3()@Vector(d),distance=distance)
class WarehouseContract(unittest.TestCase):
 def test_header_frames_open_working_interior(self):
  hit,loc,normal,face,obj,m=cast((52,20,10.2),(0,1,0))
  self.assertTrue(hit,'Reference-style industrial header missing above open warehouse')
  self.assertTrue(obj.name.startswith('WH_'),'Header must be inside warehouse scope')
  self.assertLess((U.inverted()@loc).y,26)
 def test_cyan_conveyor_has_physical_continuous_support(self):
  for p in [(50,26),(57,26),(50,28),(62.9,27),(42.1,27)]:
   hit,loc,n,face,obj,m=cast((*p,2.8),(0,0,-1),1)
   self.assertTrue(hit,'Missing conveyor support at '+str(p))
   self.assertAlmostEqual((U.inverted()@loc).z,2.65,delta=.04)
 def test_authentic_brand_is_visible_geometry(self):
  logo=[o for o in S.objects if o.name in ['WH_LOGO_CYAN','WH_LOGO_GRAY'] and o.type=='MESH']
  self.assertGreaterEqual(len(logo),2,'Authentic cyan/gray wordmark geometry missing')
  self.assertTrue(all(len(o.data.polygons)>20 for o in logo))
  colors=[tuple(round(c*255) for c in o.data.materials[0].diffuse_color[:3]) for o in logo]
  self.assertIn((0,171,225),colors);self.assertIn((120,120,121),colors)
  for o in logo:
   m=o.data.materials[0];linear=m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value
   encoded=[round((v*12.92 if v<=.0031308 else 1.055*v**(1/2.4)-.055)*255) for v in linear[:3]]
   self.assertEqual(encoded,[round(v*255) for v in m.diffuse_color[:3]],'Rendered material must encode the supplied logo color in sRGB')
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(WarehouseContract))
 if not result.wasSuccessful():raise AssertionError('Warehouse contract failed')
