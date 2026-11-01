import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R.parent/'city-expansion-v002/pnpline-city-expansion-v002.blend'))
s=bpy.context.scene;s.frame_set(349);I=s.objects['US_FRAME'].matrix_world.inverted()
def bounds(o):
 p=[I@o.matrix_world@Vector(v) for v in o.bound_box]
 return [[round(min(v[i] for v in p),3) for i in range(3)],[round(max(v[i] for v in p),3) for i in range(3)]]
prefix=('UC_CONTAINER','UC_STATIC_CRANE','US_QUAY','US_PORT','US_YARD','UC_RAIL','P02_','AR_','SHIP_','TRAILER_','TRACTOR_')
data={o.name:{'parent':o.parent.name if o.parent else None,'bounds':bounds(o),'materials':[m.name for m in o.data.materials] if o.type=='MESH' else []} for o in s.objects if o.type=='MESH' and o.name.startswith(prefix)}
samples={}
for f in [0,250,280,300,315,330,349,360,375,390,405,420,450,480,530]:
 s.frame_set(f)
 samples[f]={o.name:{'pos':list(I@o.matrix_world.translation),'bounds':bounds(o)} for o in s.objects if o.name in ['A02_SHIP','A01_CONTAINER','A03_TRACTOR','A03_TRAILER','P02_TROLLEY','P02_SPREADER','P02_SPREADER_FRAME','SHIP_HULL','TRAILER_CHASSIS','TRACTOR_CAB']}
out={'objects':data,'samples':samples,'camera':s.camera.name,'fps':s.render.fps}
(R/'review/port-survey.json').write_text(json.dumps(out,indent=2))
print(json.dumps({'object_count':len(data),'major':{n:v for n,v in data.items() if n.startswith(('US_','P02_','AR_'))},'samples':samples},indent=2))
