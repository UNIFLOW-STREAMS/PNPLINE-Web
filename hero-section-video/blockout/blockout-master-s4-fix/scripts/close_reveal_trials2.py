"""Disposable camera tests for the user's rejected distant K2 view; no .blend save."""
import bpy,json,sys
from pathlib import Path
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scene_evidence import bounds
R=Path(__file__).resolve().parents[1];S=bpy.context.scene;C=S.camera;U=bpy.data.objects['US_FRAME'].matrix_world.copy()
C.animation_data_clear();C.data.animation_data_clear();S.frame_set(502)
S.render.resolution_x=960;S.render.resolution_y=540;S.render.resolution_percentage=100
out=R/'review/close-reveal/trials2';out.mkdir(exist_ok=True);rows=[]
cases=[('a',(-4,-22,13),(5,4,0),35),('b',(-8,-22,13),(5,4,0),35),('c',(-12,-22,14),(5,4,0),35),('d',(-4,-22,13),(5,4,0),40),('e',(2,-23,14),(5,4,0),35),('f',(8,-23,14),(8,5,0),32),('g',(16,-22,14),(9,4,0),32),('h',(24,-15,12),(9,5,0),32),('i',(20,-18,12),(9,5,0),35),('j',(-8,-24,14),(7,5,0),38),('k',(-4,-24,14),(7,5,0),38),('l',(0,-24,14),(7,5,0),38)]
for name,p,t,lens in cases:
 wp=U@Vector(p);wt=U@Vector(t);z=(wp-wt).normalized();x=(U.to_3x3()@Vector((0,0,1))).cross(z).normalized();y=z.cross(x).normalized()
 C.location=wp;C.rotation_quaternion=Matrix((x,y,z)).transposed().to_quaternion();C.data.lens=lens;bpy.context.view_layer.update()
 S.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
 rows.append({'name':name,'p':p,'t':t,'lens':lens,'bounds':{n:bounds(n) for n in ['A02_SHIP','A01_CONTAINER','A03_TRACTOR','E08_WAREHOUSE']}})
(out/'poses.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print(json.dumps(rows))

