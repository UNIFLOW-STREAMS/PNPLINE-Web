"""Fixed-world PNPLINE text-based blockout. Fresh background process only.

Source of truth is this deterministic generator until a manual edit is recorded.
All motion is baked as editable frame keys; reopening needs no Python handlers.
"""
import bpy, math, json, sys, bisect
from pathlib import Path
from mathutils import Vector, Matrix, Quaternion

ROOT=Path(__file__).resolve().parents[1]
R=140.0
END=1392
FPS=12
US=math.radians(25)
CN=math.radians(-65)
V=Vector
def clamp(t): return max(0.0,min(1.0,t))
def smooth(t):
    t=clamp(t); return t*t*(3-2*t)
def ramp(f,a,b): return smooth((f-a)/(b-a))
def mix(a,b,t): return a+(b-a)*t
def rot(a): return Matrix.Rotation(a,4,'Z')
def region(theta): return Matrix.Rotation(theta,4,'Y') @ Matrix.Translation((0,0,R))
UM=region(US); CM=region(CN)
def world(p): return UM @ V(p)
def pose(p,yaw=0): return UM @ Matrix.Translation(p) @ rot(yaw)

if bpy.data.filepath and Path(bpy.data.filepath).name != 'master-v001.blend':
    raise RuntimeError('Run in a fresh --factory-startup process; refuse user scene overwrite')
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for data in list(bpy.data.collections): bpy.data.collections.remove(data)
S=bpy.context.scene
S.name='PNPLINE_MASTER_v001'
S['master_version']='v001'
S['scope']='7구간 연출안 검증용 / 기존 #61 승인안 대체 아님'
S['source_basis']='Text-based candidate; storyboard version/selection absent, no visual board comparison'
S['radius']=R
S['events']=json.dumps({'container_ship':72,'ship_depart':145,'ship_dock':510,'container_us_lift':532,'container_truck':632,'inbound_depart':649,'doors_open':[811,842],'reverse':[849,890],'unload':[908,966],'outbound_primary':1201,'outbound_secondary':1261})
S.frame_start=1; S.frame_end=END; S.render.fps=FPS
S.unit_settings.system='METRIC'; S.unit_settings.scale_length=1
S.render.engine='BLENDER_WORKBENCH'
S.render.resolution_x=768; S.render.resolution_y=432; S.render.resolution_percentage=100
S.render.image_settings.file_format='PNG'
S.render.film_transparent=False
S.display.shading.light='STUDIO'; S.display.shading.studiolight_rotate_z=0.25
S.display.shading.color_type='MATERIAL'
S.display.shading.show_shadows=True
S.display.shading.show_cavity=True
S.display.shading.cavity_type='BOTH'
S.display.shading.curvature_ridge_factor=1.35; S.display.shading.curvature_valley_factor=1.1
S.display.shading.show_specular_highlight=False
S.display.shading.background_type='WORLD'; S.world.color=(0.73,0.78,0.81)
S.view_settings.view_transform='Standard'
S.render.fps_base=1

COL={}
for name in ['01_WORLD','02_PORTS','03_SHIP','04_TRANSPORT','05_WAREHOUSE','06_CARGO_WORK','07_CAMERAS','08_REVIEW_GUIDES']:
    c=bpy.data.collections.new(name); S.collection.children.link(c); COL[name]=c
GUIDES=COL['08_REVIEW_GUIDES']; GUIDES.hide_render=True
MAT={}
for name,color in {'ocean':(.38,.58,.65,1),'land':(.65,.74,.64,1),'concrete':(.68,.70,.69,1),'road':(.32,.38,.42,1),'blue':(.025,.30,.66,1),'navy':(.04,.15,.24,1),'white':(.91,.93,.91,1),'steel':(.43,.52,.57,1),'pale':(.74,.81,.81,1),'orange':(.93,.48,.20,1),'cargo':(.66,.51,.32,1),'newcargo':(.20,.60,.57,1),'rubber':(.075,.105,.12,1),'yellow':(.96,.74,.28,1)}.items():
    m=bpy.data.materials.new(name); m.diffuse_color=color; MAT[name]=m

def tag(o,aid=None,iid=None,env=False,level='proxy'):
    if aid:o['asset_id']=aid
    if iid:o['instance_id']=iid
    if env:o['environment']=True
    o['representation']=level
    return o
def link(o,col):
    for c in list(o.users_collection):c.objects.unlink(o)
    COL[col].objects.link(o)
def empty(name,col,aid=None,parent=None,loc=(0,0,0),env=False,iid=None):
    o=bpy.data.objects.new(name,None); COL[col].objects.link(o)
    o.parent=parent; o.location=loc
    o.empty_display_size=.4
    return tag(o,aid,iid or (name if aid else None),env)
def box(name,loc,dims,mat,col,parent=None,aid=None,env=False):
    bpy.ops.mesh.primitive_cube_add(size=1)
    o=bpy.context.object; o.name=name; link(o,col)
    o.parent=parent; o.location=loc; o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(MAT[mat]); tag(o,aid,None,env)
    return o
def cylinder(name,loc,r,depth,mat,col,parent=None,axis='Z'):
    bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=r,depth=depth)
    o=bpy.context.object; o.name=name; link(o,col); o.parent=parent; o.location=loc
    if axis=='Y':o.rotation_euler.x=math.pi/2
    o.data.materials.append(MAT[mat]);return o
def text(name,body,loc,size,col,parent=None,mat='navy',rotation=(0,0,0)):
    d=bpy.data.curves.new(name,'FONT');d.body=body;d.size=size;d.align_x='CENTER';d.extrude=.002
    o=bpy.data.objects.new(name,d);COL[col].objects.link(o);o.parent=parent;o.location=loc;o.rotation_euler=rotation;d.materials.append(MAT[mat]);return o
