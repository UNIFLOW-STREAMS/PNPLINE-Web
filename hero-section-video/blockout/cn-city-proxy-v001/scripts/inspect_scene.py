"""Read-only scene inspection and baseline render; never imports old builder."""
import bpy, json, sys, hashlib, importlib.util, unittest
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
s=bpy.context.scene
s.frame_set(96)
cn=s.objects['CN_FRAME'].matrix_world.copy(); inv=cn.inverted()
out={'version':bpy.app.version_string,'file':bpy.data.filepath,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'scene':s.name,'camera':s.camera.name,'fps':s.render.fps,'fps_base':s.render.fps_base,'range':[s.frame_start,s.frame_end],'scene_props':dict(s.items()),'markers':[(m.name,m.frame,m.camera.name if m.camera else None) for m in s.timeline_markers],'cn_matrix':list(map(list,cn)),'objects':{}}
for o in s.objects:
    pts=[inv@o.matrix_world@Vector(c) for c in o.bound_box] if o.type=='MESH' else [inv@o.matrix_world.translation]
    out['objects'][o.name]={'type':o.type,'parent':o.parent.name if o.parent else None,'local_location':list(o.location),'cn_bounds':[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]],'props':dict(o.items()),'hidden':[o.hide_render,o.hide_viewport,o.hide_get()]}
out['camera_samples']={}
for f in [0,84,96,124,148,180,216,278,330,450,456,480]:
    s.frame_set(f)
    out['camera_samples'][f]={'camera_cn':list(inv@s.camera.matrix_world.translation),'target_cn':list(inv@s.objects['CAM_LOOK_TARGET'].matrix_world.translation),'lens':s.camera.data.lens,'ship_cn':list(inv@s.objects['A02_SHIP'].matrix_world.translation)}
(R/'review/scene-inventory.json').write_text(json.dumps(out,indent=2,default=str))
print('INSPECT',out['version'],out['scene'],out['fps'],out['range'],len(s.objects))
spec=importlib.util.spec_from_file_location('baseline_tests',str(R.parent/'s5-integration-v001/tests/master_regression.py'))
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(mod.MasterTests))
(R/'review/baseline-tests.json').write_text(json.dumps({'tests':result.testsRun,'failures':[(str(t),e) for t,e in result.failures],'errors':[(str(t),e) for t,e in result.errors]},indent=2))
print('BASELINE_TESTS',result.testsRun,len(result.failures),len(result.errors))
