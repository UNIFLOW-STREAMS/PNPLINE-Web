import bpy,json
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[1]
s=bpy.context.scene;s.frame_set(0)
rows=[]
for o in s.objects:
 if any(x in o.name for x in ['OPEN_TOWER','STEP_TOWER','SPHERE_TOWER']):
  rows.append(dict(name=o.name,type=o.type,parent=o.parent.name if o.parent else None,children=len(o.children_recursive),loc=list(o.location),scale=list(o.scale),dims=list(o.dimensions),bounds=[list(v) for v in o.bound_box],mat=[m.name for m in o.data.materials] if o.type=='MESH' else []))
(r/'review/pearl-survey.json').write_text(json.dumps(rows,indent=2))
print(json.dumps(rows),flush=True)

