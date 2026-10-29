"""Deterministic editable geometry; --output PATH [--reference-scale]. Never overwrites."""
import bpy,sys,json,math,random,argparse
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from safety import guard
p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--reference-scale',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
cfg=json.loads((R/'scene-config.json').read_text());out=guard(R,a.output,R/'inputs/base.blend',cfg['base_sha256'])
if Path(bpy.data.filepath).resolve()!=(R/'inputs/base.blend').resolve():raise ValueError('Build only from immutable base')
if any(o.get('uc_owner')==cfg['owner'] for o in bpy.data.objects):raise ValueError('Duplicate owned scene: regenerate from base')
s=bpy.context.scene;s.frame_set(510);U=s.objects['US_FRAME']
random.seed(cfg['seed']);owner=cfg['owner']
top=bpy.data.collections.new('US_CITY_CONCEPT_V001');s.collection.children.link(top)
cols={}
for name in ['USA_LETTERS','USA_STARS','LIBERTY','SKYLINE','URBAN_BLOCKS','CIVIC_AND_BRIDGE','HARBOR_DRESSING','SITE_AND_LANDSCAPE']:
 c=bpy.data.collections.new(name);top.children.link(c);cols[name]=c
def material(name,color,metal=0,rough=.45):
 m=bpy.data.materials.new('UC_'+name);m.diffuse_color=(*color,1);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough
 return m
navy=material('NAVY',(.009,.047,.105),.35);silver=material('SILVER',(.77,.83,.85),.65);stone=material('LIMESTONE',(.66,.61,.49));cream=material('IVORY',(.83,.81,.71));glass=material('GLASS',(.075,.18,.23),.55);dark=material('WINDOWS',(.035,.07,.09),.35);blue=material('HARBOR_BLUE',(.015,.42,.63),.4);patina=material('VERDIGRIS',(.10,.38,.31),.45);patina_light=material('PATINA_EDGE',(.18,.48,.39),.35);red=material('BRIDGE_RED',(.57,.075,.035),.45);road=material('ASPHALT',(.085,.11,.12));green=material('LAWN',(.16,.27,.10));leaf=material('TREES',(.09,.23,.08));gold=material('TORCH_GOLD',(.92,.50,.035),.6);yellow=material('TAXI',(.96,.60,.035));white=material('WHITE',(.85,.88,.87));teal=material('CONTAINER_TEAL',(.04,.34,.36));bark=material('BARK',(.20,.13,.075));brick=material('BRICK',(.35,.25,.20))
def own(o,col,parent=U):
 cols[col].objects.link(o);o.parent=parent;o['uc_owner']=owner;o['uc_zone']=col;return o
def empty(name,col,parent=U):
 return own(bpy.data.objects.new(name,None),col,parent)
city=empty('UC_CITY_DISTRICT','SKYLINE');city.location=cfg['city_translation'];city.rotation_euler.z=math.radians(cfg['city_yaw_degrees'])
def mesh(name,verts,faces,mat,col,parent=U,bevel=0):
 d=bpy.data.meshes.new(name+'_MESH');d.from_pydata(verts,[],faces);d.materials.append(mat);d.update()
 o=own(bpy.data.objects.new(name,d),col,parent)
 if bevel:
  mod=o.modifiers.new('Edge craftsmanship','BEVEL');mod.width=bevel;mod.segments=2
 return o
def box(name,c,d,mat,col,parent=U,bevel=.025):
 x,y,z=c;w,l,h=[v/2 for v in d]
 vs=[(x+i*w,y+j*l,z+k*h) for i,j,k in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
 return mesh(name,vs,[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)],mat,col,parent,bevel)
def cylinder(name,c,r,h,mat,col,parent=U,r2=None,n=20):
 r2=r if r2 is None else r2;x,y,z=c
 v=[(x+rr*math.cos(t*2*math.pi/n),y+rr*math.sin(t*2*math.pi/n),z+zz) for rr,zz in [(r,-h/2),(r2,h/2)] for t in range(n)]
 return mesh(name,v,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],mat,col,parent)
