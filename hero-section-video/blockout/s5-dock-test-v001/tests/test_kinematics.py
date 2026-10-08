"""Motion contracts, exercised on measured Blender states or the new path engine."""
import unittest,math,json,importlib.util,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));CFG=json.loads((R/'config.json').read_text())
def angle(a,b):return math.degrees(math.acos(max(-1,min(1,sum(x*y for x,y in zip(a,b))/math.hypot(*a)/math.hypot(*b)))))
class MotionContract(unittest.TestCase):
 def test_rear_axle_forward_matches_motion_through_both_joins(self):
  if '--baseline' in sys.argv:
   data=json.loads((R/'review/baseline-survey.json').read_text())['motion'];rows=[]
   for a,b in zip(data,data[1:]):
    if not 720<=a['frame']<809:continue
    x=a['objects']['A03_TRACTOR'];y=b['objects']['A03_TRACTOR'];v=[y['p'][i]-x['p'][i] for i in [0,1]]
    if math.hypot(*v)>.0001:rows.append(angle(v,[(x['forward'][i]+y['forward'][i])/2 for i in [0,1]]))
   self.assertLessEqual(max(rows),CFG['thresholds']['tangent_degrees']);return
  spec=importlib.util.find_spec('kinematics');self.assertIsNotNone(spec,'Missing smooth join correction')
  from kinematics import vehicle_state
  for j in range(649*4,810*4):
   f=j/4;a=vehicle_state(f,CFG);b=vehicle_state(f+.02,CFG)
   for root,yaw in [('trailer','trailer_yaw'),('tractor','tractor_yaw')]:
    delta=[b[root][i]-a[root][i] for i in [0,1]]
    if math.hypot(*delta)>.00001:self.assertLess(angle(delta,[math.cos(a[yaw]),math.sin(a[yaw])]),2,(f,root))
 def test_hitch_and_rigid_container_relation_are_preserved(self):
  spec=importlib.util.find_spec('kinematics');self.assertIsNotNone(spec,'Missing kinematic implementation')
  from kinematics import vehicle_state
  for f in [648,700,730,750,780,810,849,870,890,900]:
   d=vehicle_state(f,CFG);p=d['trailer'];a=d['trailer_yaw'];h=d['tractor']
   self.assertLess(math.dist(h,[p[0]+2*math.cos(a),p[1]+2*math.sin(a)]),.002)
 def test_stop_open_then_reverse_keeps_heading_and_reaches_dock(self):
  spec=importlib.util.find_spec('kinematics');self.assertIsNotNone(spec,'Missing stop/reverse implementation')
  from kinematics import vehicle_state
  c=vehicle_state(810,CFG);d=vehicle_state(890,CFG)
  for f in [810,811,826,842,848,849]:self.assertLess(math.dist(c['trailer'],vehicle_state(f,CFG)['trailer']),.002)
  self.assertAlmostEqual(c['trailer'][0],29.2,places=4);self.assertAlmostEqual(d['trailer'][0],34.4,places=4)
  self.assertAlmostEqual(d['trailer'][0]+1.6,36,places=4)
  for f in range(850,891):
   a=vehicle_state(f-1,CFG);b=vehicle_state(f,CFG)
   self.assertGreater(b['trailer'][0],a['trailer'][0]);self.assertAlmostEqual(b['trailer_yaw'],math.pi,places=5)
  self.assertLessEqual(math.dist(c['trailer'],d['trailer']),5.5)
if __name__=='__main__':
 suite=unittest.defaultTestLoader.loadTestsFromTestCase(MotionContract)
 if '--baseline' in sys.argv:suite=unittest.TestSuite([MotionContract('test_rear_axle_forward_matches_motion_through_both_joins')])
 r=unittest.TextTestRunner(verbosity=2).run(suite)
 if not r.wasSuccessful():raise SystemExit(1)
