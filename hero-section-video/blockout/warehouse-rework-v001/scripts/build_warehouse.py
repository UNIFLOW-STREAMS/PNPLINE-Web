"""Build a reference-led cutaway warehouse on an immutable arrival-v010 input."""
import bpy,sys,json,math,hashlib,argparse
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];C=json.loads((R/'scene-config.json').read_text())
p=argparse.ArgumentParser();p.add_argument('--output',required=True);args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
out=Path(args.output).resolve();base=R/C['input']
assert out.is_relative_to(R) and not out.is_relative_to(R/'inputs') and not out.exists()
assert hashlib.sha256(base.read_bytes()).hexdigest()==C['input_sha256']
bpy.ops.wm.open_mainfile(filepath=str(base));S=bpy.context.scene;S.frame_set(1)
U=S.objects['US_FRAME'];UM=U.matrix_world.copy();UI=UM.inverted()
COL=bpy.data.collections.new('WH_DESIGN');S.collection.children.link(COL)
M={};new=[];changed=[];removed=[]
def mat(name,rgb,metal=0,rough=.45,emit=0):
 m=bpy.data.materials.new('WH_'+name);m.diffuse_color=(*[v/255 for v in rgb],1);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*[(v/255/12.92 if v/255<=.04045 else ((v/255+.055)/1.055)**2.4) for v in rgb],1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal
 if emit:bs.inputs['Emission Color'].default_value=m.diffuse_color;bs.inputs['Emission Strength'].default_value=emit
 M[name]=m;return m
mat('cyan',(0,171,225),.12);mat('gray',(120,120,121),.2);mat('navy',(25,47,63),.4);mat('white',(229,235,235));mat('steel',(146,161,167),.65);mat('rubber',(28,35,39));mat('cardboard',(173,139,92));mat('tape',(218,195,151));mat('paper',(238,232,212));mat('floor',(164,172,174));mat('yellow',(244,188,51));mat('light',(230,246,255),0,.3,3)
def mesh(name,verts,faces,material,parent=U,role='detail'):
 d=bpy.data.meshes.new(name);d.from_pydata(verts,[],faces);d.update();d.materials.append(M[material])
 o=bpy.data.objects.new(name,d);COL.objects.link(o);o.parent=parent;o['wh_owner']='warehouse-v001';o['wh_role']=role;new.append(o);return o
def box(name,pos,dim,material,parent=U,bevel=0,role='detail'):
 x,y,z=[v/2 for v in dim];v=[(-x,-y,-z),(-x,-y,z),(-x,y,-z),(-x,y,z),(x,-y,-z),(x,-y,z),(x,y,-z),(x,y,z)]
 o=mesh(name,v,[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)],material,parent,role);o.location=pos
 if bevel:
  mod=o.modifiers.new('Soft manufactured edges','BEVEL');mod.width=bevel;mod.segments=2
  o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return o
def beam(name,a,b,width,material,role='detail'):
 a=Vector(a);b=Vector(b);o=box(name,(a+b)/2,(width,width,(b-a).length),material,role=role);o.rotation_mode='QUATERNION';o.rotation_quaternion=(b-a).to_track_quat('Z','Y');return o
def label(name,text,pos,size,material='white',rot=(math.pi/2,0,0)):
 d=bpy.data.curves.new(name,'FONT');d.body=text;d.size=size;d.extrude=.009;d.align_x='CENTER';d.align_y='CENTER'
 o=bpy.data.objects.new(name,d);COL.objects.link(o);o.parent=U;o.location=pos;o.rotation_euler=rot;d.materials.append(M[material]);o['wh_owner']='warehouse-v001';o['wh_role']='label';new.append(o)
 return o
def recolor(o,key):
 if hasattr(o.data,'materials'):
  o.data=o.data.copy();o.data.materials.clear();o.data.materials.append(M[key]);changed.append(o.name)
def remove(o):removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
def ease(f,a,b):
 t=max(0,min(1,(f-a)/(b-a)));return t*t*(3-2*t)
def empty(name,parent=U,role='equipment'):
 o=bpy.data.objects.new(name,None);COL.objects.link(o);o.parent=parent;o['wh_owner']='warehouse-v001';o['wh_role']=role;new.append(o);return o

