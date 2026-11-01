import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(0);I=s.objects['SF_CN_LAYOUT'].matrix_world.inverted();rows=[]
for o in s.objects:
 if o.name.startswith(('SF_FRONT','SF_COAST','CR_','CN_QUAY','A02_SHIP','A01_CONTAINER','W01_NEW_PALLET','P01_SPREADER','SF_CN_LAYOUT')):
  pts=[I@o.matrix_world@Vector(v)for v in o.bound_box]if o.type=='MESH'else[I@o.matrix_world.translation]
  rows.append({'name':o.name,'parent':o.parent.name if o.parent else None,'type':o.type,'lo':[min(p[i]for p in pts)for i in range(3)],'hi':[max(p[i]for p in pts)for i in range(3)],'location':list(o.location),'world':list(map(list,o.matrix_world)),'action':o.animation_data.action.name if o.animation_data and o.animation_data.action else None})
(R/'review/probe.json').write_text(json.dumps(rows,indent=2));print('PROBED',len(rows))
