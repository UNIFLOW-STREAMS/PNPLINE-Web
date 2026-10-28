import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];s=bpy.context.scene
rows=[]
for o in s.objects:
 rows.append({'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'children':len(o.children_recursive),'animated':bool(o.animation_data and o.animation_data.action),'data_animated':bool(o.data and hasattr(o.data,'animation_data') and o.data.animation_data and o.data.animation_data.action),'constraints':[c.type for c in o.constraints],'scale':list(o.scale)})
(R/'review/s4-s5-recheck/hierarchy.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
for o in s.objects:
 if not o.parent or o.parent.name in ['US_FRAME','A01_CONTAINER','A03_TRACTOR','A03_TRAILER'] or o.type=='FONT': print(o.name,o.type,'PARENT',o.parent.name if o.parent else None,'children',len(o.children_recursive),'anim',bool(o.animation_data and o.animation_data.action))
