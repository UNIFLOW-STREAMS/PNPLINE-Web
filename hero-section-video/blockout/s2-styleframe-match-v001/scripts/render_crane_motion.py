import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;ver=Path(bpy.data.filepath).stem.rsplit('-',1)[-1];mode=sys.argv[sys.argv.index('--')+1]if '--'in sys.argv else 'stills'
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.use_denoising=True;s.cycles.samples=16 if mode=='stills'else 6;s.render.threads_mode='FIXED';s.render.threads=10;s.render.use_persistent_data=True;s.render.use_border=False;s.render.image_settings.file_format='PNG';s.render.resolution_percentage=100
s.render.resolution_x=960 if mode=='stills'else 640;s.render.resolution_y=540 if mode=='stills'else 360
frames=[0,24,48,72,96,112,128,144,156,216]if mode=='stills'else list(range(0,217,2))
if mode in ['workbench-probe','workbench-video']:
 s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH'
 if mode=='workbench-probe':frames=[156]
folder=R/'review'/f'crane-motion-{ver}'if mode=='stills'else R/'preview'/f'crane-motion-{ver}-frames';folder.mkdir(exist_ok=True,parents=True)
for f in frames:
 s.frame_set(f);s.render.filepath=str(folder/f'f{f:04d}.png');bpy.ops.render.render(write_still=True)
(folder/'metadata.json').write_text(json.dumps({'source':bpy.data.filepath,'frames':frames,'source_fps':s.render.fps,'fps_base':s.render.fps_base,'sampling_step':2 if mode!='stills'else None,'video_fps':s.render.fps/s.render.fps_base/2 if mode!='stills'else None},indent=2))