def line(name,pts,width,mat,col,parent=None,aid=None,env=False):
    if mat=='road':
        vertices=[]
        for i,p in enumerate(pts):
            tangent=V(pts[min(i+1,len(pts)-1)])-V(pts[max(i-1,0)])
            side=V((-tangent.y,tangent.x,0)).normalized()*width
            vertices.extend([V(p)-side,V(p)+side])
        d=bpy.data.meshes.new(name)
        d.from_pydata(vertices,[],[(i,i+1,i+3,i+2) for i in range(0,len(vertices)-2,2)])
        o=bpy.data.objects.new(name,d);COL[col].objects.link(o);o.parent=parent
        d.materials.append(MAT[mat]);tag(o,aid,None,env);return o
    d=bpy.data.curves.new(name,'CURVE');d.dimensions='3D';d.resolution_u=1;d.bevel_depth=width;d.bevel_resolution=0
    p=d.splines.new('POLY');p.points.add(len(pts)-1)
    for dest,src in zip(p.points,pts):dest.co=(*src,1)
    o=bpy.data.objects.new(name,d);COL[col].objects.link(o);o.parent=parent;d.materials.append(MAT[mat]);tag(o,aid,None,env);return o
def set_matrix(o,m,f):
    o.location=m.to_translation();o.rotation_mode='QUATERNION'
    q=m.to_quaternion()
    if o.rotation_quaternion.dot(q)<0:q.negate()
    o.rotation_quaternion=q
    o.keyframe_insert('location',frame=f);o.keyframe_insert('rotation_quaternion',frame=f)
def set_loc(o,p,f):o.location=p;o.keyframe_insert('location',frame=f)
def set_angle(o,a,f):o.rotation_euler.z=a;o.keyframe_insert('rotation_euler',frame=f)
def local_root(name,aid,theta,col):
    o=empty(name,col,aid,env=True);o.matrix_world=region(theta);return o

USROOT=local_root('US_FRAME','E-05',US,'02_PORTS')
CNROOT=local_root('CN_FRAME','E-03',CN,'02_PORTS')
bpy.ops.mesh.primitive_uv_sphere_add(segments=128,ring_count=64,radius=R)
o=bpy.context.object;o.name='EARTH_CONTINUOUS_OCEAN';link(o,'01_WORLD');o.data.materials.append(MAT['ocean']);tag(o,'E-02','earth_ocean',True)
for p in o.data.polygons:p.use_smooth=True
def land(name,parent,x0,x1,y0,y1):
    # Fixed flat logistics terrace with a sloped, sphere-attached shoreline skirt.
    verts=[]
    for x,y in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]:verts.append((x,y,.68))
    for x,y in [(x0-8,y0-6),(x1+8,y0-6),(x1+8,y1+8),(x0-8,y1+8)]:
        verts.append((x,y,math.sqrt(max(1,R*R-x*x-y*y))-R+.15))
    d=bpy.data.meshes.new(name);d.from_pydata(verts,[],[(0,1,2,3),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)])
    o=bpy.data.objects.new(name,d);COL['01_WORLD'].objects.link(o);o.parent=parent;d.materials.append(MAT['land']);tag(o,'E-01',name,True)
land('CN_LAND_TERRACE',CNROOT,-25,24,5,36)
land('US_LAND_TERRACE',USROOT,-23,111,5,56)
for root,prefix in [(CNROOT,'CN'),(USROOT,'US')]:
    aid='E-03' if prefix=='CN' else 'E-05'
    box(prefix+'_QUAY',(0,8,.65),(34,8,.5),'concrete','02_PORTS',root,aid,True)
    for i in range(4):
        box(prefix+'_YARD_STACK_'+str(i),(-10+i*4,16,1.5),(3.2,1.45,1.5),'pale','02_PORTS',root,'P-03',True)
    line(prefix+'_YARD_ROAD',[(-20,20,.73),(23,20,.73)],1.1,'road','02_PORTS',root,aid,True)
    for i,(x,y,h) in enumerate([(-16,28,5),(-8,32,8),(1,30,6),(9,33,10),(18,30,7)]):
        if prefix=='US':x-=5;y+=17
        box(prefix+'_CITY_'+str(i),(x,y,.68+h/2),(3.5,3.5,h),'pale','02_PORTS',root,'E-04' if prefix=='CN' else 'E-06',True)

ship=empty('A02_SHIP','03_SHIP','A-02')
# Bow is +X, stern -X; rigid hull, no shape/scale animation.
verts=[(-7,-2.6,-.65),(5.6,-2.6,-.65),(7,0,-.65),(5.6,2.6,-.65),(-7,2.6,-.65),(-7,-2.6,.8),(5.6,-2.6,.8),(7,0,.8),(5.6,2.6,.8),(-7,2.6,.8)]
d=bpy.data.meshes.new('rigid_hull');d.from_pydata(verts,[],[(0,1,2,3,4),(5,9,8,7,6)]+[(i,(i+1)%5,(i+1)%5+5,i+5) for i in range(5)])
h=bpy.data.objects.new('SHIP_HULL',d);COL['03_SHIP'].objects.link(h);h.parent=ship;d.materials.append(MAT['navy'])
box('SHIP_DECK',(-.4,0,.84),(12.7,4.9,.12),'white','03_SHIP',ship)
box('SHIP_BRIDGE',(-5.5,0,2.0),(2,4,2.2),'white','03_SHIP',ship)
box('SHIP_BRIDGE_GLASS',(-5.3,0,2.6),(2.2,4.05,.5),'steel','03_SHIP',ship)
for x in [-2.6,.8,4.2]:
    for y in [-1.25,.65]:
        box(f'P03_DECK_{x}_{y}',(x,y,1.6),(3.2,1.45,1.5),'pale','03_SHIP',ship,'P-03')
        if not(x==.8 and y==-1.25):box(f'P03_UPPER_{x}_{y}',(x,y,3.1),(3.2,1.45,1.5),'steel','03_SHIP',ship,'P-03')
