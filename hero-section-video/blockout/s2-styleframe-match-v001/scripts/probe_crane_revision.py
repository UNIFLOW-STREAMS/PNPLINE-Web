import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;data={'objects':{},'frames':{}}
s.frame_set(156);D=s.objects['SF_CN_LAYOUT'];DI=D.matrix_world.inverted()
for o in s.objects:
 if o.name.startswith(('P01_','A01_','SF_CRANE')):
  data['objects'][o.name]={'type':o.type,'parent':o.parent.name if o.parent else None,'hide':o.hide_render,'location':list(o.location),'dimensions':list(o.dimensions),'local_pos':list(DI@o.matrix_world.translation),'constraints':[{'type':c.type,'name':c.name}for c in o.constraints],'drivers':[(d.data_path,d.driver.expression)for d in o.animation_data.drivers]if o.animation_data else []}
for f in [0,24,48,72,96,124,156,180,216,278,330,450]:
 s.frame_set(f);DI=D.matrix_world.inverted();data['frames'][f]={}
 for n in ['P01_TROLLEY','P01_SPREADER','A01_CONTAINER','A02_SHIP']:
  o=s.objects.get(n)
  if o:data['frames'][f][n]={'pos':list(DI@o.matrix_world.translation),'size':list(o.dimensions),'rot':list((DI@o.matrix_world).to_euler())}
(R/'review/crane-probe-v017.json').write_text(json.dumps(data,indent=2));print(json.dumps(data))
