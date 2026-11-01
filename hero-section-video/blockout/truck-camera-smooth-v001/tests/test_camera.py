"""Acceptance checks use independently sampled, reopened camera poses."""
import json,math,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
d=json.loads((R/'review/motion.json').read_text())

class Camera(unittest.TestCase):
 def test_high_speed_spikes_are_removed(self):
  a,b=d['before']['metrics'],d['after']['metrics']
  self.assertLess(b['speed_units_per_frame']['max'],1.05)
  self.assertLess(b['speed_units_per_frame']['mean'],a['speed_units_per_frame']['mean']*.85)
 def test_translation_is_continuous(self):
  self.assertLess(d['after']['metrics']['acceleration']['max'],.07)
  self.assertLess(d['after']['metrics']['jerk']['max'],.02)
 def test_rotation_is_continuous(self):
  self.assertLess(d['after']['metrics']['peak_angular_deg_per_frame'],3.2)
 def test_horizon_stays_level(self):
  self.assertLess(d['after']['metrics']['peak_roll_deg'],.15)
 def test_truck_center_stays_in_frame(self):
  for row in d['after']['rows']:
   if 467<=row['frame']<=565:
    x,y,z=row['screen'];self.assertGreater(z,0)
    self.assertTrue(.12<x<.88 and .12<y<.88,(row['frame'],x,y))
 def test_join_windows_do_not_create_new_jumps(self):
  rows=d['after']['rows']
  for start,end in [(439,468),(589,621)]:
   points=[row for row in rows if start<=row['frame']<=end]
   v=[[2*(b-a) for a,b in zip(x['eye'],y['eye'])] for x,y in zip(points,points[1:])]
   acceleration=[math.sqrt(sum((2*(b-a))**2 for a,b in zip(x,y))) for x,y in zip(v,v[1:])]
   self.assertLess(max(acceleration),.10,(start,max(acceleration)))

if __name__=='__main__':unittest.main(verbosity=2)
