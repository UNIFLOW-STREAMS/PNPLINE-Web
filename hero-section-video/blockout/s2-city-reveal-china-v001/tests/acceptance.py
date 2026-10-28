import bpy, unittest, json,sys,importlib.util,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];S=bpy.context.scene
class RevealTests(unittest.TestCase):
 def test_five_static_mesh_letters(self):
  for i,c in enumerate('CHINA'):
   o=bpy.data.objects.get(f'CHINA_{i}_{c}')
   self.assertIsNotNone(o,'Missing letter '+c)
   self.assertEqual(o.type,'MESH');self.assertEqual(o['letter'],c)
   self.assertIsNone(o.animation_data);self.assertEqual(len(o.constraints),0)
   self.assertEqual(o.parent.name,'S2_CHINA_ROOT')
   self.assertEqual(o.get('s2_reveal_owner'),'s2-city-reveal-china-v001')
   self.assertFalse(o.hide_render);self.assertGreater(len(o.data.materials),1)
 def test_joint_features_in_representative_view(self):
  S.frame_set(156)
  names=['CN_LM_SPHERE_TOWER_upper_sphere','CN_LM_SPHERE_TOWER_lower_sphere','CN_LM_SPHERE_TOWER_spire','CN_LM_OPEN_TOP_TOWER_lintel']
  names += [f'CHINA_{i}_{c}' for i,c in enumerate('CHINA')]
  for n in names:
   o=bpy.data.objects.get(n);self.assertIsNotNone(o,n)
   for v in o.data.vertices:
    p=world_to_camera_view(S,S.camera,o.matrix_world@v.co)
    self.assertTrue(p.z>0 and 0<=p.x<=1 and 0<=p.y<=1,f'{n}: {tuple(p)}')
 def test_world_static_title(self):
  objs=[o for o in S.objects if o.get('s2_reveal_owner')]
  self.assertGreater(len(objs),5)
  S.frame_set(0);initial={o.name:o.matrix_world.copy() for o in objs}
  for f in [96,156,216,456,900,1392]:
   S.frame_set(f)
   for o in objs:self.assertEqual(o.matrix_world,initial[o.name]);self.assertFalse(o.hide_render)
 def test_timeline_and_lens_preserved(self):
  self.assertEqual((S.frame_start,S.frame_end,S.render.fps),(0,1392,12))
  for f in [96,156,216,278]:
   S.frame_set(f);self.assertEqual(S.camera.data.lens,40)
 def test_rejoin_has_no_one_frame_rotation_pulse(self):
  angles=[];prev=None
  for f in range(209,218):
   S.frame_set(f);q=S.camera.matrix_world.to_quaternion()
   if prev is not None:angles.append(math.degrees(2*math.acos(min(1,abs(q.dot(prev))))))
   prev=q
  self.assertLess(max(abs(b-a) for a,b in zip(angles,angles[1:])),.25,'Angular step changes at the last S2 keys: '+str(angles))
if __name__=='__main__':
 suite=unittest.defaultTestLoader.loadTestsFromTestCase(RevealTests)
 if '--regression' in sys.argv:
  for path,cls in [('cn-city-proxy-v001/tests/test_proxy.py','ProxyTests'),('s5-integration-v001/tests/master_regression.py','MasterTests')]:
   spec=importlib.util.spec_from_file_location(cls,R.parent/path);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
   suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(getattr(mod,cls)))
 result=unittest.TextTestRunner(verbosity=2).run(suite)
 if not result.wasSuccessful():raise SystemExit(1)
