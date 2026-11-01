"""Camera contracts: prevent the reported skyline crop and abrupt downward turn."""
import bpy,unittest,math,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];s=bpy.context.scene
class CityReveal(unittest.TestCase):
 def test_handoff_keeps_the_active_container_on_screen(self):
  failures=[]
  for f in range(576,649,6):
   s.frame_set(f);p=world_to_camera_view(s,s.camera,s.objects['A01_CONTAINER'].matrix_world.translation)
   if p.z<=0 or not(.06<p.x<.94 and .06<p.y<.94):failures.append((f,list(p)))
  self.assertEqual(len(failures),0,str(failures))
 def test_skyline_and_landmarks_remain_framed_during_city_hold(self):
  names=['UC_LETTER_U','UC_LETTER_S','UC_LETTER_A','UC_CENTRAL_TOWER','UC_GLASS_SPIRE_TOWER','UC_LIBERTY_ISLAND_CAP']
  names=[n for n in names if n in s.objects];self.assertGreaterEqual(len(names),5)
  failures=[]
  for f in [479,*range(480,553,6)]:
   s.frame_set(f)
   for n in names:
    o=s.objects[n];points=[world_to_camera_view(s,s.camera,o.matrix_world@Vector(v)) for v in o.bound_box]
    bad=[p for p in points if p.z<=0 or not(.015<p.x<.985 and .025<p.y<.975)]
    if bad:failures.append((f,n,len(bad)))
  self.assertEqual(len(failures),0,str(failures[:12]))
 def test_no_abrupt_camera_turn_during_reveal_and_handoff(self):
  previous=None;steps=[]
  for f in range(440,649):
   s.frame_set(f);q=s.camera.matrix_world.to_quaternion()
   if previous is not None:
    angle=math.degrees(q.rotation_difference(previous).angle);steps.append((min(angle,360-angle),f))
   previous=q
  self.assertLess(max(steps)[0],1.6,str(max(steps)))
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(CityReveal))
 if not result.wasSuccessful():raise AssertionError('City reveal camera contract failed')
