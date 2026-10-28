"""Import test classes only; retain all original assertions and isolate outputs."""
import bpy,unittest,importlib.util,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
suite=unittest.TestSuite()
for path,cls in [('s2-city-reveal-china-v001/tests/acceptance.py','RevealTests'),('cn-city-proxy-v001/tests/test_proxy.py','ProxyTests'),('s5-integration-v001/tests/master_regression.py','MasterTests')]:
 spec=importlib.util.spec_from_file_location(cls,R.parent/path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(getattr(m,cls)))
r=unittest.TextTestRunner(verbosity=2).run(suite)
(R/'review/baseline-tests.json').write_text(json.dumps({'tests':r.testsRun,'failures':[(str(t),trace) for t,trace in r.failures],'errors':[(str(t),trace) for t,trace in r.errors]},indent=2))
if not r.wasSuccessful():raise SystemExit(1)
