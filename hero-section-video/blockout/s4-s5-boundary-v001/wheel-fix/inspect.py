import bpy,json
from pathlib import Path
from mathutils import Vector
s=bpy.data.scenes['PNPLINE_MASTER_v005'];bpy.context.window.scene=s;s.frame_set(596);I=bpy.data.objects['US_FRAME'].matrix_world.inverted()
rows=[]
for o in s.objects:
 if any(x in o.name for x in ['A03','TRACTOR','TRAILER','TRUCK']):
  vs=[I@o.matrix_world@Vector(v) for v in o.bound_box]
  rows.append(dict(name=o.name,type=o.type,parent=o.parent.name if o.parent else None,local=list(o.location),pos=list((I@o.matrix_world).translation),dims=list(o.dimensions),bounds=[[min(v[i] for v in vs),max(v[i] for v in vs)] for i in range(3)],hide=o.hide_render,constraints=[(c.name,c.type) for c in o.constraints]))
Path('F:/pnpline-landing/hero-section-video/blockout/s4-s5-boundary-v001/wheel-fix/inspect.json').write_text(json.dumps(rows,indent=2))
print(json.dumps(rows,indent=2))
