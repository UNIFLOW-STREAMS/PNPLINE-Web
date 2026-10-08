import bpy,sys,argparse
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--frames',default='648,720,752,784,810,842,849,870,890,900,924,948');p.add_argument('--top',action='store_true');p.add_argument('--width',type=int,default=960);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=a.width;s.render.resolution_y=int(a.width*9/16);s.render.resolution_percentage=100
s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.background_type='WORLD';s.world.color=(.18,.18,.18)
s.render.image_settings.file_format='PNG';s.render.film_transparent=False
if a.top:
 U=s.objects['US_FRAME'].matrix_world;data=bpy.data.cameras.new('DIAGNOSTIC_TOP');o=bpy.data.objects.new('DIAGNOSTIC_TOP',data);s.collection.objects.link(o);data.type='ORTHO';data.ortho_scale=65;o.location=U@Vector((21,22,65));o.rotation_mode='QUATERNION';o.rotation_quaternion=U.to_quaternion();s.camera=o
out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=True)
frames=range(*[int(v) for v in a.frames.split(':')]) if ':' in a.frames else [int(v) for v in a.frames.split(',')]
for f in frames:
 s.frame_set(f);s.render.filepath=str(out/f'{f:04d}.png');bpy.ops.render.render(write_still=True)
