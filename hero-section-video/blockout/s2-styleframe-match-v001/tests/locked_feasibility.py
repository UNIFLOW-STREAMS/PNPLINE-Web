"""Preconditions for simultaneous locked motion and D07/D08 reference semantics.

These are NOT overall visual acceptance tests. The ship probe establishes a
heading conflict under bow-first semantics. The crane probe only establishes
endpoint placement; alternate functional support/occlusion remains untested.
Independent measurements are in reference-map.json, in top-left coordinates.
"""
import bpy,unittest,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];s=bpy.context.scene
class LockedFeasibility(unittest.TestCase):
 def test_forward_heading_projects_toward_reference_left_bow(self):
  # D08 explicitly identifies the left end as bow, right end as stern/bridge.
  s.frame_set(156,subframe=.25);b=s.objects['A02_SHIP'].matrix_world.translation.copy()
  s.frame_set(155,subframe=.75);a=s.objects['A02_SHIP'].matrix_world.translation.copy()
  s.frame_set(156);centre=s.objects['A02_SHIP'].matrix_world.translation.copy()
  forward=(b-a).normalized()
  uv0=world_to_camera_view(s,s.camera,centre-forward*6.8)
  uv1=world_to_camera_view(s,s.camera,centre+forward*6.8)
  self.assertLess(uv1.x,uv0.x,'Locked forward motion projects RIGHT; a LEFT bow would sail stern-first. This is a functional/visual conflict, not a lighting issue.')
 def test_live_cable_support_fits_reference_crane_upper_silhouette(self):
  # Reference crane apex y=550/1156. Five-pixel manual boundary uncertainty,
  # set before trials; not an arbitrary overall similarity score.
  s.frame_set(156);upper=(550-5)/1156
  for i in range(4):
   o=s.objects['P01_CABLE_'+str(i)]
   p=world_to_camera_view(s,s.camera,o.matrix_world@Vector((0,0,.5)))
   self.assertGreaterEqual(1-p.y,upper,'Live cable top is ABOVE the target crane apex; shortening only visible static legs disconnects the actual support.')
if __name__=='__main__':
 r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(LockedFeasibility))
 (R/'review/locked-feasibility.json').write_text(json.dumps({'purpose':'scope-conflict probes, not overall acceptance','tests':r.testsRun,'failures':[(str(t),tr) for t,tr in r.failures],'errors':[(str(t),tr) for t,tr in r.errors]},indent=2))
 if not r.wasSuccessful():raise SystemExit(1)
