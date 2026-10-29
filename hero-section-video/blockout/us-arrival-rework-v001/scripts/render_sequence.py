"""Render every integer frame in the requested interval; preserve source FPS/time."""
import bpy,sys,json,time,hashlib,argparse
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'scripts'))
from safety import output_directory
p=argparse.ArgumentParser();p.add_argument('--label',required=True);p.add_argument('--start',type=int,required=True);p.add_argument('--end',type=int,required=True);p.add_argument('--width',type=int,default=640)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);folder=output_directory(R,'preview',a.label)
s=bpy.context.scene;start=time.time()
s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH'
s.render.resolution_x=a.width;s.render.resolution_y=round(a.width*9/16);s.render.resolution_percentage=100;s.render.use_border=False;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
for f in range(a.start,a.end+1):
 s.frame_set(f);s.render.filepath=str(folder/f'f{f:04d}.png');bpy.ops.render.render(write_still=True)
(folder/'metadata.json').write_text(json.dumps({'file':bpy.data.filepath,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'first':a.start,'last':a.end,'stride':1,'fps':s.render.fps/s.render.fps_base,'duration':(a.end-a.start+1)/(s.render.fps/s.render.fps_base),'width':a.width,'elapsed':time.time()-start,'camera':s.camera.name,'engine':s.render.engine},indent=2))
