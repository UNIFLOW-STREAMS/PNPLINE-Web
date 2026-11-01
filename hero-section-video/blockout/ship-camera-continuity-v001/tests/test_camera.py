"""Acceptance checks on independently reopened, half-frame samples."""
import json, math, unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
d=json.loads((R/'review/motion.json').read_text())

class CameraContinuity(unittest.TestCase):
 def test_ship_stays_in_view(self):
  self.assertEqual(d['after']['metrics']['ship_outside_frames'],[])
  x0,y0,x1,y1=d['after']['metrics']['ship_bounds']
  self.assertTrue(.035<x0<x1<.965 and .035<y0<y1<.965,(x0,y0,x1,y1))
 def test_camera_does_not_wait_for_ship(self):
  self.assertGreater(d['after']['metrics']['old_wait_window_speed_min'],.70)
  self.assertGreater(d['after']['metrics']['old_wait_window_speed_min'],2*d['before']['metrics']['old_wait_window_speed_min'])
 def test_camera_stays_behind_ship(self):
  lo,hi=d['after']['metrics']['longitudinal_relative_range']
  self.assertTrue(-35<lo<hi<-14,(lo,hi))
 def test_rotation_is_smooth(self):
  self.assertLess(d['after']['metrics']['peak_angular_deg_per_frame'],1.2)
  self.assertLess(d['after']['metrics']['peak_angular_deg_per_frame'],.7*d['before']['metrics']['peak_angular_deg_per_frame'])
 def test_translation_has_no_abrupt_join(self):
  self.assertLess(d['after']['metrics']['peak_acceleration'],.23)
  self.assertLess(d['after']['metrics']['peak_acceleration'],d['before']['metrics']['peak_acceleration'])
 def test_ship_horizon_stays_level(self):
  self.assertLess(d['after']['metrics']['peak_roll_deg'],.15)

if __name__=='__main__':unittest.main(verbosity=2)