HERO_OFFSET=V((.8,-1.25,3.1))
container=empty('A01_CONTAINER','04_TRANSPORT','A-01')
for name,p,sz in [('FLOOR',(0,0,-.69),(3.2,1.5,.12)),('ROOF',(0,0,.69),(3.2,1.5,.12)),('SIDE_L',(0,.73,0),(3.2,.08,1.5)),('SIDE_R',(0,-.73,0),(3.2,.08,1.5)),('FRONT',(1.56,0,0),(.08,1.5,1.5))]:
    box('A01_'+name,p,sz,'blue','04_TRANSPORT',container)
for y in [-.776,.776]:
    text('PNPLINE_BRAND_SIDE_'+str(y),'PNPLINE',(0,y,-.12),.37,'04_TRANSPORT',container,'white',(math.pi/2 if y<0 else math.pi/2,0,0 if y<0 else math.pi))
doorL=empty('A01_DOOR_L','04_TRANSPORT',parent=container,loc=(-1.6,.84,0))
doorR=empty('A01_DOOR_R','04_TRANSPORT',parent=container,loc=(-1.6,-.84,0))
box('A01_DOOR_LEFT_LEAF',(0,-.42,0),(.08,.84,1.5),'blue','04_TRANSPORT',doorL)
box('A01_DOOR_RIGHT_LEAF',(0,.42,0),(.08,.84,1.5),'blue','04_TRANSPORT',doorR)

trailer=empty('A03_TRAILER','04_TRANSPORT','A-03')
tractor=empty('A03_TRACTOR','04_TRANSPORT','A-03')
box('TRAILER_CHASSIS',(0,0,1.57),(3.2,1.5,.46),'steel','04_TRANSPORT',trailer)
box('TRAILER_COUPLING_TONGUE',(1.85,0,1.4),(.6,.5,.2),'steel','04_TRANSPORT',trailer)
empty('TRAILER_HITCH','04_TRANSPORT',parent=trailer,loc=(2,0,1.4))
empty('TRACTOR_HITCH','04_TRANSPORT',parent=tractor,loc=(0,0,1.4))
box('TRACTOR_CHASSIS',(.6,0,1.35),(2.3,1.5,.35),'navy','04_TRANSPORT',tractor)
box('TRACTOR_CAB',(1.25,0,2.03),(1.25,1.5,1.5),'white','04_TRANSPORT',tractor)
box('TRACTOR_GLASS',(1.45,0,2.32),(1.0,1.54,.48),'steel','04_TRANSPORT',tractor)
wheels=[]
for parent,xs in [(trailer,[-.25,.25]),(tractor,[0,1.65])]:
    for x in xs:
        for y in [-.85,.85]:wheels.append(cylinder(parent.name+'_WHEEL_'+str(x)+str(y),(x,y,1.1),.4,.23,'rubber','04_TRANSPORT',parent,'Y'))

def crane(prefix,root,aid):
    for x in [-2,3.5]:
        for y in [5,12]:box(prefix+'_LEG_'+str(x)+str(y),(x,y,6.3),(.4,.4,11.2),'yellow','02_PORTS',root,aid,True)
        box(prefix+'_BOOM_'+str(x),(x,4,11.9),(.4,20,.45),'yellow','02_PORTS',root,aid,True)
    spread=empty(prefix+'_SPREADER','04_TRANSPORT',aid)
    box(prefix+'_SPREADER_FRAME',(0,0,0),(3.3,1.6,.18),'yellow','04_TRANSPORT',spread)
    cables=[cylinder(prefix+'_CABLE_'+str(i),(0,0,0),.028,1,'steel','04_TRANSPORT') for i in range(4)]
    box(prefix+'_TROLLEY',(.75,0,11.8),(5.9,1.65,.3),'yellow','04_TRANSPORT',root,aid)
    return spread,cables
cnspread,cncables=crane('P01',CNROOT,'P-01')
usspread,uscables=crane('P02',USROOT,'P-02')

# Trailer axle follows a C1 straight/elliptical/straight lane. Tractor hitch
# tangent is derived from axle tangent plus curvature; no pivot-only turn.
TURN_X=29.4
ARC_RX=6.0
ARC_RY=10.0
ARC_ANGLES=[math.pi*i/1000 for i in range(1001)]
ARC_LENGTHS=[0.0]
for i in range(1,len(ARC_ANGLES)):
    a,b=ARC_ANGLES[i-1:i+1]
    ARC_LENGTHS.append(ARC_LENGTHS[-1]+math.hypot(ARC_RX*(math.sin(b)-math.sin(a)),ARC_RY*(math.cos(b)-math.cos(a))))
TURN=ARC_LENGTHS[-1]
LEN=TURN_X+TURN+.2
def lane(s):
    if s<=TURN_X:return V((s,9,0)),0.0,0.0
    if s<=TURN_X+TURN:
        distance=s-TURN_X
        i=min(len(ARC_LENGTHS)-1,max(1,bisect.bisect_left(ARC_LENGTHS,distance)))
        a=mix(ARC_ANGLES[i-1],ARC_ANGLES[i],(distance-ARC_LENGTHS[i-1])/(ARC_LENGTHS[i]-ARC_LENGTHS[i-1]))
        yaw=math.atan2(ARC_RY*math.sin(a),ARC_RX*math.cos(a))
        curvature=ARC_RX*ARC_RY/(ARC_RX**2*math.cos(a)**2+ARC_RY**2*math.sin(a)**2)**1.5
        return V((TURN_X+ARC_RX*math.sin(a),19-ARC_RY*math.cos(a),0)),yaw,curvature
    return V((TURN_X-(s-TURN_X-TURN),29,0)),math.pi,0.0
