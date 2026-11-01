"""Curved US city with a camera-tested rear skyline; preserve the animation master."""
import bpy,bmesh,math,json,hashlib,sys,random
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
sys.path.insert(0,str(R.parent/'curvature-rework-v001/scripts'))
from mapping import surface,normal,CENTER
from architecture import (create_chrysler,create_transamerica,create_willis,create_block,
                         create_one_world_trade_center,create_space_needle,create_rockefeller_plaza)
SOURCE=R.parent/'camera-micro-smooth-v001/pnpline-33s-camera-micro-smooth-v001.blend'
OUTPUT=R/'pnpline-city-expansion-v002.blend'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='6b982226d8c8d9581a25bc82105acb8811842a6f4b6f02d0423fc45168b54025'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.context.scene;s.frame_set(349)
U=s.objects['US_FRAME'];old_names=set(bpy.data.objects.keys())
col=bpy.data.collections.new('CE_US_CITY_EXPANSION');s.collection.children.link(col)
def mat(name,color):
 m=bpy.data.materials.new('CE_'+name);m.diffuse_color=(*color,1);m.use_nodes=True
 m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*color,1)
 m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.72
 return m
M={k:mat(k,c) for k,c in {'stone':(.59,.57,.51),'ivory':(.83,.82,.73),'dark':(.025,.055,.071),'glass':(.10,.23,.28),'metal':(.66,.73,.77),'brick':(.42,.26,.20),'roof':(.14,.18,.19),'cyan':(.005,.49,.68),'road':(.16,.19,.20),'paving':(.59,.62,.60),'lawn':(.25,.34,.18),'leaf':(.13,.29,.12),'pine':(.10,.24,.16),'bark':(.20,.13,.08),'white':(.9,.9,.82),'yellow':(.89,.63,.13),'red':(.57,.10,.055),'water':(.09,.34,.43)}.items()}
landmat=s.objects['US_LAND_TERRACE'].data.materials[0]
def mesh(name,verts,faces,material,parent=U):
 me=bpy.data.meshes.new(name+'_mesh');me.from_pydata(verts,[],faces);me.materials.append(material);me.update()
 o=bpy.data.objects.new(name,me);col.objects.link(o);o.parent=parent;o['ce_owner']='city-expansion-v002';return o
def frame(name,x,y,z=.96,yaw=0):
 o=bpy.data.objects.new(name,None);col.objects.link(o);o.parent=U
 o.matrix_basis=Matrix.Translation(surface(x,y,z))@Vector((0,0,1)).rotation_difference(normal(x,y)).to_matrix().to_4x4()@Matrix.Rotation(yaw,4,'Z')
 o['ce_owner']='city-expansion-v002';o['ce_anchor']=[x,y,z];o['ce_role']='tangent_frame';return o
