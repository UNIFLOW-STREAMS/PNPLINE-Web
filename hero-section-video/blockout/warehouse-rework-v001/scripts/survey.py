import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];S=bpy.context.scene
U=S.objects['US_FRAME'].matrix_world.copy();I=U.inverted()
rows=[]
for o in S.objects:
 if any(c.name.startswith(('04_TRANSPORT','05_WAREHOUSE','06_CARGO_WORK')) for c in o.users_collection):
  rows.append({'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'location':list(o.location),'dimensions':list(o.dimensions),'action':o.animation_data.action.name if o.animation_data and o.animation_data.action else None,'collections':[c.name for c in o.users_collection]})
names=['A02_TRAILER','A02_TRACTOR','A04_PRIMARY','A05_SECONDARY','W01_NEW_PALLET','W01_STORED_PALLET','W02_INBOUND_JACK','W02_STORAGE_JACK','W05_PICK_CART','W09_OUT_CART','W08_LAST_LOAD','CH_LOADER','CAM_MASTER','CAM_LOOK_TARGET']
samples={}
for f in [1,648,810,842,900,908,930,952,985,1018,1043,1074,1090,1150,1166,1193,1200,1260,1310,1392]:
 S.frame_set(f);deps=bpy.context.evaluated_depsgraph_get();samples[f]={}
 for name in names:
  o=S.objects.get(name)
  if o:
   e=o.evaluated_get(deps);m=I@e.matrix_world
   samples[f][name]={'p':list(m.translation),'q':list(m.to_quaternion())}
result={'source':bpy.data.filepath,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'objects':rows,'samples':samples,'scene':{'start':S.frame_start,'end':S.frame_end,'fps':S.render.fps,'camera':S.camera.name},'US_FRAME':[list(v) for v in U]}
(R/'review/survey.json').write_text(json.dumps(result,indent=2))
print('WAREHOUSE_SURVEY',len(rows), 'objects',len(samples),'samples')
print('ROOTS',json.dumps([x for x in rows if x['type']=='EMPTY']))
