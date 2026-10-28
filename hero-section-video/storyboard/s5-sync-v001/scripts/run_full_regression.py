import bpy,sys,unittest,json,math,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];B=Path(bpy.data.filepath).parent;src=R.parents[1]/'blockout/s5-integration-v001/tests/master_regression.py'
scope={'__name__':'regression_library','__file__':str(B/'tests/master_regression.py')};exec(compile(src.read_text(encoding='utf8'),str(src),'exec'),scope)
class FullMasterTests(scope['MasterTests']):
 def test_full_timeline_camera_continuity(self):
  s=bpy.context.scene;previous=None
  for f in range(1,1393):
   s.frame_set(f);m=s.camera.matrix_world.copy()
   if previous:
    self.assertLess((m.translation-previous.translation).length,2.5,f'camera jump {f}')
    self.assertLess(2*math.acos(min(1,abs(m.to_quaternion().dot(previous.to_quaternion())))),math.radians(8),f'camera rotation {f}')
   previous=m
  for f in [96,216,456,648,900,1200]:
   a=self.at('CAM_MASTER',f-1).translation;b=self.at('CAM_MASTER',f).translation;c=self.at('CAM_MASTER',f+1).translation
   self.assertLess((c-2*b+a).length,.15,f'boundary acceleration {f}')
   if f!=648:self.assertGreater((c-a).length,.001,f'unintended stop {f}')
  # Adopted proposal intentionally holds its departure composition through649.
  a=self.at('CAM_MASTER',648).translation;b=self.at('CAM_MASTER',660).translation
  self.assertGreater((b-a).length,.5,'Departure tracking failed to resume')
klass=FullMasterTests;suite=unittest.defaultTestLoader.loadTestsFromTestCase(klass)
# Absolute source-shore bounds are superseded by the real-mesh SAT sweep.
suite=unittest.TestSuite(t for t in suite if t._testMethodName!='test_inbound_vehicle_clears_raised_warehouse_floor')
result=unittest.TextTestRunner(verbosity=2).run(suite)
(B/'review/master-regression.json').write_text(json.dumps({'master_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'tests':result.testsRun,'failures':[(str(t),e) for t,e in result.failures],'errors':[(str(t),e) for t,e in result.errors],'replaced_test':'Source hardcoded warehouse bounds replaced by validate_space.py actual geometry SAT; approved f648 hold allowed with tracking-resumption check.'},indent=2),encoding='utf8')
if not result.wasSuccessful():raise AssertionError('Master regression failed')
