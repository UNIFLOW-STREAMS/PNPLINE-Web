"""Beijing and Guangzhou districts around the preserved integrated China city."""
import bpy,bmesh,math,json,hashlib,random,sys
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import citykit,beijing,guangzhou
SOURCE=ROOT.parent/'cn-us-integrated-v001/pnpline-cn-us-integrated-v001.blend'
OUT=ROOT/'pnpline-cn-city-expansion-v001.blend'
SHA='1aee6c14eb4140614ffa650141eed3ada783c416397fbb938a5105a8df70a7d8'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.context.scene;s.frame_set(0)
D=s.objects['SF_CN_LAYOUT'];I=D.matrix_world.inverted();old_names=set(s.objects.keys())
col=bpy.data.collections.new('CNX_BEIJING_GUANGZHOU');s.collection.children.link(col)
random.seed(773)
palette={'stone':(.58,.57,.51),'ivory':(.82,.80,.69),'red':(.55,.075,.045),'gold':(.9,.52,.09),
 'roof':(.09,.13,.15),'blue_roof':(.025,.24,.38),'glass':(.12,.29,.36),'dark_glass':(.045,.12,.17),
 'metal':(.59,.68,.70),'white':(.88,.88,.81),'dark':(.025,.04,.045),'wood':(.27,.14,.075),
 'green':(.17,.31,.12),'water':(.06,.24,.28),'road':(.22,.25,.24),'paving':(.64,.64,.58)}
M={}
for name,color in palette.items():
 m=bpy.data.materials.new('CNX_'+name);m.diffuse_color=(*color,1);m.use_nodes=True
 bsdf=m.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=(*color,1);bsdf.inputs['Roughness'].default_value=.58
 if name in ['glass','metal','gold','dark_glass']:bsdf.inputs['Metallic'].default_value=.25
 M[name]=m
ocean=s.objects['EARTH_CONTINUOUS_OCEAN'];T=I@ocean.matrix_world
water=BVHTree.FromPolygons([T@v.co for v in ocean.data.vertices],[tuple(p.vertices)for p in ocean.data.polygons])
INNER=[(-28,-10),(-28,3),(-33,14),(-29,23),(-20,29),(-2,32),(14,31),(20,28),(22,20),(23,6),(30,3)]
OUTER=[(-28,-10),(-58,-10),(-65,5),(-64,35),(-62,65),(-40,73),(-26,72),(8,71),(40,64),(60,48),(64,22),(60,3),(30,3)]
POLY=OUTER+list(reversed(INNER))[1:-1]

def ease(t):
 t=min(1,max(0,t));return t*t*t*(10+t*(-15+6*t))
def segdist(p,a,b):
 p,a,b=Vector(p),Vector(a),Vector(b);d=b-a;t=min(1,max(0,(p-a).dot(d)/d.length_squared));return (p-a-d*t).length
def wat(x,y):
 p=water.ray_cast(Vector((x,y,100)),Vector((0,0,-1)))[0]
 assert p is not None,(x,y)
 return p.z
def height(x,y):
 z=wat(x,y)+.90;distance=min(segdist((x,y),a,b)for a,b in zip(INNER,INNER[1:]))
 # A gently graded shelf joins the existing flat coast to the globe surface.
 w=1-ease(distance/18)
 return z+(1.22-z)*w
def point(x,y,z=0):return Vector((x,y,height(x,y)+z))
def normal(x,y):
 d=.12;dx=(height(x+d,y)-height(x-d,y))/(2*d);dy=(height(x,y+d)-height(x,y-d))/(2*d)
 return Vector((-dx,-dy,1)).normalized()
def inside(x,y):
 hit=False
 for a,b in zip(POLY,POLY[1:]+POLY[:1]):
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:hit=not hit
 return hit
