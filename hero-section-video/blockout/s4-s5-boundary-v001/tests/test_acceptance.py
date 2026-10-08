"""Mandatory acceptance checks deliberately remain RED for unresolved scope conflicts."""
import json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];d=json.loads((R/'review/after-validation.json').read_text());cfg=json.loads((R/'config.json').read_text(encoding='utf-8-sig'));t=cfg['thresholds'];m=d['metrics']
class Acceptance(unittest.TestCase):
 def test_boundary_warehouse_surface_visible(self):self.assertGreaterEqual(d['visibility']['648']['E08_WAREHOUSE']['fraction'],t['warehouse_visible_fraction_min'])
 def test_destination_retained_through_handoff(self):self.assertGreaterEqual(d['visibility']['720']['E08_WAREHOUSE']['fraction'],t['warehouse_visible_fraction_min'],'Original protected follow-up camera drops the destination; expansion required')
 def test_all_wheels_supported_at_departure(self):self.assertLessEqual(max(abs(w['gap']) for row in d['rows'] if row['frame']>=648 for w in row['support']),t['support_gap_m'],'Inherited 0.20m quay penetration; coordinated support correction required')
 def test_facilities_clear_entire_vehicle(self):self.assertEqual(d['collisions'],[])
 def test_camera_clearance(self):self.assertEqual(d['camera_collisions'],[])
 def test_hitch_connected(self):self.assertLess(m['hitch_gap_max'],t['hitch_m'])
 def test_cargo_relative_transform_fixed(self):self.assertLess(m['container_relative_drift_max'],t['relative_m'])
 def test_camera_motion_limits(self):self.assertLess(m['camera_speed_max'],t['camera_speed_m_frame']);self.assertLess(m['camera_angle_max'],t['camera_angle_deg_frame'])
 def test_lens_range(self):
  self.assertTrue(all(t['lens_min_mm']<=row['lens']<=t['lens_max_mm'] for row in d['rows']))
 def test_hoist_separated(self):self.assertGreater(d['states']['648']['hoist_bottom']-d['states']['648']['container_top'],.01)
 def test_saved_reproduction(self):
  a=json.loads((R/'review/after-signature.json').read_text());b=json.loads((R/'review/reproduced-signature.json').read_text());self.assertEqual(a,b)
 def test_seat_plane_corners_and_payload(self):
  rows=json.loads((R/'review/contacts.json').read_text());base=rows[0]['payload_relative']
  self.assertLess(max(abs(v) for r in rows for v in r['seat_plane_corner_gaps']),t['relative_m'])
  self.assertLess(max(abs(r['payload_relative'][i][j]-base[i][j]) for r in rows for i in range(4) for j in range(4)),t['relative_m'])
 def test_doors_closed_ship_stationary(self):
  rows=json.loads((R/'review/contacts.json').read_text());self.assertTrue(all(abs(v)<1e-5 for r in rows for door in r['doors'].values() for v in door));self.assertTrue(all(r['ship_matrix']==rows[0]['ship_matrix'] for r in rows))
 def test_reopened_pixels(self):
  from PIL import Image
  for f in ['0648','0720']:
   with Image.open(R/f'review/after/{f}.png') as a, Image.open(R/f'review/reopened/{f}.png') as b:self.assertEqual(a.size,b.size);self.assertEqual(a.convert('RGBA').tobytes(),b.convert('RGBA').tobytes())
 def test_validation_matches_current_saved_file(self):
  import hashlib
  self.assertEqual(d['sha256'],hashlib.sha256((R/'master-s4-s5-boundary-v001.blend').read_bytes()).hexdigest())
 def test_original_and_input_copy_unchanged(self):
  import hashlib
  for file in [R/'inputs/master-s4-fix.blend',R.parent/'blockout-master-s4-fix/master-s4-fix.blend']:self.assertEqual(hashlib.sha256(file.read_bytes()).hexdigest(),cfg['source_sha256'])
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Acceptance))
 (R/'review/acceptance-result.json').write_text(json.dumps(dict(tests=result.testsRun,failures=[str(t) for t,_ in result.failures],errors=[str(t) for t,_ in result.errors],passed=result.wasSuccessful()),indent=2))
 raise SystemExit(0 if result.wasSuccessful() else 1)
