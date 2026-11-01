import json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];d=json.loads((R/'review/motion.json').read_text())
class MicroSmooth(unittest.TestCase):
 def test_translation_jitter_reduced(self):
  self.assertLess(d['after']['metrics']['translation_jerk_max'],.25*d['before']['metrics']['translation_jerk_max'])
 def test_rotation_jitter_reduced(self):
  self.assertLess(d['after']['metrics']['rotation_jerk_max'],.4*d['before']['metrics']['rotation_jerk_max'])
 def test_route_and_framing_stay_close(self):
  self.assertLess(d['deviation']['position'],.25)
  self.assertLess(d['deviation']['rotation_deg'],.25)
  self.assertLess(d['deviation']['projection_pixels'],6.5)
 def test_projection_is_unchanged(self):
  self.assertTrue(d['deviation']['optics_identical'])
 def test_window_endpoints_are_exact(self):
  for row in d['deltas']:
   if row['frame']<=330 or row['frame']>=366:
    self.assertEqual(row['position'],0)
    self.assertLess(row['rotation_deg'],.00001)
    self.assertEqual(row['projection_pixels'],0)

if __name__=='__main__':unittest.main(verbosity=2)
