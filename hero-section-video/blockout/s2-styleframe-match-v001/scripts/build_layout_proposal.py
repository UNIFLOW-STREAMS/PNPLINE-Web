"""Editable art/layout study under approved separate camera proposal.
All art is real geometry, static in a CN local frame; no image projection.
Not automatically adopted as a final master. Source and existing outputs guarded.
"""
import bpy,math,random,json,sys,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.geometry import tessellate_polygon
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
import camera_proposal
OUT=Path(sys.argv[sys.argv.index('--')+1]).resolve()
assert not OUT.exists(),'Refuse existing output'
assert hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()=='b043cfbbc048cfeb90d16808852424ddaaf5c16c1dd60057fe98d73cf18132d2'
s=bpy.context.scene;cfg=camera_proposal.apply();s.frame_set(156)
col=bpy.data.collections.new('SF_LAYOUT_PROPOSAL');s.collection.children.link(col)
def tag(o):o['styleframe_owner']='s2-styleframe-match-v001';return o
def empty(n,p=None,loc=(0,0,0)):
 o=bpy.data.objects.new(n,None);col.objects.link(o);o.parent=p;o.location=loc;return tag(o)
D=empty('SF_CN_LAYOUT',s.objects['CN_FRAME']);D.rotation_euler.z=math.pi;bpy.context.view_layer.update()
DM=D.matrix_world.copy();DI=DM.inverted()
def mat(n,c,metal=0,rough=.45):
 m=bpy.data.materials.new('SF_'+n);m.diffuse_color=(*c,1);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*c,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough
 return m
M={n:mat(n,c,me,ro) for n,c,me,ro in [('glass',(.06,.20,.25),.65,.23),('silver',(.36,.46,.48),.6,.28),('stone',(.72,.64,.48),0,.68),('cream',(.9,.82,.65),0,.45),('roof',(.035,.055,.06),.15,.5),('blue',(.012,.34,.58),.4,.28),('navy',(.008,.18,.3),.4,.25),('red',(.58,.018,.012),.35,.28),('gold',(.85,.48,.095),.7,.22),('white',(.91,.91,.83),.05,.38),('cloud',(.9,.88,.79),0,.42),('water',(.008,.055,.07),.55,.17),('wave',(.13,.45,.49),.4,.23),('green',(.09,.16,.035),0,.8),('bark',(.13,.06,.025),0,.9),('pink',(.44,.065,.14),.5,.29)]}
def mesh(n,vs,fs,m,p=D):
 d=bpy.data.meshes.new(n);d.from_pydata(vs,[],fs);d.update();o=bpy.data.objects.new(n,d);col.objects.link(o);o.parent=p
 if m:d.materials.append(m)
 return tag(o)
def box(n,pos,dim,m,p=D):
 x,y,z=dim;vs=[(pos[0]+a*x/2,pos[1]+b*y/2,pos[2]+c*z/2)for a,b,c in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
 return mesh(n,vs,[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)],m,p)
def tube(n,pts,r,m,p=D,closed=False):
 c=bpy.data.curves.new(n,'CURVE');c.dimensions='3D';c.resolution_u=2;c.bevel_depth=r;c.bevel_resolution=2
 sp=c.splines.new('POLY');sp.points.add(len(pts)-1)
 for v,pt in zip(sp.points,pts):v.co=(*pt,1)
 sp.use_cyclic_u=closed;o=bpy.data.objects.new(n,c);col.objects.link(o);o.parent=p;c.materials.append(m);return tag(o)
def lathe(n,pos,rings,m,p=D,N=32):
 vs=[(pos[0]+rad*math.cos(a*2*math.pi/N),pos[1]+rad*math.sin(a*2*math.pi/N),pos[2]+z)for z,rad in rings for a in range(N)]
 fs=[(i*N+j,i*N+(j+1)%N,(i+1)*N+(j+1)%N,(i+1)*N+j)for i in range(len(rings)-1)for j in range(N)]
 fs += [tuple(range(N-1,-1,-1)),tuple((len(rings)-1)*N+j for j in range(N))]
 o=mesh(n,vs,fs,m,p)
 for f in o.data.polygons:f.use_smooth=True
 return o
