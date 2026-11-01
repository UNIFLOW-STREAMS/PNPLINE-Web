import bpy, json, math, hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1]
s=bpy.context.scene;cam=s.camera;ship=s.objects['A02_SHIP'];target=s.objects['CAM_LOOK_TARGET']
U=s.objects['US_FRAME'].matrix_world.copy();I=U.inverted();rows=[]
geo=[o for o in ship.children_recursive if o.type=='MESH']
for tick in range(180*2,391*2):
 f=tick/2;s.frame_set(int(f),subframe=f%1)
 q=cam.matrix_world.to_quaternion();eye=cam.matrix_world.translation.copy();M=ship.matrix_world.copy();S=M.inverted()
 pos=M.translation.copy();screen=world_to_camera_view(s,cam,pos)
 rows.append({'frame':f,'eye':list(eye),'q':list(q),'forward':list(q@Vector((0,0,-1))),'up':list(q@Vector((0,1,0))),
 'ship':list(pos),'ship_q':list(M.to_quaternion()),'relative_eye':list(S@eye),'screen':list(screen),
 'target':list(target.matrix_world.translation),'local_eye':list(I@eye),'local_ship':list(I@pos),
 'lens':cam.data.lens,'shift':[cam.data.shift_x,cam.data.shift_y]})
data={'source':bpy.data.filepath,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
      'US':list(map(list,U)),'rows':rows,'ship_children':[o.name for o in geo]}
(R/'review/inspection.json').write_text(json.dumps(data,indent=2))
for r in rows:
 if r['frame']%5==0 and 235<=r['frame']<=355:
  print(r['frame'],'EYE',*[round(v,2) for v in r['local_eye']],'SHIP',*[round(v,2) for v in r['local_ship']],
        'REL',*[round(v,2) for v in r['relative_eye']],'SCREEN',*[round(v,2) for v in r['screen'][:2]],'LENS',round(r['lens'],2),flush=True)
