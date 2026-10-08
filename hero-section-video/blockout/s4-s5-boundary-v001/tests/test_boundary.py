import bpy,sys,json,unittest
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];cfg=json.loads((R/'config.json').read_text(encoding='utf-8-sig'));S=bpy.data.scenes[cfg['scene']];bpy.context.window.scene=S
class Boundary(unittest.TestCase):
 def test_destination_is_inside_boundary_view(self):
  S.frame_set(648);names=['WAREHOUSE_BACK_WALL','WAREHOUSE_PARTIAL_ROOF'];pts=[world_to_camera_view(S,S.camera,bpy.data.objects[n].matrix_world@Vector(c)) for n in names for c in bpy.data.objects[n].bound_box];inside=[p for p in pts if 0<=p.x<=1 and 0<=p.y<=1 and p.z>0];self.assertTrue(inside,'Actual warehouse silhouette is wholly outside boundary camera')
 def test_baseline_departure_support(self):
  data=json.loads((R/'review/baseline-boundary.json').read_text());r=next(r for r in data['rows'] if r['frame']==648);self.assertLess(max(abs(w['gap']) for w in r['support']),cfg['thresholds']['support_gap_m'],'Original tyre/quay contact requires separate geometric resolution')
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Boundary));assert result.wasSuccessful()