def sphere(n,pos,rad,m,p=D):return lathe(n,pos,[(rad*math.cos(t*math.pi/16),rad*math.sin(t*math.pi/16))for t in range(17)],m,p)
def uvpoint(px,py,z=1.25):
 # Intersection of a fixed f156 camera ray with a local horizontal plane.
 cam=s.camera;fr=cam.data.view_frame(scene=s);xs=[v.x for v in fr];ys=[v.y for v in fr]
 v=Vector((min(xs)+(max(xs)-min(xs))*px/2048,max(ys)-(max(ys)-min(ys))*py/1156,fr[0].z))
 origin=DI@cam.matrix_world.translation;direction=DI.to_3x3()@cam.matrix_world.to_3x3()@v
 return origin+direction*((z-origin.z)/direction.z)
def topheight(pos,py):
 from bpy_extras.object_utils import world_to_camera_view
 lo,hi=pos.z,100
 for _ in range(45):
  z=(lo+hi)/2;q=world_to_camera_view(s,s.camera,DM@Vector((pos.x,pos.y,z)))
  if (1-q.y)*1156>py:lo=z
  else:hi=z
 return (lo+hi)/2-pos.z
def pxwidth(pos,pixels):
 from bpy_extras.object_utils import world_to_camera_view
 a=world_to_camera_view(s,s.camera,DM@pos);b=world_to_camera_view(s,s.camera,DM@(pos+Vector((1,0,0))))
 return pixels/2048/abs(b.x-a.x)
def sample_ring(points,N=96):
 out=[]
 for k in range(N):
  u=k/N*len(points);i=int(u);t=u-i;p0,p1,p2,p3=[Vector(points[j%len(points)])for j in [i-1,i,i+1,i+2]]
  out.append((p1*2+(p2-p0)*t+(p0*2-p1*5+p2*4-p3)*t*t+(-p0+p1*3-p2*3+p3)*t*t*t)*.5)
 return out
def annulus(n,outer,inner,z,m,p=D):
 vs=[(v.x,v.y,z)for v in outer+inner];N=len(outer);return mesh(n,vs,[(i,(i+1)%N,N+(i+1)%N,N+i)for i in range(N)],m,p)
def disk(n,pts,z,m,p=D):
 vs=[Vector((v.x,v.y,z))for v in pts];tris=tessellate_polygon([vs]);lookup={tuple(v):i for i,v in enumerate(vs)}
 return mesh(n,[tuple(v)for v in vs],[[v if isinstance(v,int) else lookup[tuple(v)]for v in tri]for tri in tris],m,p)
def wall(n,pts,top,bottom,m,p=D):
 N=len(pts);vs=[(v.x,v.y,z if not callable(z) else z(v.x,v.y))for z in [top,bottom]for v in pts]
 return mesh(n,vs,[(i,(i+1)%N,N+(i+1)%N,N+i)for i in range(N)],m,p)
def seal_to_ocean(x,y):return math.sqrt(max(1,140**2-x*x-y*y))-140-.05
hidden=[]
for o in list(s.objects):
 if o.get('cn_proxy_owner') or o.get('s2_reveal_owner') or o.name in ['CN_LAND_TERRACE'] or o.name.startswith(('CN_CITY_','P01_LEG_','P01_BOOM_')):
  o.hide_render=True;o.hide_set(True);hidden.append(o.name)
