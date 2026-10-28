import bpy, json, sys
from pathlib import Path
from mathutils import Matrix, Vector
R=Path(__file__).resolve().parents[1]
s=bpy.context.scene;s.frame_set(648)
U=s.objects['US_FRAME'].matrix_world.copy();I=U.inverted()
S=Matrix.Diagonal((1,-1,1,1));T=Matrix.Translation((0,18,0))
A=U@T@S@I
env=list(s.objects['US_FRAME'].children_recursive)
states={o.name:o.matrix_world.copy() for o in env}
for o in env:
 o.parent=None;o.animation_data_clear();o.matrix_world=A@states[o.name]@S
 if o.type=='MESH':
  o.data=o.data.copy();o.data.transform(S);o.data.flip_normals();o.data.update()
roots=['A02_SHIP','A01_CONTAINER','A03_TRACTOR','A03_TRAILER','P02_SPREADER']+[f'P02_CABLE_{i}' for i in range(4)]
for n in roots:
 o=s.objects[n];m=o.matrix_world.copy();o.animation_data_clear();o.matrix_world=A@m@S
cam=s.camera;cam.animation_data_clear();cam.data.animation_data_clear()
s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.use_border=False
s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.background_type='WORLD';s.world.color=(.18,.18,.18)
out=R/'review/s4-s5-recheck/layout-trials';out.mkdir(exist_ok=True)
trials=[((-15,18,11),(7,11,3),28),((-11,15,9),(7,10,3),30)]
for j,(loc,aim,lens) in enumerate(trials):
 cam.location=U@Vector(loc);cam.rotation_mode='QUATERNION';cam.rotation_quaternion=U.to_quaternion()@(Vector(aim)-Vector(loc)).to_track_quat('-Z','Y');cam.data.lens=lens
 bpy.context.view_layer.update();s.render.filepath=str(out/f'trial-{j+1}.png');bpy.ops.render.render(write_still=True)
print('LAYOUT_TRIAL_COMPLETE')
