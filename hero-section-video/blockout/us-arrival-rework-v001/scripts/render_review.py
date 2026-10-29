import bpy,sys,json,hashlib,time
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'scripts'))
from safety import output_directory
a=sys.argv[sys.argv.index('--')+1:];label=a[0];frames=[int(x) for x in a[1].split(',')]
folder=output_directory(R,'review',label)
s=bpy.context.scene
s.render.engine='BLENDER_WORKBENCH'
s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH'
s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100;s.render.use_border=False
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
if len(a)>3 and a[3]=='material':s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True
for f in frames:
 s.frame_set(f);s.render.filepath=str(folder/f'f{f:04d}.png');bpy.ops.render.render(write_still=True)
if len(a)>2 and a[2]=='overview':
 u=s.objects['US_FRAME'].matrix_world
 d=bpy.data.cameras.new('DIAGNOSTIC_ONLY');c=bpy.data.objects.new('DIAGNOSTIC_ONLY',d);s.collection.objects.link(c);s.camera=c
 pos=Vector((58,-90,75));q=(Vector((0,25,12))-pos).to_track_quat('-Z','Y');c.matrix_world=u@Matrix.LocRotScale(pos,q,Vector((1,1,1)));d.type='ORTHO';d.ortho_scale=135
 s.render.filepath=str(folder/'overview.png');bpy.ops.render.render(write_still=True)
(folder/'metadata.json').write_text(json.dumps({'source':bpy.data.filepath,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'camera':'CAM_MASTER (overview diagnostic only)','frames':frames,'fps':s.render.fps,'engine':s.render.engine},indent=2))
