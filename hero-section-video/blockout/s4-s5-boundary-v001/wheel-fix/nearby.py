import bpy,json
from mathutils import Vector
from pathlib import Path
s=bpy.data.scenes['PNPLINE_MASTER_v005'];bpy.context.window.scene=s;s.frame_set(596);I=bpy.data.objects['US_FRAME'].matrix_world.inverted();out=[]
for o in s.objects:
 p=(I@o.matrix_world).translation
 if o.type=='MESH' and -3<p.x<6 and 6<p.y<12 and -1<p.z<5:out.append((o.name,o.parent.name if o.parent else None,list(p)))
print(json.dumps(out,indent=2))
for f in [0,96,240,444,596,608,620,632,648,720,792,1392]:
 s.frame_set(f);print('FRAME',f,'tractor',list((I@bpy.data.objects['A03_TRACTOR'].matrix_world).translation))
