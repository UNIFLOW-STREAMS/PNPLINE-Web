"""Dense US container terminal. Add scenery only; retain every accepted object/action."""
import bpy,math,json,hashlib,sys
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree

R=Path(__file__).resolve().parents[1]
SOURCE=R.parent/'city-expansion-v002/pnpline-city-expansion-v002.blend'
OUTPUT=R/'pnpline-port-densification-v001.blend'
SOURCE_SHA='61c980107793a30b12a8d6d61f341bd233c864346e247b5c5d90cfb72c19afff'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SOURCE_SHA
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.context.scene;s.frame_set(349)
# Retain even the accepted scene's unused material datablocks across Blender's save/reload.
for material in bpy.data.materials:
 if material.users==0:material.use_fake_user=True
U=s.objects['US_FRAME'];I=U.matrix_world.inverted();old=set(bpy.data.objects.keys())
col=bpy.data.collections.new('PT_US_CONTAINER_TERMINAL');s.collection.children.link(col)
M={}
for k,c in {'cyan':(.006,.48,.67),'blue':(.018,.25,.37),'navy':(.035,.09,.14),'white':(.79,.82,.81),'gray':(.42,.49,.52),'steel':(.48,.57,.60),'dark':(.035,.047,.052),'concrete':(.43,.47,.47),'yellow':(.96,.65,.09),'glass':(.06,.17,.22)}.items():
 m=bpy.data.materials.new('PT_'+k);m.diffuse_color=(*c,1);m.use_nodes=True
 m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*c,1)
 m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.65
 M[k]=m
def mesh(name,v,f,key,parent=U):
 me=bpy.data.meshes.new(name+'_mesh');me.from_pydata(v,[],f);me.materials.append(M[key]);me.update()
 o=bpy.data.objects.new(name,me);col.objects.link(o);o.parent=parent;o['pt_owner']='port-densification-v001';return o
