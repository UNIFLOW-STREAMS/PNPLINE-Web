import bpy,sys,time,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];S=bpy.context.scene;label=sys.argv[-1];pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='OPTIX';pref.get_devices()
for d in pref.devices:d.use=d.type=='OPTIX'
S.render.engine='CYCLES';S.cycles.device='GPU';S.cycles.use_denoising=True;S.cycles.samples=24;S.cycles.seed=29;S.cycles.use_animated_seed=False;S.cycles.adaptive_min_samples=16;S.render.use_persistent_data=True;S.render.resolution_percentage=100;S.render.resolution_x=1280;S.render.resolution_y=720;S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGB';S.render.image_settings.color_depth='8'
dest=R/'review'/label;dest.mkdir(parents=True,exist_ok=True)
for f in [132,822,842]:
 S.frame_set(f);S.render.filepath=str(dest/f'f{f:04d}.png');bpy.ops.render.render(write_still=True)
if label=='B':
 S.render.resolution_x=480;S.render.resolution_y=270;S.cycles.samples=8;S.cycles.adaptive_min_samples=8;motion=dest/'motion';motion.mkdir(exist_ok=True)
 for f in range(800,921):
  S.frame_set(f);S.render.filepath=str(motion/f'f{f:04d}.png');bpy.ops.render.render(write_still=True)
  if f%20==0:print('MOTION',f,flush=True)
