"""Disposable camera tests for the user's rejected distant K2 view; no .blend save."""
import bpy,json,sys
from pathlib import Path
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scene_evidence import bounds
R=Path(__file__).resolve().parents[1];S=bpy.context.scene;C=S.camera;U=bpy.data.objects['US_FRAME'].matrix_world.copy()
C.animation_data_clear();C.data.animation_data_clear();S.frame_set(502)
S.render.resolution_x=960;S.render.resolution_y=540;S.render.resolution_percentage=100
out=R/'review/close-reveal/trials';out.mkdir(exist_ok=True);rows=[]
cases=[('a',(0,-22,12),(5,8,2),40),('b',(-4,-22,13),(6,8,2),40),('c',(-8,-22,13),(6,8,2),40),('d',(-12,-22,14),(6,8,2),40),('e',(6,-22,13),(5,8,2),40),('f',(10,-22,14),(5,8,2),40),('g',(0,-25,14),(6,9,2),40),('h',(-8,-24,14),(8,10,2),45),('i',(-12,-24,14),(8,10,2),45),('j',(-16,-26,16),(8,10,2),48),('k',(8,-25,15),(7,8,2),45),('l',(14,-26,15),(8,9,2),45)]
for name,p,t,lens in cases:
 wp=U@Vector(p);wt=U@Vector(t);z=(wp-wt).normalized();x=(U.to_3x3()@Vector((0,0,1))).cross(z).normalized();y=z.cross(x).normalized()
 C.location=wp;C.rotation_quaternion=Matrix((x,y,z)).transposed().to_quaternion();C.data.lens=lens;bpy.context.view_layer.update()
 S.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
 rows.append({'name':name,'p':p,'t':t,'lens':lens,'bounds':{n:bounds(n) for n in ['A02_SHIP','A01_CONTAINER','A03_TRACTOR','E08_WAREHOUSE']}})
(out/'poses.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print(json.dumps(rows))
