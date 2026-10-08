"""Read-only final package integrity gate; run after all logs/reports are sealed."""
import hashlib,json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
class Manifest(unittest.TestCase):
 def test_every_registered_artifact_matches(self):
  entries=json.loads((R/'hashes.json').read_text());bad=[]
  for name,expected in entries.items():
   file=R/name
   if not file.is_file() or hashlib.sha256(file.read_bytes()).hexdigest()!=expected:bad.append(name)
  self.assertEqual(bad,[])
if __name__=='__main__':unittest.main(verbosity=2)
