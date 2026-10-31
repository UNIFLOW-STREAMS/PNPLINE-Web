import bpy,sys,json,time,hashlib,argparse
from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--frames',default='45,110,200,315,390,530,720,820');p.add_argument('--width',type=int,default=1920);p.add_argument('--samples',type=int,default=128);p.add_argument('--label',default='after');p.add_argument('--device',default='OPTIX');p.add_argument('--depth',choices=['8','16'],default='8');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
s=bpy.context.scene;s.render.engine='CYCLES'
pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type=a.device;pref.get_devices()
for d in pref.devices:d.use=d.type==a.device
s.cycles.device='GPU';s.cycles.samples=a.samples;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.seed=29;s.cycles.use_animated_seed=False;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_min_samples=min(32,a.samples);s.cycles.adaptive_threshold=.02
s.render.resolution_x=a.width;s.render.resolution_y=round(a.width*9/16);s.render.resolution_percentage=100;s.render.use_persistent_data=True;s.render.use_border=False;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.color_depth=a.depth;s.render.image_settings.compression=15
dest=R/'review'/a.label;dest.mkdir(parents=True,exist_ok=True);results=[]
frames=list(range(*map(int,a.frames.split(':')))) if ':' in a.frames else list(map(int,a.frames.split(',')))
for f in frames:
 s.frame_set(f);s.render.filepath=str(dest/f'f{f:04}.png');start=time.perf_counter();bpy.ops.render.render(write_still=True)
 rec=dict(frame=f,seconds=time.perf_counter()-start,width=a.width,samples=a.samples,engine='CYCLES',device=a.device,file=s.render.filepath,source_sha256=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest());results.append(rec)
 (dest/'render-metrics.json').write_text(json.dumps(results,indent=2));print('FRAME_COMPLETE',json.dumps(rec),flush=True)
