import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(1075);u=s.objects['US_FRAME'].matrix_world.copy();inv=u.inverted()
rows=[]
for o in s.objects:
 if o.type=='MESH':pts=[inv@o.matrix_world@Vector(v) for v in o.bound_box];bb=[[min(v[k] for v in pts) for k in range(3)],[max(v[k] for v in pts) for k in range(3)]]
 else:bb=None
 rows.append({'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'collections':[c.name for c in o.users_collection],'p':list((inv@o.matrix_world).translation),'rot':list((inv@o.matrix_world).to_quaternion()),'bounds':bb,'action':o.animation_data.action.name if o.animation_data and o.animation_data.action else None,'constraints':[(c.type,c.name) for c in o.constraints],'hidden':o.hide_render,'props':{k:str(v) for k,v in o.items()}})
names=['EARTH_CONTINUOUS_OCEAN','US_FRAME','CN_FRAME','A02_SHIP','A01_CONTAINER','A03_TRAILER','A03_TRACTOR','A04_PRIMARY','A05_SECONDARY','P02_TROLLEY','P02_SPREADER_FRAME','CAM_MASTER','CAM_LOOK_TARGET']
samples={}
for f in [1,360,455,510,600,648,720,744,768,810,842,900,908,952,1075,1158,1200,1248,1261,1320,1392]:
 s.frame_set(f);samples[f]={n:{'p':list((inv@s.objects[n].matrix_world).translation),'matrix':list(map(list,inv@s.objects[n].matrix_world))} for n in names if n in s.objects}
report={'source':bpy.data.filepath,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'us_matrix':list(map(list,u)),'world':{n:{'p':list(s.objects[n].matrix_world.translation),'dimensions':list(s.objects[n].dimensions),'scale':list(s.objects[n].scale)} for n in names[:3]},'objects':rows,'samples':samples}
(R/'review/survey.json').write_text(json.dumps(report,indent=2))
print('WORLD',json.dumps(report['world']));print('ROOTS',json.dumps([o for o in rows if o['name'] in names or o['name'].startswith(('US_LAND','UC_AR_CITY_FOUNDATION','UC_CITY_DISTRICT','US_PORT'))]));print('COUNTS',len(rows))
