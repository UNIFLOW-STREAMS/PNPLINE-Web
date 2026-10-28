"""Extend the adopted layout to the full film, preserving the original inputs."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Matrix,Vector,Quaternion
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];B=R.parents[1]/'blockout/full-layout-master-v001';B.mkdir(exist_ok=True)
for folder in ['review','preview','logs']:(B/folder).mkdir(exist_ok=True)
source=R/'master/source-current.blend';proposal=R/'layout-proposal-v001/s4-s5-layout-proposal-v001.blend';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(source)=='8c76f0e184bc742309cf66dcf9f3f5fa7072e02b54b58e6985a91ff1ae57b665'
assert sha(proposal)=='c9efed5cabde76926b340732191ef8470986a5b36b2095f1a416f2064a2c4296'
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;U=s.objects['US_FRAME'].matrix_world.copy();I=U.inverted();S=Matrix.Diagonal((1,-1,1,1));A=U@Matrix.Translation((0,18,0))@S@I
frames=[i/4 for i in range(1392*4+1)]
env=list(s.objects['US_FRAME'].children_recursive)
def animated(o):return bool(o.animation_data and o.animation_data.action) or bool(o.parent and animated(o.parent))
dynamic_env=[o.name for o in env if animated(o)]
roots=[o.name for o in s.objects if o.parent is None and o.animation_data and o.animation_data.action and o.name not in ['CAM_MASTER','CAM_LOOK_TARGET'] and not o.name.startswith('P01_')]
wheels=[o.name for o in s.objects if o.name.startswith('A03') and '_WHEEL_' in o.name]
cache={n:[] for n in roots+dynamic_env};wl={n:[] for n in wheels};we={n:[] for n in wheels};camera=[];targets=[];lenses=[]
for f in frames:
 s.frame_set(int(f),subframe=f%1)
 for n in cache:cache[n].append(s.objects[n].matrix_world.copy())
 for n in wheels:wl[n].append(s.objects[n].location.copy());we[n].append(s.objects[n].rotation_euler.copy())
 camera.append(s.camera.matrix_world.copy());targets.append(s.objects['CAM_LOOK_TARGET'].matrix_world.copy());lenses.append(s.camera.data.lens)
markers={m.name:m.frame for m in s.timeline_markers};radius=s.get('radius',140.0)
def smooth(t):
 t=max(0,min(1,t));return t*t*t*(10+t*(-15+6*t))
def mixmat(a,b,t):
 la,qa,sa=a.decompose();lb,qb,sb=b.decompose();return Matrix.LocRotScale(la.lerp(lb,t),qa.slerp(qb,t),sa.lerp(sb,t))
def transport(j):
 """Latitude migration follows the globe, so the relocated ship still floats."""
 f=frames[j];w=smooth((f-216)/240);p=cache['A02_SHIP'][j].translation
 axis=Vector((p.z,0,-p.x)).normalized();lat=math.asin(18/radius)*w;q=Quaternion(axis,-lat)
 desired=Vector((p.x*math.cos(lat),radius*math.sin(lat),p.z*math.cos(lat)))
 reflected=p.lerp((A@cache['A02_SHIP'][j]@S).translation,w)
 return Matrix.Translation(desired)@q.to_matrix().to_4x4()@Matrix.Translation(-reflected)
D=transport(int(552*4));travel={'A02_SHIP','A01_CONTAINER','W01_NEW_PALLET'}
transports=[transport(j) for j in range(len(frames))]
bpy.ops.wm.open_mainfile(filepath=str(proposal));s=bpy.context.scene
# Keep the chosen camera and asset relationships exactly in US local coordinates.
pc=[];pt=[];pl=[]
for f in frames:
 if 552<=f<=948:
  s.frame_set(int(f),subframe=f%1);pc.append(s.camera.matrix_world.copy());pt.append(s.objects['CAM_LOOK_TARGET'].matrix_world.copy());pl.append(s.camera.data.lens)
 else:pc.append(None);pt.append(None);pl.append(None)
# Object references from the previous .blend are invalid after open_mainfile.
static_env=[n for n in json.loads((R/'layout-proposal-v001/build-record.json').read_text())['flattened_environment'] if n not in dynamic_env]
for n in static_env:s.objects[n].matrix_world=D@s.objects[n].matrix_world
s.objects['US_FRAME'].matrix_world=D@U
def fc(o,path,index,values,samples=None):
 samples=frames if samples is None else samples
 o.keyframe_insert(data_path=path,index=-1 if path=='lens' else index,frame=samples[0]);ad=o.animation_data
 curves=ad.action.layers[0].strips[0].channelbag(ad.action_slot).fcurves
 c=next(c for c in curves if c.data_path==path and c.array_index==index);c.keyframe_points.clear();c.keyframe_points.add(len(values));c.keyframe_points.foreach_set('co',[a for f,v in zip(samples,values) for a in (f,v)])
 for k in c.keyframe_points:k.interpolation='LINEAR'
 c.update()
def bake(o,matrices):
 o.animation_data_clear();o.rotation_mode='QUATERNION';rows=[[],[],[]];previous=None
 for m in matrices:
  l,q,z=m.decompose()
  if previous and q.dot(previous)<0:q.negate()
  previous=q.copy()
  for arr,v in zip(rows,[l,q,z]):arr.append(v)
 for path,arr,num in [('location',rows[0],3),('rotation_quaternion',rows[1],4),('scale',rows[2],3)]:
  for k in range(num):fc(o,path,k,[v[k] for v in arr])
all_mats={}
for n in roots+dynamic_env:
 mats=[]
 for j,m in enumerate(cache[n]):
  if n in travel:
   w=smooth((frames[j]-216)/240);m=transports[j]@mixmat(m,A@m@S,w)
  else:m=D@A@m@S
  mats.append(m)
 all_mats[n]=mats
# Preserve the actual occupied ship slot during transit. A layout reflection must
# not slide the blue container through the other deck cargo. The hoist joins the
# adopted pickup trajectory only after lifting clear, by the unchanged f552.
for j,f in enumerate(frames):
 if f<552:
  ship_relative=cache['A02_SHIP'][j].inverted()@cache['A01_CONTAINER'][j]
  carried=all_mats['A02_SHIP'][j]@ship_relative
  all_mats['A01_CONTAINER'][j]=mixmat(carried,all_mats['A01_CONTAINER'][j],smooth((f-542)/10))
  all_mats['W01_NEW_PALLET'][j]=all_mats['A01_CONTAINER'][j]@(cache['A01_CONTAINER'][j].inverted()@cache['W01_NEW_PALLET'][j])
pickup_delta=all_mats['A01_CONTAINER'][510*4].translation-(D@A@cache['A01_CONTAINER'][510*4]@S).translation
for n in ['P02_SPREADER','P02_TROLLEY']+[f'P02_CABLE_{i}' for i in range(4)]:
 for j,f in enumerate(frames):
  if f<552:all_mats[n][j].translation+=pickup_delta*(1-smooth((f-542)/10))
for n,mats in all_mats.items():bake(s.objects[n],mats)
for n in wheels:
 o=s.objects[n];opposite=next(k for k in wheels if s.objects[k].parent==o.parent and abs(wl[k][0].x-wl[n][0].x)<.001 and abs(wl[k][0].y+wl[n][0].y)<.001);o.animation_data_clear()
 for k in range(3):
  fc(o,'location',k,[(-v[k] if k==1 else v[k]) for v in wl[opposite]])
  fc(o,'rotation_euler',k,[(-v[k] if k==2 else v[k]) for v in we[opposite]])
def reflected(v):return (A@Matrix.Translation(v)).translation
def look(loc,aim,up):
 # Track quaternion roll agrees with the source tangent frame.
 z=(loc-aim).normalized();x=up.cross(z).normalized();y=z.cross(x).normalized();rot=Matrix((x,y,z)).transposed().to_quaternion();return Matrix.LocRotScale(loc,rot,Vector((1,1,1)))
cm=[];tm=[];ll=[]
# Join the original S4 approach to the approved f552 position AND velocity.
j0=528*4;j1=552*4
def pre_camera(j):
 f=frames[j];m=camera[j];t=targets[j];w=smooth((f-408)/96)
 if f<=216:return m,t,lenses[j]
 shift=cache['A02_SHIP'][j].translation.lerp((A@cache['A02_SHIP'][j]).translation,smooth((f-216)/240))-cache['A02_SHIP'][j].translation
 loc=m.translation+shift;aim=t.translation+shift
 loc=loc.lerp(reflected(m.translation),w);aim=aim.lerp(reflected(t.translation),w)
 loc=transports[j]@loc;aim=transports[j]@aim
 up=transports[j].to_3x3()@m.to_3x3().col[1]
 return look(loc,aim,up),Matrix.Translation(aim),lenses[j]
# Up from original image is used only for S3; by f504 settle to the destination
# tangent-up used by the approved camera, so the new shore does not introduce roll.
def basis_pre(j):
 m,t,l=pre_camera(j);f=frames[j]
 if f>456:
  up=(D@U).to_3x3().col[2];desired=look(m.translation,t.translation,up);m=mixmat(m,desired,smooth((f-456)/48))
 return m,t,l
start=basis_pre(j0);startnext=basis_pre(j0+1);startprev=basis_pre(j0-1)
end=(D@pc[j1],D@pt[j1],pl[j1]);endnext=(D@pc[j1+1],D@pt[j1+1],pl[j1+1])
def hermite(a,b,va,vb,t):
 h=24;return (2*t**3-3*t*t+1)*a+(t**3-2*t*t+t)*h*va+(-2*t**3+3*t*t)*b+(t**3-t*t)*h*vb
for j,f in enumerate(frames):
 if f<528:m,t,l=basis_pre(j)
 elif f<552:
  u=(f-528)/24;loc=hermite(start[0].translation,end[0].translation,(startnext[0].translation-startprev[0].translation)/.5,(endnext[0].translation-end[0].translation)/.25,u)
  aim=hermite(start[1].translation,end[1].translation,(startnext[1].translation-startprev[1].translation)/.5,(endnext[1].translation-end[1].translation)/.25,u)
  m=look(loc,aim,(D@U).to_3x3().col[2]);t=Matrix.Translation(aim);l=hermite(start[2],end[2],(startnext[2]-startprev[2])/.5,(endnext[2]-end[2])/.25,u)
 elif f<=948:m=D@pc[j];t=D@pt[j];l=pl[j]
 else:
  loc=D@reflected(camera[j].translation);aim=D@reflected(targets[j].translation);m=look(loc,aim,(D@U).to_3x3().col[2]);t=Matrix.Translation(aim);l=lenses[j]
 cm.append(m);tm.append(t);ll.append(l)
bake(s.camera,cm);bake(s.objects['CAM_LOOK_TARGET'],tm);s.camera.data.animation_data_clear();fc(s.camera.data,'lens',0,ll)
# Quarter-frame sampling can interpolate across a narrow road-height step.
# Solve tyre contact on the actual integrated pose at the established 1/16 cadence.
s.frame_set(0);J=s.objects['US_FRAME'].matrix_world.inverted();ground=[]
for n in ['US_QUAY','US_LAND_TERRACE','E07_INBOUND_ROAD','E09_MANEUVER_YARD']:
 o=s.objects[n];ground.append(BVHTree.FromPolygons([J@o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons]))
support_frames=[i/4 for i in range(648*4)]+[i/16 for i in range(648*16,1392*16+1)];zs={n:[] for n in wheels}
for f in support_frames:
 s.frame_set(int(f),subframe=f%1)
 for n in wheels:
  o=s.objects[n];m=J@o.matrix_world;c=m.translation;bottom=min((m@v.co).z for v in o.data.vertices)
  hits=[b.ray_cast(c+Vector((0,0,5)),Vector((0,0,-1)),20)[0] for b in ground];height=max(v.z for v in hits if v is not None)
  axis=J.to_3x3()@o.parent.matrix_world.to_3x3()@o.matrix_parent_inverse.to_3x3()@Vector((0,0,1));zs[n].append(o.location.z+(height-bottom)/axis.z)
for n in wheels:fc(s.objects[n],'location',2,zs[n],support_frames)
s.frame_start=0;s.frame_end=1392;s.use_preview_range=False;s.frame_preview_start=0;s.frame_preview_end=1392;s.frame_set(648)
for k in ['proposal_status','valid_review_range']:s.pop(k,None)
s['integration_status']='Full S1-S7 master; layout adopted by user instruction';s['integration_range']='0-1392';s['input_sha256']=sha(source);s['adopted_proposal_sha256']=sha(proposal)
out=B/'master-full-layout-v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out))
record={'source':str(source),'source_sha256':sha(source),'adopted_proposal':str(proposal),'adopted_proposal_sha256':sha(proposal),'master':str(out),'master_sha256':sha(out),'builder_sha256':sha(__file__),'range':[0,1392],'fps':12,'step':.25,'us_geographic_transport':list(map(list,D)),'latitude_degrees':math.degrees(math.asin(18/radius)),'source_markers':markers,'authorization':'User: 전체 마스터에 통합해라.','method':'Unchanged CN opening; spherical S3 latitude connection; approved proposal preserved in US coordinates; S6/S7 actor and camera continuation through1392.'}
(B/'build-record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf8');print('FULL_MASTER_SAVED',out,flush=True)
