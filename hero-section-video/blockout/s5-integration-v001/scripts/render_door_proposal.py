import bpy
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1];s=bpy.data.scenes['PNPLINE_MASTER_v005'];bpy.context.window.scene=s;s.frame_set(810);U=bpy.data.objects['US_FRAME'].matrix_world
D=bpy.data.cameras.new('INSPECTION_ONLY');C=bpy.data.objects.new('INSPECTION_ONLY',D);s.collection.objects.link(C);p=Vector((33.4,25,3.7));t=Vector((30.4,29,2.5));C.location=U@p;C.rotation_mode='QUATERNION';C.rotation_quaternion=U.to_quaternion()@(t-p).to_track_quat('-Z','Y');D.lens=58;s.camera=C
s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
for label,x in [('door-before',-1.6),('door-proposal',-1.65)]:
 for name in ['A01_DOOR_L','A01_DOOR_R']:bpy.data.objects[name].location.x=x
 bpy.context.view_layer.update();s.render.filepath=str(R/'review'/f'{label}.png');bpy.ops.render.render(write_still=True)
