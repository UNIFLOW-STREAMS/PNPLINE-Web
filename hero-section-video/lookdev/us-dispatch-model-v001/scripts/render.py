import bpy,sys,math,json,time
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];B=R.parents[1]/'blockout';sys.path.insert(0,str(B/'curvature-rework-v001/scripts'));from mapping import graded
s=bpy.context.scene;p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
for d in p.devices:d.use=d.type=='OPTIX'
s.render.engine='CYCLES';s.cycles.device='GPU';s.cycles.samples=64;s.cycles.use_denoising=True;s.cycles.adaptive_threshold=.025;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';s.render.film_transparent=False
U=s.objects['US_FRAME'].matrix_world;master=s.camera
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['overview','989']
out=R/'review';outarg=next((a for a in args if a.startswith('--out=')),None)
if outarg:out=out/outarg.split('=',1)[1];args.remove(outarg)
out.mkdir(parents=True,exist_ok=True)
for item in args:
 if item=='overview':
  s.frame_set(890);x,y=89,29;P=graded(Vector((x,y,.8)));dx=(graded(Vector((x+.01,y,.8)))-P).normalized();dy=graded(Vector((x,y+.01,.8)))-P;n=dx.cross(dy).normalized();dy=n.cross(dx).normalized();F=Matrix.Translation(P)@Matrix((dx,dy,n)).transposed().to_4x4()
  c=bpy.data.objects.new('DSP_REVIEW_CAMERA',bpy.data.cameras.new('DSP_REVIEW_CAMERA'));s.collection.objects.link(c);c.matrix_world=U@F@Matrix.Translation(Vector((41,-8,61)));target=U@F@Vector((-3,0,0));c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=66;s.camera=c;s.render.resolution_x=1200;s.render.resolution_y=1400
 else:s.camera=master;s.frame_set(int(item));s.render.resolution_x=1920;s.render.resolution_y=1080
 s.render.filepath=str(out/('render-'+item+'.png'));t=time.time();bpy.ops.render.render(write_still=True);print('RENDERED',item,time.time()-t,flush=True)
