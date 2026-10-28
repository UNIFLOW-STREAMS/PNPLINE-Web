"""Approved S1 retarget: landing at f72 and voyage after f72 remain exact.
Portal-mounted slewing jib; trolley and telescoping spreader return to the
reference parked pose by f156. Original source objects/actions are preserved
except explicitly authorized container/camera translation and spreader motion.
"""
import bpy,math,ast,json,sys
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;out=Path(sys.argv[sys.argv.index('--')+1]);assert not out.exists();version=out.stem.rsplit('-',1)[-1]
s.frame_set(156);D=s.objects['SF_CN_LAYOUT'];DM=D.matrix_world.copy();DI=DM.inverted()
col=bpy.data.collections.new('CRANE_ANIMATED_MECHANISM');s.collection.children.link(col)
def tag(o):o['crane_motion_owner']='approved-s1-v020';return o
t=ast.parse((R/'scripts/build_layout_proposal.py').read_text());exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef)and n.name in {'empty','mesh','box','tube','lathe','sphere'}],type_ignores=[]),'helpers','exec'))
M={k:bpy.data.materials['SF_'+k]for k in ['blue','white','navy','silver','gold','roof']}
cfg=json.loads((R/'review/crane-style-proposal-v019.json').read_text());A=Vector(cfg['beam_endpoints'][0]);B=Vector(cfg['beam_endpoints'][1]);axis=B-A;L=axis.length;u=axis.normalized();v=Vector((-u.y,u.x,0));pivot=A+axis*.25+v*.75
root=s.objects['CR_COMPACT_GANTRY'];jib=empty('CR_SLEW_JIB',root,pivot);jib.rotation_mode='XYZ'
upper_prefix=('CR_HORIZONTAL_BOOM','CR_TROLLEY_RAIL','CR_CROSS_MEMBER','CR_PYLON','CR_STAY','CR_BOOM_WEB','CR_MACHINERY','CR_CAB')
for o in list(root.children):
 if o.name.startswith(upper_prefix):
  local=o.matrix_local.copy();o.parent=jib;o.matrix_local=Matrix.Translation(-pivot)@local
 # Lower the fixed portal slightly to make a physical slew bearing seat.
 if o.name.startswith('CR_LEG_'):
  for vert in o.data.vertices:
   if vert.co.z>6.49:vert.co.z=6.12
  o.data.update()
for o in list(s.objects):
 if o.name.startswith('CR_REVIEW_'):o.hide_render=True;o.hide_set(True)
root['status']='S1 retarget integrated; f72 landing preserved';s['crane_v018_status']='superseded by animated integrated revision'
lathe('CR_FIXED_SLEW_SEAT',(pivot.x,pivot.y,6.09),[(0,.86),(.10,.86),(.18,.76)],M['white'],root,48)
lathe('CR_ROTATING_BEARING',(0,0,-.23),[(0,.75),(.09,.75),(.11,.67)],M['blue'],jib,48)
for tt in [.08,.42]:
 p=A+axis*tt+v*.75;p.z=6.06;beam=box('CR_FIXED_PORTAL_CAP',p,(.36,1.9,.16),M['white'],root); # rotate in-place around center
 # mesh box uses absolute vertices; orient each point about the cap centre.
 for vv in beam.data.vertices:
  q=vv.co-p;vv.co=p+u*q.x+v*q.y+Vector((0,0,q.z))
 beam.data.update()
cam=s.camera;target=s.objects['CAM_LOOK_TARGET'];cargo=s.objects['A01_CONTAINER'];spre=s.objects['P01_SPREADER'];original={}
for f in range(0,s.frame_end+1):
 s.frame_set(f);original[f]={n:s.objects[n].location.copy()for n in ['A01_CONTAINER','P01_SPREADER','CAM_MASTER','CAM_LOOK_TARGET']}
loadxy=DI@original[72]['A01_CONTAINER'];loadxy.z=0;pivotxy=Vector((pivot.x,pivot.y,0));loadrad=(loadxy-pivotxy).length
heading0=math.atan2(loadxy.y-pivot.y,loadxy.x-pivot.x)-math.atan2(u.y,u.x)
heading0=(heading0+math.pi)%math.tau-math.pi
def ease(x):
 x=min(1,max(0,x));return x*x*x*(10+x*(-15+6*x))