def mesh(name,v,f,mat,parent=D):
 me=bpy.data.meshes.new(name+'_Mesh');me.from_pydata(v,[],f);me.materials.append(M[mat]);me.update()
 obj=bpy.data.objects.new(name,me);col.objects.link(obj);obj.parent=parent;obj['cnx_owner']='cn-city-expansion-v001';return obj
def frame(name,x,y,yaw=0,z=.12):
 obj=bpy.data.objects.new(name,None);col.objects.link(obj);obj.parent=D
 obj.matrix_basis=Matrix.Translation(point(x,y,z))@Vector((0,0,1)).rotation_difference(normal(x,y)).to_matrix().to_4x4()@Matrix.Rotation(yaw,4,'Z')
 obj['cnx_owner']='cn-city-expansion-v001';obj['cnx_anchor']=[x,y,z];return obj

# Tessellated closed crescent: no overlays across the old river/city core.
bm=bmesh.new();vs=[bm.verts.new((x,y,0))for x,y in POLY];bm.faces.new(vs);bmesh.ops.triangulate(bm,faces=list(bm.faces))
for j in range(9):
 es=[e for e in bm.edges if e.calc_length()>1.4]
 if not es:break
 bmesh.ops.subdivide_edges(bm,edges=es,cuts=1,use_grid_fill=True)
bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.verts.ensure_lookup_table();bm.verts.index_update()
xy=[(v.co.x,v.co.y)for v in bm.verts];faces=[tuple(v.index for v in f.verts)for f in bm.faces]
edge=[tuple(v.index for v in e.verts)for e in bm.edges if e.is_boundary];bm.free();n=len(xy)
top=[point(x,y)for x,y in xy];bottom=[Vector((x,y,wat(x,y)-.45))for x,y in xy]
terrain=mesh('CNX_CURVED_DISTRICT_LAND',top+bottom,faces+[tuple(n+i for i in reversed(f))for f in faces]+[(a,b,n+b,n+a)for a,b in edge],'paving')
# Recalculate the closed shell consistently, including the concave coastline.
bm=bmesh.new();bm.from_mesh(terrain.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(terrain.data);bm.free()
terrain['cnx_role']='terrain';terrain['cnx_top_vertex_count']=n
for polygon in terrain.data.polygons:
 if polygon.index<len(faces):polygon.use_smooth=True
terrain_bvh=BVHTree.FromPolygons(top,faces)
def built_height(x,y):
 hit=terrain_bvh.ray_cast(Vector((x,y,100)),Vector((0,0,-1)))[0]
 return hit.z if hit is not None else height(x,y)
print('TERRAIN',len(top),flush=True)

def ribbon(name,pts,width,mat,z=.025):
 dense=[]
 for a,b in zip(pts,pts[1:]):
  a,b=Vector(a),Vector(b);steps=max(1,math.ceil((b-a).length/.6));dense.extend(a.lerp(b,i/steps)for i in range(steps))
 dense.append(Vector(pts[-1]));v=[]
 for i,p in enumerate(dense):
  d=(dense[min(i+1,len(dense)-1)]-dense[max(0,i-1)]).normalized();side=Vector((-d.y,d.x))*width*.5
  for sign in [-1,1]:q=p+side*sign;v.append(point(q.x,q.y,z))
 return mesh(name,v,[(2*i,2*i+1,2*i+3,2*i+2)for i in range(len(dense)-1)],mat)

roads=[('BEIJING_AXIS',[(-58,-6),(-57,16),(-57,40),(-46,54),(-24,61),(6,62),(34,57),(56,47)],2.0),
 ('PALACE_STREET',[(-60,-7),(-38,-7),(-29,-7)],1.8),
 ('BJ_CROSS',[(-60,27),(-44,27),(-30,27)],1.8),
 ('REAR_CROSS',[(-34,37),(-14,37),(8,38),(26,39)],1.8),
 ('NORTH_STREET',[(-24,51),(4,51),(25,51)],1.6),
 ('GZ_BOULEVARD',[(27,5),(32,15),(34,27),(39,40),(43,56)],1.9),
 ('GZ_OUTER',[(59,6),(59,27),(57,47)],1.8)]
for name,pts,w in roads:
 ribbon('CNX_'+name+'_SIDEWALK',pts,w+.5,'stone',.04);ribbon('CNX_'+name,pts,w,'road',.055)
 marks=citykit.Batch('CNX_'+name+'_MARKS',D,col,M)
 for a,b in zip(pts,pts[1:]):
  a,b=Vector(a),Vector(b);di=(b-a).normalized()
  for k in range(int((b-a).length/1.8)):
   p=a+di*(k*1.8+.3);q=p+di*.65;marks.rod('white',point(p.x,p.y,.075),point(q.x,q.y,.075),.025,4)
 marks.finish()
ribbon('CNX_OUTER_PROMENADE',OUTER[1:],.48,'ivory',.06)

sites=[];occupied=[]
def reserve(x,y,w,d,margin=.5):occupied.append((x-w*.5-margin,y-d*.5-margin,x+w*.5+margin,y+d*.5+margin))
def foundation(name,root,w,d,mat='stone'):
 T=root.matrix_basis;bottom=[];top=[]
 corners=[Vector(v)for v in [(-w/2,-d/2,0),(w/2,-d/2,0),(w/2,d/2,0),(-w/2,d/2,0)]]
 for a,b in zip(corners,corners[1:]+corners[:1]):
  steps=math.ceil((b-a).length/.42)
  for j in range(steps):
   p=T@a.lerp(b,j/steps);top.append(p);bottom.append(Vector((p.x,p.y,built_height(p.x,p.y)-.045)))
 n=len(top)
 obj=mesh(name,top+bottom,[tuple(range(n)),tuple(range(2*n-1,n-1,-1))]+[(i,n+i,n+(i+1)%n,(i+1)%n)for i in range(n)],mat)
 obj['cnx_foundation_perimeter_samples']=n
 return obj

def fit_frame(root,w,d):
 T=root.matrix_basis.copy();n=T.to_3x3()@Vector((0,0,1));lift=0
 for j in range(5):
  for i in range(5):
   p=T@Vector((w*(i/4-.5),d*(j/4-.5),0))
   lift=max(lift,(built_height(p.x,p.y)+.08-p.z)/n.z)
 if lift>0:T.translation+=n*lift;root.matrix_basis=T
 root['cnx_foundation_lift']=lift

def landmark(region,kind,x,y,w,d,h,yaw=0):
 name='CNX_'+region+'_'+kind.upper();root=frame(name+'_ROOT',x,y,yaw,.18)
 if kind!='great_wall':fit_frame(root,w+1,d+1)
 root['cnx_role']='landmark';root['cnx_landmark']=kind
 module=beijing if region=='BJ' else guangzhou
 objects=module.build(kind,name,root,col,M,w,d,h)
 for obj in objects:obj['cnx_owner']='cn-city-expansion-v001';obj['cnx_role']='landmark_geometry'
 if kind!='great_wall':foundation(name+'_TERRACE',root,w+1,d+1)
 reserve(x,y,w+1,d+1,1.0)
 sites.append({'name':name,'kind':kind,'region':region,'anchor':[x,y],'size':[w,d,h],'root':root.name,'landmark':True})
 return root

landmark('BJ','palace',-45,1,17,11,5.8)
landmark('BJ','heaven',-46,17,10.5,10,7.6)
landmark('BJ','cctv',-39,38,10,7.5,21)
landmark('BJ','zun',-51,40,5.2,5.0,31)
landmark('BJ','stadium',-29,51,12.5,9,5.3)
wall=landmark('BJ','great_wall',-41,58,26,10,6.3)

# Green ridges follow the actual winding wall walkway rather than a flat pad.
profile=[Vector((x*26,y*10,z*6.3))for x,y,z in beijing.great_wall_profile()]
hill=citykit.Batch('CNX_BJ_WALL_HILLS',wall,col,M);hv=[];nr=24;nt=128
WT=wall.matrix_basis;WI=WT.inverted()
def hill_height(x,y):
 q=min(profile,key=lambda q:abs(q.x-x))
 hit=terrain_bvh.ray_cast(WT@Vector((x,y,80)),(WT.to_3x3()@Vector((0,0,-1))).normalized())[0]
 assert hit is not None,('Hill edge outside constructed land',x,y)
 base=(WI@hit).z+.004
 fade=math.exp(-((y-q.y)/2.0)**2)*max(0,1-(abs(x)/14)**8)
 fade*=1-ease((math.sqrt((x/14)**2+(y/6)**2)-.78)/.22)
 return base+(max(0,base)+max(0,q.z-.28)-base)*fade
hv.append((0,0,hill_height(0,0)))
for j in range(1,nr+1):
 for i in range(nt):
  x=14*j/nr*math.cos(i*math.tau/nt);y=6*j/nr*math.sin(i*math.tau/nt)
  hv.append((x,y,hill_height(x,y)))
hf=[(0,1+i,1+(i+1)%nt)for i in range(nt)]
hf += [(1+j*nt+i,1+(j+1)*nt+i,1+(j+1)*nt+(i+1)%nt,1+j*nt+(i+1)%nt)for j in range(nr-1)for i in range(nt)]
hill.add('green',hv,hf)
for obj in hill.finish():
 for polygon in obj.data.polygons:polygon.use_smooth=True
for obj in wall.children:
 if obj.type=='MESH' and 'HILLS'not in obj.name:
  for vertex in obj.data.vertices:
   if abs(vertex.co.z)<1e-7:vertex.co.z=min(0,hill_height(vertex.co.x,vertex.co.y)-.025)
  obj.data.update()
forest=citykit.Batch('CNX_BJ_WALL_FOREST',wall,col,M)
for i in range(80):
 x=random.uniform(-12.5,12.5);q=min(profile,key=lambda q:abs(q.x-x));y=q.y+random.choice([-1,1])*random.uniform(1.2,3.8);z=hill_height(x,y)
 if (x/14)**2+(y/6)**2>.92:continue
 forest.rod('wood',(x,y,z),(x,y,z+.62),.04);forest.ellipsoid('green',(x,y,z+.88),(.38,.36,.5))
forest.finish()

landmark('GZ','lingnan',43,10,13,9,5.8)
landmark('GZ','pagoda',55,16,4.6,4.6,10)
landmark('GZ','canton',45,32,6.5,6.5,33)
landmark('GZ','ifc',34,46,5,5,25)
landmark('GZ','ctf',46,49,5,4.5,27)
landmark('GZ','faceted',55,40,5.2,5.0,23)
landmark('GZ','shells',26,39,11,8,6)

# Pearl River-inspired canal, tree-lined banks, two slim arch bridges.
canal=[(27,23),(37,24),(48,24),(58,26)]
ribbon('CNX_GZ_CANAL_BANK',canal,3.2,'ivory',.07);ribbon('CNX_GZ_REFLECTING_CANAL',canal,2.6,'water',.08)
for x,y in [(37,24),(53,25)]:
 root=frame('CNX_GZ_ARCH_BRIDGE_ROOT',x,y,0,.15);b=citykit.Batch('CNX_GZ_ARCH_BRIDGE',root,col,M)
 b.box('ivory',(0,0,.55),(1.5,4.4,.18))
 for side in [-1,1]:
  for i in range(24):
   a=-2.1+4.2*i/24;c=-2.1+4.2*(i+1)/24
   b.rod('metal',(side*.66,a,.6+1.25*math.sin((a+2.1)/4.2*math.pi)),(side*.66,c,.6+1.25*math.sin((c+2.1)/4.2*math.pi)),.055)
  for j in range(9):
   yy=-2+j*.5;b.rod('metal',(side*.66,yy,.62),(side*.66,yy,.6+1.25*math.sin((yy+2.1)/4.2*math.pi)),.025)
 b.finish();reserve(x,y,2.0,5.0)

def viable(x,y,w,d):
 if -26<x<20 and y<34:return False
 if not all(inside(x+sx*(w/2+.35),y+sy*(d/2+.35))for sx in [-1,1]for sy in [-1,1]):return False
 a=(x-w/2-.3,y-d/2-.3,x+w/2+.3,y+d/2+.3)
 if any(a[0]<b[2]and a[2]>b[0]and a[1]<b[3]and a[3]>b[1]for b in occupied):return False
 for _,pts,rw in roads:
  if min(segdist((x,y),p,q)for p,q in zip(pts,pts[1:]))<rw/2+max(w,d)*.52+.25:return False
 if x>24 and min(segdist((x,y),p,q)for p,q in zip(canal,canal[1:]))<1.6+max(w,d)*.5:return False
 # Retain the explicit foreground ship channel even at diagonal polygon ends.
 return y>=-7.2

counts={'hutong_compounds':0,'hutong_roof_buildings':0,'lowrise_houses':0,'qilou':0,'midrise':0}
def add_building(kind,x,y,w,d,h,index):
 region='BJ' if x<-26 else 'GZ' if x>24 else 'LINK'
 name=f'CNX_{region}_{kind.upper()}_{index:03d}';root=frame(name+'_ROOT',x,y)
 fit_frame(root,w+.25,d+.25)
 root['cnx_role']='building';root['cnx_building_kind']=kind
 if kind=='hutong':citykit.courtyard(name,root,col,M,w,d,h,index);counts['hutong_compounds']+=1;counts['hutong_roof_buildings']+=4
 elif kind=='qilou':
  for obj in guangzhou.build('qilou',name,root,col,M,w,d,h):obj['cnx_owner']='cn-city-expansion-v001'
  counts['qilou']+=1
 elif kind=='street_house':
  b=citykit.Batch(name,root,col,M);citykit.house(b,0,0,w,d,h,'ivory' if index%3 else 'stone');b.finish();counts['lowrise_houses']+=1
 else:citykit.block(name,root,col,M,w,d,h,index);counts['midrise']+=1
 foundation(name+'_FOUNDATION',root,w+.24,d+.24)
 reserve(x,y,w,d,.16)
 sites.append({'name':name,'kind':kind,'region':region,'anchor':[x,y],'size':[w,d,h],'root':root.name,'landmark':False})

# Curated rows with small footprint/height variation; roads/plazas reserve voids.
idx=0
for x0,x1,y0,y1,spacing,kind in [(-61,-32,-5,31,4.4,'hutong'),(-58,-29,30,53,3.6,'midrise'),
                              (-21,22,36,66,3.6,'midrise'),(28,58,4,22,3.3,'qilou'),(27,59,28,58,3.5,'midrise')]:
 y=y0
 while y<=y1:
  x=x0
  while x<=x1:
   w,d=(3.65,3.3)if kind=='hutong'else(2.65,2.4)if kind=='qilou'else(2.65,2.55)
   px=x+random.uniform(-.12,.12);py=y+random.uniform(-.12,.12)
   if viable(px,py,w,d):
    h=(1.65+random.random()*.45)if kind=='hutong'else(3.1+random.random()*1.7)if kind=='qilou'else(3.6+random.random()*4.6)
    local_kind='qilou' if kind=='midrise' and px>24 and py<37 else kind
    if local_kind=='qilou':h=min(h,4.5)
    if -40<px<-20 and 38<py<51:h=min(h,3.0)
    add_building(local_kind,px,py,w,d,h,idx);idx+=1
   x+=spacing
  y+=spacing
for y0 in range(-5,70,3):
 for x0 in range(-61,61,3):
  px=x0+.33;py=y0+.3;kind='qilou' if px>24 else 'street_house'
  w,d=(2.05,1.75)if kind=='qilou'else(1.85,1.65)
  if viable(px,py,w,d):
   h=2.6+random.random()*.9 if kind=='qilou' else 1.35+random.random()*.45
   add_building(kind,px,py,w,d,h,idx);idx+=1
print('BUILDINGS',counts,len(sites),flush=True)

# Street trees have trunks and multi-lobed crowns; no billboard vegetation.
trees=citykit.Batch('CNX_STREET_TREES',D,col,M);tree_count=0
for name,pts,width in roads:
 for a,b in zip(pts,pts[1:]):
  a,b=Vector(a),Vector(b);di=(b-a).normalized();side=Vector((-di.y,di.x))
  for j in range(int((b-a).length/2.0)):
   for sign in [-1,1]:
    q=a+di*(j*2+.8)+side*sign*(width/2+.46)
    if not inside(q.x,q.y):continue
    p=point(q.x,q.y,.08);n=normal(q.x,q.y)
    trees.rod('wood',p,p+n*.78,.055)
    trees.ellipsoid('green',p+n*1.0,(.36,.35,.48))
    tree_count+=1
trees.finish()

# Lighting, railings, and a few benches complete the walkable edges.
street=citykit.Batch('CNX_STREET_FURNITURE',D,col,M)
for name,pts,width in roads:
 for a,b in zip(pts,pts[1:]):
  a,b=Vector(a),Vector(b);di=(b-a).normalized();side=Vector((-di.y,di.x))
  for j in range(int((b-a).length/6)):
   q=a+di*(j*6+1)+side*(width/2+.32)
   if not inside(q.x,q.y):continue
   p=point(q.x,q.y,.06);n=normal(q.x,q.y);street.rod('dark',p,p+n*1.65,.028)
   street.ellipsoid('white',p+n*1.7,(.12,.12,.07),8,4)
street.finish()

# Existing decorative ocean loops now lie inside the newly constructed city.
# Preserve their data and explicitly hide only the nine confirmed protrusions.
hidden_waves=['SF_OCEAN_WAVE.'+suffix for suffix in ['001','003','004','009','016','027','029','030','031']]
for name in hidden_waves:
 s.objects[name].hide_render=True;s.objects[name].hide_viewport=True

s['cn_city_expansion']='Beijing and Guangzhou landmark districts; existing integrated geometry/actions/camera preserved'
s['cn_city_expansion_source_sha256']=SHA
s.frame_set(132)
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   view=area.spaces.active.region_3d
   view.view_perspective='PERSP';view.view_location=D.matrix_world@Vector((0,25,-3));view.view_distance=155
   view.view_rotation=D.matrix_world.to_quaternion()@(Vector((0,25,-3))-Vector((55,-100,115))).to_track_quat('-Z','Y')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
report={'source':str(SOURCE),'source_sha256':SHA,'file':str(OUT),'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),
 'source_objects':len(old_names),'added_objects':len(set(s.objects.keys())-old_names),'collections':[col.name],
 'outer_boundary':OUTER,'inner_boundary':INNER,'landmark_count':sum(r['landmark']for r in sites),
 'building_counts':counts,'street_trees':tree_count,'sites':sites,'roads':[{'name':n,'points':p,'width':w}for n,p,w in roads],
 'original_objects_modified':hidden_waves,'original_visibility_exceptions':hidden_waves,'camera_modified':False,'timeline':[0,989,30],
 'terrain_method':'Actual ocean height +0.9, smooth 18-unit connection shelf to original coastal top; local terrain normals and fitted foundations',
 'status':'Pending visual and independent preservation checks'}
(ROOT/'delivery.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
(ROOT/'review/build.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA
print('BUILT_CITY',report['sha256'],report['added_objects'],counts,flush=True)
