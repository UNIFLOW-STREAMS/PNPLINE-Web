import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
S=R.parent/'us-city-density-v001/pnpline-us-city-density-v001.blend'
bpy.ops.wm.open_mainfile(filepath=str(S));s=bpy.context.scene;s.frame_set(349)
rows=[]
for o in s.objects:
 if any(q in o.name for q in ['UC_LETTER_','UC_AR_LETTER_PLINTH','CV_FOUNDATION_LETTER','CV_LETTER_']):
  rows.append({'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'hide':o.hide_render,'dimensions':list(o.dimensions),'basis':[list(r)for r in o.matrix_basis],'anchor':list(o.get('cv_anchor',[])),
  'bounds_native':[[min(v.co[i]for v in o.data.vertices),max(v.co[i]for v in o.data.vertices)]for i in range(3)]if o.type=='MESH'else None,
  'materials':[m.name if m else None for m in o.data.materials]if o.type=='MESH'else[],
  'vertices':len(o.data.vertices)if o.type=='MESH'else 0})
(R/'review/title-source-survey.json').write_text(json.dumps(rows,indent=2))
print(json.dumps(rows),flush=True)
