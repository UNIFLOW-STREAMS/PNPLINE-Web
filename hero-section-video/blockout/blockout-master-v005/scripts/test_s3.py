import bpy,sys,unittest,json
from pathlib import Path
from mathutils import Matrix,Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scene_evidence import capture
from s3_metrics import sample
R=Path(__file__).resolve().parents[1];S=bpy.context.scene
BASE=json.loads((R/'review/baseline-full.json').read_text());NOW=capture();OBS={f:sample(f) for f in range(216,457)}
class S3Tests(unittest.TestCase):
 def test_midship_size_and_curvature(self):
  for f in range(278,339):
   o=OBS[f];self.assertGreaterEqual(o['ship_width'],.26,f);self.assertLessEqual(o['ship_width'],.38,f)
   b=o['ship_bounds'];self.assertGreaterEqual(min(b[0],b[1],1-b[2],1-b[3]),.04,f)
   h=o['horizon'];self.assertIsNotNone(h['rise'],f);self.assertGreaterEqual(h['rise'],.11,f)
   self.assertTrue(.65<=h['y'][1]<=.95,(f,h))
 def test_sustained_tracking(self):
  ds=[OBS[f]['distance'] for f in range(278,339)];self.assertLess(max(ds)/min(ds),1.02)
  p=[Matrix(NOW['frames'][f]['camera']).translation for f in [278,338]];self.assertGreater((p[1]-p[0]).length,40)
 def test_rear_approach_before_overtake(self):
  for f in range(366,391):
   o=OBS[f];self.assertLess(o['ship_local_camera'][0],-8,f);self.assertTrue(.32<=o['ship_width']<=.55,(f,o['ship_width']))
  self.assertGreater(OBS[398]['ship_width'],.50)
 def test_same_seaside_and_frontquarter(self):
  for f,o in OBS.items():self.assertLess(o['ship_local_camera'][1],-9,f)
  self.assertLess(OBS[398]['ship_local_camera'][0],-7);self.assertLess(abs(OBS[422]['ship_local_camera'][0]),1)
  self.assertGreater(OBS[450]['ship_local_camera'][0],12);self.assertGreater(OBS[450]['ship_width'],.48)
  widths=[OBS[f]['ship_width'] for f in range(398,451)];self.assertLess(max(widths)/min(widths),1.5)
 def test_outside_camera_exact(self):
  for f,(a,b) in enumerate(zip(BASE['frames'],NOW['frames'])):
   if not 218<=f<=454:
    for k in ['camera','target','lens']:self.assertEqual(a[k],b[k],(f,k))
 def test_noncamera_exact(self):
  for k in ['objects','materials','fps','range','markers','camera_clip']:self.assertEqual(BASE[k],NOW[k],k)
  self.assertEqual([a['noncamera'] for a in BASE['frames']],[a['noncamera'] for a in NOW['frames']])
 def test_camera_configuration_preserved(self):
  c=S.camera.data;b=json.loads((R/'review/baseline-inspection.json').read_text())
  for k,v in b['camera_settings'].items():self.assertEqual(getattr(c,k),v,k)
  self.assertEqual(len(S.objects),304);self.assertTrue(bpy.data.collections['08_REVIEW_GUIDES'].hide_render)
if __name__=='__main__':
 r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(S3Tests));sys.exit(0 if r.wasSuccessful() else 1)
