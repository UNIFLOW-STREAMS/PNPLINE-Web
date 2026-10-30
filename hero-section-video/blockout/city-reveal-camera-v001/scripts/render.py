import bpy,sys,argparse,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--label',required=True);p.add_argument('--frames',default='455,479,509,528,552,576,600,624');p.add_argument('--start',type=int);p.add_argument('--end',type=int);p.add_argument('--step',type=int,default=1);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
folder=R/('preview' if a.start else 'review')/a.label;assert not folder.exists();folder.mkdir()
s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.render.resolution_x=960 if a.start else 1440;s.render.resolution_y=540 if a.start else 810;s.render.resolution_percentage=100;s.render.use_border=False;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
frames=list(range(a.start,a.end+1,a.step)) if a.start else [int(f) for f in a.frames.split(',')]
for f in frames:s.frame_set(f);s.render.filepath=str(folder/f'f{f:04}.png');bpy.ops.render.render(write_still=True)
(folder/'metadata.json').write_text(json.dumps({'source':bpy.data.filepath,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'frames':frames,'source_fps':s.render.fps/s.render.fps_base,'preview_fps':s.render.fps/s.render.fps_base/a.step},indent=2))
