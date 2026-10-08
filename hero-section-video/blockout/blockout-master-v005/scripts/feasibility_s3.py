"""Temporary camera poses only: no blend save, no asset edits."""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scene_evidence import bounds
R=Path(__file__).resolve().parents[1];S=bpy.context.scene;C=S.camera
C.animation_data_clear() # Render updates must not restore the saved animated camera pose.
S.render.resolution_x=960;S.render.resolution_y=540;S.render.resolution_percentage=100
out=R/'review/feasibility';out.mkdir(exist_ok=True)
cases=[]
for z in [18,28,38,48]:
 for tz in [1,7]:cases.append((f'K3-z{z}-t{tz}',330,(-28,-25,z),(2,0,tz)))
for f in [370,385,398]:
 for tz in [2,8]:cases.append((f'K4-f{f}-t{tz}',f,(-24,-20,20),(5,0,tz)))
for f in [280,325]:cases.append((f'K23-selected-f{f}',f,(-25,-27,35),(0,0,5)))
for p,t,label in [((-28,-18,18),(4,0,0),'rear'),((-24,-22,18),(6,0,0),'side'),((-28,-22,23),(6,0,2),'high')]:
 for f in [368,380,392]:cases.append((f'K4-{label}-f{f}',f,p,t))
rows=[]
for name,f,p,t in cases:
 S.frame_set(f);ship=bpy.data.objects['A02_SHIP'].matrix_world.copy();p=ship@Vector(p);t=ship@Vector(t)
 up=ship.to_3x3()@Vector((0,0,1));z=(p-t).normalized();x=up.cross(z).normalized();y=z.cross(x).normalized()
 C.location=p;C.rotation_quaternion=Matrix((x,y,z)).transposed().to_quaternion();bpy.context.view_layer.update()
 b=bounds('A02_SHIP');rows.append({'name':name,'frame':f,'ship_bounds':b,'width':b[2]-b[0]})
 S.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
(out/'measurements.json').write_text(json.dumps(rows,indent=2))
print(json.dumps(rows))
