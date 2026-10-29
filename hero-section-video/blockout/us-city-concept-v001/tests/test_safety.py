"""Guard regressions: input overwrite, output escape, output collision, wrong base."""
import importlib.util,tempfile,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
class SafetyTests(unittest.TestCase):
 def test_render_directory_rejects_escape_and_reuse(self):
  spec=importlib.util.spec_from_file_location('safety',R/'scripts/safety.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  self.assertTrue(hasattr(m,'output_directory'),'Render paths bypass guards')
  with tempfile.TemporaryDirectory(dir=R/'tests') as tmp:
   root=Path(tmp)
   for label in ['../inputs','../../escape','C:/tmp/out','a/b','a\\b']:
    with self.assertRaises(ValueError):m.output_directory(root,'review',label)
   with self.assertRaises(ValueError):m.output_directory(root,'inputs','valid')
   p=m.output_directory(root,'review','valid-001');self.assertTrue(p.is_dir())
   with self.assertRaises(FileExistsError):m.output_directory(root,'review','valid-001')
 def test_output_guard_exists(self):
  self.assertTrue((R/'scripts/safety.py').exists(),'Missing output safety module')
 def test_guard_real_paths(self):
  if not (R/'scripts/safety.py').exists():self.fail('Missing output guard')
  spec=importlib.util.spec_from_file_location('safety',R/'scripts/safety.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  with tempfile.TemporaryDirectory(dir=R/'tests') as tmp:
   root=Path(tmp);base=root/'inputs/base.blend';base.parent.mkdir();base.write_bytes(b'baseline')
   self.assertEqual(m.guard(root,root/'candidate.blend',base,'8ba8496a2525ae171ffd104d632dede6ef418d9b95962a9d88e2fcdbc8d48d24'),root/'candidate.blend')
   for p in [base,root.parent/'escape.blend',root/'inputs/new.blend']:
    with self.assertRaises((ValueError,FileExistsError)):m.guard(root,p,base,None)
   used=root/'used.blend';used.write_bytes(b'keep')
   with self.assertRaises(FileExistsError):m.guard(root,used,base,None)
   with self.assertRaises(ValueError):m.guard(root,root/'new.blend',base,'wrong')
   self.assertEqual(base.read_bytes(),b'baseline');self.assertEqual(used.read_bytes(),b'keep')
unittest.main()
