import bpy,sys,unittest,math,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];s=bpy.context.scene
class Logistics(unittest.TestCase):
 def test_articulated_hitch_stays_closed(self):
  for f in range(640,909):
   s.frame_set(f);a=s.objects['TRAILER_HITCH'].matrix_world.translation;b=s.objects['TRACTOR_HITCH'].matrix_world.translation
   self.assertLess((a-b).length,.012,(f,'hitch separates'))
 def test_truck_wheels_stay_near_road_surface(self):
  violations=[];samples=[];verts=[];faces=[]
  # Isolate drivable surfaces: scene rays would incorrectly hit the wheel itself.
  for name in ['US_QUAY','US_YARD_ROAD','E07_INBOUND_ROAD','E09_MANEUVER_YARD','E10_OUTBOUND_YARD','E11_ROUTE_1','E11_ROUTE_-1','A05_WAIT_MERGE']:
   obj=s.objects[name];offset=len(verts);verts.extend(obj.matrix_world@v.co for v in obj.data.vertices);faces.extend(tuple(offset+i for i in p.vertices) for p in obj.data.polygons)
  road=BVHTree.FromPolygons(verts,faces)
  for f in range(680,1393,3):
   s.frame_set(f);deps=bpy.context.evaluated_depsgraph_get()
   roots=['A03_TRAILER','A03_TRACTOR'] if f<909 else ['A04_PRIMARY','A05_SECONDARY']
   for name in roots:
    root=s.objects[name];up=(root.matrix_world.to_3x3()@Vector((0,0,1))).normalized()
    for wheel in [o for o in root.children if 'WHEEL' in o.name]:
     # Use evaluated wheel support, not source assumptions about axis alignment.
     pts=[wheel.matrix_world@v.co for v in wheel.data.vertices];low=min(p.dot(up) for p in pts);center=wheel.matrix_world.translation;bottom=center+up*(low-center.dot(up))
     point,normal,index,distance=road.ray_cast(bottom+up*.5,-up,3)
     gap=(bottom-point).dot(up) if point is not None else 10
     samples.append((f,wheel.name,round(gap,4)))
     if point is None or abs(gap)>.14:violations.append(samples[-1])
  (R/'review'/('wheel-support-'+Path(bpy.data.filepath).stem+'.json')).write_text(json.dumps({'samples':samples,'violations':violations},indent=2))
  self.assertEqual(len(violations),0,str(violations[:16]))
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Logistics))
 if not result.wasSuccessful():raise AssertionError('Logistics tests failed')