class Batch:
 def __init__(self,name,T=None,parent=U,role='structure'):
  self.name=name;self.T=T;self.parent=parent;self.parts={};self.role=role
 def add(self,key,v,f):
  if self.T is not None:v=[self.T@Vector(p) for p in v]
  vs,fs=self.parts.setdefault(key,([],[]));n=len(vs);vs.extend(v);fs.extend(tuple(n+i for i in p) for p in f)
 def box(self,key,c,size):
  c=Vector(c);h=Vector(size)/2
  self.add(key,[c+Vector((a*h.x,b*h.y,d*h.z)) for a,b,d in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
 def rod(self,key,a,b,r=.05,n=8):
  a,b=Vector(a),Vector(b);z=(b-a).normalized();x=z.cross(Vector((0,0,1)))
  if x.length<.01:x=z.cross(Vector((0,1,0)))
  x.normalize();y=z.cross(x)
  v=[p+r*(x*math.cos(i*math.tau/n)+y*math.sin(i*math.tau/n)) for p in [a,b] for i in range(n)]
  self.add(key,v,[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)])
 def finish(self):
  out=[]
  for key,(v,f) in self.parts.items():
   o=mesh(self.name+'_'+key,v,f,key,self.parent);o['pt_role']=self.role;out.append(o)
  return out
ground=[]
for name in ['US_LAND_TERRACE','US_QUAY']:
 o=s.objects[name];T=I@o.matrix_world
 ground.append((name,BVHTree.FromPolygons([T@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons])))
def ground_hit(x,y):
 hits=[]
 for name,bvh in ground:
  p,n,idx,d=bvh.ray_cast(Vector((x,y,25)),Vector((0,0,-1)))
  if p is not None:hits.append((p.z,name,p))
 assert hits,(x,y)
 return max(hits,key=lambda v:v[0])
def ground_frame(name,x,y,w=3.2,d=1.32):
 z,kind,p=ground_hit(x,y)
 n=Vector((0,0,1)) if kind=='US_QUAY' else (p-Vector((0,0,-140))).normalized()
 T=Matrix.Translation(p)@Vector((0,0,1)).rotation_difference(n).to_matrix().to_4x4()
 # Rigid pads meet the actual terrain at their underside, never a guessed sphere height.
 pts=[T@Vector((a*(w/2+.07),b*(d/2+.07),.035)) for a,b in [(-1,-1),(1,-1),(1,1),(-1,1)]]
 bot=[Vector((q.x,q.y,ground_hit(q.x,q.y)[0]-.02)) for q in pts]
 mesh(name+'_PAD',pts+bot,[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],'concrete')['pt_role']='foundation'
 T.translation+=n*.04
 return T
containers=[]
def container(name,T,length=3.2,width=1.32,height=1.08,color='cyan',parent=U):
 b=Batch(name,T,parent,'container');l,w,h=length,width,height
 b.box(color,(0,0,h/2),(l-.07,w-.06,h-.06))
 # Closed shell, top/bottom rails, corrugation, paired doors, locking rods, corner castings.
 for sy in [-1,1]:
  for z in [.045,h-.045]:b.box(color,(0,sy*(w/2-.025),z),(l,.07,.09))
  count=round(l/.16)
  for j in range(count):b.box(color,(-l/2+.13+j*(l-.26)/(count-1),sy*(w/2-.017),h/2),(.045,.055,h-.17))
 for sx in [-1,1]:
  for sy in [-1,1]:
   b.box(color,(sx*(l/2-.04),sy*(w/2-.04),h/2),(.08,.08,h))
   for z in [.045,h-.045]:b.box('steel',(sx*(l/2-.047),sy*(w/2-.047),z),(.094,.094,.09))
  for y in [-w*.25,w*.25]:
   b.box(color,(sx*(l/2-.017),y,h/2),(.045,w/2-.075,h-.16))
   b.rod('steel',(sx*(l/2+.013),y,.13),(sx*(l/2+.013),y,h-.13),.013,6)
   b.box('steel',(sx*(l/2+.024),y,.42*h),(.025,.14,.025))
 for j in range(round(l/.22)):b.box(color,(-l/2+.14+j*(l-.28)/(round(l/.22)-1),0,h-.016),(.04,w-.14,.035))
 b.box('white' if color in ['cyan','blue','navy'] else 'navy',(-.75,-w/2-.024,h*.72),(.47,.015,.14))
 for j in range(4):b.box('dark',(.55+j*.09,-w/2-.026,h*.72),(.045,.017,.07))
 obs=b.finish();containers.append({'name':name,'parent':parent.name,'matrix':list(map(list,T)),'size':[l,w,h],'color':color,'objects':[o.name for o in obs]})
palette=['cyan','white','blue','cyan','navy','gray','cyan','white']
stacks=[]
def stack(x,y,levels,block):
 idx=len(stacks);name=f'PT_STACK_{idx:03}';T=ground_frame(name,x,y)
 for level in range(levels):
  container(name+f'_L{level+1}',T@Matrix.Translation((0,0,level*1.105)),color=palette[(idx*3+level)%len(palette)])
 stacks.append({'name':name,'xy':[x,y],'levels':levels,'block':block})
# Six compact blocks flank the protected central unloading bay and continuous truck lane at y=9.
for x in [-14.1,-10.5,-6.9,7.2,10.8,14.4]:
 for y in [6.35,10.95]:stack(x,y,2 if y<8 and x in [-14.1,14.4] else 3,'quay')
# Rear stack row follows the curved land; keeps the rail line and back road unobstructed.
for x in [-23,-19,-15,-11,-7,-3,1,5,9,13,17,21]:stack(x,13.05,3 if x not in [-23,21] else 2,'rear')
for x in [-23,-19]:stack(x,10.65,3,'west_yard')
# Add a matching top tier to the accepted corrugated stacks without changing their lower tiers.
groups={}
for o in s.objects:
 if o.type=='MESH' and (o.name=='UC_CONTAINER' or o.name.startswith('UC_CONTAINER.') and o.name.split('.')[-1].isdigit()):
  groups.setdefault(o.parent.name,[]).append(o)
for i,(pname,obs) in enumerate(sorted(groups.items())):
 parent=s.objects[pname];inv=parent.matrix_world.inverted();pts=[inv@o.matrix_world@Vector(v) for o in obs for v in o.bound_box]
 lo=Vector(tuple(min(p[k] for p in pts) for k in range(3)));hi=Vector(tuple(max(p[k] for p in pts) for k in range(3)))
 center=(lo+hi)/2;T=Matrix.Translation((center.x,center.y,hi.z+.025))
 container(f'PT_LEGACY_TOP_{i:02}',T,length=hi.x-lo.x,width=hi.y-lo.y,height=.8,color=palette[(i+2)%8],parent=parent)

def crane(name,cx,half=2.2,y0=5,y1=12,z=12,existing=False):
 b=Batch(name,role='crane')
 if not existing:
  for x in [cx-half,cx+half]:
   for y in [y0,y1]:
    b.box('white',(x,y,(z+.9)/2),(.36,.40,z-.9))
    if y>12:
     # Landward supports sit on small piers meeting the curved terrain.
     pts=[Vector((x+dx,y+dy,.915)) for dx,dy in [(-.39,-.28),(.39,-.28),(.39,.28),(-.39,.28)]]
     bot=[Vector((q.x,q.y,ground_hit(q.x,q.y)[0]-.04)) for q in pts]
     b.add('concrete',pts+bot,[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)])
   boom_end=max(14,y1+.4)
   b.box('cyan',(x,(boom_end-6)/2,z),(.32,boom_end+6,.40))
  # Parked spreader safely above the ship's complete approach envelope.
  b.box('cyan',(cx,1,9.25),(3.3,1.6,.16))
  for dx in [-1.4,1.4]:
   for y in [.4,1.6]:b.rod('dark',(cx+dx,y,9.35),(cx+dx,y,z-.16),.018)
 # Portal ties are above the truck/container clearance; open sides preserve view of the cargo.
 for y in [y0,y1]:
  if not existing:b.box('cyan',(cx,y,5.55),(half*2+.55,.48,.40))
  tie_z=z+1.2 if existing else z
  b.box('cyan',(cx,y,tie_z),(half*2+.5,.42,.40))
  for x in [cx-half,cx+half]:
   b.box('navy',(x,y,1.05),(.70,.55,.28))
   for dy in [-.12,.12]:b.rod('dark',(x-.29,y+dy,1),(x+.29,y+dy,1),.13)
   if not existing:b.rod('cyan',(x,y,5.4),(cx+(x-cx)*.54,y,6.6),.10)
   else:
    # Start above the existing rail beam, outside the moving trolley's vertical envelope.
    b.box('white',(x,y,12.8375),(.36,.40,1.425))
    b.box('steel',(x,y,12.16),(.48,.48,.065))
 # Raised A-frame / stay cables give the concept's recognizable ship-to-shore silhouette.
 for x in [cx-half,cx+half]:
  b.rod('cyan',(x,y0,z),(x,8.7,z+3.3),.12)
  b.rod('cyan',(x,y1,z),(x,8.7,z+3.3),.12)
  b.rod('steel',(x,-5.75,z+.12),(x,8.7,z+3.3),.032)
  b.rod('steel',(x,13.7,z+.12),(x,8.7,z+3.3),.032)
  for y in [y0,y1]:
   # Ladders stay on the outer side of each leg.
   if existing and y==y1:continue  # Preserve accepted rear camera passage.
   lx=x+(.60 if x>cx else -.60)
   for side in [-.14,.14]:b.rod('steel',(lx,y+side,1.15),(lx,y+side,z-.2),.018,6)
   for k in range(int((z-1.4)/.32)):b.rod('steel',(lx,y-.14,1.3+k*.32),(lx,y+.14,1.3+k*.32),.014,6)
 b.rod('cyan',(cx-half,8.7,z+3.3),(cx+half,8.7,z+3.3),.12)
 b.box('white',(cx,12.9,z+.40),(2.6,1.45,.80));b.box('navy',(cx,13.64,z+.40),(2.1,.03,.48))
 cabx=cx-half-(.85 if existing else .48)
 b.box('cyan',(cabx,6.1,z-.85),(1.0,1.1,.76));b.box('glass',(cabx,5.54,z-.83),(.80,.035,.48))
 b.finish()
