"""Disposable poses: do not save scene or change any assets."""
import bpy,json,sys
from pathlib import Path
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent));from scene_evidence import bounds
R=Path(__file__).resolve().parents[1];S=bpy.context.scene;C=S.camera;U=bpy.data.objects['US_FRAME'].matrix_world.copy()
C.animation_data_clear();C.data.animation_data_clear();S.render.resolution_x=960;S.render.resolution_y=540;S.render.resolution_percentage=100
out=R/'review/feasibility';out.mkdir(exist_ok=True)
rows=[]
cases=[('K5-sea4',648,(-4,-18,14),(5,7,3),38),('K5-sea0',648,(0,-18,14),(5,7,3),38),('K5-sea8',648,(-8,-18,14),(5,7,3),38),('K5-north0',648,(0,32,16),(6,8,2.5),38),('K5-north4',648,(-4,32,16),(6,8,2.5),38),('K5-north8',648,(-8,32,16),(6,8,2.5),38),('K5-north12',648,(-12,32,16),(6,8,2.5),38)]
for name,f,p,t,lens in cases:
 S.frame_set(f);wp=U@Vector(p);wt=U@Vector(t);up=U.to_3x3()@Vector((0,0,1));z=(wp-wt).normalized();x=up.cross(z).normalized();y=z.cross(x).normalized()
 C.location=wp;C.rotation_quaternion=Matrix((x,y,z)).transposed().to_quaternion();C.data.lens=lens;bpy.context.view_layer.update()
 S.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
 rows.append({'name':name,'frame':f,'position':p,'target':t,'lens':lens,'bounds':{n:bounds(n) for n in ['A02_SHIP','A01_CONTAINER','A03_TRACTOR','A03_TRAILER','E08_WAREHOUSE','E07_INBOUND_ROAD']}})
(out/'measurements.json').write_text(json.dumps(rows,indent=2));print('Trial poses',len(rows))
