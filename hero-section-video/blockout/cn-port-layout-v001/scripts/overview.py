import bpy,sys
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(0);D=s.objects['SF_CN_LAYOUT'].matrix_world
cam=bpy.data.objects.new('REVIEW_CAMERA',bpy.data.cameras.new('REVIEW_CAMERA'));s.collection.objects.link(cam);s.camera=cam
arg=sys.argv[sys.argv.index('--')+1]if '--'in sys.argv else 'before'
top=arg.endswith('top');pos=Vector((0,-25,42))if not top else Vector((0,8,65));target=Vector((-4,9,2))
cam.matrix_world=D@Matrix.LocRotScale(pos,(target-pos).to_track_quat('-Z','Y'),Vector((1,1,1)));cam.data.type='ORTHO';cam.data.ortho_scale=60 if top else 54
s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.use_border=False;s.render.filepath=str(R/'review'/f'{arg}.png');bpy.ops.render.render(write_still=True)
