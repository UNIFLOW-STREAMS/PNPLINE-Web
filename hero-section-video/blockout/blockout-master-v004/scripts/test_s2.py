"""Behavior probes: early full-ship shrinkage and side-wide ending are regressions.
Projection checks are supporting evidence, not visual similarity acceptance.
"""
import bpy,sys,json,unittest,math
from pathlib import Path
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scene_evidence import bounds,capture
ROOT=Path(__file__).resolve().parents[1];S=bpy.context.scene
mode=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'limited'
base=json.loads((ROOT/'review/baseline-full.json').read_text())
class S2Tests(unittest.TestCase):
 def test_k2_keeps_ship_cropped_and_large(self):
    S.frame_set(124);b=bounds('A02_SHIP')
    self.assertGreater(b[2]-b[0],1.0,'K2 ship must remain a large cropped foreground subject')
 def test_k3_reduces_top_down_distance(self):
    S.frame_set(148);p=bpy.data.objects['A02_SHIP'].matrix_world.inverted()@S.camera.matrix_world.translation
    self.assertLess(p.z,10,'K3 must retain deck/port depth instead of climbing to a distant top view')
 @unittest.skipIf(mode not in ['candidate','integrated'],'Limited alternative deliberately retains old B23')
 def test_candidate_k5_has_large_rear_quarter(self):
    S.frame_set(216);p=bpy.data.objects['A02_SHIP'].matrix_world.inverted()@S.camera.matrix_world.translation;b=bounds('A02_SHIP')
    self.assertGreater(b[2]-b[0],.60,'K5 must remain prominent')
    self.assertGreater(abs(p.x),abs(p.y),'Rearward offset must dominate sideways offset')
    self.assertLess(p.x,-7,'View must lie behind the physical stern')
 def test_noncamera_and_unauthorized_camera_preserved(self):
    now=capture()
    for key in ['objects','materials','fps','range','markers','camera_clip']:self.assertEqual(now[key],base[key],key)
    for a,b in zip(base['frames'],now['frames']):
      self.assertEqual(a['noncamera'],b['noncamera'],str(a['frame']))
      self.assertEqual(a['lens'],b['lens'])
      f=a['frame'];unchanged=(f<=97 or f>=215) if mode=='limited' else (f<=97 or f>=(252 if mode=='integrated' else 217))
      if unchanged:
        self.assertEqual(a['camera'],b['camera'],f'camera {f}')
        self.assertEqual(a['target'],b['target'],f'target {f}')
 @unittest.skipIf(mode not in ['candidate','integrated'],'Applies to the approved K5 composition')
 def test_candidate_stern_and_bow_not_clipped_at_k5(self):
    S.frame_set(216);b=bounds('SHIP_HULL')
    self.assertGreater(min(b[0],b[1]),.03,'Keep stern/bow within the frame')
    self.assertLess(max(b[2],b[3]),.97,'Keep space ahead of the bow')
 def test_continuity_inside_declared_range(self):
    ps=[];qs=[];ts=[]
    for i in range(95*4,(254 if mode=='integrated' else 217)*4+1):
      f=i/4
      if mode=='candidate' and f>216:break
      S.frame_set(int(f),subframe=f-int(f));ps.append(S.camera.matrix_world.translation.copy());qs.append(S.camera.matrix_world.to_quaternion());ts.append(bpy.data.objects['CAM_LOOK_TARGET'].matrix_world.translation.copy())
    self.assertLess(max((ps[i+1]-ps[i]).length for i in range(len(ps)-1)),2.5/4)
    self.assertLess(max(math.degrees(qs[i].rotation_difference(qs[i+1]).angle) for i in range(len(qs)-1)),8/4)
    self.assertLess(max((ts[i+1]-ts[i]).length for i in range(len(ts)-1)),2.5/4)
    if mode in ['limited','integrated']:
      for f in ([96,216,252] if mode=='integrated' else [96,216]):
        p=[]
        for k in [f-1,f,f+1]:S.frame_set(k);p.append(S.camera.matrix_world.translation.copy())
        self.assertLess((p[2]-2*p[1]+p[0]).length,.15)
 @unittest.skipIf(mode!='integrated','Approved S3 join only')
 def test_join_keeps_approved_s2_candidate_and_rejoins_at_252(self):
    expected=json.loads((ROOT/'review/states-candidate.json').read_text())['frames']
    for f in range(98,217):
      S.frame_set(f)
      self.assertEqual([list(r) for r in S.camera.matrix_world],expected[f]['camera'],f'candidate changed at {f}')
    for f in range(216,253):
      ps=[];ts=[]
      for k in [f-1,f,f+1]:
        S.frame_set(k);ps.append(S.camera.matrix_world.translation.copy());ts.append(bpy.data.objects['CAM_LOOK_TARGET'].matrix_world.translation.copy())
      self.assertLess((ps[2]-2*ps[1]+ps[0]).length,.15,f'position acceleration f{f}')
      self.assertLess((ts[2]-2*ts[1]+ts[0]).length,.15,f'target acceleration f{f}')
if __name__=='__main__':
 r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(S2Tests))
 (ROOT/'logs'/('s2-'+mode+'-tests.json')).write_text(json.dumps({'tests':r.testsRun,'failures':r.failures,'errors':r.errors},default=str,indent=2))
 if not r.wasSuccessful():raise SystemExit(1)
