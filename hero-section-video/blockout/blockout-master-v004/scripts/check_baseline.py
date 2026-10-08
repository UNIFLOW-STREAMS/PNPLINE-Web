"""Run existing v003 behavioral tests without overwriting original test logs."""
import importlib.util, unittest, json, sys
sys.dont_write_bytecode=True
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=ROOT.parent/'blockout-master-v003/scripts'
suite=unittest.TestSuite()
for name in ['test_scene','test_s1_camera','test_framing']:
    spec=importlib.util.spec_from_file_location(name,source/(name+'.py'))
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))
r=unittest.TextTestRunner(verbosity=2).run(suite)
(ROOT/'logs/baseline-tests.json').write_text(json.dumps({'tests':r.testsRun,'failures':r.failures,'errors':r.errors},default=str,indent=2),encoding='utf-8')
if not r.wasSuccessful(): raise SystemExit(1)
