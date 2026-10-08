"""Disposable camera tests for the user's rejected distant K2 view; no .blend save."""
import bpy,json,sys
from pathlib import Path
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scene_evidence import bounds
R=Path(__file__).resolve().parents[1];S=bpy.context.scene;C=S.camera;U=bpy.data.objects['US_FRAME'].matrix_world.copy()
C.animation_data_clear();C.data.animation_data_clear();S.frame_set(502)
S.render.resolution_x=960;S.render.resolution_y=540;S.render.resolution_percentage=100
out=R/'review/close-reveal/trials4';out.mkdir(exist_ok=True);rows=[]
cases=[('a',(-4,-28,13),(5,6,2),38),('b',(0,-30,14),(6,6,2),35),('c',(-2,-30,14),(6,6,2),38),('d',(-4,-30,14),(6,6,2),38),('e',(-4,-28,12),(5,6,2),38),('f',(-4,-28,12),(5,6,2),40),('g',(0,-28,12),(5,6,2),35),('h',(-2,-28,12),(5,6,2),35),('i',(-2,-28,12),(5,6,2),38),('j',(-4,-26,11),(5,5,2),35),('k',(-2,-26,11),(5,5,2),35),('l',(0,-26,11),(5,5,2),35)]
for name,p,t,lens in cases:
 wp=U@Vector(p);wt=U@Vector(t);z=(wp-wt).normalized();x=(U.to_3x3()@Vector((0,0,1))).cross(z).normalized();y=z.cross(x).normalized()
 C.location=wp;C.rotation_quaternion=Matrix((x,y,z)).transposed().to_quaternion();C.data.lens=lens;bpy.context.view_layer.update()
 S.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
 rows.append({'name':name,'p':p,'t':t,'lens':lens,'bounds':{n:bounds(n) for n in ['A02_SHIP','A01_CONTAINER','A03_TRACTOR','E08_WAREHOUSE']}})
(out/'poses.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print(json.dumps(rows))