class Batch:
 def __init__(self,name):self.name=name;self.parts={}
 def add(self,key,v,f):
  vs,fs=self.parts.setdefault(key,([],[]));n=len(vs);vs.extend(v);fs.extend(tuple(n+i for i in p) for p in f)
 def box(self,key,center,size,T=None):
  c=Vector(center);h=Vector(size)/2;v=[c+Vector((a*h.x,b*h.y,d*h.z)) for a,b,d in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
  if T is not None:v=[T@p for p in v]
  self.add(key,v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
 def rod(self,key,a,b,r=.08,n=6):
  a,b=Vector(a),Vector(b);z=(b-a).normalized();x=z.cross(Vector((0,0,1)))
  if x.length<.01:x=z.cross(Vector((0,1,0)))
  x.normalize();y=z.cross(x);v=[p+r*(x*math.cos(i*math.tau/n)+y*math.sin(i*math.tau/n)) for p in [a,b] for i in range(n)]
  self.add(key,v,[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)])
 def ellipsoid(self,key,c,r,T):
  v=[];n=8;m=6
  for j in range(m+1):
   t=math.pi*j/m
   for i in range(n):
    p=Vector((r[0]*math.sin(t)*math.cos(i*math.tau/n),r[1]*math.sin(t)*math.sin(i*math.tau/n),r[2]*math.cos(t)))+Vector(c);v.append(T@p)
  self.add(key,v,[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(m) for i in range(n)])
 def finish(self):
  return [mesh(self.name+'_'+key,v,f,M[key]) for key,(v,f) in self.parts.items()]
def sheet(poly,step=1.25):
 bm=bmesh.new();vs=[bm.verts.new((x,y,0)) for x,y in poly];bm.faces.new(vs);bmesh.ops.triangulate(bm,faces=list(bm.faces))
 for _ in range(10):
  es=[e for e in bm.edges if e.calc_length()>step]
  if not es:break
  bmesh.ops.subdivide_edges(bm,edges=es,cuts=1,use_grid_fill=True)
 bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.verts.ensure_lookup_table();bm.verts.index_update()
 p=[(v.co.x,v.co.y) for v in bm.verts];f=[tuple(v.index for v in face.verts) for face in bm.faces];e=[tuple(v.index for v in edge.verts) for edge in bm.edges if edge.is_boundary];bm.free();return p,f,e
def patch(name,poly,material,z=.68,bottom=-.12):
 p,f,e=sheet(poly);n=len(p);v=[surface(x,y,z) for x,y in p]+[surface(x,y,bottom) for x,y in p]
 o=mesh(name,v,f+[tuple(n+i for i in reversed(q)) for q in f]+[(a,b,n+b,n+a) for a,b in e],material)
 o['ce_role']='curved_terrain';o['ce_top_vertices']=n;o['ce_height']=z;return o
LEFT=[(-31.398,40),(-39,53),(-40,73),(-23,91),(3,95),(30,92),(57,79),(82,64),(83,60.58),(-9.438,75.735),(-23,56)]
RIGHT=[(-7,-29),(-3,-43),(12,-50),(36,-53),(58,-46),(70,-31),(61,-21),(45,-18),(30,-18),(20,-23),(10,-24)]
patch('CE_NY_CURVED_LAND',LEFT,landmat)
patch('CE_SF_CURVED_ISLAND',RIGHT,landmat)
roads=[]
def ribbon(name,points,width,material,z=.80):
 pts=[]
 for a,b in zip(points,points[1:]):
  a,b=Vector(a),Vector(b);n=max(1,math.ceil((b-a).length/1.0));pts.extend(a.lerp(b,j/n) for j in range(n))
 pts.append(Vector(points[-1]));vs=[]
 for i,p in enumerate(pts):
  d=(pts[min(i+1,len(pts)-1)]-pts[max(0,i-1)]).normalized();side=Vector((-d.y,d.x))*width/2
  for sign in [-1,1]:
   q=p+side*sign;vs.append(surface(q.x,q.y,z if isinstance(z,(int,float)) else z(q.x,q.y)))
 return mesh(name,vs,[(2*i,2*i+1,2*i+3,2*i+2) for i in range(len(pts)-1)],material)
def road(name,points,width=3.3):
 ribbon(name+'_SIDEWALK',points,width+.7,M['paving'],.77);ribbon(name+'_ASPHALT',points,width,M['road'],.82)
 b=Batch(name+'_MARKS')
 for a,c in zip(points,points[1:]):
  a,c=Vector(a),Vector(c);d=(c-a).normalized();l=(c-a).length
  for j in range(int(l/2)):
   q=a+d*(j*2+.6);p=q+d*.9;n=Vector((-d.y,d.x))*.055
   b.add('yellow',[surface(v.x,v.y,.837) for v in [q-n,q+n,p+n,p-n]],[(0,1,2,3)])
 b.finish();roads.append({'name':name,'points':points,'width':width})
CONFIG=json.loads((R/'scripts/dense_layout.json').read_text())
CHICAGO=CONFIG['terrain_polygons']['chicago']
patch('CE_CHICAGO_CURVED_LAND',CHICAGO,landmat)
for spec in CONFIG['roads']:road(spec['name'],spec['points'],spec['width'])
NY_MAIN=next(r['points'] for r in CONFIG['roads'] if r['name']=='CE_NY_BROADWAY')
SF_MAIN=next(r['points'] for r in CONFIG['roads'] if r['name']=='CE_SF_BRIDGE_BOULEVARD')
SF_CROSS=next(r['points'] for r in CONFIG['roads'] if r['name']=='CE_SF_MARKET_STREET')
# Thin spherical promenades follow both coastlines without changing existing land.
ribbon('CE_NY_COAST_PROMENADE',LEFT[:9],.70,M['paving'],.735)
ribbon('CE_SF_COAST_PROMENADE',RIGHT+[RIGHT[0]],.85,M['paving'],.735)
ribbon('CE_CHI_COAST_PROMENADE',CHICAGO[:8],.70,M['paving'],.735)
buildings=[]
def building(name,x,y,w,d,h,kind='masonry',yaw=0,landmark=None):
 root=frame(name+'_ROOT',x,y,.96,yaw);root['ce_role']='building_root'
 # A flat upper podium and radial underside join the rigid building to the curved land.
 local=[(-w/2-.22,-d/2-.22,0),(w/2+.22,-d/2-.22,0),(w/2+.22,d/2+.22,0),(-w/2-.22,d/2+.22,0)]
 top=[root.matrix_basis@Vector(p) for p in local];bot=[CENTER+(p-CENTER).normalized()*140.69 for p in top]
 mesh(name+'_FOUNDATION',top+bot,[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],M['stone'])
 if landmark=='chrysler':create_chrysler(name,root,col,M,height=h,width=w,depth=d)
 elif landmark=='transamerica':create_transamerica(name,root,col,M,height=h,width=w,depth=d)
 elif landmark=='willis':create_willis(name,root,col,M,height=h,width=w,depth=d)
 elif landmark=='one_world_trade_center':create_one_world_trade_center(name,root,col,M,height=h,width=w,depth=d)
 elif landmark=='space_needle':create_space_needle(name,root,col,M,height=h,width=w,depth=d)
 elif landmark=='rockefeller_plaza':create_rockefeller_plaza(name,root,col,M,height=h,width=w,depth=d)
 else:
  kwargs={'floor_count':max(8,min(30,round(h/1.1)))} if name.startswith('CE_REAR_') else {}
  create_block(name,root,col,M,width=w,depth=d,height=h,kind=kind,seed=len(buildings)+831,**kwargs)
 buildings.append({'name':name,'xy':[x,y],'size':[w,d,h],'yaw':yaw,'landmark':landmark})
for spec in CONFIG['buildings']:
 building(spec['name'],*spec['xy'],*spec['size'],kind=spec.get('kind','masonry'),yaw=spec.get('yaw',0),landmark=spec.get('landmark'))
# Public squares, park lawns, street furniture and planted shore belts.
cx,cy=next(b['xy'] for b in CONFIG['buildings'] if b.get('landmark')=='chrysler')
patch('CE_CHRYSLER_PLAZA',[(cx-3.5,cy-3.2),(cx+3.5,cy-3.2),(cx+3.5,cy+3.2),(cx-3.5,cy+3.2)],M['paving'],.75,.70)
patch('CE_SF_REDWOOD_PARK',[(35,-36),(38,-38.5),(48,-38.5),(49,-35.5),(48,-28),(38,-28)],M['lawn'],.75,.70)
wx,wy=next(b['xy'] for b in CONFIG['buildings'] if b.get('landmark')=='willis')
patch('CE_WILLIS_PLAZA',[(wx-4.5,wy-4.5),(wx+4.5,wy-4.5),(wx+4.5,wy+4.5),(wx-4.5,wy+4.5)],M['paving'],.75,.70)
for b in CONFIG['buildings']:
 if b['name'].startswith('CE_REAR_') and b.get('landmark'):
  x,y=b['xy'];w,d=b['size'][:2];w=w/2+.6;d=d/2+.6
  patch(b['name']+'_PLAZA',[(x-w,y-d),(x+w,y-d),(x+w,y+d),(x-w,y+d)],M['paving'],.75,.70)
props=Batch('CE_STREET_FURNITURE');trees=[]
def tangent(x,y,z=.79):return Matrix.Translation(surface(x,y,z))@Vector((0,0,1)).rotation_difference(normal(x,y)).to_matrix().to_4x4()
def tree(x,y,pine=False,scale=1):
 T=tangent(x,y);props.box('bark',(0,0,.60*scale),(.17*scale,.17*scale,1.2*scale),T)
 if pine:
  for z,r in [(1.4,.8),(2,.62),(2.5,.43)]:
   v=[T@Vector((r*scale*math.cos(i*math.tau/8),r*scale*math.sin(i*math.tau/8),(z-.6)*scale)) for i in range(8)]+[T@Vector((0,0,(z+.8)*scale))]
   props.add('pine',v,[(i,(i+1)%8,8) for i in range(8)])
 else:props.ellipsoid('leaf',(0,0,1.7*scale),(.66*scale,.63*scale,1.0*scale),T)
 trees.append((x,y))
def blocked(x,y):return any(abs(x-b['xy'][0])<b['size'][0]/2+1.2 and abs(y-b['xy'][1])<b['size'][1]/2+1.2 for b in buildings)
for line,center in [(LEFT[:9],(15,78)),(RIGHT+[RIGHT[0]],(30,-35)),(CHICAGO[:8],(15,-65))]:
 for a,b in zip(line,line[1:]):
  a,b=Vector(a),Vector(b);n=max(1,int((b-a).length/3.5))
  for j in range(n):
   p=a.lerp(b,(j+.5)/n);c=Vector(center);p+=(c-p).normalized()*1.8
   if not blocked(p.x,p.y):tree(p.x,p.y,False,.95)
for x,y in [(36.5,-31),(36.5,-34),(39,-37.3),(42,-37.7),(46,-37.6),(48,-32),(47,-29.5),(-22,86),(-30,55),(-10,90),(4,92),(15,89),(37,82),(65,65)]:
 if not blocked(x,y):tree(x,y,y<0,1.0)
for pts in [NY_MAIN,SF_CROSS,SF_MAIN]+[r['points'] for r in CONFIG['roads'] if r['name'].startswith('CE_CHI')]:
 for a,b in zip(pts,pts[1:]):
  a,b=Vector(a),Vector(b);d=(b-a).normalized();side=Vector((-d.y,d.x))*1.75
  for j in range(max(1,int((b-a).length/7))):
   p=a.lerp(b,(j+.5)/max(1,int((b-a).length/7)))+side
   if blocked(p.x,p.y):continue
   T=tangent(p.x,p.y);props.box('dark',(0,0,1.25),(.085,.085,2.5),T);props.box('metal',(.2,0,2.45),(.6,.25,.11),T)
for x,y in [(-21,86),(37,-36),(47,-29),(32,82),(63,-25),(4,-28)]:
 if blocked(x,y):continue
 T=tangent(x,y);props.box('brick',(0,0,.4),(1.3,.45,.14),T);props.box('dark',(-.45,0,.2),(.1,.35,.4),T);props.box('dark',(.45,0,.2),(.1,.35,.4),T)
# Small parked vehicles add a legible street scale; they are static scenery.
for i,(x,y,ang) in enumerate([(-30,62,0),(-3,80,1.57),(43,66,1.1),(15,-34,1.57),(30,-31,0),(52,-37,1.0)]):
 if blocked(x,y):continue
 T=tangent(x,y)@Matrix.Rotation(ang,4,'Z');props.box('cyan' if i%2 else 'ivory',(0,0,.36),(.8,1.55,.48),T);props.box('glass',(0,-.05,.70),(.7,.8,.32),T)
 for xx in [-.43,.43]:
  for yy in [-.46,.46]:props.box('dark',(xx,yy,.20),(.13,.3,.33),T)
props.finish()
# Replace only the explicitly requested existing bridge and its curvature wrapper.
removed=[]
for o in list(s.objects):
 if o.name.startswith(('UC_BRIDGE','CV_BRIDGE')):removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
def bridge_z(x,y):
 t=max(0,min(1,(8.8-y)/30.8));return .88+1.25*math.sin(math.pi*t)**2
bridge_points=[(30,8.8),(30,-22)]
ribbon('CE_BRIDGE_DECK',bridge_points,3.8,M['paving'],bridge_z)
ribbon('CE_BRIDGE_ROAD',bridge_points,2.7,M['road'],lambda x,y:bridge_z(x,y)+.035)
bridge=Batch('CE_BRIDGE_STRUCTURE')
for x in [28.22,31.78]:
 pts=[surface(x,8.8-j*.55,bridge_z(x,8.8-j*.55)+.42) for j in range(57)]
 for a,b in zip(pts,pts[1:]):bridge.rod('metal',a,b,.055)
 for j in range(32):
  y=8.8-j*.99;bridge.rod('metal',surface(x,y,bridge_z(x,y)+.04),surface(x,y,bridge_z(x,y)+.42),.035)
for y in [2,-15]:
 T=tangent(30,y,bridge_z(30,y));
 for x in [-1.95,1.95]:
  bridge.box('stone',(x,0,-.75),(1.3,1.5,1.5),T);bridge.box('red',(x,0,4.6),(.43,.60,9.2),T)
 for z in [3.1,7.9,8.9]:bridge.box('red',(0,0,z),(4.3,.48,.35),T)
 for x in [-1.95,1.95]:
  for z in [3.4,5.5]:bridge.rod('red',T@Vector((x,0,z)),T@Vector((-x,0,z+2.1)),.08)
for x in [28.05,31.95]:
 for ya,yb,ha,hb,sag in [(8.8,2,.5,9.2,0),(2,-15,9.2,9.2,5.5),(-15,-22,9.2,.5,0)]:
  pts=[]
  for i in range(41):
   t=i/40;y=ya+(yb-ya)*t;h=ha+(hb-ha)*t-sag*4*t*(1-t);pts.append(surface(x,y,bridge_z(x,y)+h))
  for a,b in zip(pts,pts[1:]):bridge.rod('red',a,b,.075)
  for i in range(2,40,4):
   t=i/40;y=ya+(yb-ya)*t;bridge.rod('metal',surface(x,y,bridge_z(x,y)+.45),pts[i],.027)
for j in range(15):
 y=8.4-j*2;bridge.rod('yellow',surface(30,y,bridge_z(30,y)+.055),surface(30,y-.85,bridge_z(30,y-.85)+.055),.035)
bridge.finish()
shadow_disabled=[]
for o in col.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data)
 invalid=any(not e.is_manifold for e in bm.edges) or any(f.calc_area()<1e-10 for f in bm.faces)
 bm.free()
 if invalid:o.display.show_shadows=False;shadow_disabled.append(o.name)