def beam(name,start,end,width,mat,col,parent=U):
 st=Vector(start);en=Vector(end);v=en-st
 o=box(name,(0,0,0),(width,width,v.length),mat,col,parent,0)
 o.location=(st+en)/2;o.rotation_euler=v.to_track_quat('Z','Y').to_euler();return o
def sphere(name,c,scale,mat,col,parent=U,n=20,rings=12):
 vs=[]
 for j in range(rings+1):
  t=math.pi*j/rings
  for i in range(n):
   q=2*math.pi*i/n;vs.append((c[0]+scale[0]*math.sin(t)*math.cos(q),c[1]+scale[1]*math.sin(t)*math.sin(q),c[2]+scale[2]*math.cos(t)))
 fs=[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(rings) for i in range(n)]
 o=mesh(name,vs,fs,mat,col,parent)
 for f in o.data.polygons:f.use_smooth=True
 return o
def line(name,points,r,mat,col,parent=U):
 d=bpy.data.curves.new(name+'_CURVE','CURVE');d.dimensions='3D';d.bevel_depth=r;d.bevel_resolution=2
 sp=d.splines.new('POLY');sp.points.add(len(points)-1)
 for p,co in zip(sp.points,points):p.co=(*co,1)
 d.materials.append(mat);return own(bpy.data.objects.new(name,d),col,parent)
def batch_boxes(name,items,mat,col,parent=city):
 vs=[];fs=[]
 for (x,y,z),(w,l,h) in items:
  off=len(vs);w/=2;l/=2;h/=2
  vs.extend([(x+i*w,y+j*l,z+k*h) for i,j,k in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]])
  fs.extend([tuple(off+i for i in f) for f in [(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]])
 return mesh(name,vs,fs,mat,col,parent)
for name in cfg['hidden_proxies']:
 s.objects[name].hide_render=True;s.objects[name].hide_viewport=True

# D01: separate mesh letters, inset navy faces and broad silver perimeter.
font=bpy.data.fonts.load(cfg['font_path'])
for idx,ch in enumerate('USA'):
 pieces=[]
 for tone,offset,depth,front,mat in [('RIM',.033,.055,0,silver),('FACE',0,.018,-.08,navy)]:
  d=bpy.data.curves.new('UC_TEXT_'+ch+'_'+tone,'FONT');d.body=ch;d.font=font;d.size=1;d.extrude=depth;d.bevel_depth=.009;d.bevel_resolution=3;d.resolution_u=18;d.offset=offset
  ob=own(bpy.data.objects.new('UC_'+ch+'_'+tone,d),'USA_LETTERS',city);d.materials.append(mat)
  bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.convert(target='MESH');ob=bpy.context.object
  if tone=='RIM':
   ymin=min(v.co.y for v in ob.data.vertices);ymax=max(v.co.y for v in ob.data.vertices);vertical_scale=27/(ymax-ymin);baseline=1-ymin*vertical_scale
  ob.rotation_euler.x=math.pi/2;ob.scale=(23,vertical_scale,23);ob.location=(-24+idx*15.0,53+front*23,baseline)
  bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);ob.select_set(False);pieces.append(ob)
 bpy.ops.object.select_all(action='DESELECT')
 for ob in pieces:ob.select_set(True)
 bpy.context.view_layer.objects.active=pieces[0];bpy.ops.object.join();ob=bpy.context.object;ob.name='UC_LETTER_'+ch;ob['uc_role']='letter';ob['font_note']='Arial Black approximation; expanded silver contour, inset navy front, converted mesh. No font redistributed.';ob.select_set(False)
bpy.data.fonts.remove(font)

