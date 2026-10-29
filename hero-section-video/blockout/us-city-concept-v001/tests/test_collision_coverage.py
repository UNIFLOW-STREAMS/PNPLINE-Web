import json,sys,unittest
from pathlib import Path
report=json.loads(Path(sys.argv.pop()).read_text())
class CoverageTests(unittest.TestCase):
 def test_independent_load_and_fixed_equipment_audited(self):
  self.assertFalse({'W08_LAST_LOAD','P02_FIXED','WAREHOUSE_FIXED'}-set(report['groups']))
unittest.main()
