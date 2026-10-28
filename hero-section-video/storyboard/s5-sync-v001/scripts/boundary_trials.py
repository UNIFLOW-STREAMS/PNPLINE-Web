import bpy,json,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from contracts import digest
out=R/'review/s4-s5-recheck/trials-framing';out.mkdir(exist_ok=True);s=bpy.context.scene;U=s.objects['US_FRAME'].matrix_world.copy()
s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.use_border=False;s.render.use_crop_to_border=False
s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.background_type='WORLD';s.world.color=(.18,.18,.18)
trials=[((14,-14,13),(17,12,3),18),((9,-8,10),(10,14,2.5),17),((10,-6,10),(10,14,2.5),16),((10,-4,10),(10,14,2.5),14),((8,-4,9),(10,14,3),15),((8,-2,8),(9,14,3),13)]
records=[]
s.frame_set(648);s.camera.animation_data_clear();s.camera.data.animation_data_clear()
for j,(loc,aim,lens) in enumerate(trials):
 s.frame_set(648);cam=s.camera;cam.location=U@Vector(loc);cam.rotation_mode='QUATERNION';cam.rotation_quaternion=U.to_quaternion()@(Vector(aim)-Vector(loc)).to_track_quat('-Z','Y');cam.data.lens=lens;bpy.context.view_layer.update();p=out/f'trial-{j+1}.png';s.render.filepath=str(p);bpy.ops.render.render(write_still=True)
 assert (cam.matrix_world.translation-U@Vector(loc)).length<.0001,'render replaced trial camera with animation'
 records.append({'trial':j+1,'frame':648,'camera_us':loc,'aim_us':aim,'lens':lens,'actual_camera_matrix':list(map(list,cam.matrix_world)),'source_sha256':digest(bpy.data.filepath),'path':str(p),'sha256':digest(p),'purpose':'camera-only temporary proposal; not applied or saved'})
(out/'records.json').write_text(json.dumps(records,indent=2),encoding='utf8')