def vehicle_at(f):
    s=LEN*ramp(f,649,810)
    p,a,k=lane(s)
    if f>=849:p.x=mix(29.2,34.4,ramp(f,849,890))
    # Smooth the tractor steering transition around curvature discontinuities.
    eps=.08
    pm,am,_=lane(max(0,s-eps));pp,ap,_=lane(min(LEN,s+eps))
    hm=pm+V((2*math.cos(am),2*math.sin(am),0))
    hp=pp+V((2*math.cos(ap),2*math.sin(ap),0))
    ha=math.atan2(hp.y-hm.y,hp.x-hm.x) if (hp-hm).length>1e-8 else a
    if f>=810:ha=math.pi
    hp=p+V((2*math.cos(a),2*math.sin(a),0))
    return p,a,hp,ha,s

# Road meshes and yard remain fixed for all frames.
roadpts=[(*lane(LEN*i/160)[0][:2],.735) for i in range(161)]
line('E07_INBOUND_ROAD',roadpts,1.25,'road','02_PORTS',USROOT,'E-07',True)
box('E09_MANEUVER_YARD',(27,29,.72),(24,6,.08),'concrete','05_WAREHOUSE',USROOT,'E-09',True)
warehouse=empty('E08_WAREHOUSE','05_WAREHOUSE','E-08',parent=USROOT,env=True)
box('WAREHOUSE_FLOOR',(52,32,1.27),(32,14,1.18),'concrete','05_WAREHOUSE',warehouse,'E-08',True)
box('WAREHOUSE_BACK_WALL',(52,39,4.35),(32,.25,5),'pale','05_WAREHOUSE',warehouse,'E-08',True)
box('WAREHOUSE_PARTIAL_ROOF',(52,37.6,6.95),(32,3,.22),'white','05_WAREHOUSE',warehouse,'E-08',True)
for x in [36,44,52,60,68]:box('WAREHOUSE_COLUMN_'+str(x),(x,38.6,4.3),(.25,.25,5),'steel','05_WAREHOUSE',warehouse,'E-08',True)
dock=empty('DOCK_TARGET','05_WAREHOUSE',parent=USROOT,loc=(36,29,1.8),env=True)
box('DOCK_BRIDGE',(35.98,29,1.82),(.18,1.48,.08),'steel','05_WAREHOUSE',USROOT,'E-09',True)
box('E10_OUTBOUND_YARD',(75,30,.72),(14,14,.08),'concrete','05_WAREHOUSE',USROOT,'E-10',True)
rd=bpy.data.meshes.new('loading_bridge_mesh')
rd.from_pydata([(68,27.2,1.86),(71,27.2,1.54),(71,30.4,1.54),(68,30.4,1.86)],[],[(0,1,2,3)])
ro=bpy.data.objects.new('E10_LOADING_BRIDGE',rd);COL['05_WAREHOUSE'].objects.link(ro);ro.parent=USROOT;rd.materials.append(MAT['steel']);tag(ro,'E-10',None,True)
for name,x,y,w,dep,aid,color in [('INBOUND_WAIT',40,29,4,4,'W-10','newcargo'),('STORAGE',45,34,7,7,'W-03','steel'),('PICKING',50,29,4,3,'W-05','yellow'),('PACKING',57,29,5,4,'W-06','cargo'),('OUTBOUND_WAIT',64,29,4,4,'W-10','orange')]:
    box(name+'_ZONE',(x,y,1.88),(w,dep,.03),color,'05_WAREHOUSE',USROOT,aid,True)
    text(name+'_REVIEW_LABEL',name,(x,24,1.9),.8,'08_REVIEW_GUIDES',USROOT)
for x in [44,48]:
    for y in [32.5,36.5]:
        for dx in [-1.4,1.4]:
            for dy in [-.75,.75]:box(f'RACK_POST_{x}_{y}_{dx}_{dy}',(x+dx,y+dy,3.7),(.12,.12,3.65),'steel','05_WAREHOUSE',USROOT,'W-03',True)
        for z in [2.1,3.65,5.25]:
            box(f'RACK_SHELF_{x}_{y}_{z}',(x,y,z),(3,1.7,.14),'steel','05_WAREHOUSE',USROOT,'W-03',True)
            if not (x==44 and y==32.5 and z==2.1):
                for dx in [-.85,0,.85]:box(f'RACK_CARGO_{x}_{y}_{z}_{dx}',(x+dx,y,z+.5),(.7,1.05,.9),'cargo','06_CARGO_WORK',USROOT,'W-01')

def pallet(name,aid,color):
    o=empty(name,'06_CARGO_WORK',aid)
    box(name+'_BASE',(0,0,0),(1.1,.95,.12),'cargo','06_CARGO_WORK',o)
    for x in [-.27,.27]:
        for y in [-.22,.22]:box(name+'_BOX_'+str(x)+str(y),(x,y,.43),(.5,.4,.73),color,'06_CARGO_WORK',o)
    return o
newpal=pallet('W01_NEW_PALLET','W-01','newcargo')
storedpal=pallet('W01_STORED_PALLET','W-01','cargo')
remaining=pallet('W01_REMAINING_CONTAINER_CARGO','W-01','newcargo');remaining.parent=container;remaining.location=(.65,0,-.51)
jack=empty('W02_INBOUND_JACK','06_CARGO_WORK','W-02')
storejack=empty('W02_STORAGE_JACK','06_CARGO_WORK','W-02')
for o in [jack,storejack]:
    box(o.name+'_FORKS',(0,0,0),(1.3,1,.1),'yellow','06_CARGO_WORK',o)
    box(o.name+'_HANDLE',(.72,0,.6),(.12,.12,1.2),'yellow','06_CARGO_WORK',o)
cart=empty('W05_PICK_CART','06_CARGO_WORK','W-05')
outcart=empty('W09_OUT_CART','06_CARGO_WORK','W-09')
for o in [cart,outcart]:
    box(o.name+'_TRAY',(0,0,.5),(1.25,.95,.14),'steel','06_CARGO_WORK',o)
    for x in [-.46,.46]:
        for y in [-.36,.36]:cylinder(o.name+'_CASTER'+str(x)+str(y),(x,y,.12),.12,.12,'rubber','06_CARGO_WORK',o,'Y')
