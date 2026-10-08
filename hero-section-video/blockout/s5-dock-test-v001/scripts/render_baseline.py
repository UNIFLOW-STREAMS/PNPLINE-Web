"""Read-only source diagnostic renders; never saves the source file."""
import bpy,sys,argparse,math
from pathlib import Path
from mathutils import Matrix,Vector
p=argparse.ArgumentParser();p.add_argument('--scene',required=True);p.add_argument('--output-dir',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);s=bpy.data.scenes[a.scene];bpy.context.window.scene=s;U=bpy.data.objects['US_FRAME'].matrix_world.copy();inv=U.inverted();s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
data=bpy.data.cameras.new('BASELINE_DIAGNOSTIC');cam=bpy.data.objects.new('BASELINE_DIAGNOSTIC',data);s.collection.objects.link(cam);s.camera=cam;data.clip_end=500;out=Path(a.output_dir)
for f in [720,746,810,842,890]:
 s.frame_set(f);focus=(inv@bpy.data.objects['A03_TRAILER'].matrix_world).translation+Vector((0,0,2.1))
 for view in ['oblique','top']:
  if view=='top':data.type='ORTHO';data.ortho_scale=44;cam.matrix_world=U@Matrix.Translation((32,20,60))
  else:
   data.type='PERSP';data.lens=40;pos=focus+Vector((8,-12,8));cam.matrix_world=U@Matrix.Translation(pos)@(focus-pos).to_track_quat('-Z','Y').to_matrix().to_4x4()
  (out/view).mkdir(parents=True,exist_ok=True);s.render.filepath=str(out/view/f'{f:04d}.png');bpy.ops.render.render(write_still=True)
