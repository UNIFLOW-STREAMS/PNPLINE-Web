"""Run all24 original master behavior tests at matched source times."""
import bpy,sys,json,runpy,unittest,hashlib
from bpy_extras.object_utils import world_to_camera_view as project
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from motion import TimeMap
cfg=json.loads((R/'config.json').read_text())
class SourceTimeScene:
 def __init__(self,scene,m):self.scene=scene;self.m=m
 def __getattr__(self,k):return getattr(self.scene,k)
 def __getitem__(self,k):return self.scene[k]
 def frame_set(self,frame,subframe=0,**kwargs):
  t=self.m.forward(frame+subframe);self.scene.frame_set(int(t),subframe=t%1,**kwargs)
for variant in ['A','B']:
 path=R/f'master-motion-polish-{variant}.blend';bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;m=TimeMap(1392,cfg['easing'],cfg['compression_B'] if variant=='B' else [])
 original=R.parent/'s5-integration-v001/tests/master_regression.py';ns=runpy.run_path(str(original));cls=ns['MasterTests'];cls.at.__globals__['S']=SourceTimeScene(s,m)
 cls.at.__globals__['world_to_camera_view']=lambda scene,camera,point:project(scene.scene,camera,point)
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(cls))
 record={'variant':variant,'test_source':str(original),'test_source_sha256':hashlib.sha256(original.read_bytes()).hexdigest(),'blend_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'tests':result.testsRun,'failures':[(str(t),e) for t,e in result.failures],'errors':[(str(t),e) for t,e in result.errors],'adapter':'Only scene.frame_set(source) maps to candidate output time; all original assertions unchanged'}
 (R/'review'/f'master-regression-{variant}.json').write_text(json.dumps(record,indent=2),encoding='utf8')
 assert result.wasSuccessful(),record