box('W04_PICK_BIN_PRODUCT',(50,32,2.6),(.65,.55,.5),'orange','06_CARGO_WORK',USROOT,'W-04')
box('W04_PICK_BIN_SUPPORT',(50,32,2.29),(.9,.8,.12),'steel','05_WAREHOUSE',USROOT,'W-03',True)
for y in [31.7,32.3]:box('W04_BIN_STAND_'+str(y),(50,y,2.045),(.65,.1,.37),'steel','05_WAREHOUSE',USROOT,'W-03',True)
box('W04_CART_ORDER_ALREADY_PICKED',(0,0,.86),(.6,.6,.6),'orange','06_CARGO_WORK',cart,'W-04')
box('W06_PACK_TABLE',(57,30,2.9),(3,1.6,.2),'white','05_WAREHOUSE',USROOT,'W-06',True)
for x in [55.8,58.2]:box('TABLE_LEG_'+str(x),(x,30,2.35),(.17,1.1,1.0),'steel','05_WAREHOUSE',USROOT,'W-06',True)
openbox=empty('W07_OPEN_PACK','06_CARGO_WORK','W-07',parent=USROOT,loc=(56.5,30,3.05))
box('PACK_BOX_BOTTOM',(0,0,0),(1,.8,.08),'cargo','06_CARGO_WORK',openbox)
for p,sz in [((-.48,0,.28),(.06,.8,.56)),((.48,0,.28),(.06,.8,.56)),((0,-.38,.28),(1,.06,.56)),((0,.38,.28),(1,.06,.56))]:box('PACK_BOX_WALL',p,sz,'cargo','06_CARGO_WORK',openbox)
box('PACK_BOX_CONTENT',(0,0,.2),(.55,.45,.3),'orange','06_CARGO_WORK',openbox)
box('W08_SEALED_READY',(58.2,30,3.34),(.9,.8,.66),'cargo','06_CARGO_WORK',USROOT,'W-08')
loadbox=empty('W08_LAST_LOAD','06_CARGO_WORK','W-08')
box('LAST_BOX_BODY',(0,0,0),(.6,.65,.55),'cargo','06_CARGO_WORK',loadbox)

def worker(name,p):
    o=empty(name,'06_CARGO_WORK','CH-01',parent=USROOT,loc=p)
    cylinder(name+'_TORSO',(0,0,.95),.24,.72,'orange','06_CARGO_WORK',o)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=.21)
    h=bpy.context.object;h.name=name+'_HEAD';link(h,'06_CARGO_WORK');h.parent=o;h.location=(0,0,1.55);h.data.materials.append(MAT['pale'])
    for y in [-.12,.12]:box(name+'_LEG'+str(y),(0,y,.35),(.18,.17,.7),'navy','06_CARGO_WORK',o)
    return o
worker('CH_PICKER',(50,30.7,1.86));worker('CH_PACKER',(57,31.4,1.86))
loader=worker('CH_LOADER',(66,27.05,1.86))
hands=box('CH_LOAD_SUPPORT',(0,0,0),(.6,.65,.06),'pale','06_CARGO_WORK',None,'CH-01')
arms=[cylinder('CH_LOAD_ARM_'+str(i),(0,0,0),.075,1,'orange','06_CARGO_WORK') for i in range(2)]

def van(name,aid,color):
    root=empty(name,'04_TRANSPORT',aid)
    box(name+'_FLOOR',(-.2,0,1.45),(3.6,1.65,.18),'steel','04_TRANSPORT',root)
    for p,sz in [((-.5,-.8,2.25),(3,.12,1.5)),((-.5,.8,2.25),(3,.12,1.5)),((-.5,0,3.02),(3,1.7,.12))]:box(name+'_CARGO_SHELL',p,sz,color,'04_TRANSPORT',root)
    box(name+'_CAB',(1.45,0,1.92),(1.25,1.6,1.4),color,'04_TRANSPORT',root)
    box(name+'_GLASS',(1.6,0,2.15),(1,1.63,.45),'steel','04_TRANSPORT',root)
    for x in [-1.3,1.5]:
        for y in [-.91,.91]:cylinder(name+'_WHEEL'+str(x)+str(y),(x,y,1.1),.4,.24,'rubber','04_TRANSPORT',root,'Y')
    for x in [-.8,.2]:box(name+'_PRELOADED'+str(x),(x,0,1.95),(.8,.9,.8),'cargo','06_CARGO_WORK',root,'W-08')
    l=empty(name+'_DOOR_L','04_TRANSPORT',parent=root,loc=(-2,.93,2.25))
    r=empty(name+'_DOOR_R','04_TRANSPORT',parent=root,loc=(-2,-.93,2.25))
    box(name+'_LEFT_LEAF',(0,-.465,0),(.1,.93,1.5),color,'04_TRANSPORT',l)
    box(name+'_RIGHT_LEAF',(0,.465,0),(.1,.93,1.5),color,'04_TRANSPORT',r)
    return root,l,r
van1,v1l,v1r=van('A04_PRIMARY','A-04','blue')
van2,v2l,v2r=van('A05_SECONDARY','A-05','white')
def delivery_path(t,branch):
    t=clamp(t)
    if t<.45:return V((73+12*t/.45,29,0)),0
    u=(t-.45)/.55
    # Smooth branch after common road, never split one vehicle.
    y=29+branch*12*smooth(u)
    x=85+22*u
    return V((x,y,0)),math.atan2(branch*72*u*(1-u),22)
for branch in [1,-1]:
    line('E11_ROUTE_'+str(branch),[(*delivery_path(i/100,branch)[0][:2],.74) for i in range(101)],1.1,'road','02_PORTS',USROOT,'E-11',True)
