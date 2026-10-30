"""The port should read level while the accepted camera path stays unchanged."""
import bpy, math, unittest
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
s=bpy.context.scene

class PortRoll(unittest.TestCase):
    def test_quay_edge_is_horizontal_during_side_view(self):
        samples=[]
        for half in range(980,1025):
            s.frame_set(half//2,subframe=(half%2)/2)
            u=s.objects['US_FRAME'].matrix_world
            a,b=[world_to_camera_view(s,s.camera,u@Vector(p)) for p in [(-10,4,.4),(10,4,.4)]]
            angle=math.degrees(math.atan2((b.y-a.y)*s.render.resolution_y,(b.x-a.x)*s.render.resolution_x))
            angle=(angle+90)%180-90
            samples.append((abs(angle),half/2))
        self.assertLess(max(samples)[0],.1,str(max(samples)))

    def test_ship_long_side_reads_nearly_horizontal_at_497(self):
        s.frame_set(497)
        ship=s.objects['A02_SHIP']
        a,b=[world_to_camera_view(s,s.camera,ship.matrix_world@Vector(p)) for p in [(-6,-2.6,0),(6,-2.6,0)]]
        angle=math.degrees(math.atan2((b.y-a.y)*s.render.resolution_y,(b.x-a.x)*s.render.resolution_x))
        angle=(angle+90)%180-90
        self.assertLess(abs(angle),5,str(angle))

    def test_entry_pitch_is_still_constant(self):
        values=[]
        for half in range(880,1009):
            s.frame_set(half//2,subframe=(half%2)/2)
            front=s.camera.matrix_world.to_quaternion()@Vector((0,0,-1))
            values.append(math.degrees(math.asin(max(-1,min(1,front.z)))))
        self.assertLess(max(values)-min(values),.02)

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(PortRoll))
    if not result.wasSuccessful(): raise AssertionError('Port roll is visibly tilted')
