"""Catch the visible pitch dip and horizon roll in the city-entry transition."""
import bpy,math,unittest
from mathutils import Vector
s=bpy.context.scene
def attitude():
 q=s.camera.matrix_world.to_quaternion();forward=q@Vector((0,0,-1));right=q@Vector((1,0,0))
 level_right=forward.cross(Vector((0,0,1))).normalized();level_up=level_right.cross(forward).normalized()
 return math.degrees(math.asin(max(-1,min(1,forward.z)))),math.degrees(math.atan2(right.dot(level_up),right.dot(level_right)))
class PitchLock(unittest.TestCase):
 def test_entry_and_city_hold_do_not_change_pitch(self):
  values=[]
  for tick in range(440*2,552*2+1):
   s.frame_set(tick//2,subframe=(tick%2)/2);values.append(attitude()[0])
  self.assertLess(max(values)-min(values),.02,('pitch span',max(values)-min(values)))
 def test_entry_and_city_hold_do_not_roll_the_horizon(self):
  values=[]
  for tick in range(440*2,552*2+1):
   s.frame_set(tick//2,subframe=(tick%2)/2);values.append(attitude()[1])
  self.assertLess(max(values)-min(values),.02,('roll span',max(values)-min(values)))
 def test_pitch_does_not_snap_at_entry_or_handoff(self):
  previous=None;steps=[]
  for f in range(438,651):
   s.frame_set(f);p,r=attitude()
   if previous is not None:steps.append(max(abs(p-previous[0]),abs(r-previous[1])))
   previous=(p,r)
  self.assertLess(max(steps),.42,('pitch/roll step',max(steps)))
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(PitchLock))
 if not result.wasSuccessful():raise AssertionError('Pitch/roll lock regression')
