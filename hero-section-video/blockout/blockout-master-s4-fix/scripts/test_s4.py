"""Requirements frozen before S4 patch; finite rays supplemented by real playback."""
import bpy,json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scene_evidence import capture
from s4_metrics import sample
from camera_math import orientation_degrees
from mathutils import Matrix
R=Path(__file__).resolve().parents[1];B=json.loads((R/'review/baseline-full.json').read_text(encoding='utf-8'));A=capture()
obs={f:sample(f) for f in [499,522,532,555,590,615,631,632,638,642,648]}
class S4Requirements(unittest.TestCase):
 def test_entry_has_no_single_frame_roll_spike(self):
  # A camera whose orientation changes ~1 degree/frame at B34 must not roll
  # five degrees on the first revised frame. This complements the broad 8deg cap.
  angles=[orientation_degrees(Matrix(A['frames'][f-1]['camera']).to_quaternion(),Matrix(A['frames'][f]['camera']).to_quaternion()) for f in range(456,482)]
  self.assertLess(max(abs(b-a) for a,b in zip(angles,angles[1:])),1.0,'Abrupt angular-speed change at S4 entry')
 def test_same_scene_and_events(self):
  for k in ['objects','materials','fps','range','markers','camera_clip']:self.assertEqual(B[k],A[k],k)
  self.assertEqual(B['metadata']['events'],A['metadata']['events'])
  self.assertEqual([r['noncamera'] for r in B['frames']],[r['noncamera'] for r in A['frames']])
 def test_unapproved_camera_outside_s4_exact(self):
  join_approved=A['metadata'].get('s4_review_status','').startswith('S4 camera plus user-approved')
  if join_approved:
   approval=json.loads((R/'review/approval-s5-join.json').read_text(encoding='utf-8'))
   self.assertTrue(approval['approved']);self.assertEqual(approval['camera_target_lens_frames'],[649,671])
  for f in list(range(458))+list(range(672 if join_approved else 649,1393)):
   for k in ['camera','target','lens']:self.assertEqual(B['frames'][f][k],A['frames'][f][k],(f,k))
 def test_k2_whole_identifiable_ship(self):
  # At 960 px, at least 230 px width with a 1% border; no cropped reveal.
  box=obs[499]['bounds']['A02_SHIP'];self.assertGreaterEqual(box[2]-box[0],.24)
  self.assertGreater(min(box),.01);self.assertLess(max(box),.99)
 def test_k2_road_and_identifiable_destination(self):
  road=obs[499]['road_points'];self.assertGreaterEqual(sum(p[2]>0 and .01<p[0]<.99 and .01<p[1]<.99 for p in road),3)
  box=obs[499]['bounds']['E08_WAREHOUSE'];self.assertGreater(min(box[2],1)-max(box[0],0),.18)
 def test_k3_seated_cargo_and_receiving_vehicle(self):
  for f in [522,532]:
   self.assertGreater(obs[f]['cargo']['visible_fraction'],.30,(f,'cargo'))
   self.assertGreater(obs[f]['cab']['visible_fraction'],.45,(f,'cab'))
   for n in ['A01_CONTAINER','A03_TRACTOR','A03_TRAILER']:
    box=obs[f]['bounds'][n];self.assertGreater(min(box),.005,(f,n));self.assertLess(max(box),.995,(f,n))
 def test_k4_cargo_and_receive_vehicle_not_cropped(self):
  for f in [555,590,615,631,632]:
   for n in ['A01_CONTAINER','A03_TRACTOR','A03_TRAILER']:
    box=obs[f]['bounds'][n];self.assertGreater(min(box),.005,(f,n));self.assertLess(max(box),.995,(f,n))
 def test_contact_separation_cab_and_cargo_clear(self):
  # No more than 15% weighted crane occlusion of cab/cargo at critical events.
  # Actual renders must still confirm the seat/gap, rays are not pixel proof.
  for f in [631,632,638,642,648]:
   for n in ['cab','cargo']:
    self.assertLess(obs[f][n]['crane_fraction'],.15,(f,n,obs[f][n]))
    self.assertGreater(obs[f][n]['visible_fraction'],.40,(f,n))
 def test_k5_exit_road_and_ship_context(self):
  for f in [642,648]:
   self.assertGreaterEqual(sum(p[2]>0 and .01<p[0]<.99 and .01<p[1]<.99 for p in obs[f]['road_points']),2)
   b=obs[f]['bounds']['A02_SHIP'];self.assertGreater(min(b[2],1)-max(b[0],0),.25)
if __name__=='__main__':
 label=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 's4'
 (R/'review'/f'{label}-metrics.json').write_text(json.dumps(obs,indent=2),encoding='utf-8')
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(S4Requirements))
 if not result.wasSuccessful():raise SystemExit(1)
