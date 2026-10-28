import bpy,json
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1];out=R/'review/s4-s5-recheck';out.mkdir(exist_ok=True)
s=bpy.context.scene;I=s.objects['US_FRAME'].matrix_world.inverted();rows={}
for f in [552,576,600,624,636,648,660,672,696,720]:
 s.frame_set(f);rows[f]={}
 for o in s.objects:
  if any(k in o.name for k in ['SHIP','CRANE','WAREHOUSE','ROAD']) or o.name in ['A03_TRACTOR','A03_TRAILER','A01_CONTAINER','CAM_MASTER','CAM_LOOK_TARGET','DOCK_BRIDGE']:
   m=I@o.matrix_world;bb=[m@Vector(c) for c in o.bound_box] if o.type=='MESH' else [m.translation]
   rows[f][o.name]={'center':list(m.translation),'min':[min(v[j] for v in bb) for j in range(3)],'max':[max(v[j] for v in bb) for j in range(3)],'type':o.type,'matrix_us':list(map(list,m))}
 rows[f]['lens']=s.camera.data.lens
(out/'scene-probe.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
for f in rows:
 print('FRAME',f,{k:rows[f][k]['center'] for k in ['A03_TRAILER','CAM_MASTER','CAM_LOOK_TARGET']},rows[f]['lens'])
print('STRUCTURE', {k:v for k,v in rows[648].items() if k!='lens' and any(t in k for t in ['SHIP_HULL','WAREHOUSE_FLOOR','ROAD','CRANE_LEG'])})
