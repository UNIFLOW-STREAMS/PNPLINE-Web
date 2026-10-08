import bpy,sys,argparse
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--scene',required=True);p.add_argument('--output-dir',required=True);p.add_argument('--camera',choices=['oblique','top'],default='oblique');p.add_argument('--frames',default='648,746,810,826,842,849,890,900');p.add_argument('--animation',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
s=bpy.data.scenes[a.scene];bpy.context.window.scene=s;s.camera=bpy.data.objects['S5T__CAM_'+a.camera.upper()];s.render.image_settings.file_format='PNG';s.render.resolution_percentage=100
out=Path(a.output_dir)/a.camera;out.mkdir(parents=True,exist_ok=True)
frames=range(s.frame_start,s.frame_end+1) if a.animation else [int(f) for f in a.frames.split(',')]
for f in frames:
 s.frame_set(f);s.render.filepath=str(out/f'{f:04d}.png');bpy.ops.render.render(write_still=True)
print('RENDERED',a.camera,len(frames))
