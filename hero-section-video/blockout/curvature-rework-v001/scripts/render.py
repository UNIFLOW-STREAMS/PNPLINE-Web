import bpy,sys,argparse,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--label',required=True);p.add_argument('--frames',default='455,720,768,930,1075,1158,1320,1392');p.add_argument('--overview',action='store_true');p.add_argument('--start',type=int);p.add_argument('--end',type=int);p.add_argument('--step',type=int,default=1);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
folder=R/('preview' if a.start else 'review')/a.label;assert not folder.exists();folder.mkdir()
s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH'
s.render.resolution_x=640 if a.start else 1440;s.render.resolution_y=360 if a.start else 900;s.render.resolution_percentage=100;s.render.use_border=False;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
frames=list(range(a.start,a.end+1,a.step)) if a.start else [int(f) for f in a.frames.split(',') if f]
for f in frames:s.frame_set(f);s.render.filepath=str(folder/f'f{f:04}.png');bpy.ops.render.render(write_still=True)
if a.overview:
 s.frame_set(1075);u=s.objects['US_FRAME'].matrix_world.copy();d=bpy.data.cameras.new('CV_DIAGNOSTIC_CAMERA');o=bpy.data.objects.new('CV_DIAGNOSTIC_CAMERA',d);s.collection.objects.link(o);s.camera=o;d.type='ORTHO';d.ortho_scale=161
 for name,pos,target,scale in [('overview',(-95,-130,95),(34,33,-2),161),('side',(20,-170,35),(37,30,-4),160),('city',(-70,-85,80),(0,42,3),132)]:
  d.ortho_scale=scale;pt=Vector(pos);q=(Vector(target)-pt).to_track_quat('-Z','Y');o.matrix_world=u@Matrix.LocRotScale(pt,q,Vector((1,1,1)));s.render.filepath=str(folder/(name+'.png'));bpy.ops.render.render(write_still=True)
(folder/'metadata.json').write_text(json.dumps({'source':bpy.data.filepath,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'frames':frames,'fps':s.render.fps,'preview_fps':s.render.fps/a.step,'camera':'CAM_MASTER','diagnostic_views':['overview','side','city'] if a.overview else []},indent=2))
