"""Compare actual reopened poses; measure screen-space deviation and jitter."""
import bpy,json,hashlib,math
import numpy as np
from mathutils import Vector
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];cfg=json.loads((R/'config.json').read_text());data={}
for kind,path in [('before',(R/cfg['source']).resolve()),('after',R/cfg['output'])]:
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;cam=s.camera
 landmarks={n:s.objects[n] for n in ['A02_SHIP','A01_CONTAINER','SHIP_BRIDGE','US_FRAME']};rows=[];last=None
 for tick in range(326*2,370*2+1):
  f=tick/2;s.frame_set(int(f),subframe=f%1);q=cam.matrix_world.to_quaternion()
  if last and q.dot(last)<0:q.negate()
  last=q.copy()
  screen={n:list(world_to_camera_view(s,cam,o.matrix_world.translation)) for n,o in landmarks.items()}
  rows.append({'frame':f,'eye':list(cam.matrix_world.translation),'q':list(q),'screen':screen,'lens':cam.data.lens,'shift':[cam.data.shift_x,cam.data.shift_y]})
 p=np.array([r['eye'] for r in rows]);q=np.array([r['q'] for r in rows]);q/=np.linalg.norm(q,axis=1)[:,None]
 v=np.diff(p,axis=0)*2;a=np.diff(v,axis=0)*2;j=np.diff(a,axis=0)*2
 qv=np.diff(q,axis=0)*2;qa=np.diff(qv,axis=0)*2;qj=np.diff(qa,axis=0)*2
 def peak(x,offset=0):
  selected=[np.linalg.norm(v) for v,r in zip(x,rows[offset:]) if 336<=r['frame']<=360]
  return float(max(selected))
 metrics={'speed_max':peak(v),'acceleration_max':peak(a,1),'translation_jerk_max':peak(j,1),
  'rotation_speed_max_deg_per_frame':peak(qv)*2*180/math.pi,
  'rotation_jerk_max':peak(qj,1)}
 data[kind]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'rows':rows,'metrics':metrics}
 print(kind,json.dumps(metrics),flush=True)
before=data['before']['rows'];after=data['after']['rows'];deltas=[]
for a,b in zip(before,after):
 q1=np.array(a['q']);q2=np.array(b['q']);q1/=np.linalg.norm(q1);q2/=np.linalg.norm(q2)
 deltas.append({'frame':a['frame'],'position':math.dist(a['eye'],b['eye']),
  'rotation_deg':2*math.degrees(math.acos(min(1,abs(float(q1@q2))))),
  'projection_pixels':max(math.hypot((a['screen'][n][0]-b['screen'][n][0])*1280,(a['screen'][n][1]-b['screen'][n][1])*720) for n in a['screen']),
  'optics_identical':a['lens']==b['lens'] and a['shift']==b['shift']})
data['deltas']=deltas
data['deviation']={k:max(r[k] for r in deltas) for k in ['position','rotation_deg','projection_pixels']}
data['deviation']['optics_identical']=all(r['optics_identical'] for r in deltas)
(R/'review/motion.json').write_text(json.dumps(data,indent=2));print('DEVIATION',data['deviation'],flush=True)
