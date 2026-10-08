import bpy,sys,argparse
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--scene',required=True);p.add_argument('--output-dir',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);s=bpy.data.scenes[a.scene];bpy.context.window.scene=s;out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True);s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100;s.render.engine='BLENDER_WORKBENCH';s.render.image_settings.file_format='PNG'
for f in [0,48,95]:s.frame_set(f);s.render.filepath=str(out/f'{f:04d}.png');bpy.ops.render.render(write_still=True)
