"""Retain the accepted v008 path contracts, replacing world-roll lock with port leveling."""
import importlib.util,unittest
from pathlib import Path
R=Path(__file__).resolve().parent
def module(name):
    spec=importlib.util.spec_from_file_location(name,R/(name+'.py'))
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
side=module('test_side_handoff');port=module('test_port_roll')
suite=unittest.TestSuite(side.SideHandoff(n) for n in unittest.defaultTestLoader.getTestCaseNames(side.SideHandoff) if n!='test_city_entry_does_not_pitch_or_roll')
suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(port.PortRoll))
result=unittest.TextTestRunner(verbosity=2).run(suite)
if not result.wasSuccessful():raise AssertionError('Level side-to-rear camera regression')
