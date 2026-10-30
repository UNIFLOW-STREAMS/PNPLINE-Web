"""Ship side must be established before unloading, with direct travel to truck rear."""
import bpy,math,unittest
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
s=bpy.context.scene
class SideHandoff(unittest.TestCase):
 def test_ship_is_nearly_broadside_before_frame_504(self):
  for f in [500,501,502,503,504]:
   s.frame_set(f);ship=s.objects['A02_SHIP'];p=ship.matrix_world.inverted()@s.camera.matrix_world.translation
   angle=math.degrees(math.atan2(abs(p.x),abs(p.y)))
   self.assertLess(angle,20,(f,angle))
 def test_camera_takes_direct_paths_instead_of_orbiting(self):
  for start,end in [(440,500),(504,592)]:
   points=[]
   for f in range(start,end+1):s.frame_set(f);points.append(s.camera.matrix_world.translation.copy())
   length=sum((b-a).length for a,b in zip(points,points[1:]));chord=(points[-1]-points[0]).length
   self.assertLess(length,chord*1.03,(start,end,length,chord))
 def test_camera_reaches_the_truck_rear_before_container_descent(self):
  for f in [592,600,608,624,648]:
   s.frame_set(f);truck=s.objects['A03_TRAILER'];p=truck.matrix_world.inverted()@s.camera.matrix_world.translation
   self.assertLess(p.x,-8,(f,'camera must be behind trailer'))
   self.assertLess(-p.x,26,(f,'rear tracking must already be close'))
   self.assertLess(math.degrees(math.atan2(abs(p.y),-p.x)),20,(f,'rear view is too lateral'))
 def test_unloading_container_stays_inside_frame(self):
  failures=[]
  for f in range(504,649,4):
   s.frame_set(f);o=s.objects['A01_CONTAINER'];p=[world_to_camera_view(s,s.camera,o.matrix_world@Vector(v)) for v in o.bound_box]
   if any(v.z<=0 or not(.04<v.x<.96 and .04<v.y<.96) for v in p):failures.append(f)
  self.assertFalse(failures,str(failures))
 def test_city_entry_does_not_pitch_or_roll(self):
  pitches=[];rolls=[]
  for f in range(440,505):
   s.frame_set(f);q=s.camera.matrix_world.to_quaternion();front=q@Vector((0,0,-1));right=q@Vector((1,0,0));lr=front.cross(Vector((0,0,1))).normalized();lu=lr.cross(front).normalized()
   pitches.append(math.degrees(math.asin(front.z)));rolls.append(math.degrees(math.atan2(right.dot(lu),right.dot(lr))))
  self.assertLess(max(pitches)-min(pitches),.02);self.assertLess(max(rolls)-min(rolls),.02)
 def test_no_camera_rotation_snap(self):
  last=None;turns=[]
  for f in range(439,650):
   s.frame_set(f);q=s.camera.matrix_world.to_quaternion()
   if last is not None:
    angle=math.degrees(q.rotation_difference(last).angle);turns.append((min(angle,360-angle),f))
   last=q
  self.assertLess(max(turns)[0],2.0,str(max(turns)))
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(SideHandoff))
 if not result.wasSuccessful():raise AssertionError('Ship-side / truck-rear handoff regression')