for i,(x,y) in enumerate([(101,48),(110,49),(106,8),(96,9)]):box('E12_DESTINATION_'+str(i),(x,y,2.7),(4,4,4),'pale','02_PORTS',USROOT,'E-12',True)
line('A05_WAIT_MERGE',[(72+11*i/60,35-6*smooth(i/60),.74) for i in range(61)],1.2,'road','02_PORTS',USROOT,'E-11',True)

camdata=bpy.data.cameras.new('MASTER_LENS');camdata.lens=40;camdata.clip_start=.08;camdata.clip_end=1500
cam=bpy.data.objects.new('CAM_MASTER',camdata);COL['07_CAMERAS'].objects.link(cam);S.camera=cam
target=empty('CAM_LOOK_TARGET','07_CAMERAS')
cam.rotation_mode='QUATERNION'

def ship_angle(f):
    if f<=145:return CN
    # One Hermite curve through departure, cruise, deceleration, with bounded velocity.
    return interp_scalar([(145,CN),(216,math.radians(-60.7)),(300,math.radians(-39)),(390,math.radians(-3)),(456,math.radians(17)),(510,US),(END,US)],f,zero_ends=True)
def spline(keys,f):
    if f<=keys[0][0]:return V(keys[0][1])
    if f>=keys[-1][0]:return V(keys[-1][1])
    for i in range(len(keys)-1):
        t0,p0=keys[i];t1,p1=keys[i+1]
        if t0<=f<=t1:
            p0=V(p0);p1=V(p1);dt=t1-t0;u=(f-t0)/dt
            left=keys[max(i-1,0)];right=keys[min(i+2,len(keys)-1)]
            m0=(p1-V(left[1]))/(t1-left[0])
            m1=(V(right[1])-p0)/(right[0]-t0)
            return (2*u**3-3*u*u+1)*p0+(u**3-2*u*u+u)*dt*m0+(-2*u**3+3*u*u)*p1+(u**3-u*u)*dt*m1
def interp_scalar(keys,f,zero_ends=False):
    if f<=keys[0][0]:return keys[0][1]
    if f>=keys[-1][0]:return keys[-1][1]
    for i in range(len(keys)-1):
        a,x=keys[i];b,y=keys[i+1]
        if a<=f<=b:
            u=(f-a)/(b-a);dt=b-a
            prev=keys[max(0,i-1)];nxt=keys[min(len(keys)-1,i+2)]
            m0=(y-prev[1])/(b-prev[0]);m1=(nxt[1]-x)/(nxt[0]-a)
            if x==y:m0=m1=0
            if zero_ends and i==0:m0=0
            if zero_ends and (i+1==len(keys)-1 or y==US):m1=0
            return (2*u**3-3*u*u+1)*x+(u**3-2*u*u+u)*dt*m0+(-2*u**3+3*u*u)*y+(u**3-u*u)*dt*m1

# Anchors are one global continuous spline, not per-scene camera resets.
camera_keys=[]; target_keys=[]
def camera_anchor(f,p,t,space='US'):
    frame=region(ship_angle(f)) if space=='SHIP' else UM
    camera_keys.append((f,tuple(frame@V(p))));target_keys.append((f,tuple(frame@V(t))))
camera_anchor(1,(5.9,-8.7,8.8),(.8,-1.25,5.7),'SHIP')
camera_anchor(50,(5.9,-8.7,6.9),(.8,-1.25,4.0),'SHIP')
camera_anchor(80,(6.2,-9.7,6.1),(.8,-1.25,2.9),'SHIP')
camera_anchor(110,(5,-16,10),(0,0,2.0),'SHIP')
camera_anchor(160,(-5,-25,17),(0,2,2),'SHIP')
camera_anchor(216,(-17,-26,19),(3,0,1),'SHIP')
camera_anchor(270,(-25,-40,52),(5,0,-2),'SHIP')
camera_anchor(325,(-35,-70,100),(8,0,-8),'SHIP')
camera_anchor(370,(-27,-44,54),(10,3,0),'SHIP')
camera_anchor(398,(-17,-27,23),(7,3,1),'SHIP')
camera_anchor(421,(-3,-23,17),(2,0,1),'SHIP')
camera_anchor(447,(16,-20,15),(0,0,1),'SHIP')
camera_anchor(476,(23,-14,20),(1,3,2),'SHIP')
camera_anchor(510,(40,-38,40),(25,17,2),'US')
camera_anchor(548,(22,22,18),(2,5,6),'US')
camera_anchor(590,(14,21,13),(1,8,5.5),'US')
camera_anchor(638,(5,19,9),(1,9,2),'US')
for f in [668,700,731,760,788,818]:
    p,a,_,_,_=vehicle_at(f)
    offset=V((-1.5*math.cos(a)-12*math.sin(a),-1.5*math.sin(a)+12*math.cos(a),10))
    camera_anchor(f,p+offset,p+V((.8*math.cos(a),.8*math.sin(a),2.0)))
for f,p,t in [(850,(34,20,9),(31,29,2.3)),(882,(38,20,8),(34,29,2.2)),(915,(42,21,7.5),(37,29,2.3)),(947,(45,21.5,7.2),(40,29,2.4)),(985,(49,21.5,7.5),(44,32,3)),(1022,(53,21,7.8),(49,31,3)),(1075,(60,21,7.5),(56,30,2.8)),(1117,(66,20.5,7.8),(63,29,2.8)),(1170,(73,19.5,8),(71,29,2.2)),(1210,(77,19,8),(75,29,2)),(1250,(82,15,11),(80,29,2)),(1290,(95,3,26),(82,29,2)),(1340,(103,-24,50),(78,30,2)),(1392,(105,-40,65),(73,30,2))]:camera_anchor(f,p,t)

