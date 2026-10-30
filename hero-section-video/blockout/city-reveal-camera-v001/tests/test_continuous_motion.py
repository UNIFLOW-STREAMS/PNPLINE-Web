"""Reject the stop/start motion at the joins of the accepted camera route."""
import bpy,unittest,json
from pathlib import Path
s=bpy.context.scene
points={}
for f in range(407,698):
 s.frame_set(f);points[f]=s.camera.matrix_world.translation.copy()
speeds={f:(points[f+1]-points[f]).length for f in range(408,697)}
print('JOIN_SPEEDS',json.dumps({f:round(speeds[f],6) for f in [408,430,439,440,441,445,455,479,496,499,500,503,504,510,552,590,595,596,600,640,647,648,649,650,660,672]}))
class ContinuousMotion(unittest.TestCase):
 def test_no_stop_at_entry_side_or_rear_join(self):
  for a,b in [(438,455),(492,515),(586,610),(640,674)]:
   slow=min((speeds[f],f) for f in range(a,b+1))
   self.assertGreater(slow[0],.10,str(slow))
 def test_velocity_connects_without_a_jump(self):
  acceleration=[((points[f+1]-2*points[f]+points[f-1]).length,f) for f in range(438,611)]
  self.assertLess(max(acceleration)[0],.12,str(max(acceleration)))
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ContinuousMotion))
 if not result.wasSuccessful():raise AssertionError('Camera stops or jumps at a path join')
