import bpy,importlib.util,unittest,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('master_suite',str(R.parent/'s5-integration-v001/tests/master_regression.py'))
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(mod.MasterTests))
(R/'review/final-master-tests.json').write_text(json.dumps({'tests':r.testsRun,'failures':[(str(t),e) for t,e in r.failures],'errors':[(str(t),e) for t,e in r.errors]},indent=2))
if not r.wasSuccessful():raise SystemExit(1)