crane('PT_CRANE_WEST',-14.5,half=1.8)
crane('PT_CRANE_EAST',9.1,half=1.8,y1=14.3,z=12.3)
crane('PT_CRANE_MAIN_DETAILS',.75,2.75,z=12.35,existing=True)

# Quay edge, rail tracks and safety lines. The middle of the quay is the working truck corridor.
b=Batch('PT_QUAY_FURNITURE',role='quay_fixture')
for y in [4.8,12.25]:
 b.box('steel',(0,y,.927),(33.6,.055,.045))
for x in [-16,-12,-8,-4,4,8,12,16]:
 b.box('dark',(x,3.94,.46),(.58,.24,.70))
 b.box('yellow',(x,4.45,1.02),(.38,.36,.10))
 b.rod('dark',(x,4.45,1.03),(x,4.45,1.31),.10)
 b.rod('dark',(x-.18,4.45,1.30),(x+.18,4.45,1.30),.07)
for x in [-15.5,-5.0,5.1,15.7]:
 b.box('concrete',(x,11.95,1.02),(.42,.42,.24));b.rod('steel',(x,11.95,1.1),(x,11.95,5.0),.045)
 b.box('dark',(x,11.95,5.02),(.70,.22,.14));b.box('white',(x,11.95,4.95),(.60,.19,.035))
b.finish()
marks=Batch('PT_APRON_MARKS',role='marking')
for y in [7.72,10.18]:marks.box('white',(0,y,.916),(33.5,.055,.018))
for x in range(-16,18,2):marks.box('yellow',(x,9,.919),(.85,.05,.018))
for x in [-15,-10,-5,5,10,15]:
 marks.box('yellow',(x,4.16,.918),(.65,.12,.02))
for x in [-4.1,4.5]:
 for j in range(8):
  y=5.25+j*.30
  marks.rod('yellow',(x-.28,y,.923),(x+.28,y+.20,.923),.022,4)
marks.finish()

new=[o for o in s.objects if o.name not in old]
for o in new:
 if o.type=='MESH':
  assert all(math.isfinite(v) for p in o.data.vertices for v in p.co)
  o['pt_static']=True
s.frame_set(349);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT))
report={'source':str(SOURCE),'source_sha256':SOURCE_SHA,'output':str(OUTPUT),'output_sha256':hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),'removed':[],
 'new_containers':len(containers),'new_stack_blocks':len(stacks),'additional_cranes':2,'enhanced_existing_cranes':1,
 'container_specs':containers,'stack_specs':stacks,'new_objects':len(new),'new_vertices':sum(len(o.data.vertices) for o in new if o.type=='MESH'),
 'new_polygons':sum(len(o.data.polygons) for o in new if o.type=='MESH'),'protected_truck_lane_y':[7.72,10.18],
 'notes':['Every source object preserved.','Quay stacks use existing flat berth; inland pads meet curved terrain.','Camera, logistics animation and 33 s / 30 fps timing remain unchanged.']}
(R/'review/build.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if not k.endswith('_specs')},indent=2))
