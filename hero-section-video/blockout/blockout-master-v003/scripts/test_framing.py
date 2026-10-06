import bpy,unittest,json,math
from pathlib import Path
from mathutils import Matrix,Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[1];S=bpy.context.scene
BASE=json.loads((ROOT/'inputs/base-camera.json').read_text())
class FramingTests(unittest.TestCase):
 def test_camera_rotation_and_lens_preserved(self):
  for f in range(1393):
   S.frame_set(f);m=Matrix(BASE['frames'][f]['matrix'])
   self.assertLess(max(abs(S.camera.matrix_world[i][j]-m[i][j]) for i in range(3) for j in range(3)),1e-6)
   self.assertAlmostEqual(S.camera.data.lens,BASE['frames'][f]['lens'])
 def test_container_lower_and_cables_more_visible(self):
  S.frame_set(0);obj=bpy.data.objects['A01_CONTAINER']
  p=[world_to_camera_view(S,S.camera,obj.matrix_world@Vector((x,y,z))) for x in [-1.6,1.6] for y in [-.8,.8] for z in [-.75,.75]]
  self.assertTrue(.075<min(v.y for v in p)<.105,'Container bottom should be near lower tenth of image')
  self.assertLess(max(v.y for v in p),BASE['frame0_bounds']['top']-.1,'More space above for suspension cables')
  self.assertTrue(all(.03<v.x<.97 and v.z>0 for v in p))
 def test_world_altitude_increased(self):
  S.frame_set(0);self.assertGreater(S.camera.matrix_world.translation.z,Matrix(BASE['frames'][0]['matrix']).translation.z+.1)
 def test_s1_end_and_later_camera_unchanged(self):
  for f in range(96,1393):
   S.frame_set(f);m=Matrix(BASE['frames'][f]['matrix'])
   self.assertLess(max(abs(S.camera.matrix_world[i][j]-m[i][j]) for i in range(4) for j in range(4)),1e-6)
if __name__=='__main__':
 r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(FramingTests))
 (ROOT/'logs/framing-test-result.json').write_text(json.dumps({'tests':r.testsRun,'failures':len(r.failures),'errors':len(r.errors)}))
 if not r.wasSuccessful():raise SystemExit(1)
