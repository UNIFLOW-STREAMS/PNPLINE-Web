import bpy,json
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;original=s.camera
folder=R/'review/statue-scale-comparison-final';folder.mkdir(exist_ok=False)
s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.use_border=False
body=s.objects['UC_LIBERTY_BODY'];chosen=body.scale.copy();U=s.objects['US_FRAME'].matrix_world.copy();lib=s.objects['UC_LIBERTY'];root=lib.matrix_world.copy()
d=bpy.data.cameras.new('SCALE_DIAGNOSTIC');cam=bpy.data.objects.new('SCALE_DIAGNOSTIC',d);s.collection.objects.link(cam);d.type='ORTHO';d.ortho_scale=31
pos=Vector((13,-24,15));q=(Vector((0,0,6))-pos).to_track_quat('-Z','Y');cam.matrix_world=root@Matrix.LocRotScale(pos,q,Vector((1,1,1)))
for name,scale in [('reference',chosen/1.4),('enlarged',chosen)]:
 body.scale=scale
 for f in [390,421,450]:
  s.camera=original;s.frame_set(f);s.render.filepath=str(folder/f'{name}-f{f:04d}.png');bpy.ops.render.render(write_still=True)
 s.camera=cam;s.render.filepath=str(folder/f'{name}-diagnostic.png');bpy.ops.render.render(write_still=True)
body.scale=chosen;s.camera=original
(folder/'metadata.json').write_text(json.dumps({'source':bpy.data.filepath,'comparison':'Same camera position/lens/frame and pedestal/island; only statue body scale differs','reference_body_height':7.74,'selected_body_height':10.836,'factor':1.4,'saved_scene_modified':False,'artistic_status':'Both same-camera variants still clip. Diagnostic closeup is shape/scale evidence only.'},indent=2))
