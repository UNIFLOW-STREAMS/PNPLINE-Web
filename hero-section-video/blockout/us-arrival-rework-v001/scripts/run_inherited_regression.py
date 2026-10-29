"""Run the unchanged inherited suite and retain named baseline failures."""
import bpy,json,ast,unittest,sys,math,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;file=Path(bpy.data.filepath)
tree=ast.parse((R.parent/'blockout-master-s4-fix/scripts/test_scene.py').read_text())
ns=dict(bpy=bpy,json=json,math=math,unittest=unittest,Path=Path,Vector=Vector,S=s,ROOT=R,world_to_camera_view=world_to_camera_view)
exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x,ast.ClassDef)],type_ignores=[]),'unchanged-inherited-test-class','exec'),ns)
r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ns['MasterTests']))
(R/'review'/f'{file.stem}-inherited-regression.json').write_text(json.dumps({'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'tests':r.testsRun,'failures':[(str(t),m) for t,m in r.failures],'errors':[(str(t),m) for t,m in r.errors]},indent=2))
if not r.wasSuccessful():raise SystemExit(1)