# No edits to the active camera, animation, settings, original meshes, or source material.
s.frame_set(349);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT),compress=True)
new=[o for o in s.objects if o.name not in old_names]
report={'source':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'output':str(OUTPUT),'removed':removed,'new_objects':len(new),'new_vertices':sum(len(o.data.vertices) for o in new if o.type=='MESH'),'new_polygons':sum(len(o.data.polygons) for o in new if o.type=='MESH'),'buildings':buildings,'roads':roads,'tree_count':len(trees),'terrain_polygons':{'left':LEFT,'right':RIGHT,'chicago':CHICAGO},'bridge_endpoints':bridge_points,'bridge_width':3.8,'seed':831,'open_surface_shadow_disabled':shadow_disabled,'sidewalk_extra_width':.7,'landmarks':['Chrysler Building inspired','Transamerica Pyramid inspired','Willis Tower inspired'],'preserved_camera':'CAM_MASTER','fps':s.render.fps,'frames':[s.frame_start,s.frame_end]}
report['landmarks']=[b['landmark'] for b in CONFIG['buildings'] if b.get('landmark')]
(R/'review/build.json').write_text(json.dumps(report,indent=2));print('CITY_EXPANSION_BUILT',json.dumps({k:report[k] for k in ['new_objects','new_vertices','new_polygons','tree_count','fps','frames']}))
