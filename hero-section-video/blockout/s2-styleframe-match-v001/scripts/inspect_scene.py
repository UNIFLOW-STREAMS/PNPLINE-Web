"""Read-only baseline inventory and projection evidence; never saves a blend."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(156)
inv=s.objects['CN_FRAME'].matrix_world.inverted()
data={'scene':s.name,'camera':s.camera.name,'markers':[(m.name,m.frame) for m in s.timeline_markers],'camera_cn':list(inv@s.camera.matrix_world.translation),'objects':{}}
for o in s.objects:
 pts=[o.matrix_world@Vector(v) for v in o.bound_box] if o.type=='MESH' else [o.matrix_world.translation]
 p=[world_to_camera_view(s,s.camera,x) for x in pts]
 data['objects'][o.name]={'type':o.type,'parent':o.parent.name if o.parent else None,'data':o.data.name if o.data else None,'data_users':o.data.users if o.data else 0,'materials':[(m.name,m.users) for m in o.data.materials if m] if hasattr(o.data,'materials') else [],'local':list(o.location),'dimensions':list(o.dimensions),'cn':list(inv@o.matrix_world.translation),'visible':not(o.hide_render or o.hide_get()),'animation':o.animation_data.action.name if o.animation_data and o.animation_data.action else None,'bbox_top_left':[min(v.x for v in p),1-max(v.y for v in p),max(v.x for v in p),1-min(v.y for v in p)],'props':{k:str(v) for k,v in o.items()}}
(R/'review/baseline-inventory.json').write_text(json.dumps(data,indent=2))
print('INVENTORY',len(data['objects']))
