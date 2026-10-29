"""Exercise actual scene mutations against the scoped preservation verifier."""
import bpy,sys,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
import verify_rework as v
s=bpy.context.scene
class PreservationScope(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.baseline=v.samples()[0]
 def changed_samples(self,name,at):
  obj=s.objects[name];original=obj.animation_data.action;action=original.copy();action.name='AR_TEST_MUTATION';obj.animation_data.action=action
  try:
   curves=[fc for l in action.layers for st in l.strips for bag in st.channelbags for fc in bag.fcurves if fc.data_path=='location' and fc.array_index==0]
   key=min(curves[0].keyframe_points,key=lambda k:abs(k.co.x-at))
   if at==450:self.assertTrue(300<key.co.x<528)
   else:self.assertGreater(key.co.x,528)
   key.co.y+=1;key.handle_left.y+=1;key.handle_right.y+=1;curves[0].update()
   return v.compare_evaluations(self.baseline,v.samples()[0])[0]
  finally:
   obj.animation_data.action=original;bpy.data.actions.remove(action)
 def test_camera_edit_inside_interval_is_allowed(self):self.assertEqual(self.changed_samples('CAM_MASTER',450),[])
 def test_camera_edit_outside_interval_is_detected(self):
  errors=self.changed_samples('CAM_MASTER',648)
  self.assertTrue(any(e['object']=='CAM_MASTER' and float(e['f'])>528 for e in errors))
 def test_ship_edit_inside_camera_interval_is_detected(self):
  errors=self.changed_samples('A02_SHIP',450)
  self.assertTrue(any(e['object']=='A02_SHIP' and 300<float(e['f'])<528 for e in errors))
r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(PreservationScope))
if not r.wasSuccessful():raise SystemExit(1)