route_points=[]
for f in range(1,END+1):
    a=ship_angle(f);shipm=region(a)
    set_matrix(ship,shipm,f)
    tp,ta,hp,ha,distance=vehicle_at(f)
    tm=pose(tp,ta);set_matrix(trailer,tm,f);set_matrix(tractor,pose(hp,ha),f)
    if f<72:
        cm=shipm@Matrix.Translation(HERO_OFFSET+V((0,0,3.65*(1-ramp(f,1,72)))))
    elif f<=532:cm=shipm@Matrix.Translation(HERO_OFFSET)
    elif f<=555:cm=UM@Matrix.Translation(HERO_OFFSET+V((0,0,4.3*ramp(f,532,555))))
    elif f<=599:cm=UM@Matrix.Translation((mix(.8,0,ramp(f,555,599)),mix(-1.25,9,ramp(f,555,599)),7.4))
    elif f<=632:cm=UM@Matrix.Translation((0,9,mix(7.4,2.55,ramp(f,599,632))))
    else:cm=tm@Matrix.Translation((0,0,2.55))
    set_matrix(container,cm,f)
    doorangle=math.radians(270)*ramp(f,811,842)
    set_angle(doorL,-doorangle,f);set_angle(doorR,doorangle,f)
    if f<=72:cp=HERO_OFFSET+V((0,0,3.65*(1-ramp(f,1,72))+.89))
    else:cp=HERO_OFFSET+V((0,0,.89+5*ramp(f,77,139)))
    if f<510:up=V((.8,-1.25,9))
    elif f<=529:up=V((.8,-1.25,mix(9,3.99,ramp(f,510,529))))
    elif f<=632:up=UM.inverted()@cm.translation+V((0,0,.89))
    else:up=V((0,9,3.44+5*ramp(f,637,666)))
    for spread,cables,p,base in [(cnspread,cncables,cp,CM),(usspread,uscables,up,UM)]:
        set_matrix(spread,base@Matrix.Translation(p),f)
        trolley=bpy.data.objects['P01_TROLLEY' if spread==cnspread else 'P02_TROLLEY']
        set_loc(trolley,(.75,p.y,11.8),f)
        for cable,(dx,dy) in zip(cables,[(-1.4,-.6),(-1.4,.6),(1.4,-.6),(1.4,.6)]):
            low=p+V((dx,dy,.1));high=V((p.x+dx,p.y+dy,11.7))
            set_matrix(cable,base@Matrix.Translation((low+high)/2),f)
            cable.scale.z=max(.01,high.z-low.z);cable.keyframe_insert('scale',frame=f)
    if f<=908:nm=cm@Matrix.Translation((-.65,0,-.49))
    else:
        u=ramp(f,908,952);p=V((mix(35.05,40,u),mix(29,29,u),2.06-.14*ramp(f,952,966)))
        nm=pose(p,math.pi)
    set_matrix(newpal,nm,f)
    jp=UM.inverted()@nm.translation-V((0,0,.15));jp.x+=2*ramp(f,967,985)
    if f<=908:jp=V((mix(38,35.05,ramp(f,900,908)),29,1.91))
    set_matrix(jack,pose(jp,math.pi),f)
    st=V((44,mix(29,32.5,ramp(f,985,1018)),2.3-.07*ramp(f,1018,1026)))
    set_matrix(storedpal,pose(st,math.pi/2),f)
    sj=st-V((0,0,.15));sj.y-=2*ramp(f,1027,1043);set_matrix(storejack,pose(sj,math.pi/2),f)
    cartp=V((mix(50,54,ramp(f,1030,1074)),28,1.86));set_matrix(cart,pose(cartp),f)
    oc=V((mix(60,66,ramp(f,1090,1150)),28,1.86));oc.y-=2*ramp(f,1167,1193);set_matrix(outcart,pose(oc),f)
    transfer=ramp(f,1150,1166)
    lb=V((oc.x if f<=1150 else mix(66,71.4,transfer),mix(28,29,transfer),mix(2.705,1.815,transfer)))
    if f>1200:
        vp,va=delivery_path(ramp(f,1201,1392),1);lm=pose(vp,va)@Matrix.Translation((-1.6,0,1.815))
    else:lm=pose(lb)
    set_matrix(loadbox,lm,f)
    walkx=mix(66,70.7,transfer)
    walkz=1.86-.32*clamp((walkx-68)/3)
    walk=V((walkx,mix(27.05,28.05,transfer),walkz))
    # Withdraw back along the same supported bridge before the van departs.
    retreat=ramp(f,1168,1195)
    walk=walk.lerp(V((66,27.2,1.86)),retreat)
    walk.z=1.86-.32*clamp((walk.x-68)/3)
    set_loc(loader,walk,f)
    resting=walk+V((0,.45,.7))
    supportpos=lb-V((0,0,.305))
    supportpos=resting.lerp(supportpos,ramp(f,1145,1150)*(1-ramp(f,1167,1192)))
    set_matrix(hands,pose(supportpos),f)
    for arm,side in zip(arms,[-1,1]):
        start=walk+V((side*.2,0,1.0));end=supportpos+V((side*.2,0,0))
        am=(end-start).to_track_quat('Z','Y').to_matrix().to_4x4();am.translation=(start+end)/2
        set_matrix(arm,UM@am,f);arm.scale.z=(end-start).length;arm.keyframe_insert('scale',frame=f)
    vp,va=delivery_path(ramp(f,1201,1392),1);set_matrix(van1,pose(vp,va),f)
    if f<1261:vp2=V((72,35,0));va2=0
    elif f<1310:
        u=ramp(f,1261,1310);vp2=V((mix(72,83,u),35-6*smooth(u),0));va2=math.atan2(-36*u*(1-u),11)
    else:vp2,va2=delivery_path(mix(.375,1,ramp(f,1310,1392)),-1)
    set_matrix(van2,pose(vp2,va2),f)
    shut=1-ramp(f,1168,1193)
    set_angle(v1l,-math.radians(270)*shut,f);set_angle(v1r,math.radians(270)*shut,f)
    set_angle(v2l,0,f);set_angle(v2r,0,f)
    cp=spline(camera_keys,f);ct=spline(target_keys,f)
    # Horizon up interpolates radially over the globe and ends on the US tangent frame.
    up=region(mix(a,US,ramp(f,447,535))).to_3x3()@V((0,0,1))
    z=(cp-ct).normalized();x=up.cross(z).normalized();y=z.cross(x).normalized()
    qm=Matrix((x,y,z)).transposed().to_4x4();qm.translation=cp
    set_matrix(cam,qm,f);set_loc(target,ct,f)
    camdata.lens=40-8*ramp(f,476,510)*(1-ramp(f,510,555))
    camdata.keyframe_insert('lens',frame=f)
    if f%6==1:route_points.append(cp)
    for wheel in wheels:
        wheel.rotation_euler.y=-distance/.4;wheel.keyframe_insert('rotation_euler',frame=f)