# Replace only the existing warehouse proxy and storage stock; all trucks stay intact.
for o in list(S.objects):
 if o.name.startswith(('WAREHOUSE_BACK_WALL','WAREHOUSE_PARTIAL_ROOF','WAREHOUSE_COLUMN_','RACK_')) or o.name.endswith('_ZONE') or o.name in [k+'_REVIEW_LABEL' for k in ['INBOUND_WAIT','STORAGE','PICKING','PACKING','OUTBOUND_WAIT']]:remove(o)
recolor(S.objects['WAREHOUSE_FLOOR'],'floor')

# Real end loading openings align with the existing trailer and delivery-van backs.
box('WH_FACADE_HEADER',(52,25.15,10.35),(32.6,.65,2.3),'navy',bevel=.055,role='structure')
for x in [36,68]:
 if x==36:
  box('WH_INBOUND_REAR_PIER',(36,31.55,5.6),(.7,.7,7.48),'navy',bevel=.04,role='structure')
  beam('WH_INBOUND_OVERHEAD_BRACE',(36,31.5,7.7),(36,25.15,9.5),.22,'navy','structure')
 else:
  box('WH_FRONT_PIER_'+str(x),(x,25.35,5.6),(.7,.9,7.48),'navy',bevel=.04,role='structure')
  box('WH_SIDE_FRONT_'+str(x),(x,26.05,5.65),(.35,1.25,7.58),'navy',role='structure')
 box('WH_SIDE_REAR_'+str(x),(x,35.25,6.55),(.35,7.5,9.38),'navy',role='structure')
 box('WH_END_HEADER_'+str(x),(x,29.05,8.55),(.5,4.7,5.9),'navy',role='structure')
 for y in [26.9,31.1]:
  box('WH_DOCK_JAMB_'+str(x)+'_'+str(y),(x,y,3.73),(.55,.24,3.74),'white',role='structure')
  box('WH_DOCK_BUMPER_'+str(x)+'_'+str(y),(x+(-.3 if x==36 else .3),y,2.6),(.12,.26,1.1),'rubber',bevel=.04,role='structure')
 box('WH_DOCK_LINTEL_'+str(x),(x,29,5.65),(.6,4.4,.3),'cyan',role='structure')
 for z in [5.98,6.2,6.42]:box('WH_SHUTTER_'+str(x)+'_'+str(z),(x,29,z),(.45,4,.12),'steel',role='structure')
 for y in [26.65,31.4]:
  guardx=37.1 if x==36 and y==26.65 else x+(-.6 if x==36 else .6)
  box('WH_DOCK_GUARD_'+str(x)+'_'+str(y),(guardx,y,2.5),(.18,.18,1.2),'yellow',bevel=.05,role='structure')
box('WH_REAR_WALL',(52,39,6.57),(32.3,.35,9.42),'navy',role='structure')
for x in range(37,68):
 box('WH_REAR_PANEL_'+str(x),(x,38.8,6.55),(.025,.035,9.25),'steel')
 box('WH_FASCIA_SEAM_'+str(x),(x,24.813,10.35),(.018,.012,2.15),'gray')
box('WH_PARTIAL_ROOF',(52,37.9,11.5),(32.6,2.8,.22),'white',role='structure')
box('WH_ROOF_EDGE',(52,39.2,11.73),(32.6,.22,.35),'navy',role='structure')
for x in [36.4,40,44,48,52,56,60,64,67.6]:
 box('WH_ROOF_RIB_'+str(x),(x,37.9,11.64),(.1,2.8,.08),'steel')
 beam('WH_TRUSS_'+str(x),(x,25.5,9.2),(x,38.7,9.2),.14,'steel','structure')
 for y in [31.5,35.8]:box('WH_LED_'+str(x)+'_'+str(y),(x,y,9.04),(.12,2.0,.07),'light')
