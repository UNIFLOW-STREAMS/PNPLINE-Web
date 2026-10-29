"""Saved-camera positions, shortest-arc rotation and local-water roll at 48 samples/sec."""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;file=Path(bpy.data.filepath)
def at(f):
 s.frame_set(int(f),subframe=f%1);m=s.camera.matrix_world.copy();up=m.translation.normalized();forward=-m.to_3x3().col[2]
 roll=math.degrees(math.atan2(up.dot(m.to_3x3().col[0]),up.dot(m.to_3x3().col[1])))
 return m.translation.copy(),m.to_quaternion(),s.camera.data.lens,s.objects['CAM_LOOK_TARGET'].matrix_world.translation.copy(),roll
def omega(a,b,dt):
 q=a.rotation_difference(b)
 if q.w<0:q.negate()
 v=Vector((q.x,q.y,q.z));ang=2*math.atan2(v.length,q.w)
 return v.normalized()*(math.degrees(ang)/dt) if v.length>1e-10 else Vector((0,0,0))
rows=[];previous=None
for i in range(288*4,720*4+1):
 f=i/4;p,q,l,t,roll=at(f)
 row={'frame':f,'roll_degrees':roll,'height':p.length-140}
 if previous:
  pp,pq,pl,pt,pr=previous
  row.update(speed=(p-pp).length*48,angular_speed=omega(pq,q,1/48).length,roll_rate=abs((roll-pr+180)%360-180)*48)
 rows.append(row);previous=(p,q,l,t,roll)
joins=[]
for f in [300,420,468,528]:
 a,b,c=at(f-.25),at(f),at(f+.25);dt=1/48
 joins.append({'frame':f,'velocity_jump':((c[0]-b[0])-(b[0]-a[0])).length/dt,'angular_velocity_jump':(omega(b[1],c[1],dt)-omega(a[1],b[1],dt)).length,'lens_velocity_jump':abs((c[2]-b[2])-(b[2]-a[2]))/dt,'target_velocity_jump':((c[3]-b[3])-(b[3]-a[3])).length/dt})
report={'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'joins':joins,'range':[288,720],'samples_per_second':48,'rows':rows}
(R/'review'/f'{file.stem}-motion.json').write_text(json.dumps(report,indent=2))
print('JOINS',json.dumps(joins));print('MAXIMA',json.dumps({k:max((r.get(k,0),r['frame']) for r in rows) for k in ['speed','angular_speed','roll_rate']}))