# Existing actors, root motions and all their actions are untouched.
outer=sample_ring([uvpoint(*p) for p in [(235,720),(330,580),(610,490),(1010,470),(1390,530),(1610,730),(1770,800),(1470,866),(1030,905),(275,960)]])
wateredge=sample_ring([uvpoint(*p) for p in [(479,583),(620,520),(1020,505),(1255,528),(1312,578),(1230,652),(1046,696),(880,705),(657,708),(490,649)]])
island=sample_ring([uvpoint(*p) for p in [(629,548),(785,513),(1050,515),(1225,532),(1280,566),(1130,597),(950,613),(793,614),(663,583)]])
coast=empty('SF_WHITE_COAST',D);annulus('SF_FRONT_LAND',outer,wateredge,1.25,M['cream'],coast)
wall('SF_COAST_FOLDED_FACE',outer,1.25,seal_to_ocean,M['white'],coast)
wall('SF_BASIN_OUTER_WALL',wateredge,1.25,-.2,M['white'],coast)
water=empty('SF_INTERNAL_WATER',D);annulus('SF_BASIN_WATER_SURFACE',wateredge,island,.92,M['water'],water)
disk('SF_ISLAND_TOP',island,1.25,M['cream']);wall('SF_ISLAND_WALL',island,1.25,.1,M['white'])
tube('SF_ISLAND_EDGE',[(v.x,v.y,1.28)for v in island],.09,M['white'],closed=True)
# Bridge joins the two banks with a real curved span, balustrades and piers.
br=empty('SF_ARCH_BRIDGE',D);a=uvpoint(486,689);b=uvpoint(654,714);axis=b-a;side=Vector((-axis.y,axis.x,0)).normalized()*.42
vs=[]
for i in range(25):
 t=i/24;c=a.lerp(b,t);c.z+=.85*math.sin(math.pi*t)
 for off,z in [(-1,0),(1,0),(-1,-.19),(1,-.19)]:vs.append(tuple(c+side*off+Vector((0,0,z))))
mesh('SF_ARCH_SPAN',vs,[(i*4,i*4+1,(i+1)*4+1,(i+1)*4)for i in range(24)]+[(i*4+2,(i+1)*4+2,(i+1)*4+3,i*4+3)for i in range(24)],M['stone'],br)
for sign in [-1,1]:
 pts=[]
 for i in range(25):
  t=i/24;c=a.lerp(b,t)+side*sign;c.z+=.85*math.sin(math.pi*t)+.48;pts.append(tuple(c));tube(f'SF_BRIDGE_POST_{sign}_{i}',[tuple(c-Vector((0,0,.48))),tuple(c)],.035,M['cream'],br)
 tube('SF_BRIDGE_RAIL',pts,.06,M['cream'],br)
for j,p in enumerate([a,b]):box('SF_BRIDGE_PIER_'+str(j),(p.x,p.y,.5),(1,.9,1.5),M['stone'],br)
# Rounded title from an installed font, converted to mesh; font not distributed.
font_path=Path('C:/Windows/Fonts/arialbd.ttf');font=bpy.data.fonts.load(str(font_path)) if font_path.exists() else bpy.data.fonts[0]
def text(n,body,pos,height,width,m,p=D,rot=(math.pi/2,0,0),depth=.15,bevel=.045,bake=False):
 d=bpy.data.curves.new(n,'FONT');d.body=body;d.font=font;d.align_x='CENTER';d.size=1;d.extrude=depth;d.bevel_depth=bevel;d.bevel_resolution=3;d.resolution_u=16
 o=bpy.data.objects.new(n,d);col.objects.link(o);o.parent=p;o.location=pos;o.rotation_euler=rot;d.materials.append(m);tag(o);bpy.context.view_layer.update()
 # Local font X/Y dimensions; scaling before rotation is independent of parent.
 local=[Vector(c)for c in o.bound_box];wx=max(v.x for v in local)-min(v.x for v in local);hy=max(v.y for v in local)-min(v.y for v in local)
 o.scale=(width/max(wx,.001),height/max(hy,.001),1)
 if bake:
  bpy.ops.object.select_all(action='DESELECT');o.hide_set(False);o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
 return o
