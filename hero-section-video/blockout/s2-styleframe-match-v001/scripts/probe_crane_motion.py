import bpy,json
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(0);D=s.objects['SF_CN_LAYOUT'];DI=D.matrix_world.inverted();data={'range':[s.frame_start,s.frame_end],'objects':{},'samples':{}}
for n in ['A01_CONTAINER','P01_SPREADER','CAM_MASTER','CAM_LOOK_TARGET']:
 o=s.objects[n];data['objects'][n]={'parent':o.parent.name if o.parent else None,'rotation_mode':o.rotation_mode,'action':o.animation_data.action.name if o.animation_data and o.animation_data.action else None,'constraints':[c.type for c in o.constraints],'children':[c.name for c in o.children]}
for f in [0,24,48,71,72,73,84,96,104,124,144,156]:
 s.frame_set(f);data['samples'][f]={n:{'pos':list(DI@s.objects[n].matrix_world.translation),'rotation':list((DI@s.objects[n].matrix_world).to_quaternion())}for n in ['A01_CONTAINER','P01_SPREADER','CAM_MASTER','CAM_LOOK_TARGET']}
data['cargo_bounds']={o.name:[list(DI@o.matrix_world@Vector(p))for p in o.bound_box]for o in s.objects if o.name.startswith(('A01_','P03_'))and o.type=='MESH'and not o.hide_render}
(R/'review/crane-motion-baseline.json').write_text(json.dumps(data,indent=2));print(json.dumps({k:v for k,v in data.items()if k!='cargo_bounds'}))