# Curved wake ribbon is baked as geometry keys only on its own guide-like proxy,
# separate from the fixed environment. It stays on the sphere behind the ship.
wake=empty('FX01_WAKE','03_SHIP','FX-01')
for j in range(2):
    d=bpy.data.meshes.new('wake_mesh_'+str(j));d.from_pydata([(0,0,0)]*42,[],[(i,i+1,i+3,i+2) for i in range(0,40,2)])
    o=bpy.data.objects.new('WAKE_RIBBON_'+str(j),d);COL['03_SHIP'].objects.link(o);d.materials.append(MAT['white'])
    # Shape is fixed in ship angular coordinates, posed tangentially; sampled arc
    # accounts for water curvature, unlike a flat line behind a tangent hull.
    for i in range(21):
        x=-7-i*.45;y=(-1 if j==0 else 1)*(1.5+i*.045)
        for q,dy in enumerate([-.045,.045]):d.vertices[i*2+q].co=(x,y+dy,math.sqrt(R*R-x*x-(y+dy)**2)-R+.025)
    o.parent=ship
    for f in [1,145,180,490,510,END]:
        o.hide_render=f<=145 or f>=510;o.keyframe_insert('hide_render',frame=f)

line('CAMERA_PATH',route_points,.055,'orange','08_REVIEW_GUIDES')
line('SHIP_ROUTE',[tuple(region(mix(CN,US,i/160))@V((0,0,.2))) for i in range(161)],.1,'yellow','08_REVIEW_GUIDES')
for name,f in [('S1',1),('B12',96),('S2',96),('B23',216),('S3',216),('B34',456),('S4',456),('B45',648),('S5',648),('B56',900),('S6',900),('B67',1200),('S7',1200)]:S.timeline_markers.new(name,frame=f)
for name,f in [('DETAIL_DEFERRED_PICK_HAND',1020),('DETAIL_DEFERRED_PACK_FOLD_TAPE',1090),('DETAIL_DEFERRED_LOADING_HAND',1158)]:S.timeline_markers.new(name,frame=f)
S['detail_deferred']='Picking hand/grasp; carton flap fold/tape; loader hands; mechanism latches. Fixed open and sealed boxes are separate work-in-progress cargo, never a magical transformation.'

# All transforms interpolate linearly between dense samples; no hidden per-shot ease stops.
for action in bpy.data.actions:
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fc in bag.fcurves:
                    for kp in fc.keyframe_points:kp.interpolation='LINEAR'
assets=[]
for aid in sorted({o.get('asset_id') for o in S.objects if o.get('asset_id')}):
    obs=[o for o in S.objects if o.get('asset_id')==aid]
    assets.append({'asset_id':aid,'objects':[o.name for o in obs],'instances':[o['instance_id'] for o in obs if 'instance_id'in o],'representation':'editable proxy / occupancy / route','detail_followup':'Final appearance and detailed operator action deferred'})
sources=[]
for f in sorted((ROOT/'inputs').glob('N*.json')):
    item=json.loads(f.read_text(encoding='utf-8'));sources.append({k:item.get(k) for k in ['id','title','url','page_last_edited_at','verification']})
manifest={'version':'v001','scope':S['scope'],'sources':sources,'asset_inventory':'../plan/inputs/asset-inventory-source-v0.1.txt','repo':{'branch':'main','head':'8e3d5700b671a2b0e0b6af0daa42bf3644ba8c43','existing_changes':'untracked hero-section-video/; preserved'},'environment':{'blender':bpy.app.version_string,'binary':bpy.app.binary_path,'connection':'local headless bpy','model_identifier':'not exposed by runtime; Codex/GPT-6 family per host instructions','reasoning_setting':'not exposed','ffmpeg':'7.1'},'settings':{'unit':'test metre (not operational scale)','earth_radius':R,'ship_length':14,'china_angle_deg':-65,'us_angle_deg':25,'flat_terraces':'fixed logistics terraces with skirts attached to spherical terrain','fps':FPS,'frames':END,'duration_seconds':END/FPS,'lens_mm':40,'resolution':[768,432],'ratio':'16:9 review only','engine':S.render.engine,'camera_side':'ship sea side local -Y through S3; around bow to shore in S4; truck left side through S5'},'assets':assets,'provisional_choices':['one auxiliary outbound box van','pallet-jack occupancy proxy','picking cart and outbound cart','270 degree two-leaf rear doors','frame timings for spatial testing only'],'unverified':['storyboard image comparison (no version/selection metadata)','mobile aspect ratio not supplied','final web copy/CTA layout','detailed worker and crane mechanisms'],'authoritative_source':'scripts/build_master.py; saved blend contains all baked motion; no manual edits'}
manifest['settings']['lens_mm']={'range':[32,40],'base':40,'animated_interval':[476,555],'minimum_frame':510,'purpose':'Reveal US port and warehouse without excessive camera speed'}
manifest['settings']['output_frame_count']=END
(ROOT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
S.frame_set(1)
S.render.filepath=str(ROOT/'preview'/'frames'/'frame-')
S['generator']='scripts/build_master.py'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'master-v001.blend'))
print('MASTER_SAVED',len(S.objects),'objects',END,'frames')