arc=json.loads((R/'title-arc-config.json').read_text());ar=arc['radius'];yaw=math.radians(arc['yaw_degrees'])
def bend(v):
 angle=v.x/ar;r=ar+v.y;x=r*math.sin(angle);y=r*math.cos(angle)-ar
 return Vector((arc['midpoint'][0]+math.cos(yaw)*x-math.sin(yaw)*y,arc['midpoint'][1]+math.sin(yaw)*x+math.cos(yaw)*y,v.z))
cursor=-(sum(arc['widths'])+arc['gap']*4)/2
for char,w in zip('CHINA',arc['widths']):
 centre_s=cursor+w/2;cursor+=w+arc['gap'];root=empty('SF_CHINA_'+char,D)
 centre=bend(Vector((centre_s,0,1.25)))
 for label,yoff,hfactor,wfactor,depth,bevel in [('GOLD',0,1,1,.65,.008),('RED',-.72,.94,.94,.10,.004)]:
  o=text('SF_CHINA_'+label+'_'+char,char,(centre_s,yoff,1.25+(1-hfactor)*arc['height']/2),arc['height']*hfactor,w*wfactor,M[label.lower()],root,depth=depth,bevel=bevel,bake=True)
  bpy.context.view_layer.update();matrix=o.matrix_local.copy()
  # Bake physical cylindrical deformation into editable mesh coordinates.
  # A single radius/spacing domain governs both faces of every glyph.
  coords=[bend(matrix@v.co)-centre for v in o.data.vertices]
  o.location=(0,0,0);o.rotation_euler=(0,0,0);o.scale=(1,1,1)
  for v,p in zip(o.data.vertices,coords):v.co=p
  o.data.update()
 root.location=centre
# Sculptural white spiral clouds, fixed independently of the camera.
for side,center,size in [('LEFT',(300,485),1),('RIGHT',(1602,539),arc['right_cloud_scale'])]:
 pos=uvpoint(*center,8) if side=='LEFT' else bend(Vector((cursor+1.3,-.5,6)))
 root=empty('SF_CLOUD_'+side,D,tuple(pos))
 for j,(dx,dz,radius)in enumerate([(-2,0,1.2),(0,0,1.5),(1.8,.6,1.55),(.2,2,1.4),(-1,-1.8,1.15),(1.5,-1.5,.95),(-3,-1.5,.65)]):
  dx*=size;dz*=size;radius*=size
  sphere('SF_CLOUD_BODY_'+side+str(j),(dx,.15,dz),radius,M['cloud'],root)
  pts=[]
  for k in range(70):
   t=k/69*math.pi*3.1;r=radius*(1-.8*k/69);front=-math.sqrt(max(.01,radius*radius-r*r))-.17*size
   pts.append((dx+r*math.cos(t),front,dz+r*math.sin(t)))
  tube('SF_CLOUD_SPIRAL_'+side+str(j),pts,.18*size,M['white'],root)