# D02: ten individually modeled stars, distributed five on each side.
for side,entries in [('L',[(-28,15,1.7),(-31,11,1.1),(-27,9,0.85),(-33,7,1.0),(-24.5,10,.65)]),('R',[(25.5,15,1.7),(29,12,1.1),(25.5,9.8,1),(31,8.7,.8),(28,7,.65)])]:
 for j,(x,z,r) in enumerate(entries):
  pts=[(x+(r if i%2==0 else r*.43)*math.sin(i*math.pi/5),z+(r if i%2==0 else r*.43)*math.cos(i*math.pi/5)) for i in range(10)]
  vs=[(px,50+y,pz) for y in [-.28,.28] for px,pz in pts]+[(x,49.60,z),(x,50.28,z)]
  fs=[(20,i,(i+1)%10) for i in range(10)]+[(21,10+(i+1)%10,10+i) for i in range(10)]+[(i,10+i,10+(i+1)%10,(i+1)%10) for i in range(10)]
  ob=mesh(f'UC_STAR_{side}_{j+1}',vs,fs,silver,'USA_STARS',city,.035);ob['uc_role']='star'

# D03: tapered, folded robe, face, seven rays, tablet and raised torch.
lib=empty('UC_LIBERTY','LIBERTY');lib.location=cfg['liberty_position'];lib.rotation_euler.z=math.radians(cfg['liberty_yaw_degrees'])
ref=cfg['liberty_reference_body_height'];mult=1 if a.reference_scale else cfg['liberty_body_scale'];lib['reference_body_height']=ref;lib['selected_body_height']=ref*mult;lib['body_scale']=mult
cylinder('UC_LIBERTY_ISLAND',(0,0,-.75),3.2,1.8,stone,'LIBERTY',lib,n=10)
cylinder('UC_LIBERTY_ISLAND_CAP',(0,0,.22),3.35,.18,cream,'LIBERTY',lib,n=10)
cylinder('UC_LIBERTY_GARDEN',(0,0,.36),2.7,.1,green,'LIBERTY',lib,n=10)
box('UC_LIBERTY_PEDESTAL',(0,0,1.45),(2.5,2.5,2.1),stone,'LIBERTY',lib,.07)
for z,d in [(.55,3.0),(.8,2.7),(2.25,2.65),(2.55,2.8)]:box('UC_LIBERTY_CORNICE',(0,0,z),(d,d,.18),cream,'LIBERTY',lib)
for i in range(6):
 for y in [-1.27,1.27]:box('UC_LIBERTY_PEDESTAL_RECESS',(-.95+i*.38,y,1.65),(.19,.04,.62),dark,'LIBERTY',lib,0)
body=empty('UC_LIBERTY_BODY','LIBERTY',lib);body.location.z=2.65;body.scale=(ref*mult/8.5,)*3
vs=[];n=64
for j,(z,rx,ry,cx) in enumerate([(0,.78,.57,0),(.2,.79,.58,0),(1,.64,.52,.05),(2.2,.48,.45,.1),(3.1,.56,.42,0),(4.1,.66,.39,-.03),(4.8,.73,.38,0),(5.05,.45,.32,0)]):
 for i in range(n):
  t=i*2*math.pi/n;fold=1+.085*math.cos(t*12+j*.35)+.035*math.sin(t*21)
  vs.append((cx+rx*math.cos(t)*fold,ry*math.sin(t)*fold,z))
fs=[tuple(reversed(range(n))),tuple(range(7*n,8*n))]+[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(7) for i in range(n)]
mesh('UC_LIBERTY_ROBE',vs,fs,patina,'LIBERTY',body)
for i in range(13):
 t=math.pi+math.pi*i/12
 line('UC_LIBERTY_DRAPE',[(math.cos(t)*(.76-.08*j)+.05*j,math.sin(t)*(.59-.035*j)-.02,j*.7) for j in range(7)],.025,patina_light,'LIBERTY',body)
