"""User-authorized separate city rotation proposal; original voyage/US retained."""
import bpy,math,json,hashlib,sys
from pathlib import Path
from mathutils import Matrix,Vector,Quaternion
R=Path(__file__).resolve().parents[1];folder=R/'city-rotation-proposal';folder.mkdir(exist_ok=True)
args=sys.argv[sys.argv.index('--')+1:]if '--'in sys.argv else []
out=R/args[0]if args else folder/'candidate-city-rotation-v002.blend'
if out.exists():raise RuntimeError('Refuse overwrite')
if hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()!=json.loads((R/'inputs/manifest.json').read_text())['source_sha256']:raise RuntimeError('Wrong input')
s=bpy.context.scene;cn=s.objects['CN_FRAME'];s.frame_set(0);oldcn=cn.matrix_world.copy();T=oldcn@Matrix.Rotation(math.pi,4,'Z')@oldcn.inverted()
old={n:[]for n in ['A01_CONTAINER','P01_SPREADER','CAM_MASTER','CAM_LOOK_TARGET','A02_SHIP']}
for f in range(1393):
 s.frame_set(f)
 for n in old:old[n].append(s.objects[n].matrix_world.copy())
cn.matrix_world=T@oldcn;s.frame_set(0);bpy.context.view_layer.update();D=s.objects['SF_CN_LAYOUT'].matrix_world.copy();DI=D.inverted()
gantry=s.objects['CR_COMPACT_GANTRY'];shift=Vector((0,-2,0));gantry.location+=shift
geometry=json.loads((R.parent/'s2-styleframe-match-v001/review/crane-style-proposal-v019.json').read_text());A=Vector(geometry['beam_endpoints'][0]);B=Vector(geometry['beam_endpoints'][1]);u=(B-A).normalized();L=(B-A).length;v=Vector((-u.y,u.x,0));pivot=A+(B-A)*.25+v*.75+shift
load=DI@old['P01_SPREADER'][72].translation;delta=Vector((load.x-pivot.x,load.y-pivot.y,0));radius=delta.length;heading=math.atan2(delta.y,delta.x)-math.atan2(u.y,u.x);heading=(heading+math.pi)%math.tau-math.pi
def smooth(t):
 t=max(0,min(1,t));return t*t*t*(10+t*(-15+6*t))
def key(o,props,f):
 for p in props:o.keyframe_insert(p,frame=f)
affected=['CR_SLEW_JIB','CR_TROLLEY_CARRIAGE','CR_SUSPENSION_HEAD',*[o.name for o in s.objects if o.name.startswith('CR_WORKING_CABLE')]]
for n in affected:s.objects[n].animation_data_clear()
spre=s.objects['P01_SPREADER'];spre.animation_data_clear();spre.rotation_mode='QUATERNION';prev={}
for f in range(157):
 p=DI@old['P01_SPREADER'][f].translation
 # Preserve source vertical hoist profile and every contact/release time.
 a=smooth((f-100)/38);ang=heading*(1-a);rr=radius+(L*.47-radius)*a;direction=Matrix.Rotation(ang,3,'Z')@u
 p.x=pivot.x+direction.x*rr;p.y=pivot.y+direction.y*rr
 jib=s.objects['CR_SLEW_JIB'];jib.rotation_euler.z=ang;key(jib,['rotation_euler'],f)
 car=s.objects['CR_TROLLEY_CARRIAGE'];car.location=(p.x,p.y,6.85);car.rotation_euler.z=math.atan2(u.y,u.x)+ang;key(car,['location','rotation_euler'],f)
 head=s.objects['CR_SUSPENSION_HEAD'];head.location=(p.x,p.y,6.16);key(head,['location'],f)
 spre.location=D@p;spre.rotation_quaternion=old['P01_SPREADER'][f].to_quaternion();key(spre,['location','rotation_quaternion'],f)
 fold=1-smooth((f-88)/12);hx=.27+1.13*fold;hy=.17+.43*fold
 for i,c in enumerate(sorted((s.objects[n]for n in affected if n.startswith('CR_WORKING_CABLE')),key=lambda o:o.name)):
  sx=-1 if i<2 else 1;sy=-1 if i%2==0 else 1
  bottom=p+Vector((sx*hx,sy*hy,.10));top=Vector((p.x+sx*hx,p.y+sy*hy,6.14));dv=top-bottom;c.location=(top+bottom)/2;c.scale=(1,1,dv.length);q=dv.to_track_quat('Z','Y')
  if c.name in prev and q.dot(prev[c.name])<0:q.negate()
  prev[c.name]=q.copy();c.rotation_quaternion=q;key(c,['location','rotation_quaternion','scale'],f)
