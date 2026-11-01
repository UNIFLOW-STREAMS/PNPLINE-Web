import bpy,sys,json,time,importlib.util
from pathlib import Path
R=Path(__file__).resolve().parents[1];S=bpy.context.scene;label=sys.argv[-1]
spec=importlib.util.spec_from_file_location('framing',R.parents[1]/'blockout/cn-shanghai-density-v001/scripts/render_review.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='OPTIX';pref.get_devices()
for d in pref.devices:d.use=d.type=='OPTIX'
S.render.engine='CYCLES';S.cycles.device='GPU' if any(d.use for d in pref.devices) else 'CPU';S.cycles.samples=40;S.cycles.use_denoising=True;S.render.use_persistent_data=True
S.render.resolution_percentage=100;S.render.resolution_x=1600;S.render.resolution_y=900;S.render.use_border=False
S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGB';S.render.image_settings.color_depth='8'
active=S.camera;stats=[]
for f in [57,132,390,600,780]:
 S.frame_set(f);S.render.filepath=str(R/'review'/f'{label}-{f:04d}.png');start=time.time();bpy.ops.render.render(write_still=True);stats.append(dict(frame=f,seconds=time.time()-start))
S.frame_set(57);S.render.resolution_y=1000
cam,meta=mod.diagnostic_camera(S,'skyline',dict(bounds=[[-15,8],[17,29],[-3,23]],direction=[.35,-1,.65],margin=1.06,description='Shanghai material study'),1.6)
S.render.filepath=str(R/'review'/f'{label}-skyline.png');bpy.ops.render.render(write_still=True)
S.camera=active
(R/'review'/f'{label}-render.json').write_text(json.dumps(stats,indent=2))
