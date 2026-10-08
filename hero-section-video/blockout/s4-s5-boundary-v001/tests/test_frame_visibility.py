import bpy,sys,json,math,unittest
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];cfg=json.loads((R/'config.json').read_text());s=bpy.data.scenes[cfg['scene']];bpy.context.window.scene=s
class Framing(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  objects={o.name:o for n in ['A03_TRACTOR','A03_TRAILER','A01_CONTAINER'] for o in [bpy.data.objects[n],*bpy.data.objects[n].children_recursive] if o.type=='MESH' and not o.hide_render};bad=[];widths=[]
  for j in range(648*4,cfg['edit_end']*4+1):
   f=j/4;s.frame_set(math.floor(f),subframe=f%1);pts=[world_to_camera_view(s,s.camera,o.matrix_world@Vector(v)) for o in objects.values() for v in o.bound_box];bounds=[min(p.x for p in pts),min(p.y for p in pts),max(p.x for p in pts),max(p.y for p in pts)];widths.append(bounds[2]-bounds[0])
   if not(bounds[0]>=0 and bounds[1]>=0 and bounds[2]<=1 and bounds[3]<=1):bad.append([f,bounds])
  cls.data=dict(failures=bad,min_width=min(widths),max_width=max(widths));(R/'review/framing.json').write_text(json.dumps(cls.data,indent=2))
 def test_whole_vehicle_remains_inside_departure_and_rejoin(self):self.assertEqual(self.data['failures'],[],f'First crop: {self.data["failures"][:3]}')
 def test_vehicle_minimum_screen_size(self):
  self.assertGreaterEqual(self.data['min_width'],cfg['thresholds']['vehicle_screen_width_min'])
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Framing));raise SystemExit(0 if result.wasSuccessful() else 1)
