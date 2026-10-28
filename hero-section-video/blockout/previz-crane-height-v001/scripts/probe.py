import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;rows=[]
for f in [0,24,48,72,96,156,888,900,948]:
 s.frame_set(f);I=s.objects['A01_CONTAINER'].matrix_world.inverted();D=s.objects['SF_CN_LAYOUT'].matrix_world.inverted()
 for o in s.objects:
  if o.name.startswith(('CR_','P01_','W01_','A01_CONTAINER','CAM_MASTER','CAM_LOOK_TARGET')):
   pts=[I@o.matrix_world@v.co for v in o.data.vertices] if o.type=='MESH' else [I@o.matrix_world.translation]
   rows.append({'frame':f,'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'hide_render':o.hide_render,'hide_viewport':o.hide_viewport,'hide_set':o.hide_get(),'location':list(o.location),'city_location':list(D@o.matrix_world.translation),'min_cargo':[min(p[i]for p in pts) for i in range(3)],'max_cargo':[max(p[i]for p in pts) for i in range(3)],'materials':[(m.name,list(m.diffuse_color)) for m in o.data.materials if m] if o.type=='MESH' else [],'action':o.animation_data.action.name if o.animation_data and o.animation_data.action else None})
(R/'review/probe.json').write_text(json.dumps({'file':bpy.data.filepath,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'rows':rows},indent=2))
