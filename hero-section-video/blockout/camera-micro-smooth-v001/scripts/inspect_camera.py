import bpy,json,hashlib,math
import numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;cam=s.camera;rows=[]
previous=None
for tick in range(320*8,376*8+1):
 f=tick/8;s.frame_set(int(f),subframe=f%1);q=cam.matrix_world.to_quaternion()
 if previous and q.dot(previous)<0:q.negate()
 previous=q.copy()
 rows.append({'frame':f,'eye':list(cam.matrix_world.translation),'q':list(q),
  'lens':cam.data.lens,'shift':[cam.data.shift_x,cam.data.shift_y]})
data={'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'rows':rows}
(R/'review/inspection.json').write_text(json.dumps(data,indent=2))
for name in ['eye','q','lens','shift']:
 p=np.array([r[name] for r in rows]);v=np.diff(p,axis=0)*8;a=np.diff(v,axis=0)*8;j=np.diff(a,axis=0)*8
 if p.ndim>1:v=np.linalg.norm(v,axis=1);a=np.linalg.norm(a,axis=1);j=np.linalg.norm(j,axis=1)
 else:v=np.abs(v);a=np.abs(a);j=np.abs(j)
 for kind,x,offset in [('velocity',v,.0625),('acceleration',a,.125),('jerk',j,.1875)]:
  mask=np.array([330<=r['frame']+offset<=366 for r in rows[:len(x)]])
  ids=np.where(mask)[0];peak=ids[np.argsort(x[ids])[-8:][::-1]]
  print(name,kind,[(rows[i]['frame']+offset,round(float(x[i]),6)) for i in peak],flush=True)
