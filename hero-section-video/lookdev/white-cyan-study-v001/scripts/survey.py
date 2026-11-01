import bpy,json,collections
from pathlib import Path
R=Path(__file__).resolve().parents[1];S=bpy.context.scene
usage=collections.defaultdict(list)
for o in S.objects:
 if o.type in {'MESH','CURVE','FONT'}:
  for sl in o.material_slots:
   if sl.material:usage[sl.material.name].append(o.name)
rows=[]
for m in bpy.data.materials:
 b=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) if m.node_tree else None
 rows.append(dict(name=m.name,users=len(usage[m.name]),examples=usage[m.name][:6],color=list(b.inputs['Base Color'].default_value) if b else list(m.diffuse_color)))
data=dict(materials=rows,markers=[(m.name,m.frame) for m in S.timeline_markers],camera=S.camera.name,water=[(o.name,[m.name for m in o.data.materials if m]) for o in S.objects if o.type=='MESH' and any(k in o.name.lower() for k in ['ocean','river','water','wake'])])
(R/'review/survey.json').write_text(json.dumps(data,indent=2))
print('survey saved',len(rows))
