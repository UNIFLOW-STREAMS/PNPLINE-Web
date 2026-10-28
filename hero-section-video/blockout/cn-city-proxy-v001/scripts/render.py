"""Read-only output. Diagnostic camera exists only in this unsaved process."""
import bpy,sys,argparse,json,hashlib
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--frames',default='96,124,148,180,216,278,330,450,456');p.add_argument('--diagnostic',action='store_true');p.add_argument('--width',type=int,default=960);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
s=bpy.context.scene;out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=True)
s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=a.width;s.render.resolution_y=int(a.width*9/16);s.render.resolution_percentage=100
s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.background_type='WORLD';s.world.color=(.18,.18,.18)
s.render.image_settings.file_format='PNG';s.render.film_transparent=False
records={'blend':bpy.data.filepath,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'width':a.width,'fps':s.render.fps,'diagnostic':a.diagnostic,'images':{}}
if a.diagnostic:
 s.frame_set(96);cn=s.objects['CN_FRAME'].matrix_world
 d=bpy.data.cameras.new('CN_DIAGNOSTIC_ONLY');cam=bpy.data.objects.new('CN_DIAGNOSTIC_ONLY',d);s.collection.objects.link(cam);d.type='ORTHO';s.camera=cam
 for name,pos,target,scale in [('overview',(43,-43,40),(0,17,4),66),('top',(0,18,85),(0,18,0),67),('shore',(-37,-5,15),(-16,19,0),38)]:
  cam.location=cn@Vector(pos);cam.rotation_euler=(cn.to_quaternion()@(Vector(target)-Vector(pos)).to_track_quat('-Z','Y')).to_euler();d.ortho_scale=scale
  s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);records['images'][name]=hashlib.sha256(Path(s.render.filepath).read_bytes()).hexdigest()
else:
 assert s.camera.name=='CAM_MASTER'
 frames=range(*map(int,a.frames.split(':'))) if ':' in a.frames else list(map(int,a.frames.split(',')))
 for f in frames:
  s.frame_set(f);s.render.filepath=str(out/f'{f:04}.png');bpy.ops.render.render(write_still=True);records['images'][f]=hashlib.sha256(Path(s.render.filepath).read_bytes()).hexdigest()
(out/'render-record.json').write_text(json.dumps(records,indent=2))
