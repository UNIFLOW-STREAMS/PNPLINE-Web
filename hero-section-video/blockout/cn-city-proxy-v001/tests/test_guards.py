"""Input/output contract: unsafe paths must fail before any Blender mutation."""
import unittest,sys,tempfile,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from guards import validate_paths
class GuardTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]/'review');self.addCleanup(self.tmp.cleanup)
  self.root=Path(self.tmp.name);self.base=self.root/'base.blend';self.base.write_bytes(b'baseline')
  self.sha=hashlib.sha256(b'baseline').hexdigest()
 def test_same_input_output_refused(self):
  with self.assertRaises(ValueError):validate_paths(self.base,self.base,self.root,self.sha)
 def test_outside_folder_refused(self):
  with self.assertRaises(ValueError):validate_paths(self.base,self.root.parent/'escape.blend',self.root,self.sha)
 def test_existing_output_refused(self):
  out=self.root/'result.blend';out.write_bytes(b'user edits')
  with self.assertRaises(FileExistsError):validate_paths(self.base,out,self.root,self.sha)
  self.assertEqual(out.read_bytes(),b'user edits')
 def test_changed_source_refused(self):
  with self.assertRaises(ValueError):validate_paths(self.base,self.root/'new.blend',self.root,'0'*64)
 def test_new_output_allowed_without_writing(self):
  out=self.root/'new.blend';validate_paths(self.base,out,self.root,self.sha);self.assertFalse(out.exists())
if __name__=='__main__':unittest.main()
