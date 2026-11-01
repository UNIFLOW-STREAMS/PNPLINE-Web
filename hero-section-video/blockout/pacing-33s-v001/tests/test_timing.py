import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from timing import TimeMap,CONFIG

class Timing(unittest.TestCase):
    def test_exact_duration_and_section_budgets(self):
        self.assertEqual(CONFIG['frame_count']/CONFIG['fps'],33)
        self.assertEqual([r[4]-r[3] for r in CONFIG['sections']],[75,90,150,150,195,210,120])

    def test_clock_never_stops_or_reverses(self):
        m=TimeMap()
        speeds=[m.speed(i/8) for i in range(989*8+1)]
        self.assertGreater(min(speeds),.35)
        self.assertLess(max(speeds),2.8)

    def test_joins_have_continuous_velocity(self):
        m=TimeMap()
        for t in m.x[1:-1]:
            self.assertLess(abs(m.speed(t-.001)-m.speed(t+.001)),.003)

    def test_endpoints_and_roundtrip(self):
        m=TimeMap()
        self.assertEqual(m.source(0),0)
        self.assertAlmostEqual(m.source(989),1392)
        for f in range(1393):
            self.assertAlmostEqual(m.source(m.output(f)),f,places=7)

    def test_door_reverse_and_loading_remain_readable(self):
        m=TimeMap()
        for start,end,minimum in [(811,842,1.19),(849,890,1.49),(1150,1166,.64),(1074,1090,.54)]:
            self.assertGreaterEqual((m.output(end)-m.output(start))/30,minimum)
        self.assertLess(m.output(842),m.output(849))
        self.assertLess(m.output(1166),m.output(1168))

if __name__=='__main__': unittest.main(verbosity=2)