for j in range(5):line('UC_LIBERTY_SASH',[(-.57,-.40,4.6-j*.18),(-.1,-.47,3.85-j*.18),(.49,-.34,3.35-j*.18)],.045,patina_light,'LIBERTY',body)
cylinder('UC_LIBERTY_NECK',(0,0,5.15),.2,.43,patina,'LIBERTY',body)
sphere('UC_LIBERTY_HEAD',(0,-.02,5.65),(.35,.30,.50),patina,'LIBERTY',body)
box('UC_LIBERTY_NOSE',(0,-.315,5.65),(.09,.16,.21),patina_light,'LIBERTY',body)
for x in [-.14,.14]:line('UC_LIBERTY_BROW',[(x-.07,-.29,5.83),(x+.07,-.30,5.82)],.026,patina_light,'LIBERTY',body)
line('UC_LIBERTY_MOUTH',[(-.09,-.30,5.47),(.09,-.30,5.47)],.017,patina_light,'LIBERTY',body)
sphere('UC_LIBERTY_HAIR',(0,.09,5.75),(.38,.32,.43),patina,'LIBERTY',body)
cylinder('UC_LIBERTY_CROWN',(0,0,5.94),.39,.14,patina_light,'LIBERTY',body)
for i in range(7):
 angle=math.pi*i/6;start=(.33*math.cos(angle),-.07,5.96+.13*math.sin(angle));end=(.92*math.cos(angle),-.07,5.97+.85*math.sin(angle))
 beam('UC_LIBERTY_CROWN_RAY',start,end,.055,patina_light,'LIBERTY',body)
beam('UC_LIBERTY_RAISED_ARM',(-.56,0,4.78),(-.98,-.02,6.2),.35,patina,'LIBERTY',body)
beam('UC_LIBERTY_FOREARM',(-.98,-.02,6.2),(-1.14,-.04,7.34),.23,patina,'LIBERTY',body)
sphere('UC_LIBERTY_HAND',(-1.14,-.04,7.31),(.17,.15,.23),patina,'LIBERTY',body)
cylinder('UC_LIBERTY_TORCH',(-1.14,-.04,7.65),.09,.65,gold,'LIBERTY',body)
cylinder('UC_LIBERTY_TORCH_BOWL',(-1.14,-.04,7.95),.16,.24,gold,'LIBERTY',body,r2=.30)
sphere('UC_LIBERTY_FLAME',(-1.14,-.04,8.22),(.17,.15,.28),gold,'LIBERTY',body)
beam('UC_LIBERTY_LEFT_ARM',(.56,0,4.7),(.82,-.25,3.8),.36,patina,'LIBERTY',body)
beam('UC_LIBERTY_LEFT_FOREARM',(.82,-.25,3.8),(.48,-.60,4.18),.26,patina,'LIBERTY',body)
tablet=box('UC_LIBERTY_TABLET',(.57,-.52,4.13),(.70,.18,1.1),patina_light,'LIBERTY',body);tablet.rotation_euler.y=-.15
for j in range(3):box('UC_LIBERTY_TABLET_INSCRIPTION',(.56,-.63,4.35-j*.13),(.39,.018,.025),patina,'LIBERTY',body,0)

# D04/D06: narrow street grid and distinct dense facade modules.
def building(name,x,y,w,d,h,mat,style='stone'):
 col='SKYLINE' if h>7 else 'URBAN_BLOCKS';z=.7
 box(name,(x,y,z+h/2),(w,d,h),mat,col,city,.05)
 windows=[];trim=[]
 floors=max(2,int(h/.58));nx=max(2,int(w/.55));ny=max(2,int(d/.55))
 for j in range(floors):
  zz=z+.43+j*(h-.65)/floors
  if style=='glass':trim.extend([((x,y-d/2-.015,zz),(w,.035,.035)),((x-w/2-.015,y,zz),(.035,d,.035))])
  for i in range(nx):
   xx=x-w*.40+i*w*.8/max(1,nx-1)
   for yy in [y-d/2-.018,y+d/2+.018]:windows.append(((xx,yy,zz),(.23,.035,.32)))
  for i in range(ny):
   yy=y-d*.40+i*d*.8/max(1,ny-1)
   for xx in [x-w/2-.018,x+w/2+.018]:windows.append(((xx,yy,zz),(.035,.23,.32)))
 batch_boxes(name+'_WINDOWS',windows,dark if style=='stone' else silver,col)
 if trim:batch_boxes(name+'_MULLIONS',trim,silver,col)
 for zz in [z+.15,z+h-.12]:box(name+'_CORNICE',(x,y,zz),(w+.14,d+.14,.14),cream if style=='stone' else silver,col,city)
 box(name+'_ROOF',(x,y,z+h+.07),(w*.87,d*.87,.15),road,col,city)
 box(name+'_ROOFTOP',(x+w*.17,y+d*.12,z+h+.32),(w*.28,d*.25,.45),mat,col,city)
 return h
