"""Saved-scene behavior, independent geometric route-distance assertions."""
import bpy,sys,json,math,unittest
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R.parent/'s5-dock-test-v001/scripts'))
from geometry import hull,overlap
s=bpy.data.scenes['PNPLINE_MASTER_v005'];bpy.context.window.scene=s
I=s.objects['US_FRAME'].matrix_world.inverted()
def at(n,f):
 s.frame_set(int(f),subframe=f%1);return I@s.objects[n].matrix_world
class IntegrationTests(unittest.TestCase):
 def test_selected_forward_turn_uses_donor_spatial_path(self):
  # Middle of selected donor ellipse, away from bounded entry/exit repairs.
  worst=0;count=0
  for f in range(721,810):
   p=at('A03_TRAILER',f).translation
   if 14<p.y<24:
    residual=abs(((p.x-29.4)/6)**2+((p.y-19)/10)**2-1)
    worst=max(worst,residual);count+=1
  print('ELLIPSE_RESIDUAL',worst,count);self.assertGreater(count,5);self.assertLess(worst,.002)
 def test_heading_follows_forward_motion_and_hitch(self):
  worst=0
  for j in range(721*4,809*4):
   f=j/4
   for n in ['A03_TRAILER','A03_TRACTOR']:
    # A one-frame chord remains well above float32 world-coordinate noise
    # during the final millimetres of braking; sample its center every1/4f.
    a=at(n,f-.5).translation;b=at(n,f+.5).translation;m=at(n,f)
    angle=(b-a).normalized().angle(m.to_3x3()@Vector((1,0,0)))
    if math.degrees(angle)>worst:
     worst=math.degrees(angle);worst_case=(f,n,(b-a).length)
   self.assertLess((s.objects['TRACTOR_HITCH'].matrix_world.translation-s.objects['TRAILER_HITCH'].matrix_world.translation).length,.002)
  print('MAX_TANGENT_DEG',worst,worst_case);self.assertLess(worst,2)
 def test_doors_clear_container_through_opening(self):
  worst=0
  for j in range(810*4,843*4):
   s.frame_set(j//4,subframe=(j%4)/4)
   for d in ['A01_DOOR_LEFT_LEAF','A01_DOOR_RIGHT_LEAF']:
    for b in ['A01_FLOOR','A01_ROOF','A01_SIDE_L','A01_SIDE_R','A01_FRONT']:
     worst=max(worst,overlap(*hull(s.objects[d]),*hull(s.objects[b])))
  print('DOOR_PENETRATION',worst);self.assertLess(worst,.01)
 def test_payload_remains_inside_until_inbound(self):
  s.frame_set(720);rel=s.objects['A01_CONTAINER'].matrix_world.inverted()@s.objects['W01_NEW_PALLET'].matrix_world
  for j in range(720*4,901*4):
   s.frame_set(j//4,subframe=(j%4)/4);now=s.objects['A01_CONTAINER'].matrix_world.inverted()@s.objects['W01_NEW_PALLET'].matrix_world
   self.assertLess((now.translation-rel.translation).length,.002)
 def test_original_timing_and_single_scene(self):
  self.assertEqual(s.render.fps,12);self.assertEqual(s.frame_end,1392)
  self.assertEqual(len(bpy.data.scenes),1);self.assertEqual(len(s.objects),304)
  self.assertEqual({m.name:m.frame for m in s.timeline_markers}['B56'],900)
  for n in ['A01_DOOR_L','A01_DOOR_R']:self.assertAlmostEqual(s.objects[n].location.x,-1.65,places=5)
result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(IntegrationTests))
(R/'logs/integration-result.json').write_text(json.dumps({'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors)}))
if not result.wasSuccessful():raise RuntimeError('Integration contract failed')
