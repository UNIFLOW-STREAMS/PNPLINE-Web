"""Build an unadopted B candidate from the immutable full master only."""
import bpy,json,math,hashlib,sys
import numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];args=sys.argv[sys.argv.index('--')+1:]if '--'in sys.argv else []
out=R/(args[0]if args else 'candidate-b-a-side-v001.blend')
if out.exists()or out.resolve()==(R/'inputs/base.blend').resolve():raise RuntimeError('Output exists or aliases input')
manifest=json.loads((R/'inputs/manifest.json').read_text())
if hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()!=manifest['source_sha256']:raise RuntimeError('Wrong input')
s=bpy.context.scene;s.frame_set(144);cn=s.objects['CN_FRAME'].matrix_world.copy();oldus=s.objects['US_FRAME'].matrix_world.copy();basis=cn.to_3x3();up0=basis.col[2].normalized()
names=['A02_SHIP','A01_CONTAINER','CAM_MASTER','CAM_LOOK_TARGET'];old={n:[]for n in names}
for f in range(1393):
 s.frame_set(f)
 for n in names:old[n].append(s.objects[n].matrix_world.copy())
# A smooth offshore turn, then ocean transit. Positive local y is seaward.
# Smoothstep heading has zero curvature at both ends of the turn.
turn_length=72.;end_x=-190.;dt=.05
arc=np.arange(0,turn_length+dt/2,dt);u=arc/turn_length
head=math.pi*(u*u*(3-2*u));x=np.cumsum(np.cos(head))*dt;y=np.cumsum(np.sin(head))*dt;x-=x[0];y-=y[0]
xy=[(float(a),float(b))for a,b in zip(x,y)]
xy.extend([(float(a),float(y[-1]))for a in np.arange(x[-1]-dt,end_x-dt/2,-dt)])
def sphere(a,b):
 r=math.hypot(a,b)
 return basis@Vector((math.sin(r/140)*a/r,math.sin(r/140)*b/r,math.cos(r/140)))*140 if r else up0*140
pts=[sphere(a,b)for a,b in xy];dist=np.array([0.]+[(pts[i]-pts[i-1]).length for i in range(1,len(pts))]).cumsum();length=float(dist[-1])
def pos(t):
 target=max(0,min(1,t))*length;j=min(len(pts)-2,max(0,int(np.searchsorted(dist,target))-1));v=(target-dist[j])/(dist[j+1]-dist[j]);return pts[j].lerp(pts[j+1],float(v)).normalized()*140
def pose(t):
 p=pos(t);z=p.normalized();v=pos(min(1,t+.0001))-pos(max(0,t-.0001));v=(v-z*v.dot(z)).normalized();q=Matrix((v,z.cross(v).normalized(),z)).transposed().to_quaternion();return Matrix.LocRotScale(p,q,Vector((1,1,1)))
end=pose(1);T=end@old['A02_SHIP'][532].inverted();newus=T@oldus
def smooth(t):
 t=max(0,min(1,t));return t*t*t*(10+t*(-15+6*t))
def look(p,target,up):
 z=(p-target).normalized();x=up.cross(z).normalized();y=z.cross(x).normalized();return Matrix((x,y,z)).transposed().to_quaternion()
newship=[];progress=[]
for f,m in enumerate(old['A02_SHIP']):
 p=m.translation;theta=math.atan2(p.dot(basis.col[0]),p.dot(up0));t=max(0,min(1,theta/(math.pi/2)));progress.append(t)
 newship.append(m.copy()if f<=144 else pose(t))
regional=['US_FRAME','A03_TRAILER','A03_TRACTOR','P02_SPREADER',*['P02_CABLE_'+str(i)for i in range(4)],'A04_PRIMARY','A05_SECONDARY','W01_NEW_PALLET','W01_STORED_PALLET','W02_INBOUND_JACK','W02_STORAGE_JACK','W05_PICK_CART','W09_OUT_CART','W08_LAST_LOAD','CH_LOAD_SUPPORT','CH_LOAD_ARM_0','CH_LOAD_ARM_1']
if any(s.objects[n].parent for n in regional):raise RuntimeError('Unexpected parent: do not double-transform')
root=bpy.data.objects.new('B_US_RIGID_TRANSFER',None);s.collection.objects.link(root);root.matrix_world=T;root['candidate_status']='UNADOPTED B ROUTE'
for n in regional:
 o=s.objects[n];o.parent=root;o.matrix_parent_inverse=Matrix.Identity(4)
