"""Bounded integration into the selected master, never into either input file."""
import bpy,sys,json,math,argparse,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
p=argparse.ArgumentParser()
for k in ['base','donor','config','output']:p.add_argument('--'+k,required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);cfg=json.loads(Path(a.config).read_text())
assert (cfg['F_lock'],cfg['F_rejoin'],cfg['fps'],cfg['frame_end'])==(720,948,12,1392),'This bounded revision does not authorize arbitrary retiming'
base,donor,out=map(lambda x:Path(x).resolve(),[a.base,a.donor,a.output])
assert out not in [base,donor]
for path,key in [(base,'base_sha256'),(donor,'donor_sha256')]:assert hashlib.sha256(path.read_bytes()).hexdigest()==cfg[key]
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R.parent/'s5-dock-test-v001/scripts'))
from kinematics import route,table,smooth
routecfg=json.loads((R.parent/'s5-dock-test-v001/config.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(base));s=bpy.data.scenes[cfg['scene']];bpy.context.window.scene=s
U=s.objects['US_FRAME'].matrix_world.copy();I=U.inverted();L=cfg['F_lock'];J=cfg['F_rejoin']
def frame(f):s.frame_set(int(f),subframe=f%1)
def curves(o):
 ad=o.animation_data
 return [f for l in ad.action.layers for st in l.strips for b in st.channelbags for f in b.fcurves] if ad and ad.action else []
def isolated(o):
 if o.animation_data and o.animation_data.action:o.animation_data.action=o.animation_data.action.copy()
def replace(o,path,rows,end,index=None):
 """Preserve the exact protected keys/handles; replace only (lock,end)."""
 indices=[index] if index is not None else list(range(len(rows[0][1])))
 for i in indices:
  fc=next(f for f in curves(o) if f.data_path==path and f.array_index==i)
  protected={float(k.co.x):(tuple(k.handle_left),tuple(k.handle_right),k.handle_left_type,k.handle_right_type,k.interpolation) for k in fc.keyframe_points if k.co.x<=L or k.co.x>=end}
  for k in reversed(list(fc.keyframe_points)):
   if L<k.co.x<end:fc.keyframe_points.remove(k,fast=True)
  for f,v in rows:
   if f<=L or f>=end:continue
   k=fc.keyframe_points.insert(f,v[i],options={'FAST'});k.interpolation='LINEAR'
  fc.update()
  for k in fc.keyframe_points:
   if float(k.co.x) in protected:
    hl,hr,lt,rt,interp=protected[float(k.co.x)];k.handle_left_type=lt;k.handle_right_type=rt;k.handle_left=hl;k.handle_right=hr;k.interpolation=interp
def mat(n,f):frame(f);return s.objects[n].matrix_world.copy()
def hermite(x,nodes):
 # Nodes: time, value, derivative per frame.
 for (f,p,v),(g,q,w) in zip(nodes,nodes[1:]):
  if f<=x<=g:
   t=(x-f)/(g-f);h=g-f
   return (2*t**3-3*t*t+1)*p+(t**3-2*t*t+t)*h*v+(-2*t**3+3*t*t)*q+(t**3-t*t)*h*w
 return nodes[-1][1]
def nodes(points,startv,endv):
 return [(f,Vector(v),startv if i==0 else endv if i==len(points)-1 else (Vector(points[i+1][1])-Vector(points[i-1][1]))/(points[i+1][0]-points[i-1][0])) for i,(f,v) in enumerate(points)]
tr=s.objects['A03_TRAILER'];tc=s.objects['A03_TRACTOR'];container=s.objects['A01_CONTAINER'];pallet=s.objects['W01_NEW_PALLET']
roots=[tr,tc,container,pallet];frame(L)
relc=tr.matrix_world.inverted()@container.matrix_world;relp=container.matrix_world.inverted()@pallet.matrix_world
initial=I@tr.matrix_world;p0=initial.translation.copy();prev=(I@mat(tr.name,L-.125)).translation
v0=(p0.x-prev.x)/.125
r=routecfg['route'];end=r['turn_x']+table(r['arc_rx'],r['arc_ry'])[1][-1]+.2
# Quintic with initial finite-difference velocity, mild entry deceleration,
# stationary end with zero acceleration; no replay of donor standstill.
h=810-L;c=[p0.x,v0*h,-.005*h*h/2];A=end-sum(c);B=-c[1]-2*c[2];C=-2*c[2]
c.extend([10*A-4*B+C/2,-15*A+7*B-C,6*A-3*B+C/2])
def localstate(f):
 if f<810:
  t=(f-L)/h;distance=sum(v*t**i for i,v in enumerate(c));p,v,acc=route(distance,routecfg)
  speed=math.hypot(*v);fw=Vector((v[0]/speed,v[1]/speed,0));k=(v[0]*acc[1]-v[1]*acc[0])/speed**3;yaw=math.atan2(v[1],v[0])
 else:
  p=(29.2+5.2*smooth((f-849)/41),29);fw=Vector((-1,0,0));k=0;yaw=math.pi
 # Original local height is numerical zero; taper its rounding residual.
 z=p0.z*(1-smooth((f-L)/4));tx=p[0]+2*math.cos(yaw);ty=p[1]+2*math.sin(yaw);tyaw=yaw+math.atan(2*k)
 return (p[0],p[1],z,yaw),(tx,ty,z,tyaw)
def pose(f):
 (x,y,z,yaw),(tx,ty,tz,tyaw)=localstate(f)
 tm=U@Matrix.Translation((x,y,z))@Matrix.Rotation(yaw,4,'Z');cm=U@Matrix.Translation((tx,ty,tz))@Matrix.Rotation(tyaw,4,'Z')
 return [tm,cm,tm@relc,tm@relc@relp]
rootrows={o.name:{'location':[],'rotation_quaternion':[]} for o in roots};priorq={}
for j in range(L*16+1,890*16):
 f=j/16
 for o,m in zip(roots,pose(f)):
  q=m.to_quaternion()
  if o.name in priorq and q.dot(priorq[o.name])<0:q.negate()
  priorq[o.name]=q.copy();rootrows[o.name]['location'].append((f,tuple(m.translation)));rootrows[o.name]['rotation_quaternion'].append((f,tuple(q)))
for o in roots:
 isolated(o)
 for path,rows in rootrows[o.name].items():replace(o,path,rows,890)
for n in ['A01_DOOR_L','A01_DOOR_R']:s.objects[n].location.x=-1.65
bridge=s.objects['DOCK_BRIDGE'];bridge.scale.y*=1.34/1.48;bridge.location.z=1.88
for n in ['A01_DOOR_LEFT_LEAF','A01_DOOR_RIGHT_LEAF']:
 o=s.objects[n];o.scale.z*=1.43/1.5;o.location.z+=.035
print('ROOTS_AND_HINGES',flush=True)
# Wheel rotation from evaluated trajectories, not transplanted old Euler keys.
wheels=[o for o in s.objects if o.name.startswith('A03') and '_WHEEL_' in o.name]
def wheelpoint(f,o):
 state=localstate(f)[1 if 'TRACTOR' in o.name else 0];x,y,z,yaw=state;wx,wy=o.location[:2]
 return (x+math.cos(yaw)*wx-math.sin(yaw)*wy,y+math.sin(yaw)*wx+math.cos(yaw)*wy,yaw)
frame(L);roll={o.name:float(o.rotation_euler.y) for o in wheels};previous={o.name:wheelpoint(L,o) for o in wheels};wr={o.name:[] for o in wheels}
for j in range(L*16+1,890*16+1):
 f=j/16;frame(f)
 for o in wheels:
  px,py,yaw=wheelpoint(f,o);old=previous[o.name];dx,dy=px-old[0],py-old[1];sign=1 if dx*math.cos(yaw)+dy*math.sin(yaw)>=0 else -1;roll[o.name]-=sign*math.hypot(dx,dy)/.4
  steering=0.
  if 'TRACTOR' in o.name and o.location.x>0:
   wa=wheelpoint(f-.01,o);wb=wheelpoint(f+.01,o);vx,vy=wb[0]-wa[0],wb[1]-wa[1]
   if math.hypot(vx,vy)>1e-10:
    vsign=1 if vx*math.cos(yaw)+vy*math.sin(yaw)>=0 else -1;steering=math.atan2(vsign*(-vx*math.sin(yaw)+vy*math.cos(yaw)),vsign*(vx*math.cos(yaw)+vy*math.sin(yaw)))
  wr[o.name].append((f,(math.pi/2,roll[o.name],steering)));previous[o.name]=(px,py,yaw)
for o in wheels:
 isolated(o)
 # All following phases belong to the recalculated rolling distance. Add
 # a final hold just before 1393 and remove obsolete post-dock wheel keys.
 rows=wr[o.name];rows.append((1392,rows[-1][1]));replace(o,'rotation_euler',rows,1393)
print('WHEEL_ROLL',flush=True)
ground=[]
for n in ['US_QUAY','US_LAND_TERRACE','E07_INBOUND_ROAD','E09_MANEUVER_YARD']:
 o=s.objects[n];ground.append(BVHTree.FromPolygons([I@o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons]))
zr={o.name:[] for o in wheels}
for j in range(L*16+1,890*16+1):
 f=j/16;frame(f)
 for o in wheels:
  m=I@o.matrix_world;center=m.translation;bottom=min((m@v.co).z for v in o.data.vertices)
  axis=I.to_3x3()@o.parent.matrix_world.to_3x3()@o.matrix_parent_inverse.to_3x3()@Vector((0,0,1))
  hits=[b.ray_cast(center+Vector((0,0,5)),Vector((0,0,-1)),20)[0] for b in ground];height=max(v.z for v in hits if v is not None)
  z=o.location.z+(height-bottom)/axis.z;zr[o.name].append((f,(0,0,z)))
for o in wheels:
 rows=zr[o.name];rows.append((1392,rows[-1][1]));replace(o,'location',rows,1393,index=2)
print('WHEEL_SUPPORT',flush=True)
# Camera/aim Hermite trajectory with original evaluated endpoint derivatives.
cam=s.camera;aim=s.objects['CAM_LOOK_TARGET'];saved={}
for f in [L-.125,L,L+.125,J-.125,J,J+.125]:
 frame(f);saved[f]=(I@cam.matrix_world,I@aim.matrix_world,float(cam.data.lens))
cp=[(L,tuple(saved[L][0].translation)),(752,(19,14.5,8.4)),(784,(25,17,9)),(810,(29.4,18.5,8.6)),(850,(33.6,19.5,7.8)),(890,(39,21,7.3)),(900,(40.5,21.5,7)),(924,(42.9,21.2,7.4)),(J,tuple(saved[J][0].translation))]
ap=[(L,tuple(saved[L][1].translation)),(752,(32,17,2.6)),(784,(31,26,2.4)),(810,(28.5,29,2.3)),(850,(28.8,29,2.3)),(890,(34.8,29,2.3)),(900,(35.6,29,2.3)),(924,(37.8,29,2.315)),(J,tuple(saved[J][1].translation))]
cn=nodes(cp,(saved[L][0].translation-saved[L-.125][0].translation)/.125,(saved[J+.125][0].translation-saved[J][0].translation)/.125)
an=nodes(ap,(saved[L][1].translation-saved[L-.125][1].translation)/.125,(saved[J+.125][1].translation-saved[J][1].translation)/.125)
def look(p,t):return (t-p).to_track_quat('-Z','Y')
# Retain original endpoint roll, smoothly distributed through the camera path.
offset0=look(saved[L][0].translation,saved[L][1].translation).inverted()@saved[L][0].to_quaternion()
offset1=look(saved[J][0].translation,saved[J][1].translation).inverted()@saved[J][0].to_quaternion()
cr={'location':[],'rotation_quaternion':[]};ar=[];lr=[];previousq=saved[L][0].to_quaternion()
for j in range(L*4+1,J*4):
 f=j/4;p=hermite(f,cn);t=hermite(f,an);q=U.to_quaternion()@(look(p,t)@offset0.slerp(offset1,smooth((f-L)/(J-L))))
 # A bounded C1 blend to evaluated original orientations carries its actual
 # angular velocity across both joins, including the inherited roll.
 frame(f);originalq=cam.matrix_world.to_quaternion()
 if f<L+8:q=originalq.slerp(q,smooth((f-L)/8))
 if f>J-12:q=q.slerp(originalq,smooth((f-J+12)/12))
 if q.dot(previousq)<0:q.negate()
 previousq=q.copy();cr['location'].append((f,tuple(U@p)));cr['rotation_quaternion'].append((f,tuple(q)));ar.append((f,tuple(U@t)))
 lens=saved[L][2]+(saved[J][2]-saved[L][2])*smooth((f-L)/(J-L));lr.append((f,(lens,)))
isolated(cam);isolated(aim);isolated(cam.data)
for path,rows in cr.items():replace(cam,path,rows,J)
replace(aim,'location',ar,J);replace(cam.data,'lens',lr,J,index=0)
frame(720)
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
s.frame_preview_start=624;s.frame_preview_end=948;s.use_preview_range=True
s['stage2_integration']='v001';s['stage2_F_lock']=L;s['stage2_F_rejoin']=J
bpy.ops.wm.save_as_mainfile(filepath=str(out))
print('SAVED',str(out),flush=True)
