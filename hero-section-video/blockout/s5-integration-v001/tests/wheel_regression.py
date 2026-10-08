import bpy,math,json,sys,unittest
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
s=bpy.data.scenes['PNPLINE_MASTER_v005'];bpy.context.window.scene=s
I=bpy.data.objects['US_FRAME'].matrix_world.inverted()
wheels=[o for o in s.objects if o.name.startswith('A03') and '_WHEEL_' in o.name]
ground=[]
for n in ['US_QUAY','US_LAND_TERRACE','E07_INBOUND_ROAD','E09_MANEUVER_YARD']:
 o=bpy.data.objects[n];ground.append(BVHTree.FromPolygons([I@o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons]))
class VehicleTests(unittest.TestCase):
 def test_initial_contact_without_rising(self):
  worst=0
  for j in range(0,648*4):
   f=j/4;s.frame_set(int(f),subframe=f%1)
   for o in wheels:
    c=(I@o.matrix_world).translation
    hits=[b.ray_cast(c+Vector((0,0,5)),Vector((0,0,-1)),20)[0] for b in ground];z=max(v.z for v in hits if v is not None)
    bottom=min((I@o.matrix_world@v.co).z for v in o.data.vertices)
    worst=max(worst,abs(bottom-z))
  print('INITIAL_MAX_CONTACT_ERROR',worst)
  self.assertLess(worst,.002)
 def test_tandem_wheel_clearance(self):
  s.frame_set(596)
  for side in [-1,1]:
   pair=sorted([o for o in wheels if 'TRAILER' in o.name and o.location.y*side>0],key=lambda o:o.location.x)
   ranges=[]
   for o in pair:
    pts=[o.matrix_local@v.co for v in o.data.vertices];ranges.append((min(v.x for v in pts),max(v.x for v in pts)))
   gap=ranges[1][0]-ranges[0][1];print('TANDEM_CLEARANCE',side,gap);self.assertGreaterEqual(gap,.09)
 def test_departure_contact(self):
  worst=0
  for j in range(648*16,1392*16+1):
   f=j/16;s.frame_set(int(f),subframe=f%1)
   for o in wheels:
    c=(I@o.matrix_world).translation
    hits=[b.ray_cast(c+Vector((0,0,5)),Vector((0,0,-1)),20)[0] for b in ground];z=max(v.z for v in hits if v is not None)
    bottom=min((I@o.matrix_world@v.co).z for v in o.data.vertices);worst=max(worst,abs(bottom-z))
  print('DEPARTURE_MAX_CONTACT_ERROR',worst);self.assertLess(worst,.002)
 def test_cab_chassis_no_coincident_sides(self):
  s.frame_set(596);a=bpy.data.objects['TRACTOR_CAB'];b=bpy.data.objects['TRACTOR_CHASSIS']
  self.assertGreaterEqual(a.location.z-a.dimensions.z/2,b.location.z+b.dimensions.z/2-.0001)
 def test_single_tractor_and_trailer(self):
  self.assertEqual([o.name for o in s.objects if o.name.startswith('A03_TRACTOR') and o.type=='EMPTY'],['A03_TRACTOR'])
  self.assertEqual([o.name for o in s.objects if o.name.startswith('A03_TRAILER') and o.type=='EMPTY'],['A03_TRAILER'])
result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(VehicleTests))
if not result.wasSuccessful():raise RuntimeError('Vehicle regression failed')