def pose(f):
 if f<=72:
  old=DI@original[f]['A01_CONTAINER'];z=3.100008010864258+(old.z-3.100008010864258)*(1.85/3.65)+.89
 elif f<=78:z=3.990008010864258
 elif f<=100:z=3.990008010864258+(5.5-3.990008010864258)*ease((f-78)/22)
 elif f<=138:z=5.5
 else:z=5.5+(3.0-5.5)*ease((f-138)/18)
 a=ease((f-100)/38);heading=heading0*(1-a);r=loadrad+(L*.47-loadrad)*a
 direction=Matrix.Rotation(heading,3,'Z')@u;p=pivotxy+direction*r;p.z=z
 fold=1-ease((f-88)/12);return p,heading,r,fold
def change_existing(o,path,values):
 curves=[fc for l in o.animation_data.action.layers for st in l.strips for bag in st.channelbags for fc in bag.fcurves if fc.data_path==path]
 assert len(curves)==3,(o.name,path)
 seen={}
 for fc in curves:
  existing={round(k.co.x)for k in fc.keyframe_points if abs(k.co.x-round(k.co.x))<1e-5}
  for k in fc.keyframe_points:
   f=round(k.co.x)
   if abs(k.co.x-f)>1e-5 or f not in values:continue
   val=values[f][fc.array_index];delta=val-k.co.y;k.co.y=val;k.handle_left.y+=delta;k.handle_right.y+=delta;seen[f]=1
  for f in values.keys()-existing:
   k=fc.keyframe_points.insert(f,values[f][fc.array_index],options={'FAST'});k.interpolation='LINEAR';seen[f]=1
  fc.update()
 assert len(seen)==len(values),(o.name,len(seen),len(values))
cv={};mv={};tv={};sp={};max_delta=0
for f in range(s.frame_end+1):
 p,heading,r,fold=pose(f);sp[f]=DM@p
 if f<72:
  old=DI@original[f]['A01_CONTAINER'];new=old.copy();new.z=p.z-.89;delta=DM.to_3x3()@Vector((0,0,new.z-old.z));max_delta=max(max_delta,abs(new.z-old.z))
  cv[f]=original[f]['A01_CONTAINER']+delta;mv[f]=original[f]['CAM_MASTER']+delta;tv[f]=original[f]['CAM_LOOK_TARGET']+delta
change_existing(cargo,'location',cv);change_existing(cam,'location',mv);change_existing(target,'location',tv);change_existing(spre,'location',sp)
# New visual lifting frame: full width while locked, telescopes after release.
hoist=empty('CR_LIFT_VISUAL',spre);core=box('CR_LIFT_CORE',(0,0,0),(.52,.45,.20),M['gold'],hoist)
arms=[];locks=[]
for sign in [-1,1]:
 arm=box('CR_TELESCOPIC_ARM',(0,0,0),(1,1,1),M['gold'],hoist);arms.append((sign,arm))
 for sy in [-1,1]:
  lock=box('CR_TWISTLOCK',(0,0,0),(.14,.14,.16),M['gold'],hoist);locks.append((sign,sy,lock))
endbars=[]
for sign in [-1,1]:endbars.append((sign,box('CR_SPREAD_END',(0,0,0),(1,1,1),M['gold'],hoist)))
car=empty('CR_TROLLEY_CARRIAGE',D);car.rotation_mode='XYZ'
box('CR_CARRIAGE_BODY',(0,0,0),(.70,1.66,.18),M['blue'],car)
for sx in [-1,1]:
  for sy in [-1,1]:sphere('CR_RAIL_WHEEL',(sx*.24,sy*.76,-.03),.10,M['roof'],car)
