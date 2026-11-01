import bpy,sys,json,importlib.util,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];S=bpy.context.scene
spec=importlib.util.spec_from_file_location('framing',R.parents[1]/'blockout/cn-shanghai-density-v001/scripts/render_review.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
label=sys.argv[-1]
pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='OPTIX';pref.get_devices()
for d in pref.devices:d.use=d.type=='OPTIX'
S.render.engine='CYCLES';S.cycles.device='GPU' if any(d.use for d in pref.devices) else 'CPU';S.cycles.samples=32;S.cycles.use_denoising=True
S.render.use_persistent_data=True;S.render.resolution_percentage=100;S.render.use_border=False
S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGB'
active=S.camera
views=[('skyline',1600,1000,[[-15,8],[17,29],[-3,23]],[.35,-1,.65]),('landmarks',1000,1400,[[-8.3,-1.8],[21,25],[-1,19.5]],[.35,-1,.22])]
stats=[]
for name,w,h,bounds,direction in views:
 S.frame_set(57);S.render.resolution_x=w;S.render.resolution_y=h
 cam,meta=mod.diagnostic_camera(S,name,dict(bounds=bounds,direction=direction,margin=1.06,description=name),w/h)
 S.render.filepath=str(R/'review'/f'{label}-{name}.png');t=time.time();bpy.ops.render.render(write_still=True)
 stats.append(dict(view=name,seconds=time.time()-t,framing=meta));S.camera=active;bpy.data.objects.remove(cam,do_unlink=True)
S.frame_set(57);S.render.resolution_x=1920;S.render.resolution_y=1080
S.render.filepath=str(R/'review'/f'{label}-camera-0057.png');bpy.ops.render.render(write_still=True)
(R/'review'/f'{label}-render.json').write_text(json.dumps(stats,indent=2))
