import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
s=bpy.context.scene;cam=s.camera;truck=s.objects['A03_TRAILER'];target=s.objects['CAM_LOOK_TARGET']
U=s.objects['US_FRAME'].matrix_world.copy();W=s.objects['CV_WH_US_FRAME'].matrix_world.copy();I=U.inverted()
portup=(U.to_quaternion()@Vector((0,0,1))).normalized();whup=(W.to_quaternion()@Vector((0,0,1))).normalized()
rows=[]
for tick in range(760,1321):
 f=tick/2;s.frame_set(int(f),subframe=f%1)
 q=cam.matrix_world.to_quaternion();eye=cam.matrix_world.translation.copy();forward=q@Vector((0,0,-1));up=q@Vector((0,1,0));right=q@Vector((1,0,0))
 row={'frame':f,'eye':list(eye),'q':list(q),'forward':list(forward),'target':list(target.matrix_world.translation),
      'truck':list(truck.matrix_world.translation),'truck_q':list(truck.matrix_world.to_quaternion()),
      'local_eye':list(I@eye),'local_truck':list(I@truck.matrix_world.translation),
      'lens':cam.data.lens,'shift':[cam.data.shift_x,cam.data.shift_y],
      'roll_port':math.degrees(math.atan2(portup.dot(right),portup.dot(up))),
      'roll_wh':math.degrees(math.atan2(whup.dot(right),whup.dot(up)))}
 rows.append(row)
data={'source':bpy.data.filepath,'rows':rows,'US':list(map(list,U)),'WH':list(map(list,W)),
      'camera_parent':cam.parent.name if cam.parent else None,'constraints':[c.type for c in cam.constraints],
      'portup':list(portup),'whup':list(whup),'camera_chain':[]}
o=cam
while o:
 data['camera_chain'].append([o.name,o.animation_data.action.name if o.animation_data and o.animation_data.action else None]);o=o.parent
(R/'review/inspection.json').write_text(json.dumps(data,indent=2))
print('CHAIN',data['camera_chain'],'CONSTRAINTS',data['constraints'])
for r in rows:
 if r['frame'] in [430,450,465,467,480,490,500,510,520,526,530,540,550,565,580,600,620,640]:
  print(r['frame'],'EYE',list(map(lambda x:round(x,2),r['local_eye'])),'TRUCK',list(map(lambda x:round(x,2),r['local_truck'])),'ROLL',[round(r['roll_port'],1),round(r['roll_wh'],1)],'LENS',round(r['lens'],2))
