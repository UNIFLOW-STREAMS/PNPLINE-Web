import bpy,sys,json,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from preservation import capture,sha
from build_s5_test import build
p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--output-dir',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);cfg=json.loads(Path(a.config).read_text());master=bpy.data.scenes[cfg['source_scene']];test=bpy.data.scenes[cfg['test_scene']]
baseline=capture(master);original=capture(test)
def counts():return {name:len(getattr(bpy.data,name)) for name in ['objects','scenes','collections','actions','cameras','curves','meshes']}
before=counts();bpy.context.window.scene=test;test.frame_set(810)
for name,path,value in [('S5T__A03_TRAILER','location',900),('S5T__A01_DOOR_L','rotation_euler',1.23)]:
 o=bpy.data.objects[name];getattr(o,path)[0]=value;o.keyframe_insert(path,frame=810)
cam=bpy.data.objects['S5T__CAM_OBLIQUE'];cam.data.lens=110;cam.data.keyframe_insert('lens',frame=810)
unchanged=baseline==capture(master);assert unchanged,'Clone mutation changed master'
# The temporary lens action is test-owned too, allowing controlled cleanup.
cam.data.animation_data.action['s5_owner']=test['s5_owner'];cam.data.animation_data.action.name='S5T__temporary_lens_action'
build(cfg);rebuilt=capture(bpy.data.scenes[cfg['test_scene']]);after=counts();assert original==rebuilt,'Regeneration differs';assert before==after,(before,after);assert capture(master)==baseline
out=dict(pass_all=True,mutation_preserves_master=True,regeneration_semantic_equal=True,counts_before=before,counts_after=after,test_signature=sha(original),master_signature=sha(baseline),saved=False)
(Path(a.output_dir)/'reproduction-validation.json').write_text(json.dumps(out,indent=2),encoding='utf8');print('REPRODUCTION',out)