# Landmark functions and dense authored highrise ensemble.
def tower(n,px,basepy,toppy,widthpx,kind='box',tone='glass'):
 pos=uvpoint(px,basepy);h=topheight(pos,toppy);w=pxwidth(pos,widthpx);root=empty(n,D,tuple(pos));root['role']=kind
 if kind=='sphere':
  lathe(n+'_mast',(0,0,0),[(0,w*.1),(h*.92,w*.08),(h,.025)],M['silver'],root)
  for z,r in [(h*.24,w*.53),(h*.72,w*.46),(h*.92,w*.17)]:
   sphere(n+'_sphere',(0,0,z),r,M['pink'],root)
   for frac in [-.5,0,.5]:tube(n+'_sphere_band',[(math.sqrt(1-frac*frac)*r*math.cos(t*math.tau/40),math.sqrt(1-frac*frac)*r*math.sin(t*math.tau/40),z+frac*r)for t in range(40)],.035,M['silver'],root,True)
  for a0 in [0,2.094,4.188]:tube(n+'_leg',[(math.cos(a0)*w*.65,math.sin(a0)*w*.65,0),(0,0,h*.22)],w*.075,M['cream'],root)
 elif kind=='taper':
  rings=[(h*t,w*.5*(1-.5*t)*(1+.07*math.sin(t*5)))for t in [i/24 for i in range(25)]]
  lathe(n+'_body',(0,0,0),rings,M[tone],root,48)
  for i in range(1,70):
   t=i/70;r=w*.5*(1-.5*t)*(1+.07*math.sin(t*5));tube(n+'_floor',[(r*math.cos(a*math.tau/32),r*math.sin(a*math.tau/32),h*t)for a in range(32)],.018,M['silver'],root,True)
 elif kind=='open':
  box(n+'_lower',(0,0,h*.41),(w*.65,w*.6,h*.82),M[tone],root)
  for sign in [-1,1]:box(n+'_pillar',(sign*w*.38,0,h*.91),(w*.16,w*.6,h*.18),M[tone],root)
  box(n+'_lintel',(0,0,h*.985),(w,.6*w,.03*h),M['silver'],root)
 elif kind=='step':
  for j in range(8):
   z=h*j*.105;wid=w*(1-.085*j);box(n+'_tier',(0,0,z+h*.0525),(wid,wid,h*.105),M[tone],root)
  lathe(n+'_spire',(0,0,h*.84),[(0,w*.2),(h*.13,w*.06),(h*.16,.01)],M['silver'],root)
 else:box(n+'_body',(0,0,h/2),(w,w*.65,h),M[tone],root)
 if kind in ['box','open','step']:
  for z in [i*.24 for i in range(1,int(h/.24)) if i*.24<h*.8 or kind=='box']:
   tube(n+'_floor',[(-w*.5,-w*.335,z),(w*.5,-w*.335,z)],.018,M['silver'],root)
  for j in range(-3,4):tube(n+'_mullion',[(w*j/7,-w*.34,0),(w*j/7,-w*.34,h*(.80 if kind=='open' else .72 if kind=='step' else 1))],.018,M['silver'],root)
 return root
tower('SF_SPHERE_TOWER',742,594,279,44,'sphere')
tower('SF_OPEN_TOWER',920,570,212,49,'open')
tower('SF_STEP_TOWER',936,574,283,48,'step','silver')
tower('SF_TALLEST_TOWER',1036,561,108,57,'taper')
for j,(x,y,top,w,tone)in enumerate([(660,574,491,28,'glass'),(697,576,475,28,'glass'),(801,591,444,45,'cream'),(833,577,405,30,'silver'),(868,576,391,31,'glass'),(890,595,501,26,'cream'),(957,594,399,38,'glass'),(986,595,513,26,'cream'),(1078,569,448,32,'glass'),(1108,579,384,37,'glass'),(1145,574,460,25,'silver'),(1177,562,427,29,'glass'),(1220,555,415,37,'stone'),(1264,559,470,31,'glass'),(858,598,542,26,'glass'),(1015,593,542,25,'cream')]):tower('SF_HIGHRISE_'+str(j),x,y,top,w,'box',tone)
def building(n,px,py,widthpx,height,depth=2.0,dome=False):
 pos=uvpoint(px,py);w=pxwidth(pos,widthpx);root=empty(n,D,tuple(pos));box(n+'_body',(0,0,height/2),(w,depth,height),M['stone'],root)
 for z in [.12,height*.3,height*.6,height*.9,height]:box(n+'_cornice',(0,0,z),(w+.16,depth+.16,.11),M['cream'],root)
 for i in range(max(2,int(w/.45))):
  x=-w/2+.23+i*.45
  for j in range(max(2,int(height/.65))):
   z=.45+j*.65;box(n+'_window',(x,-depth/2-.012,z),(.19,.028,.32),M['roof'],root)
   box(n+'_pilaster',(x+.16,-depth/2-.06,z),(.055,.10,.5),M['cream'],root)
 if dome:
  lathe(n+'_dome',(0,0,height),[(0,w*.32),(.3,w*.32),(.55,w*.28),(.85,w*.16),(1.05,.04),(1.35,.025)],M['cream'],root)
 return root