# Exterior logo uses the actual supplied two-color silhouettes, not a typed approximation.
box('WH_LOGO_BACKPLATE',(52,24.79,10.35),(19.4,.06,1.95),'white',bevel=.05)
img=bpy.data.images.load(str(R/'inputs/PNP-LINE.webp'),check_existing=False);img.pack()
pixels=list(img.pixels[:]);w,h=img.size
for key,color in [('cyan',(0,171,225)),('gray',(120,120,121))]:
 verts=[];faces=[];step=4
 for yy in range(0,h,step):
  starts=[];start=None
  for xx in range(0,w+step,step):
   hit=False
   if xx<w:
    idx=(min(h-1,yy+step//2)*w+min(w-1,xx+step//2))*4;r,g,b,alpha=pixels[idx:idx+4]
    hit=alpha>.5 and ((b>r*1.3) if key=='cyan' else (abs(r-g)<.03 and r>.1))
   if hit and start is None:start=xx
   if not hit and start is not None:
    x0=52+(start/w-.5)*19;x1=52+(min(xx,w)/w-.5)*19;z0=10.35+(yy/h-.5)*19*h/w;z1=z0+step/w*19
    k=len(verts);verts.extend([(x0,24.745,z0),(x1,24.745,z0),(x1,24.745,z1),(x0,24.745,z1)]);faces.append((k,k+1,k+2,k+3));start=None
 mesh('WH_LOGO_'+key.upper(),verts,faces,key,role='brand')

# Four-tier pallet racks with structural cross braces, kick guards and varied cartons.
for y,xs in [(32.5,C['rack_x_front']),(36.5,C['rack_x_back'])]:
 for x in xs:
  bay=f'{x}_{y}'
  for dx in [-1.6,1.6]:
   for dy in [-.85,.85]:
    box('WH_RACK_POST_'+bay+f'_{dx}_{dy}',(x+dx,y+dy,5.36),(.13,.13,7.0),'navy',role='rack')
    box('WH_RACK_GUARD_'+bay+f'_{dx}_{dy}',(x+dx,y+dy,2.16),(.23,.23,.6),'yellow',role='rack')
   for z in [2.4,4.2,6,7.8]:
    beam('WH_RACK_X_'+bay+f'_{dx}_{z}',(x+dx,y-.78,z),(x+dx,y+.78,z+1.0),.055,'steel','rack')
    beam('WH_RACK_XR_'+bay+f'_{dx}_{z}',(x+dx,y+.78,z),(x+dx,y-.78,z+1.0),.055,'steel','rack')
  for tier,z in enumerate(C['rack_tiers']):
   box('WH_RACK_DECK_'+bay+'_'+str(tier),(x,y,z),(3.2,1.7,.14),'steel',role='rack')
   for dy in [-.88,.88]:box('WH_RACK_BEAM_'+bay+f'_{tier}_{dy}',(x,y+dy,z),(3.35,.12,.21),'cyan',role='rack')
   label('WH_BIN_LABEL_'+bay+'_'+str(tier),f'{int(x)-40:02d}-{tier+1}',(x,y-.955,z+.01),.13)
   if x==44 and y==32.5 and tier==0:continue
   for col,dx in enumerate([-1.06,0,1.06]):
    height=1.12+(.1 if (tier+col)%2 else 0)
    basez=z+.07
    for dy in [-.47,0,.47]:box('WH_STOCK_PALLET_'+bay+f'_{tier}_{col}_{dy}',(x+dx,y+dy,basez+.045),(.95,.16,.09),'tape',role='stock')
    center=basez+.09+height/2
    box('WH_STOCK_'+bay+f'_{tier}_{col}',(x+dx,y,center),(.91,1.28,height),'cardboard',bevel=.025,role='stock')
    box('WH_STOCK_TAPE_'+bay+f'_{tier}_{col}',(x+dx,y-.648,center),(.09,.012,height*.97),'tape')
    box('WH_STOCK_LABEL_'+bay+f'_{tier}_{col}',(x+dx+.22,y-.657,center+.18),(.24,.012,.18),'paper')

# A closed, continuous racetrack conveyor separates processing aisle and front cutaway.
cv=C['conveyor'];L=cv['left'];H=cv['right'];cy=cv['cy'];radius=cv['radius'];straight=H-L;length=2*straight+2*math.pi*radius
def path(s):
 s=s%length
 if s<straight:return Vector((L+s,cy-radius,0)),0
 s-=straight
 if s<math.pi*radius:
  a=-math.pi/2+s/radius;return Vector((H+radius*math.cos(a),cy+radius*math.sin(a),0)),a+math.pi/2
 s-=math.pi*radius
 if s<straight:return Vector((H-s,cy+radius,0)),math.pi
 s-=straight;a=math.pi/2+s/radius;return Vector((L+radius*math.cos(a),cy+radius*math.sin(a),0)),a+math.pi/2
def ribbon(name,width,z,thick,material):
 verts=[];N=256
 for i in range(N):
  pt,a=path(length*i/N);normal=Vector((-math.sin(a),math.cos(a),0))
  for side,dz in [(-1,-thick),(-1,0),(1,-thick),(1,0)]:verts.append(tuple(pt+normal*width/2*side+Vector((0,0,z+dz))))
 faces=[]
 for i in range(N):
  a=i*4;b=((i+1)%N)*4;faces.extend([(a+1,b+1,b+3,a+3),(a,b,b+1,a+1),(a+2,a+3,b+3,b+2),(a,a+2,b+2,b)])
 return mesh(name,verts,faces,material,role='conveyor')
ribbon('WH_CONVEYOR_CHASSIS',1.12,2.55,.2,'navy');ribbon('WH_CONVEYOR_BELT',.9,2.65,.1,'cyan')
for x in range(43,63,3):
 for y in [26,28]:
  for dy in [-.35,.35]:box('WH_BELT_LEG_'+f'{x}_{y}_{dy}',(x,y+dy,2.17),(.13,.13,.62),'steel',role='conveyor')
  box('WH_BELT_FOOT_'+f'{x}_{y}',(x,y,1.9),(.38,1.02,.08),'navy',role='conveyor')
for x in range(44,62,3):
 for y in [26,28]:
  for dx in [-.11,.11]:box('WH_BELT_MARK_'+f'{x}_{y}_{dx}',(x+dx,y,2.656),(.028,.55,.01),'white')
for x in [44,61.5]:
 box('WH_SCAN_POST_'+str(x),(x,28.65,3.05),(.12,.12,2.38),'navy',role='equipment')
 box('WH_SCAN_HEAD_'+str(x),(x,28,4.18),(.4,1.4,.18),'gray',bevel=.025)
 box('WH_SCAN_WINDOW_'+str(x),(x,27.98,4.08),(.25,.8,.018),'cyan')

# Keep all original batch identities, but fit the actual stock/equipment to the new aisle.
for name in ['W06_PACK_TABLE','W07_OPEN_PACK','W08_SEALED_READY','CH_PACKER']+[o.name for o in S.objects if o.name.startswith('TABLE_LEG_')]:
 o=S.objects[name];o.location.y+=1.5;changed.append(name)
recolor(S.objects['W06_PACK_TABLE'],'white')
for name in ['W04_PICK_BIN_PRODUCT','W04_PICK_BIN_SUPPORT']+[o.name for o in S.objects if o.name.startswith('W04_BIN_STAND_')]:
 o=S.objects[name];o.location.x+=2;changed.append(name)
S.objects['CH_PICKER'].location=(52,31.05,1.86);changed.append('CH_PICKER')
for o in S.objects:
 if o.name.startswith('CH_') and ('TORSO' in o.name or 'LOAD_ARM' in o.name):recolor(o,'cyan')
for x in [56,58]:
 box('WH_PACK_DRAWER_'+str(x),(x,31.55,2.45),(.75,1.15,.65),'gray',bevel=.035)
box('WH_PACK_MONITOR_BASE',(57.5,32.1,3.15),(.6,.3,.12),'gray')
box('WH_PACK_MONITOR',(57.5,32.2,3.6),(.75,.1,.6),'navy',bevel=.04)
box('WH_PACK_SCREEN',(57.5,32.14,3.6),(.65,.015,.48),'cyan')
box('WH_PACK_TAPE_MACHINE',(56,32,3.25),(.45,.45,.45),'gray',bevel=.08)
for o in list(S.objects):
 if o.name in ['W01_NEW_PALLET_BASE','W01_STORED_PALLET_BASE','W02_INBOUND_JACK_FORKS','W02_STORAGE_JACK_FORKS']:remove(o)
for name in ['W01_NEW_PALLET','W01_STORED_PALLET']:
 root=S.objects[name]
 box('WH_'+name+'_DECK',(0,0,.06),(1.1,.95,.12),'tape',root,role='pallet')
 for x in [-.42,.42]:
  inbound=name=='W01_NEW_PALLET';cross=.4 if x>0 else -.4
  box('WH_'+name+'_RUNNER_'+str(x),(0,cross,-.15) if inbound else (x,0,-.15),(1.1,.15,.1) if inbound else (.15,.95,.1),'cardboard',root,role='pallet')
  for y in [-.38,.38]:box('WH_'+name+'_BLOCK_'+f'{x}_{y}',(y,cross,-.04) if inbound else (x,y,-.04),(.15,.15,.12),'cardboard',root,role='pallet')
 for child in root.children:
  if child.name.startswith(name+'_BOX'):
   child.location.z+=.055;recolor(child,'cardboard');changed.append(child.name)
forks={}
for name in ['W02_INBOUND_JACK','W02_STORAGE_JACK']:
 root=S.objects[name];forks[name]=[]
 for y in [-.22,.22]:forks[name].append(box('WH_'+name+'_FORK_'+str(y),(0,y,.1),(1.3,.13,.1),'cyan',root,role='fork'))
 for x in [-.25,.25]:
  for y in [-.22,.22]:box('WH_'+name+'_WHEEL_'+f'{x}_{y}',(x,y,.015),(.17,.17,.13),'rubber',root,bevel=.06,role='equipment')
 recolor(S.objects[name+'_HANDLE'],'gray')
 if name=='W02_STORAGE_JACK':S.objects[name+'_HANDLE'].location.x=1.15;changed.append(name+'_HANDLE')
for name,text,x in [('INBOUND','01  INBOUND',37.9),('OUTBOUND','04  DISPATCH',65.9)]:
 box('WH_'+name+'_SIGNBOARD',(x,24.88,8.65),(3.35,.12,.65),'navy')
 for dx in [-1.2,1.2]:beam('WH_'+name+'_SIGN_HANGER_'+str(dx),(x+dx,24.88,8.95),(x+dx,24.88,9.3),.06,'steel')
 label('WH_'+name+'_SIGN',text,(x,24.8,8.65),.33,'white')
for text,x in [('STORAGE',46),('PICK / PACK',55.7),('OUTBOUND',64.3)]:
 box('WH_AISLE_SIGN_'+text,(x,35.0,8.75),(3.5,.09,.55),'navy')
 label('WH_AISLE_LABEL_'+text,text,(x,34.94,8.75),.22)
for x in [38.4,65.6]:
 lane=box('WH_FLOOR_LANE_'+str(x),(x,30.15,1.872),(.055,7.1,.02),'cyan')
 lane['asset_id']='W-10'

moving=['W01_NEW_PALLET','W01_STORED_PALLET','W02_INBOUND_JACK','W02_STORAGE_JACK','W05_PICK_CART','W09_OUT_CART','W08_LAST_LOAD','CH_LOADER','CH_LOAD_SUPPORT','CH_LOAD_ARM_0','CH_LOAD_ARM_1']
# Capture evaluated original poses before replacing any action.
poses={n:[] for n in moving}
for f in range(1,1393):
 S.frame_set(f)
 for n in moving:poses[n].append(UI@S.objects[n].matrix_world.copy())
for n in moving:
 o=S.objects[n];o.animation_data.action=o.animation_data.action.copy();o.animation_data.action.name='WH_'+n+'_ACTION';changed.append(n)
for f in range(1,1393):
 S.frame_set(f);transfer=ease(f,1150,1166);retreat=ease(f,1168,1195)
 for n in moving:
  o=S.objects[n];m=poses[n][f-1].copy();pt=m.translation.copy()
  if n=='W01_NEW_PALLET' and f>=909:pt.z=2.06
  elif n=='W01_STORED_PALLET':pt=Vector((44,30+2.5*ease(f,994,1018),2.06+.36*ease(f,985,994)-.05*ease(f,1018,1025)))
  elif n=='W02_INBOUND_JACK':
   if f>=909:pt.z=1.91
  elif n=='W02_STORAGE_JACK':
   pt=Vector((44,30+2.5*ease(f,994,1018)-2*ease(f,1027,1043),1.91))
   o.rotation_mode='XYZ';o.rotation_euler=(UM.to_3x3()@Matrix.Rotation(-math.pi/2,3,'Z')).to_euler();o.keyframe_insert('rotation_euler',frame=f)
  elif n=='W05_PICK_CART':pt.x=52+3.3*ease(f,1030,1074);pt.y=30
  elif n=='W09_OUT_CART':pt.y=30+2*ease(f,1167,1193)
  elif n=='W08_LAST_LOAD' and f<=1200:pt.y+=2*(1-transfer)
  elif n=='CH_LOADER':pt.y+=2*(1-transfer)*(1-retreat)+2*retreat
  elif n=='CH_LOAD_SUPPORT':
   # Same cargo/hand timing, translated toward the new two-way aisle.
   grasp=ease(f,1145,1150)*(1-ease(f,1167,1192));off=2*(1-transfer)
   walkoff=2*(1-transfer)*(1-retreat)+2*retreat;pt.y+=walkoff*(1-grasp)+off*grasp
  if n not in ['CH_LOAD_ARM_0','CH_LOAD_ARM_1']:
   o.location=pt if o.parent==U else UM@pt;o.keyframe_insert('location',frame=f)
 # Rebuild loader arm endpoints from actual new supported hands.
 walk=UI@S.objects['CH_LOADER'].matrix_world.translation;support=UI@S.objects['CH_LOAD_SUPPORT'].matrix_world.translation
 # Update dependency graph before reading animated local positions at this frame.
 bpy.context.view_layer.update();walk=UI@S.objects['CH_LOADER'].matrix_world.translation;support=UI@S.objects['CH_LOAD_SUPPORT'].matrix_world.translation
 for i,side in enumerate([-1,1]):
  start=walk+Vector((side*.2,0,1));end=support+Vector((side*.2,0,0));o=S.objects['CH_LOAD_ARM_'+str(i)]
  rot=(UM.to_3x3()@(end-start)).to_track_quat('Z','Y');o.location=UM@((start+end)/2);o.rotation_mode='QUATERNION';o.rotation_quaternion=rot;o.scale.z=(end-start).length
  for prop in ['location','rotation_quaternion','scale']:o.keyframe_insert(prop,frame=f)
 lift=(.36*ease(f,985,994)-.05*ease(f,1018,1025))*(1-ease(f,1043,1054))
 for fork in forks['W02_STORAGE_JACK']:fork.location.z=.1+lift;fork.keyframe_insert('location',frame=f)

for i in range(14):
 root=empty('WH_FLOW_PARCEL_'+str(i),role='flow_parcel');height=.48+(i%3)*.06
 box('WH_FLOW_BODY_'+str(i),(0,0,height/2),(.58,.5,height),'cardboard',root,bevel=.025,role='parcel_body')
 box('WH_FLOW_TAPE_'+str(i),(0,0,height+.007),(.09,.5,.015),'tape',root)
 box('WH_FLOW_LABEL_'+str(i),(.18,0,height+.012),(.16,.24,.012),'paper',root)
 previous=None
 for f in list(range(1,1393,2))+[1392]:
  t=max(0,f-900);travel=(t*t/48 if t<24 else t-12)*length/cv['period_frames'];pt,a=path(i*length/14+travel)
  if previous is not None:
   while a-previous>math.pi:a-=2*math.pi
   while a-previous<-math.pi:a+=2*math.pi
  previous=a;root.location=(pt.x,pt.y,cv['top']);root.rotation_euler.z=a
  root.keyframe_insert('location',frame=f);root.keyframe_insert('rotation_euler',frame=f)
for x in [42,50,58,65]:
 d=bpy.data.lights.new('WH_INTERIOR_'+str(x),'AREA');d.energy=130;d.shape='DISK';d.size=5
 o=bpy.data.objects.new(d.name,d);COL.objects.link(o);o.parent=U;o.location=(x,33,9);o['wh_owner']='warehouse-v001';o['wh_role']='lighting';new.append(o)
for o in new+[S.objects[n] for n in moving]:
 if o.animation_data and o.animation_data.action:
  for layer in o.animation_data.action.layers:
   for strip in layer.strips:
    for bag in strip.channelbags:
     for fc in bag.fcurves:
      for key in fc.keyframe_points:key.interpolation='LINEAR'
S['warehouse_revision']='warehouse-v001';S.frame_set(1075)
bpy.ops.wm.save_as_mainfile(filepath=str(out))
manifest={'input_sha256':C['input_sha256'],'candidate_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'new':[o.name for o in new],'changed':sorted(set(changed)),'removed':removed,'camera_changed':False,'truck_actions_changed':False,'brand_source':'inputs/PNP-LINE.webp','version':out.stem}
(R/'review'/f'{out.stem}-build.json').write_text(json.dumps(manifest,indent=2))
print('WAREHOUSE_BUILD',out,len(new),'new',len(set(changed)),'changed',len(removed),'replaced')
