"""Disposable camera tests for the user's rejected distant K2 view; no .blend save."""
import bpy,json,sys
from pathlib import Path
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scene_evidence import bounds
R=Path(__file__).resolve().parents[1];S=bpy.context.scene;C=S.camera;U=bpy.data.objects['US_FRAME'].matrix_world.copy()
C.animation_data_clear();C.data.animation_data_clear();S.frame_set(502)
S.render.resolution_x=960;S.render.resolution_y=540;S.render.resolution_percentage=100
out=R/'review/close-reveal/trials3';out.mkdir(exist_ok=True);rows=[]
cases=[('a',(-4,-22,8),(6,5,2),35),('b',(-8,-22,8),(6,5,2),35),('c',(0,-22,8),(6,5,2),35),('d',(-4,-22,8),(8,8,2),35),('e',(-8,-22,10),(6,5,2),35),('f',(4,-18,8),(8,6,1),28),('g',(0,-17,8),(6,6,1),30),('h',(-4,-18,8),(6,6,1),32),('i',(4,-17,8),(5,5,1),30),('j',(0,-20,10),(6,6,1),32),('k',(-4,-20,10),(6,6,1),35),('l',(-8,-20,10),(6,6,1),35)]
for name,p,t,lens in cases:
 wp=U@Vector(p);wt=U@Vector(t);z=(wp-wt).normalized();x=(U.to_3x3()@Vector((0,0,1))).cross(z).normalized();y=z.cross(x).normalized()
 C.location=wp;C.rotation_quaternion=Matrix((x,y,z)).transposed().to_quaternion();C.data.lens=lens;bpy.context.view_layer.update()
 S.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
 rows.append({'name':name,'p':p,'t':t,'lens':lens,'bounds':{n:bounds(n) for n in ['A02_SHIP','A01_CONTAINER','A03_TRACTOR','E08_WAREHOUSE']}})
(out/'poses.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print(json.dumps(rows))

