import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;I=s.objects['US_FRAME'].matrix_world.inverted();rows=[]
names=['A04_PRIMARY_FLOOR','A04_PRIMARY_CARGO_SHELL','A04_PRIMARY_LEFT_LEAF','E10_LOADING_BRIDGE','A01_FLOOR','TRAILER_CHASSIS','DOCK_BRIDGE','WAREHOUSE_FLOOR','W02_INBOUND_JACK_FORKS','W02_INBOUND_JACK_HANDLE','W01_NEW_PALLET_BASE','W02_STORAGE_JACK_FORKS','W02_STORAGE_JACK_HANDLE','W01_STORED_PALLET_BASE','RACK_SHELF_44_32.5_2.1','CH_LOADER_LEG-0.12','CH_LOAD_SUPPORT','P02_TROLLEY','P02_LEG_-25','P02_BOOM_-2']
for f in [0,582,888,900,924,960,966,1014,1032,1164,1200]:
 s.frame_set(f)
 for n in names:
  o=s.objects.get(n)
  if not o:continue
  pts=[I@o.matrix_world@v.co for v in o.data.vertices]
  rows.append({'frame':f,'name':n,'parent':o.parent.name if o.parent else None,'location':list(o.location),'min':[min(p[i] for p in pts) for i in range(3)],'max':[max(p[i] for p in pts) for i in range(3)]})
(R/'review/us-bounds.json').write_text(json.dumps(rows,indent=2))
