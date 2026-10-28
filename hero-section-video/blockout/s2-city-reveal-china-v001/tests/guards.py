import bpy,unittest,sys,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from build import guard
SOURCE=Path(bpy.data.filepath);SHA=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
class Guards(unittest.TestCase):
 def test_same_path(self):
  with self.assertRaises(ValueError):guard(SOURCE,SOURCE,SHA)
 def test_input_directory(self):
  with self.assertRaises(ValueError):guard(SOURCE,R/'inputs/forbidden.blend',SHA)
 def test_external_output(self):
  with self.assertRaises(ValueError):guard(SOURCE,R.parent/'forbidden.blend',SHA)
 def test_existing_output(self):
  with self.assertRaises(FileExistsError):guard(SOURCE,R/'baseline-with-title.blend',SHA)
 def test_bad_source_hash(self):
  with self.assertRaises(ValueError):guard(SOURCE,R/'unused.blend','bad hash')
 def test_duplicate_application(self):
  self.assertTrue(any(o.get('s2_reveal_owner') for o in bpy.data.objects))
  with self.assertRaisesRegex(ValueError,'already applied'):guard(SOURCE,R/'unused.blend',SHA)
result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Guards))
if not result.wasSuccessful():raise SystemExit(1)
