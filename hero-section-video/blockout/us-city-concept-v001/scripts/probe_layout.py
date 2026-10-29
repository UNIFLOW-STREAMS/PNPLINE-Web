import bpy,json,ast,unittest,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];s=bpy.context.scene
label=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'baseline'
if label not in {'baseline','candidate-final'}:raise ValueError('Unknown survey label')
rows=[]
for f in [216,280,330,360,390,421,456,480,510,532,600,648,720,900,1200,1392]:
 s.frame_set(f);inv=s.objects['US_FRAME'].matrix_world.inverted()
 rows.append({'frame':f,'camera':list(inv@s.camera.matrix_world.translation),'ship':list(inv@s.objects['A02_SHIP'].matrix_world.translation),'look':list(inv@s.objects['CAM_LOOK_TARGET'].matrix_world.translation)})
(R/'review'/f'{label}-camera-layout.json').write_text(json.dumps(rows,indent=2))
tree=ast.parse((R.parent/'blockout-master-s4-fix/scripts/test_scene.py').read_text())
ns={'bpy':bpy,'json':json,'math':__import__('math'),'unittest':unittest,'Path':Path,'Vector':Vector,'S':s,'ROOT':R,'world_to_camera_view':__import__('bpy_extras.object_utils',fromlist=['world_to_camera_view']).world_to_camera_view}
exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x,ast.ClassDef)],type_ignores=[]),'inherited-test-class','exec'),ns)
result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ns['MasterTests']))
(R/'review'/f'{label}-regression.json').write_text(json.dumps({'tests':result.testsRun,'failures':[(str(t),m) for t,m in result.failures],'errors':[(str(t),m) for t,m in result.errors]},indent=2))
print('LAYOUT',json.dumps(rows))