new={n:[]for n in names};cam170=old['CAM_MASTER'][170];tar170=old['CAM_LOOK_TARGET'][170].translation;ship170=old['A02_SHIP'][170]
off=ship170.inverted()@cam170.translation;phi0=math.atan2(off.y,off.x);r0=math.hypot(off.x,off.y);taroff=ship170.inverted()@tar170
arr=old['A02_SHIP'][456].inverted()@old['CAM_MASTER'][456].translation
arrtar=old['A02_SHIP'][456].inverted()@old['CAM_LOOK_TARGET'][456].translation
residual=look(cam170.translation,tar170,ship170.to_3x3().col[2]).inverted()@cam170.to_quaternion()
for f in range(1393):
 sm=newship[f];new['A02_SHIP'].append(sm)
 new['A01_CONTAINER'].append(sm@old['A02_SHIP'][f].inverted()@old['A01_CONTAINER'][f]if f<510 else T@old['A01_CONTAINER'][f])
 if f<=170:
  cm=old['CAM_MASTER'][f];tm=old['CAM_LOOK_TARGET'][f]
 elif f>=456:cm=T@old['CAM_MASTER'][f];tm=T@old['CAM_LOOK_TARGET'][f]
 else:
  a=smooth((f-170)/145);b=smooth((f-340)/116)
  # Counter-turn the relative azimuth so the camera stays on the seaward side.
  phi=phi0+(math.radians(-120)-phi0)*a;r=r0+(38-r0)*a;h=off.z+(20-off.z)*a
  offset=Vector((r*math.cos(phi),r*math.sin(phi),h)).lerp(arr,b)
  target_offset=taroff.lerp(Vector((0,0,2)),a).lerp(arrtar,b)
  p=sm@offset;target=sm@target_offset;q=look(p,target,sm.to_3x3().col[2]);q=q@residual.slerp(type(residual)((1,0,0,0)),a)
  # Blend to the actual moving S4 world states, not a fixed relative offset.
  # The initial trial exposed a 4.315m jump at the S4 join.
  arrival=T@old['CAM_MASTER'][f];arrival_target=(T@old['CAM_LOOK_TARGET'][f]).translation
  p=p.lerp(arrival.translation,b);target=target.lerp(arrival_target,b)
  q=q.slerp(arrival.to_quaternion(),b)
  cm=Matrix.LocRotScale(p,q,Vector((1,1,1)));tm=Matrix.Translation(target)
 new['CAM_MASTER'].append(cm);new['CAM_LOOK_TARGET'].append(tm)
for n,ms in new.items():
 o=s.objects[n];o.animation_data_clear();o.rotation_mode='QUATERNION';previous=None
 for f,m in enumerate(ms):
  p,q,sc=m.decompose()
  if previous and q.dot(previous)<0:q.negate()
  previous=q.copy();o.location=p;o.rotation_quaternion=q;o.scale=sc
  for prop in ['location','rotation_quaternion','scale']:o.keyframe_insert(prop,frame=f,group='B_ROUTE_BAKE')
 for l in o.animation_data.action.layers:
  for st in l.strips:
   for bag in st.channelbags:
    for fc in bag.fcurves:
     for k in fc.keyframe_points:k.interpolation='LINEAR'
# Replace only existing non-rendering diagnostic paths; do not hide obstructions.
for n,ms in [('SHIP_ROUTE',new['A02_SHIP']),('CAMERA_PATH',new['CAM_MASTER'])]:
 o=s.objects[n]
 if o.type=='CURVE':
  o.data=o.data.copy();o.data.splines.clear();sp=o.data.splines.new('POLY');sp.points.add(len(ms)-1)
  for p,m in zip(sp.points,ms):p.co=(*m.translation,1)
  o.matrix_world=Matrix.Identity(4)
s['route_b_status']='UNADOPTED — broad offshore turn; acceptance pending metrics and playback'
s.frame_start=0;s.frame_end=1392;s.use_preview_range=False;s.frame_set(156)
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
s.render.filepath=str(R/'preview/candidate-b')
cfg={'A_direction':'negative CN_FRAME x; y positive is seaward. Layout x axis is reversed relative to CN_FRAME.','source_bow_axis':'+X, tapered hull tip at +7.3; bridge at -5.5','departure_frame':146,'dock_frame':510,'turn_length_m':turn_length,'planar_end_x':end_x,'turn_seaward_y':float(y[-1]),'spherical_route_length':length,'new_US_frame':[list(v)for v in newus],'rigid_transfer':[list(v)for v in T],'regional_roots':regional,'candidate':str(out),'camera_changed_frames':[171,1392],'ship_changed_frames':[145,1392],'shared_container_handoff':510,'time_mapping':'original ship angular progress; 12fps and all events unchanged','lens':'original data and lens animation unchanged'}
(out.with_suffix('.config.json')).write_text(json.dumps(cfg,indent=2));(out.with_suffix('.scope.json')).write_text(json.dumps({'protected':['China hierarchy geometry/transforms/actions','Earth','ship and container child geometry','all lens/sensor/shift/clip','timeline/markers','S1 camera and lift','US internal local motion'],'shared_bakes':names,'US_parent_transform':regional,'guide_geometry':['SHIP_ROUTE','CAMERA_PATH'],'new_objects':['B_US_RIGID_TRANSFER'],'candidate_status':'UNADOPTED'},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(out));print('BUILD_COMPLETE',str(out),length)