building('SF_STONE_LEFT',400,771,157,4.5,2.5,True)
building('SF_STONE_LEFT_REAR',367,675,83,3.3,2.1,True)
building('SF_STONE_CENTER',737,840,160,4.8,3,True)
building('SF_STONE_FACADE',883,847,167,3.8,2.3,False)
building('SF_STONE_RIGHT',991,817,95,3.0,2,False)
def roof(n,pos,w,d,h,p=D,pavilion=False):
 root=empty(n,p,pos)
 if not pavilion:box(n+'_wall',(0,0,h/2),(w*.92,d*.88,h),M['stone'],root)
 else:
  for x in [-w*.35,w*.35]:
   for y in [-d*.3,d*.3]:lathe(n+'_column',(x,y,0),[(0,.09),(h,.09)],M['red'],root,12)
 # Upturned eave, raised ridge, actual double-slope surface.
 vs=[]
 for x in [-w/2,w/2]:
  for y,z in [(-d*.6,h+.15),(-d*.4,h),(0,h+.7),(d*.4,h),(d*.6,h+.15)]:vs.append((x,y,z))
 mesh(n+'_tiles',vs,[(j,j+1,j+6,j+5)for j in range(4)],M['roof'],root)
 for j in range(int(w/.12)+1):
  x=-w/2+j*.12;tube(n+'_tile_rib',[(x,-d*.6,h+.17),(x,-d*.4,h+.02),(x,0,h+.72),(x,d*.4,h+.02),(x,d*.6,h+.17)],.022,M['silver'],root)
 return root
for j,(x,y,w)in enumerate([(317,889,97),(348,838,95),(1517,744,100),(1589,749,90)]):roof('SF_HISTORIC_'+str(j),tuple(uvpoint(x,y)),pxwidth(uvpoint(x,y),w),2,2.3)
roof('SF_GARDEN_PAVILION',tuple(uvpoint(518,799)),3.1,2.5,2.1,pavilion=True)
for row in range(4):
 for j in range(7):
  x=850+j*43+row*16;y=711+row*22;pos=uvpoint(x,y)
  roof(f'SF_LOW_ROOFS_{row}_{j}',tuple(pos),1.25,1.5,1.0)
# Landscape along both waterfronts. Seed fixed for reproducibility.
rng=random.Random(218)
for j in range(105):
 curve=outer if j<45 else island;t=(j*.618)%1;pos=curve[int(t*len(curve))].copy();pos.z=1.3
 pos.x+=rng.uniform(-.2,.2);pos.y+=rng.uniform(-.2,.2)
 lathe('SF_TREE_TRUNK',pos,[(0,.05),(.5,.045)],M['bark'],D,8)
 sphere('SF_TREE_CROWN',pos+Vector((0,0,.72)),rng.uniform(.28,.48),M['green'])
for j,(px,py)in enumerate([(600,871),(753,861),(1658,773)]):
 pos=uvpoint(px,py);box('SF_SMALL_VEHICLE_'+str(j),(pos.x,pos.y,1.8),(1.4,.55,.65),M['blue'])
 for x in [-.45,.45]:
  for y in [-.32,.32]:sphere('SF_SMALL_TIRE',(pos.x+x,pos.y+y,1.46),.17,M['roof'])
