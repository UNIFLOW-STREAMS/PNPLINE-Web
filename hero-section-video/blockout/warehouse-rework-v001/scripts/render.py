import bpy,sys,argparse,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--label',required=True);p.add_argument('--frames',default='900,985,1075,1158,1200');p.add_argument('--overview',action='store_true');p.add_argument('--material',action='store_true');p.add_argument('--sequence',action='store_true');p.add_argument('--start-frame',type=int,default=744);p.add_argument('--end-frame',type=int,default=1248);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
folder=R/('preview' if a.sequence else 'review')/a.label
assert folder.parent in [R/'review',R/'preview'] and not folder.exists();folder.mkdir()
S=bpy.context.scene;S.render.engine='CYCLES' if a.material else 'BLENDER_WORKBENCH'
if a.material:S.cycles.samples=24;S.cycles.use_denoising=True
S.display.shading.light='STUDIO';S.display.shading.color_type='MATERIAL';S.display.shading.show_shadows=True;S.display.shading.show_cavity=True;S.display.shading.cavity_type='BOTH'
S.render.resolution_x=640 if a.sequence else 1280;S.render.resolution_y=360 if a.sequence else 720;S.render.resolution_percentage=100;S.render.use_border=False;S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGB'
assert 1<=a.start_frame<=a.end_frame<=S.frame_end
frames=list(range(a.start_frame,a.end_frame+1)) if a.sequence else [int(x) for x in a.frames.split(',')]
for f in frames:
 S.frame_set(f);S.render.filepath=str(folder/f'f{f:04d}.png');bpy.ops.render.render(write_still=True)
if a.overview:
 S.frame_set(1075);U=S.objects['US_FRAME'].matrix_world.copy();d=bpy.data.cameras.new('WH_REVIEW_CAMERA');o=bpy.data.objects.new('WH_REVIEW_CAMERA',d);S.collection.objects.link(o);S.camera=o;d.type='ORTHO';d.ortho_scale=47
 for name,pos in [('overview',(24,0,30)),('front',(52,-14,25))]:
  pt=Vector(pos);q=(Vector((52,32,5.6))-pt).to_track_quat('-Z','Y');o.matrix_world=U@Matrix.LocRotScale(pt,q,Vector((1,1,1)));S.render.filepath=str(folder/(name+'.png'));bpy.ops.render.render(write_still=True)
(folder/'metadata.json').write_text(json.dumps({'source':bpy.data.filepath,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'actual_camera':'CAM_MASTER','diagnostic_views':['overview.png','front.png'] if a.overview else [],'frames':frames,'fps':S.render.fps,'engine':S.render.engine},indent=2))
