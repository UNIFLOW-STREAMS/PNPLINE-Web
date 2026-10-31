import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent;s=bpy.context.scene;s.frame_set(870);U=s.objects['US_FRAME'].matrix_world.copy();I=U.inverted()
names=['US_FRAME','US_LAND_TERRACE','CV_WH_US_FRAME','WAREHOUSE_FLOOR','E10_OUTBOUND_YARD','E10_LOADING_BRIDGE','CV_FOUNDATION_WAREHOUSE','E11_ROUTE_1','E11_ROUTE_-1','A05_WAIT_MERGE','A04_PRIMARY','A05_SECONDARY','CAM_MASTER','CAM_LOOK_TARGET']+[o.name for o in s.objects if o.name.startswith('E12_DESTINATION')]
data={}
for n in names:
 o=s.objects.get(n)
 if not o:continue
 pts=[I@o.matrix_world@Vector(v) for v in o.bound_box] if o.type=='MESH' else [I@o.matrix_world.translation]
 data[n]={'parent':o.parent.name if o.parent else None,'matrix_local_us':list(map(list,I@o.matrix_world)),'bounds_us':[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]],'materials':[m.name if m else None for m in o.data.materials] if o.type=='MESH' else []}
samples={}
for f in [820,869,870,890,910,930,950,970,989]:
 s.frame_set(f);samples[f]={n:list(I@s.objects[n].matrix_world.translation) for n in ['CAM_MASTER','CAM_LOOK_TARGET','A04_PRIMARY','A05_SECONDARY']}
result={'US_FRAME':list(map(list,U)),'objects':data,'samples':samples}
(R/'current-scene-audit.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
