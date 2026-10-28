import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;I=s.objects['US_FRAME'].matrix_world.inverted()
rows=[]
for f in [0,96,216,300,360,408,432,456,480,504,528,551,552,948,960,1008,1020,1090,1158,1200,1296,1392]:
 s.frame_set(f);r={'frame':f,'lens':s.camera.data.lens,'objects':{}}
 for n in ['A02_SHIP','A01_CONTAINER','W01_NEW_PALLET','CAM_MASTER','CAM_LOOK_TARGET','A04_PRIMARY','A05_SECONDARY','W01_STORED_PALLET','W08_LAST_LOAD']:
  o=s.objects[n];r['objects'][n]={'world':list(o.matrix_world.translation),'us':list((I@o.matrix_world).translation),'q':list(o.matrix_world.to_quaternion())}
 rows.append(r)
(R/'review/full-integration-probe.json').write_text(json.dumps({'scene_props':{k:str(s[k]) for k in s.keys()},'rows':rows},indent=2),encoding='utf8')
for r in rows:
 print(r['frame'],'CAM_US',r['objects']['CAM_MASTER']['us'],'AIM_US',r['objects']['CAM_LOOK_TARGET']['us'],'SHIP_US',r['objects']['A02_SHIP']['us'],'LENS',r['lens'])