for y in [24,33,41.5,49]:box('UC_CITY_STREET',(0,y,.71),(52,1.5,.06),road,'SITE_AND_LANDSCAPE',city,0)
for x in [-18.8,-8.5,4.5,17.8]:box('UC_CITY_AVENUE',(x,37,.72),(1.7,27,.06),road,'SITE_AND_LANDSCAPE',city,0)
for row,y in enumerate([27,30.7,36.3,39.4,45.1,48]):
 for i,x in enumerate([-24,-20.8,-16,-12.4,-5.4,-1.7,2,8,11.8,15.2,21]):
  if (abs(x+5)<3.5 and 34<y<40) or (abs(x-10)<3.5 and y>41):continue
  h=random.uniform(2.7,5.8) if row<2 else random.uniform(5.4,12.8)
  if row>=4:h+=1.5
  building(f'UC_BLOCK_{row:02}_{i:02}',x,y,random.uniform(2.1,2.8),2.6,h,random.choice([stone,cream,brick]) if row<2 else random.choice([glass,stone,cream]),'stone' if row<2 or i%3==0 else 'glass')
# Central stepped limestone tower, vertical ribs and spire.
for i,(z,w,d,h) in enumerate([(.7,5,4.7,2.4),(3.1,3.8,3.4,3.0),(6.1,2.9,2.6,8.2),(14.3,2.2,2,1.8),(16.1,1.6,1.5,1.1),(17.2,.8,.8,1.5)]):
 box('UC_CENTRAL_TOWER_TIER',(-5,37,z+h/2),(w,d,h),cream,'SKYLINE',city,.06)
 for j in range(max(3,int(w/.26))):
  x=-5-w*.43+j*w*.86/max(2,int(w/.26)-1)
  box('UC_CENTRAL_TOWER_RIB',(x,37-d/2-.025,z+h/2),(.07,.06,h-.1),stone,'SKYLINE',city,0)
 for zz in range(int(h/.45)):
  box('UC_CENTRAL_TOWER_FLOOR',(-5,37-d/2-.03,z+.2+zz*.45),(w*.9,.02,.045),dark,'SKYLINE',city,0)
cylinder('UC_CENTRAL_SPIRE',(-5,37,20.2),.10,3,cream,'SKYLINE',city,r2=.035)
# Right tapering glass tower with triangulated silhouette.
levels=[(.7,2.5),(2,2.4),(18,1.65),(21,1.0)];vs=[]
for z,r in levels:
 for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]:vs.append((10+x*r,44+y*r,z))
mesh('UC_GLASS_SPIRE_TOWER',vs,[(0,3,2,1),(12,13,14,15)]+[(j*4+i,j*4+(i+1)%4,(j+1)*4+(i+1)%4,(j+1)*4+i) for j in range(3) for i in range(4)],glass,'SKYLINE',city)
for z in [1+i*.42 for i in range(48)]:
 r=2.45-(z-.7)*.067
 line('UC_GLASS_SPIRE_FLOOR',[(10-r,44-r,z),(10+r,44-r,z),(10+r,44+r,z),(10-r,44+r,z),(10-r,44-r,z)],.018,silver,'SKYLINE',city)
for side in [-1,1]:
 for i in range(9):
  t=-1+i*.25;line('UC_GLASS_SPIRE_MULLION',[(10+t*2.5,44+side*2.5,.7),(10+t,44+side,21)],.025,silver,'SKYLINE',city)
cylinder('UC_GLASS_SPIRE_ANTENNA',(10,44,23),.065,4,silver,'SKYLINE',city,r2=.015)