# Actual replacement gantry: rear-bank legs and cantilevers to unchanged trolley.
# This is a feasibility study; do not count original hidden legs as support.
cn=s.objects['CN_FRAME'];cr=empty('SF_CN_CRANE',cn)
for x in [-2,3.5]:
 for y in [-12,-5]:
  box('SF_CRANE_LEG',(x,y,6.4),(.35,.4,10.9),M['white'],cr)
  box('SF_CRANE_BASE',(x,y,.96),(1.1,1.4,.4),M['blue'],cr)
 tube('SF_CRANE_BOOM',[(x,-13,11.9),(x,14,11.9)],.2,M['blue'],cr)
 tube('SF_CRANE_DIAGONAL',[(x,-12,2),(x,-5,11.9)],.12,M['blue'],cr)
for y in [-12,-5]:tube('SF_CRANE_CROSS',[(-2,y,11.9),(3.5,y,11.9)],.18,M['blue'],cr)
for x in [-2,3.5]:
 tube('SF_CRANE_PYLON',[(x,-8,11.9),(x,-8,15.2)],.15,M['blue'],cr)
 for y in [-12,4,14]:tube('SF_CRANE_TIE',[(x,-8,15.2),(x,y,11.9)],.045,M['white'],cr)
# Copy only visual data of authorized ship parts and static cargo; never shared mats.
ship=s.objects['A02_SHIP']
for o in list(s.objects):
 if o.name in ['SHIP_HULL','SHIP_DECK','SHIP_BRIDGE','SHIP_BRIDGE_GLASS'] or o.name.startswith('P03_'):
  if o.type!='MESH':continue
  o.data=o.data.copy();o.data.materials.clear();o.data.materials.append(M['navy'] if o.name=='SHIP_HULL' else M['glass'] if o.name=='SHIP_BRIDGE_GLASS' else M['blue'] if 'UPPER' in o.name and rng.random()<.65 else M['white'])
# Better ship silhouette, preserving the real deck z=.90 and all cargo support.
s.objects['SHIP_HULL'].hide_render=True;s.objects['SHIP_HULL'].hide_set(True)
for n,z0,z1,m in [('SF_HULL_BLUE',-.3,.78,M['blue']),('SF_HULL_RED',-.68,-.3,M['red'])]:
 outline=[(-7,-2.1),(-6.5,-2.6),(4.8,-2.6),(6.3,-1.8),(7.3,0),(6.3,1.8),(4.8,2.6),(-6.5,2.6),(-7,2.1)]
 pts=[Vector((x,y,0))for x,y in outline];wall(n,pts,z1,z0,m,ship)
disk('SF_BOW_DECK',[Vector((x,y,0))for x,y in [(-6.9,-2.4),(4.8,-2.5),(6.3,-1.7),(7.25,0),(6.3,1.7),(4.8,2.5),(-6.9,2.4)]],.90,M['white'],ship)
for i in range(4):
 z=3.15+i*.65;box('SF_BRIDGE_LEVEL_'+str(i),(-5.5,0,z),(1.7-i*.22,2.2-i*.24,.65),M['white'],ship)
 box('SF_BRIDGE_WINDOWS_'+str(i),(-5.5,1.12-i*.12,z+.1),(1.75-i*.22,.035,.22),M['navy'],ship)
lathe('SF_BRIDGE_MAST',(-5.5,0,5.7),[(0,.09),(1.3,.06)],M['white'],ship,12)
brand=text('SF_HULL_PNPLINE','PNPLINE',(0,2.64,.02),.58,4.8,M['white'],ship,depth=.008,bevel=.002)
brand.rotation_euler=Matrix(((-1,0,0),(0,0,1),(0,1,0))).to_euler()
for o in list(s.objects):
 if o.name.startswith('P03_') and o.type=='MESH':
  for j in range(15):
   x=o.location.x-1.5+j*.21;y=o.location.y+.735;z=o.location.z
   box('SF_CARGO_CORRUGATION',(x,y,z),(.035,.035,1.35),o.data.materials[0],ship)
