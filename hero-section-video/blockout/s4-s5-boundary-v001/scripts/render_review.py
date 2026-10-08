import bpy,sys,argparse
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--scene',required=True);p.add_argument('--output-dir',required=True);p.add_argument('--frames',default='600,620,632,648,660,672,696,720');p.add_argument('--start',type=int);p.add_argument('--end',type=int);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);s=bpy.data.scenes[a.scene];bpy.context.window.scene=s;s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=768;s.render.resolution_y=432;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
frames=range(a.start,a.end+1) if a.start is not None else map(int,a.frames.split(','))
for f in frames:s.frame_set(f);s.render.filepath=str(out/f'{f:04d}.png');bpy.ops.render.render(write_still=True)
