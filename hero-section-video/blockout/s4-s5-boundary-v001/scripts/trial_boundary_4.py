"""Read-only camera feasibility study; no blend saved."""
import bpy,sys,argparse,json
from pathlib import Path
from mathutils import Matrix,Vector
p=argparse.ArgumentParser();p.add_argument('--scene',required=True);p.add_argument('--output-dir',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);S=bpy.data.scenes[a.scene];bpy.context.window.scene=S;S.frame_set(648);C=S.camera;C.animation_data_clear();C.data.animation_data_clear();U=bpy.data.objects['US_FRAME'].matrix_world.copy();out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True);S.render.engine='BLENDER_WORKBENCH';S.render.resolution_x=960;S.render.resolution_y=540;S.render.resolution_percentage=100;S.render.image_settings.file_format='PNG'
trials=[([-9,13,9],[7,12,2],28),([-11,14,10],[7,12,2],28),([-12,14,11],[7,12,2],30),([-10,13,9],[7,11,2],28)]
for i,(p,t,lens) in enumerate(trials):
 p,t=Vector(p),Vector(t);z=(p-t).normalized();x=Vector((0,0,1)).cross(z).normalized();y=z.cross(x);C.matrix_world=U@Matrix.Translation(p)@Matrix((x,y,z)).transposed().to_4x4();C.data.lens=lens;S.render.filepath=str(out/f'trial-{i}.png');bpy.ops.render.render(write_still=True)
(out/'trials.json').write_text(json.dumps(trials,indent=2))