# Anti-twist suspension crosshead can rotate beneath the rail carriage.
head=empty('CR_SUSPENSION_HEAD',D);box('CR_WINCH_HOUSING',(0,0,0),(.62,.52,.18),M['blue'],head)
box('CR_TROLLEY_SUSPENSION_PIN',(0,0,.28),(.12,.12,.60),M['silver'],head)
toparms=[]
for sx in [-1,1]:toparms.append((sx,box('CR_TOP_SPREAD_ARM',(0,0,0),(1,1,1),M['blue'],head)))
topbars=[(sx,box('CR_TOP_END_BAR',(0,0,0),(1,1,1),M['blue'],head))for sx in [-1,1]]
cables=[]
for sx in [-1,1]:
 for sy in [-1,1]:
  cable=lathe('CR_WORKING_CABLE',(0,0,0),[(-.5,.018),(.5,.018)],M['roof'],D,8);cable.rotation_mode='QUATERNION';cables.append((sx,sy,cable))
def key(o,paths,f):
 for path in paths:o.keyframe_insert(data_path=path,frame=f)
prevq={}
trajectory=[]
for f in range(157):
 p,heading,r,fold=pose(f);jib.rotation_euler.z=heading;key(jib,['rotation_euler'],f)
 top=p.copy();top.z=6.16;car.location=Vector((p.x,p.y,6.85));car.rotation_euler.z=math.atan2(u.y,u.x)+heading;key(car,['location','rotation_euler'],f)
 head.location=top;key(head,['location'],f)
 hx=.27+1.13*fold;hy=.17+.43*fold
 for sign,arm in arms:arm.location=(sign*hx/2,0,0);arm.scale=(hx,.18,.13);key(arm,['location','scale'],f)
 for sign,sy,lock in locks:lock.location=(sign*hx,sy*hy,-.105);key(lock,['location'],f)
 for sign,bar in endbars:bar.location=(sign*hx,0,0);bar.scale=(.16,hy*2+.12,.16);key(bar,['location','scale'],f)
 for sign,arm in toparms:arm.location=(sign*hx/2,0,-.02);arm.scale=(hx,.16,.13);key(arm,['location','scale'],f)
 for sign,bar in topbars:bar.location=(sign*hx,0,-.02);bar.scale=(.16,hy*2+.12,.13);key(bar,['location','scale'],f)
 # Spreader local axes are rotated 180 degrees in the China layout frame.
 for sx,sy,c in cables:
  bottom=p+Vector((-sx*hx,-sy*hy,.10));upper=top+Vector((-sx*hx,-sy*hy,-.02));delta=upper-bottom
  assert delta.z>.04,(f,delta.z)
  c.location=(upper+bottom)/2;c.scale=(1,1,delta.length);q=delta.to_track_quat('Z','Y')
  if c.name in prevq and q.dot(prevq[c.name])<0:q.negate()
  c.rotation_quaternion=q;prevq[c.name]=q;key(c,['location','rotation_quaternion','scale'],f)
 trajectory.append({'frame':f,'spreader':list(p),'slew':heading,'radius':r,'fold':fold,'rope_length':6.14-(p.z+.10)})
# Linear interpolation of dense samples avoids Bezier overshoot around contact.
for o in col.objects:
 if o.animation_data and o.animation_data.action:
  for l in o.animation_data.action.layers:
   for st in l.strips:
    for bag in st.channelbags:
     for fc in bag.fcurves:
      for k in fc.keyframe_points:k.interpolation='LINEAR'
s.frame_set(156);bpy.context.view_layer.update()
for screen in bpy.data.screens:
 for ar in screen.areas:
  if ar.type=='VIEW_3D':ar.spaces.active.shading.type='SOLID';ar.spaces.active.shading.color_type='MATERIAL';ar.spaces.active.region_3d.view_perspective='CAMERA'
s['crane_integration_status']='approved S1 motion connected; original landing f72 preserved'
record={'source':bpy.data.filepath,'output':str(out),'approved':'S1 lift path/height/cables and close camera connection','landing_frame':72,'cargo_changed_frames':[0,71],'camera_changed_frames':[0,71],'max_initial_height_reduction':max_delta,'pivot':list(pivot),'load_radius':loadrad,'initial_slew_degrees':math.degrees(heading0),'parked_frame':156,'trajectory':trajectory,'changed_original_actions':[o.animation_data.action.name for o in [cargo,cam,target,spre]],'new_objects':[o.name for o in col.objects]}
(R/f'review/crane-integration-{version}.json').write_text(json.dumps(record,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out));print('INTEGRATED',str(out),len(col.objects),max_delta)
