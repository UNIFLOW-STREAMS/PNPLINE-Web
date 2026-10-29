import bpy,unittest,math
from mathutils import Vector
s=bpy.context.scene;center=s.objects['EARTH_CONTINUOUS_OCEAN'].matrix_world.translation
class Curvature(unittest.TestCase):
 def test_terrain_is_thin_spherical_skin(self):
  o=s.objects['US_LAND_TERRACE'];r=[(o.matrix_world@v.co-center).length for v in o.data.vertices]
  self.assertGreater(len(r),1000,'Need sufficient spherical topology')
  self.assertLess(max(r)-min(r),1.0,'Deep flat plate or foundation remains')
  self.assertAlmostEqual(max(r),140.68,delta=.025)
  self.assertGreater(min(r),139.7)
 def test_buildings_point_along_their_footprint_normals(self):
  for name in ['UC_BLOCK_00_00','UC_BLOCK_02_02','UC_BLOCK_05_10','UC_GLASS_SPIRE_TOWER','E12_DESTINATION_1']:
   o=s.objects[name];z=min(v.co.z for v in o.data.vertices);base=[o.matrix_world@v.co for v in o.data.vertices if abs(v.co.z-z)<.0001]
   anchor=sum(base,Vector())/len(base);radial=(anchor-center).normalized();up=(o.matrix_world.to_3x3()@Vector((0,0,1))).normalized()
   self.assertLess(math.degrees(up.angle(radial)),.15,(name,'not radial'))
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Curvature))
 if not result.wasSuccessful():raise AssertionError('Curvature contract failed')