# D05: domed civic group with wings and planted forecourt.
col='CIVIC_AND_BRIDGE'
box('UC_CIVIC_PLAZA',(29,41,.76),(13.6,15,.16),cream,col,city)
box('UC_CIVIC_LAWN',(29,36,.88),(12,5,.12),green,col,city)
for x,w in [(23.7,3.8),(29,5.8),(34.3,3.8)]:
 box('UC_CIVIC_WING',(x,43,2.8),(w,5,4),cream,col,city)
 box('UC_CIVIC_ENTABLATURE',(x,42.8,4.95),(w+.35,5.3,.3),white,col,city)
 for i in range(int(w/.6)):
  xx=x-w/2+.35+i*.6
  cylinder('UC_CIVIC_COLUMN',(xx,40.15,2.9),.14,3.4,white,col,city)
  box('UC_CIVIC_RECESS',(xx,40.45,2.9),(.33,.06,2.6),dark,col,city,0)
cylinder('UC_CIVIC_DRUM',(29,43,5.5),2.1,1.1,cream,col,city,n=48)
sphere('UC_CIVIC_DOME',(29,43,6.05),(2.0,2.0,2.35),white,col,city,n=48,rings=20)
for i in range(24):
 t=2*math.pi*i/24
 line('UC_CIVIC_DOME_RIB',[(29+2.03*math.sin(q)*math.cos(t),43+2.03*math.sin(q)*math.sin(t),6.05+2.38*math.cos(q)) for q in [j*math.pi/2/15 for j in range(16)]],.035,stone,col,city)
cylinder('UC_CIVIC_LANTERN',(29,43,8.55),.38,.7,cream,col,city)
sphere('UC_CIVIC_FINIAL',(29,43,9.1),(.17,.17,.34),dark,col,city)
for j in range(8):box('UC_CIVIC_STEP',(29,38.8-j*.25,.9+j*.075),(5.4,.35,.15),white,col,city,0)

# Suspension bridge follows the right shoreline, away from the arrival route.
box('UC_BRIDGE_DECK',(28,0,1.4),(16,2,.28),road,col)
for x in [22,34]:
 for y in [-.9,.9]:
  box('UC_BRIDGE_TOWER',(x,y,4.2),(.45,.45,6.2),red,col)
  bottom=math.sqrt(140**2-(abs(x)+.7)**2-(abs(y)+.7)**2)-140-.35
  cylinder('UC_BRIDGE_PIER',(x,y,(bottom+1.2)/2),.7,1.2-bottom,stone,col)
 for z in [2.4,5.4,7.1]:beam('UC_BRIDGE_CROSSBEAM',(x,-1,z),(x,1,z),.28,red,col)
for y in [-1,1]:
 points=[]
 for i in range(49):
  x=20+i/3
  z=2.2+4.8*((x-28)/6)**2 if 22<=x<=34 else 7.0-2.4*min(abs(x-22),abs(x-34))
  points.append((x,y,z))
  if i%2==0 and 22<=x<=34:beam('UC_BRIDGE_HANGER',(x,y,1.6),(x,y,z),.035,red,col)
 line('UC_BRIDGE_MAIN_CABLE',points,.055,red,col)
 line('UC_BRIDGE_RAIL',[(20,y,1.85),(36,y,1.85)],.04,red,col)
# Shore links use solid tapered foundations down to the existing sphere.
for x in [20,36]:
 bottom=math.sqrt(140**2-(x+1.1)**2-4.3**2)-140-.35
 box('UC_BRIDGE_ABUTMENT',(x,1.8,(bottom+1.4)/2),(2.2,5,1.4-bottom),stone,col)

# D06/07: retain real functional warehouse, add only rear facade rhythm.
for x in range(37,68,2):box('UC_WAREHOUSE_REAR_PILASTER',(x,39.2,4.3),(.12,.13,4.8),silver,'HARBOR_DRESSING')
for x in [39,45,51,57,63]:box('UC_WAREHOUSE_REAR_PANEL',(x,39.25,5.5),(4.8,.08,.8),blue,'HARBOR_DRESSING')
for x in range(-23,20,4):
 for y in [15.3,17.2]:
  if -4<x<6 or (y<16 and -12<x<4):continue
  for z in [.7,1.5]:
   box('UC_CONTAINER',(x,y,z+.4),(3.2,1.4,.8),random.choice([teal,blue,white]),'HARBOR_DRESSING')
   for j in range(13):box('UC_CONTAINER_RIB',(x-1.45+j*.24,y-.72,z+.4),(.035,.04,.70),silver,'HARBOR_DRESSING',bevel=0)
