"""Breaks: reversed time, lost endpoint/event, compounded speed, stop at camera join."""
import unittest, math
from motion import TimeMap,hermite,patch_tangent
class TimeTests(unittest.TestCase):
 def test_compression_shortens_only_the_named_interval(self):
  m=TimeMap(100,compression=[(20,80,20)])
  self.assertAlmostEqual(m.forward(20),20)
  self.assertAlmostEqual(m.forward(50),40)
  self.assertAlmostEqual(m.forward(80),60)
  self.assertAlmostEqual(m.forward(100),80)
 def test_ease_spends_more_time_near_start_and_finish(self):
  m=TimeMap(100,easing=[(0,100,.15)])
  self.assertGreater(m.forward(25),25)
  self.assertLess(m.forward(75),75)
  self.assertEqual(m.forward(0),0)
  self.assertAlmostEqual(m.forward(100),100)
 def test_inverse_recovers_source_subframe(self):
  m=TimeMap(100,compression=[(20,80,20)])
  self.assertAlmostEqual(m.inverse(40),50,places=6)
  for f in [0,.25,19.75,30.125,50.5,99.875,100]:self.assertAlmostEqual(m.inverse(m.forward(f)),f,places=6)
 def test_zero_or_reversed_span_rejected(self):
  for span in [(50,50,1),(80,20,1),(-1,20,1)]:
   with self.assertRaises(ValueError):TimeMap(100,compression=[span])
 def test_combined_compression_cannot_reverse_or_stop_time(self):
  with self.assertRaises(ValueError):TimeMap(100,compression=[(0,100,30),(0,100,30)])
 def test_nan_or_outside_domain_rejected(self):
  m=TimeMap(100)
  for f in [-1,101,math.nan]:
   with self.assertRaises(ValueError):m.forward(f)
 def test_event_order_monotone_and_boundary_rate_is_not_zero(self):
  m=TimeMap(100,easing=[(0,50,.12),(50,100,.12)],compression=[(10,40,7)])
  samples=[m.forward(i/10) for i in range(1001)]
  self.assertTrue(all(b>a for a,b in zip(samples,samples[1:])))
  self.assertAlmostEqual(m.derivative(50),1)
  self.assertAlmostEqual(m.derivative(49.999),m.derivative(50.001),places=5)
class CameraTests(unittest.TestCase):
 def test_hermite_preserves_nonzero_endpoint_velocity(self):
  eps=.00001
  self.assertAlmostEqual(hermite(0,10,2,3,0,10),0)
  self.assertAlmostEqual(hermite(0,10,2,3,1,10),10)
  self.assertAlmostEqual((hermite(0,10,2,3,eps,10)-0)/(eps*10),2,places=3)
  self.assertAlmostEqual((10-hermite(0,10,2,3,1-eps,10))/(eps*10),3,places=3)
 def test_camera_join_tangent_is_shared_and_nonzero(self):
  self.assertAlmostEqual(patch_tangent(2,10,4),2)
if __name__=='__main__':unittest.main()
