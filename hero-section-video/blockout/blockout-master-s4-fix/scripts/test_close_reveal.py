"""Regression for the user-rejected f502 panorama, frozen before camera patch."""
import bpy,json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scene_evidence import capture,bounds
R=Path(__file__).resolve().parents[1]
B=json.loads((R/'review/close-reveal/before-states.json').read_text(encoding='utf-8'))
A=capture();S=bpy.context.scene
boxes={}
for f in range(486,511):
 S.frame_set(f);boxes[f]=bounds('A02_SHIP')
class CloseReveal(unittest.TestCase):
 def test_ship_remains_foreground_during_reveal(self):
  # The board's ship fills roughly 40% of picture width. The shorter proxy
  # needs at least 42% width and 35% height, not the old 24%-width-only gate.
  # Apply over the reveal, not a single chosen pose. Real renders remain required.
  for f in range(494,507):
   b=boxes[f]
   self.assertGreaterEqual(b[2]-b[0],.42,(f,'width',b))
   self.assertGreaterEqual(b[3]-b[1],.35,(f,'height',b))
 def test_whole_ship_stays_inside_reveal(self):
  for f,b in boxes.items():
   self.assertGreaterEqual(min(b),.015,(f,b))
   self.assertLessEqual(max(b),.985,(f,b))
 def test_later_camera_and_entry_are_exact(self):
  for f in list(range(458))+list(range(522,1393)):
   for key in ['camera','target','lens']:
    self.assertEqual(A['frames'][f][key],B['frames'][f][key],(f,key))
 def test_latest_saved_objects_and_motion_are_preserved(self):
  for key in ['objects','materials','fps','range','markers','camera_clip']:
   self.assertEqual(A[key],B[key],key)
  self.assertEqual(A['metadata']['events'],B['metadata']['events'])
  self.assertEqual([f['noncamera'] for f in A['frames']],[f['noncamera'] for f in B['frames']])
if __name__=='__main__':
 label=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'test'
 (R/'review/close-reveal'/f'{label}-ship-bounds.json').write_text(json.dumps(boxes,indent=2),encoding='utf-8')
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(CloseReveal))
 if not result.wasSuccessful():raise SystemExit(1)