# Regional wave ribbons sit on the existing spherical ocean and avoid the route.
for j in range(32):
 cx=rng.uniform(-50,45);cy=rng.choice([-1,1])*rng.uniform(9,48);pts=[]
 for k in range(65):
  a=k/64*math.pi*1.8;rad=2.4+1.4*k/64;x=cx+math.cos(a)*rad*1.7;y=cy+math.sin(a)*rad
  if x*x+y*y<120**2:pts.append((x,y,seal_to_ocean(x,y)+.1))
 tube('SF_OCEAN_WAVE',pts,.065,M['wave'])
# Ocean gets a copied material with a CN-local tint mask; mesh/radius stay intact.
ocean=s.objects['EARTH_CONTINUOUS_OCEAN'];ocean.data=ocean.data.copy();oldm=ocean.data.materials[0];watermat=oldm.copy();watermat.name='SF_REGIONAL_OCEAN';ocean.data.materials[0]=watermat
watermat.use_nodes=True;bs=watermat.node_tree.nodes.get('Principled BSDF')
if bs:
 oldcolor=tuple(bs.inputs['Base Color'].default_value);nt=watermat.node_tree
 geo=nt.nodes.new('ShaderNodeTexCoord');geo.object=D
 length=nt.nodes.new('ShaderNodeVectorMath');length.operation='LENGTH';nt.links.new(geo.outputs['Object'],length.inputs[0])
 ramp=nt.nodes.new('ShaderNodeMapRange');ramp.inputs['From Min'].default_value=45;ramp.inputs['From Max'].default_value=65;ramp.inputs['To Min'].default_value=1;ramp.inputs['To Max'].default_value=0;nt.links.new(length.outputs['Value'],ramp.inputs['Value'])
 mix=nt.nodes.new('ShaderNodeMixRGB');mix.inputs[1].default_value=oldcolor;mix.inputs[2].default_value=(.006,.16,.22,1);nt.links.new(ramp.outputs['Result'],mix.inputs[0]);nt.links.new(mix.outputs[0],bs.inputs['Base Color']);bs.inputs['Roughness'].default_value=.25
# Local comparison lighting; original material datablocks untouched.
ld=bpy.data.lights.new('SF_COMPARISON_KEY','AREA');lo=bpy.data.objects.new('SF_COMPARISON_KEY',ld);col.objects.link(lo);lo.parent=D;lo.location=(-30,-10,60);ld.energy=80000;ld.shape='DISK';ld.size=35;lo.rotation_euler=(Vector((0,10,0))-lo.location).to_track_quat('-Z','Y').to_euler();tag(lo)
s.world=s.world.copy();s.world.use_nodes=True;s.world.node_tree.nodes.get('Background').inputs[0].default_value=(.22,.35,.43,1);s.world.node_tree.nodes.get('Background').inputs[1].default_value=.5
s.render.engine='BLENDER_EEVEE';s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.view_settings.view_transform='AgX';s.frame_set(156)
for screen in bpy.data.screens:
 for ar in screen.areas:
  if ar.type=='VIEW_3D':ar.spaces.active.region_3d.view_perspective='CAMERA';ar.spaces.active.shading.type='MATERIAL'
new=[o.name for o in col.objects]
data={'status':'layout/design feasibility proposal; not final accepted master','camera':cfg,'hidden_original_visuals':hidden,'new_objects':new,'count':len(new),'font_source':str(font_path),'font_redistributed':False,'assumptions':['hidden building rear faces simplified','closed internal basin depth not measured','regional waves static on existing spherical ocean'],'known_unverified':['S1 ground at old pick point','new crane feet support and silhouette','new camera collisions/velocity','hull side clearance','sphere horizon differs from target flat sea'],'renderer':'EEVEE/AgX, local area light; comparison only'}
(R/'review/layout-proposal-build.json').write_text(json.dumps(data,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(OUT));print('LAYOUT_OBJECTS',len(new))
