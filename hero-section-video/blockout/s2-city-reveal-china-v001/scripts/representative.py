"""Only two directions at the identical ship state. Unsaved camera edits."""
import bpy,sys,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from build import pose
s=bpy.context.scene;s.frame_set(156);cam=s.camera
cam.animation_data_clear();s.objects['CAM_LOOK_TARGET'].animation_data_clear()
s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.background_type='WORLD';s.world.color=(.18,.18,.18)
configs={'A':{'p':[15,-40,23],'t':[0,17,8]},'B':{'p':[-24,-52,18],'t':[0,13,7]}}
for name,c in configs.items():
 p,t,q=pose(c['p'],c['t']);cam.location=p;cam.rotation_quaternion=q;s.objects['CAM_LOOK_TARGET'].location=t;bpy.context.view_layer.update()
 s.render.filepath=str(R/'review'/f'view-{name}.png');bpy.ops.render.render(write_still=True)
(R/'review/directions.json').write_text(json.dumps({'frame':156,'lens':40,'title_config':json.loads((R/'title-config.json').read_text()),'candidates':configs},indent=2))
