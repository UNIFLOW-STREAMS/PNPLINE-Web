import bpy, unittest, math, json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[1]
S=bpy.context.scene
class S1CameraTests(unittest.TestCase):
    def elevation(self,f):
        S.frame_set(f)
        inv=bpy.data.objects['CN_FRAME'].matrix_world.inverted()
        p=inv@S.camera.matrix_world.translation
        t=inv@bpy.data.objects['A01_CONTAINER'].matrix_world.translation
        return math.degrees(math.atan2(p.z-t.z,math.hypot(p.x-t.x,p.y-t.y)))
    def test_starts_at_frame_zero_and_low_angle(self):
        self.assertEqual(S.frame_start,0)
        self.assertLess(self.elevation(0),-10)
    def test_s1_rises_to_reference_high_angle(self):
        heights=[]; angles=[]
        for f in range(97):
            angles.append(self.elevation(f))
            inv=bpy.data.objects['CN_FRAME'].matrix_world.inverted()
            heights.append((inv@S.camera.matrix_world.translation).z)
        self.assertGreater(angles[-1],15)
        self.assertTrue(all(b>=a-.002 for a,b in zip(heights,heights[1:])), 'Camera must ascend')
        self.assertTrue(all(b>=a-.02 for a,b in zip(angles,angles[1:])), 'Angle must progress upward')
    def test_container_readable_through_s1(self):
        for f in range(97):
            S.frame_set(f);o=bpy.data.objects['A01_CONTAINER']
            pts=[world_to_camera_view(S,S.camera,o.matrix_world@Vector((x,y,z))) for x in [-1.6,1.6] for y in [-.8,.8] for z in [-.75,.75]]
            self.assertTrue(all(.03<p.x<.97 and .03<p.y<.97 and p.z>0 for p in pts),f'Container cropped at {f}')
        self.assertGreater(max(p.x for p in pts)-min(p.x for p in pts),.29,'End reference needs close framing')
    def test_s1_s2_connection_has_no_camera_reset(self):
        for f in [96,160]:
            mats=[]
            for t in [f-1,f,f+1]:S.frame_set(t);mats.append(S.camera.matrix_world.copy())
            a,b,c=[m.translation for m in mats]
            self.assertLess((c-2*b+a).length,.05)
            self.assertLess((c-a).length,1)
if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(S1CameraTests))
    (ROOT/'logs/s1-test-result.json').write_text(json.dumps({'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors)},indent=2))
    if not result.wasSuccessful():raise SystemExit(1)
