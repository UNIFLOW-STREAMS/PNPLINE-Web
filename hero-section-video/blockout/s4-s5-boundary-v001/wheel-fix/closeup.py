import bpy
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1];s=bpy.data.scenes['PNPLINE_MASTER_v005'];bpy.context.window.scene=s;s.frame_set(596)
U=bpy.data.objects['US_FRAME'].matrix_world;data=bpy.data.cameras.new('REVIEW_ONLY');c=bpy.data.objects.new('REVIEW_ONLY',data);s.collection.objects.link(c)
p=Vector((6,16,5.5));aim=Vector((1.6,9,1.8));c.location=U@p;c.rotation_mode='QUATERNION';c.rotation_quaternion=U.to_quaternion()@(aim-p).to_track_quat('-Z','Y');data.lens=45;s.camera=c
s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=1280;s.render.resolution_y=800;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.filepath=str(R/'wheel-fix/closeup.png');bpy.ops.render.render(write_still=True)