cam=s.camera;target=s.objects['CAM_LOOK_TARGET'];cam.animation_data_clear();target.animation_data_clear();cam.rotation_mode='QUATERNION';target.rotation_mode='QUATERNION'
cm170=T@old['CAM_MASTER'][170];tm170=T@old['CAM_LOOK_TARGET'][170];sm170=old['A02_SHIP'][170];off=sm170.inverted()@cm170.translation;toff=sm170.inverted()@tm170.translation
def look(p,t,up):
 z=(p-t).normalized();x=up.cross(z).normalized();return Matrix((x,z.cross(x),z)).transposed().to_quaternion()
res=look(cm170.translation,tm170.translation,sm170.to_3x3().col[2]).inverted()@cm170.to_quaternion();last=None
for f in range(1393):
 if f<=72:cm=old['CAM_MASTER'][f];tm=old['CAM_LOOK_TARGET'][f]
 elif f<144:
  # Both endpoint cameras are on the new seaward side. Avoid rotating the
  # close camera through the crane just because the city has rotated.
  a=smooth((f-72)/72);start=old['CAM_MASTER'][72];finish=T@old['CAM_MASTER'][144]
  st=old['CAM_LOOK_TARGET'][72].translation;ft=(T@old['CAM_LOOK_TARGET'][144]).translation
  p=start.translation.lerp(finish.translation,a);t=st.lerp(ft,a);up=oldcn.to_3x3().col[2]
  rs=look(start.translation,st,up).inverted()@start.to_quaternion();rf=look(finish.translation,ft,up).inverted()@finish.to_quaternion()
  q=look(p,t,up)@rs.slerp(rf,a);cm=Matrix.LocRotScale(p,q,Vector((1,1,1)));tm=Matrix.Translation(t)
 elif f<=170:cm=T@old['CAM_MASTER'][f];tm=T@old['CAM_LOOK_TARGET'][f]
 elif f>=340:cm=old['CAM_MASTER'][f];tm=old['CAM_LOOK_TARGET'][f]
 else:
  sm=old['A02_SHIP'][f];a=smooth((f-170)/110);b=smooth((f-230)/110);p=sm@off.lerp(Vector((-24,-34,20)),a);t=sm@toff.lerp(Vector((0,0,2)),a);q=look(p,t,sm.to_3x3().col[2])@res.slerp(Quaternion((1,0,0,0)),a)
  p=p.lerp(old['CAM_MASTER'][f].translation,b);t=t.lerp(old['CAM_LOOK_TARGET'][f].translation,b);q=q.slerp(old['CAM_MASTER'][f].to_quaternion(),b);cm=Matrix.LocRotScale(p,q,Vector((1,1,1)));tm=Matrix.Translation(t)
 q=cm.to_quaternion()
 if last and q.dot(last)<0:q.negate()
 last=q.copy();cam.location=cm.translation;cam.rotation_quaternion=q;target.location=tm.translation;target.rotation_quaternion=tm.to_quaternion();key(cam,['location','rotation_quaternion'],f);key(target,['location','rotation_quaternion'],f)
for n in affected+['P01_SPREADER','CAM_MASTER','CAM_LOOK_TARGET']:
 o=s.objects[n]
 for l in o.animation_data.action.layers:
  for st in l.strips:
   for bag in st.channelbags:
    for fc in bag.fcurves:
     for k in fc.keyframe_points:k.interpolation='LINEAR'
s['route_b_status']='UNADOPTED alternative: city rotated 180 degrees; ship route and US unchanged'
s.frame_set(156);s.use_preview_range=False;s.render.filepath=str(folder/'preview')
(out.with_suffix('.config.json')).write_text(json.dumps({'approval':'User explicitly authorized separate city rotation + port/S1 connection proposal','China_rotation_world':[list(v)for v in T],'gantry_shift_in_new_layout':list(shift),'load_radius':radius,'reference_load_radius':4.471926,'existing_voyage_and_US':'unchanged','cargo_all_frames':'unchanged','camera_changed_range':[73,339],'new_cargo_suspension_heading_degrees':math.degrees(heading),'S1_mechanism_retargeted':affected,'status':'UNADOPTED; needs collision and visual review'},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(out));print('CITY_ROTATION_SAVED',radius,heading)
