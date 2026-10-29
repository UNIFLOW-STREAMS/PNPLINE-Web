"""Read-only composition experiments, no saved scene changes."""
import bpy,math,json,sys
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1]
s=bpy.context.scene;s.frame_set(450);u=s.objects['US_FRAME'].matrix_world.copy()
# City pivot turns its existing dense skyline toward the approach.
city=s.objects['UC_CITY_DISTRICT']
city.matrix_local=Matrix.Translation(Vector((-8,38,0)))@Matrix.Rotation(math.radians(-32),4,'Z')@Matrix.Translation(Vector((0,-37,0)))
for ch,angle in zip('USA',[-14,0,14]):
 o=s.objects['UC_LETTER_'+ch];o.location.y += -3 if ch!='S' else 0
 o.rotation_euler.z=math.radians(angle);o.location.z+=7
lib=s.objects['UC_LIBERTY'];lib.location=(-39,14,-6.0);lib.rotation_euler.z=math.radians(-48)
d=bpy.data.cameras.new('COMPOSITION_TRIAL');c=bpy.data.objects.new('COMPOSITION_TRIAL',d);s.collection.objects.link(c);s.camera=c
s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH'
s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
folder=R/'review/target-trials-03';folder.mkdir(exist_ok=False)
trials=[((-53,-17,1),(-9,18,12),28),((-56,-18,0),(-9,19,12),30),((-54,-20,2),(-12,19,13),28)]
for i,(p,t,lens) in enumerate(trials):
 p=Vector(p);t=Vector(t);wp=u@p;wt=u@t;up=s.objects['A02_SHIP'].matrix_world.translation.normalized();z=(wp-wt).normalized();x=up.cross(z).normalized();y=z.cross(x);rot=Matrix((x,y,z)).transposed().to_4x4();rot.translation=wp;c.matrix_world=rot;d.lens=lens;bpy.context.view_layer.update()
 s.render.filepath=str(folder/f'trial-{i+1}.png');bpy.ops.render.render(write_still=True)
(folder/'settings.json').write_text(json.dumps(trials,indent=2))


