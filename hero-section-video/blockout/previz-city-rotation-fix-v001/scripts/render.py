import bpy,json,sys,hashlib,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];a=sys.argv[sys.argv.index('--')+1:];label=a[0];s=bpy.context.scene
frames=list(range(96,673))if len(a)<2 else (list(range(int(a[1].split(':')[1]),int(a[1].split(':')[2])+1))if a[1].startswith('range:')else [int(f)for f in a[1].split(',')])
if len(a)>2:frames=frames[::int(a[2])]
folder=R/'review'/label;folder.mkdir(parents=True,exist_ok=True)
if any(folder.glob('f*.png')):raise RuntimeError('Refusing to overwrite render frames')
s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH'
s.render.resolution_x=640;s.render.resolution_y=360;s.render.resolution_percentage=100;s.render.use_border=False;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.fps=12;s.render.fps_base=1
t=time.time()
for f in frames:
 s.frame_set(f);s.render.filepath=str(folder/f'f{f:04d}.png');bpy.ops.render.render(write_still=True)
(folder/'metadata.json').write_text(json.dumps({'file':bpy.data.filepath,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'frames':frames,'fps':12,'engine':s.render.engine,'resolution':[640,360],'elapsed_s':time.time()-t},indent=2))
