import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(144)
cn=s.objects['CN_FRAME'].matrix_world;ci=cn.inverted();ship=s.objects['A02_SHIP'];si=ship.matrix_world.inverted()
rows={}
for n in ['SF_FRONT_LAND','SF_COAST_FOLDED_FACE','SF_HULL_BLUE','SF_HULL_RED','SF_BOW_DECK','SF_BRIDGE_LEVEL_0','SHIP_BRIDGE','SF_CHINA_A','SF_CHINA_C','US_FRAME','EARTH_CONTINUOUS_OCEAN']:
 o=s.objects[n];m=si if n.startswith(('SF_HULL','SF_BOW','SF_BRIDGE','SHIP_'))else ci
 vs=[m@o.matrix_world@v.co for v in o.data.vertices]if o.type=='MESH'else [m@o.matrix_world.translation]
 rows[n]={'min':[min(v[j]for v in vs)for j in range(3)],'max':[max(v[j]for v in vs)for j in range(3)]}
 if n in ['SF_HULL_BLUE','SF_FRONT_LAND']:rows[n]['vertices']=[list(v)for v in vs]
rows['root_data']={o.name:{'location':list(o.location),'rotation':list(o.rotation_quaternion),'constraints':len(o.constraints),'children':len(o.children_recursive),'collections':[c.name for c in o.users_collection]}for o in s.objects if not o.parent}
rows['constraints']={o.name:[c.type for c in o.constraints]for o in s.objects if o.constraints}
rows['drivers']={o.name:[d.data_path for d in o.animation_data.drivers]for o in s.objects if o.animation_data and o.animation_data.drivers}
(R/'review/geometry-probe.json').write_text(json.dumps(rows,indent=2))
camera=s.camera;rows2=[]
for f in range(1393):
 s.frame_set(f)
 if f>=140 and f<=540:rows2.append({'f':f,'ship':list(ci@ship.matrix_world.translation),'camera':list(ci@camera.matrix_world.translation),'q':list(camera.matrix_world.to_quaternion()),'ship_q':list(ship.matrix_world.to_quaternion())})
(R/'review/baseline-motion.json').write_text(json.dumps(rows2))
print('Probe complete')