# A static decorative gantry cluster is kept behind the working berth.
for x in [-16,-24]:
 for dx in [-1.5,1.5]:
  for y in [9,13]:box('UC_STATIC_CRANE_LEG',(x+dx,y,4.8),(.30,.30,8.0),white,'HARBOR_DRESSING')
  beam('UC_STATIC_CRANE_BOOM',(x+dx,5,8.8),(x+dx,16,8.8),.28,blue,'HARBOR_DRESSING')
  beam('UC_STATIC_CRANE_STAY',(x+dx,10.5,11),(x+dx,5,8.8),.10,blue,'HARBOR_DRESSING')
  beam('UC_STATIC_CRANE_STAY',(x+dx,10.5,11),(x+dx,16,8.8),.10,blue,'HARBOR_DRESSING')
 beam('UC_STATIC_CRANE_TOP',(x-1.5,10.5,11),(x+1.5,10.5,11),.22,blue,'HARBOR_DRESSING')
 box('UC_STATIC_CRANE_CAB',(x,12,8.5),(1.4,1.2,1),blue,'HARBOR_DRESSING')
# Railway runs behind the functional quay road, never across the truck route.
for y in [22.1,22.7]:line('UC_RAIL',[(-26,y,.8),(15,y,.8)],.035,silver,'HARBOR_DRESSING')
for x in range(-26,16):box('UC_RAIL_SLEEPER',(x,22.4,.76),(.12,1.1,.08),bark,'HARBOR_DRESSING',bevel=0)
for x in [-18,-13,-8]:
 box('UC_RAIL_WAGON',(x,22.4,1.05),(4,1.1,.3),dark,'HARBOR_DRESSING')
 box('UC_RAIL_LOAD',(x,22.4,1.7),(3.6,.95,1),teal,'HARBOR_DRESSING')
for x,y in [(-12,24),(7,24),(19,33),(-18.7,37)]:
 box('UC_TAXI',(x,y,1.1),(1.45,.65,.55),yellow,'URBAN_BLOCKS',city,.07)
 box('UC_TAXI_GLASS',(x,y,1.45),(.75,.58,.3),dark,'URBAN_BLOCKS',city,.04)
for x,y in [(24,35),(34,35),(24,38),(34,38),(-26,31),(-26,39),(19,47),(34,47)]:
 cylinder('UC_TREE_TRUNK',(x,y,1.3),.08,1.3,bark,'SITE_AND_LANDSCAPE',city)
 sphere('UC_TREE_CROWN',(x,y,2.25),(.70,.65,1.0),leaf,'SITE_AND_LANDSCAPE',city,n=12,rings=8)
for x,y in [(37,5),(39,7),(40,3)]:
 sphere('UC_SHORE_HILL',(x,y,-4.0),(3,3,5.2),green,'SITE_AND_LANDSCAPE')
 cylinder('UC_SHORE_TREE_TRUNK',(x,y,1.6),.10,2,bark,'SITE_AND_LANDSCAPE')
 for i in range(7):
  t=i*math.pi*2/7;line('UC_PALM_FROND',[(x,y,2.7),(x+math.cos(t)*.8,y+math.sin(t)*.8,3.1),(x+math.cos(t)*1.6,y+math.sin(t)*1.6,2.6)],.09,leaf,'SITE_AND_LANDSCAPE')

bpy.context.view_layer.update()
owned=[o for o in s.objects if o.get('uc_owner')==owner]
object_map={o.name:{'zone':o['uc_zone'],'type':o.type,'parent':o.parent.name if o.parent else None,'role':o.get('uc_role'),'data':o.data.name if o.data else None} for o in owned}
out.parent.mkdir(parents=True,exist_ok=True)
s.frame_set(390)
bpy.ops.wm.save_as_mainfile(filepath=str(out),check_existing=True)
(out.parent/(out.stem+'-object-map.json')).write_text(json.dumps(object_map,indent=2))
print('BUILT',str(out),'OWNED',len(owned),'BODY_HEIGHT',ref*mult)
