import bpy,math,json,hashlib,random,sys
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(0);src=Path(bpy.data.filepath)
assert hashlib.sha256(src.read_bytes()).hexdigest()=='e29fe506211d1b7f647f3eee01e066e49319aaae29dffe bc6e4ed82aca371af3'.replace(' ','')
out=R/'master-cn-port-layout-v001.blend'
D=s.objects['SF_CN_LAYOUT'];delta=Vector((14,-13.5,0));dw=D.matrix_world.to_3x3()@delta;random.seed(31)
coll=bpy.data.collections.new('CN_PORT_TERMINAL');s.collection.children.link(coll)
def empty(n,parent=None,loc=(0,0,0)):
 o=bpy.data.objects.new(n,None);coll.objects.link(o);o.parent=parent;o.location=loc;return o
def reparent(o,p):
 basis=o.matrix_basis.copy();inv=o.matrix_parent_inverse.copy();o.parent=p;o.matrix_parent_inverse=inv;o.matrix_basis=basis
static=empty('PORT_CRANE_PLACEMENT',D,delta)
for n in ['CR_COMPACT_GANTRY','CR_TROLLEY_CARRIAGE','CR_SUSPENSION_HEAD']+[o.name for o in s.objects if o.name.startswith('CR_WORKING_CABLE')]:reparent(s.objects[n],static)
sp=empty('PORT_HOIST_PLACEMENT',loc=dw);reparent(s.objects['P01_SPREADER'],sp)
motion=empty('PORT_BERTH_PLACEMENT')
for n in ['A02_SHIP','A01_CONTAINER','W01_NEW_PALLET']:reparent(s.objects[n],motion)
for f in range(361):
 t=max(0,min(1,(f-252)/108));w=1-t*t*t*(10+t*(-15+6*t));motion.location=dw*w;motion.keyframe_insert('location',frame=f)
for l in motion.animation_data.action.layers:
 for st in l.strips:
  for b in st.channelbags:
   for fc in b.fcurves:
    for k in fc.keyframe_points:k.interpolation='LINEAR'
root=empty('PORT_MODEL_ROOT',D)
def mat(n,c,metal=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=.43;p.inputs['Metallic'].default_value=metal;return m
concrete=mat('PORT concrete',(.62,.65,.64));edge=mat('PORT edge',(.78,.8,.76));blue=mat('PORT cyan',(.025,.46,.64),.25);deep=mat('PORT blue',(.015,.25,.39),.15);white=mat('PORT ivory',(.83,.85,.81));dark=mat('PORT rubber',(.025,.035,.038));yellow=mat('PORT safety',(.98,.65,.12));road=mat('PORT road',(.28,.33,.35));glass=mat('PORT glazing',(.04,.16,.21),.2);steel=mat('PORT rail',(.24,.31,.32),.5)
def mesh(n,vs,fs,m,parent=root):
 me=bpy.data.meshes.new(n);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(n,me);coll.objects.link(o);o.parent=parent;o.data.materials.append(m);return o
cubevs=[(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)];cubefs=[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]
def box(n,p,size,m,parent=root):
 o=mesh(n,cubevs,cubefs,m,parent);o.location=p;o.scale=Vector(size)/2;return o

def box_batch(n,parts,m,parent=root):
 vs=[];fs=[]
 for p,size in parts:
  k=len(vs);vs.extend(tuple(p[i]+v[i]*size[i]/2 for i in range(3))for v in cubevs);fs.extend(tuple(k+i for i in f)for f in cubefs)
 return mesh(n,vs,fs,m,parent)
def beam(n,a,b,w,m,parent=root):
 a=Vector(a);b=Vector(b);o=box(n,(a+b)/2,(w,w,(b-a).length),m,parent);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def cyl(n,p,r,h,m,parent=root):
 vs=[(r*math.cos(i*math.tau/12),r*math.sin(i*math.tau/12),z)for z in [-h/2,h/2]for i in range(12)];fs=[tuple(range(11,-1,-1)),tuple(range(12,24))]+[(i,(i+1)%12,(i+1)%12+12,i+12)for i in range(12)];o=mesh(n,vs,fs,m,parent);o.location=p;return o
# Replace obsolete foreground quay with the new port foundation, preserving its name.
quay=s.objects['CN_QUAY'];quay.parent=D;quay.matrix_parent_inverse=Matrix.Identity(4);quay.location=(1,-6.65,.25);quay.rotation_euler=(0,0,0);quay.scale=(1,1,1)
me=bpy.data.meshes.new('PORT_QUAY_FOUNDATION');me.from_pydata([(x*29,y*8.35,1 if z>0 else -7.25)for x,y,z in cubevs],[],cubefs);me.materials.append(concrete);me.update();quay.data=me
box('PORT_APRON',(1,-6.65,1.265),(58,16.7,.03),concrete)
box('PORT_EDGE_FRONT',(1,-14.93,1.27),(58,.14,.12),edge)
for y,width in [(-13.8,1.35),(-6.6,1.55)]:
 box('PORT_ACCESS_ROAD',(1,y,1.29),(57,width,.04),road)
 for x in range(-27,30,2):box('PORT_ROAD_DASH',(x,y,1.316),(.85,.035,.012),white)
for x in [-16.8,-6.3,4.3,14.8,27.5]:
 box('PORT_YARD_CROSS_LANE',(x,-2.6,1.29),(1.4,7.8,.04),road)
for y in [-11.6,-9.25]:box('PORT_CRANE_RAIL',(-12,y,1.305),(29,.055,.045),steel)
for x in range(-27,30,2):
 cyl('PORT_BOLLARD',(x,-14.77,1.42),.095,.30,dark);box('PORT_BOLLARD_CAP',(x,-14.77,1.59),(.29,.17,.08),yellow)
 box('PORT_FENDER',(x,-15.07,.45),(.42,.22,1.05),dark)
for x in [-27,-17,-6,4,15,28]:
 beam('PORT_LIGHT_POLE',(x,1.25,1.25),(x,1.25,4.1),.055,steel);box('PORT_LIGHT',(x,1.25,4.15),(.35,.18,.08),white)
# Rows of individual corrugated containers, staggered one/two/three high.
count=0
for row,y in enumerate([.4,-1.1,-2.6,-4.1]):
 for j,x in enumerate([-25,-22,-19,-14.5,-11.5,-8.5,-4,-1,2,6.5,9.5,12.5,17,20,23]):
  levels=2 if (j+row)%4 else 3
  if row==3 and j%4==1:levels=1
  for level in range(levels):
   color=[blue,deep,white][(j+level+row)%3];z=1.25+.44+level*.9;g=empty('PORT_CONTAINER_'+str(count).zfill(3),root,(x,y,z));count+=1
   box('PORT_CONTAINER_BODY',(0,0,0),(2.55,.95,.86),color,g)
   for yy in [-.485,.485]:
    for q in range(17):box('PORT_CORRUGATION',(-1.18+q*.148,yy,0),(.036,.018,.76),color,g)
   for xx in [-1.25,1.25]:
    for yy in [-.46,.46]:box('PORT_CORNER',(xx,yy,0),(.05,.055,.88),edge,g)
   for yy in [-.2,.2]:box('PORT_DOOR_BAR',(1.285,yy,0),(.025,.026,.72),steel,g)
   box('PORT_DOOR_SEAM',(1.284,0,0),(.026,.018,.8),dark,g)
   roof=[((-1.16+q*.145,0,.442),(.033,.82,.024))for q in range(17)]
   roof += [((0,yy,zz),(2.55,.045,.045))for yy in [-.475,.475]for zz in [-.415,.415]]
   box_batch('PORT_CONTAINER_ROOF_RIBS',roof,color,g)
   # Small identification plate and corner castings remain separate editable parts.
   box('PORT_CONTAINER_ID_PLATE',(.92,-.498,.21),(.32,.012,.13),white,g)
# Two static companion cranes echo the concept. Existing animated crane is retained.
for index,x in enumerate([-19,-3]):
 g=empty('PORT_COMPANION_CRANE_'+str(index),root)
 for xx in [x-1.15,x+1.15]:
  for y in [-11.6,-9.25]:
   box('PORT_CRANE_BOGIE',(xx,y,1.43),(.42,.68,.35),blue,g);beam('PORT_CRANE_LEG',(xx,y,1.6),(xx,y,9.5),.25,white,g)
  beam('PORT_CRANE_SILL',(xx,-11.8,2.5),(xx,-9.05,2.5),.20,blue,g)
 for y in [-11.6,-9.25]:beam('PORT_CRANE_CROSS',(x-1.3,y,9.45),(x+1.3,y,9.45),.3,blue,g)
 for xx in [x-1.0,x+1.0]:
  beam('PORT_CRANE_BOOM',(xx,-19,9.5),(xx,-5.5,9.5),.28,blue,g)
  beam('PORT_CRANE_PYLON',(xx,-10.4,9.5),(x,-10.4,11.65),.17,blue,g)
  beam('PORT_CRANE_STAY',(x,-10.4,11.65),(xx,-19,9.5),.085,blue,g)
  beam('PORT_CRANE_BACKSTAY',(x,-10.4,11.65),(xx,-5.5,9.5),.085,blue,g)
 for y in [-19,-16.3,-13.6,-10.9,-8.2,-5.5]:beam('PORT_BOOM_TIE',(x-1,y,9.5),(x+1,y,9.5),.15,blue,g)
 box('PORT_TROLLEY',(x,-16.6,9.3),(1.6,.65,.28),deep,g)
 for xx in [x-.65,x+.65]:beam('PORT_STATIC_CABLE',(xx,-16.6,9.15),(xx,-16.6,4.4),.025,dark,g)
 box('PORT_STATIC_SPREADER',(x,-16.6,4.35),(1.8,.7,.18),yellow,g)
 box('PORT_OPERATOR_CAB',(x+1.4,-11.4,8.8),(.55,.6,.7),white,g);box('PORT_CAB_WINDOW',(x+1.4,-11.71,8.85),(.42,.02,.38),glass,g)
 for xx in [x-1.15,x+1.15]:beam('PORT_CRANE_BRACE',(xx,-11.6,2.6),(xx,-9.25,5.3),.12,blue,g)
def truck(x,y,angle=0):
 g=empty('PORT_TRUCK',root,(x,y,1.25));g.rotation_euler.z=angle
 box('PORT_TRUCK_CHASSIS',(0,0,.28),(1.5,.55,.16),dark,g);box('PORT_TRUCK_CAB',(.55,0,.65),(.48,.57,.65),blue,g);box('PORT_TRUCK_GLASS',(.795,0,.75),(.018,.45,.24),glass,g);box('PORT_TRUCK_LOAD',(-.35,0,.73),(1.05,.58,.72),white if x%2 else blue,g)
 for xx in [-.55,.53]:
  for yy in [-.32,.32]:
   w=cyl('PORT_TRUCK_WHEEL',(xx,yy,.23),.19,.13,dark,g);w.rotation_euler.x=math.pi/2
for x in [-26,-21,-16,-11,-6,0,6,17,23,28]:truck(x,-13.8)
for x in [-24,-13,-2,9,20,28]:truck(x,-6.6)
for x in [-16.8,4.3,27.5]:truck(x,-1.8,math.pi/2)
box('PORT_SERVICE_OFFICE',(27,.4,1.75),(2.5,1.3,.94),white)
box('PORT_OFFICE_ROOF',(27,.4,2.25),(2.6,1.4,.10),edge)
box('PORT_OFFICE_DOOR',(26.2,-.26,1.65),(.3,.02,.72),glass)
for x in [26.8,27.4,28]:box('PORT_OFFICE_WINDOW',(x,-.26,1.88),(.35,.02,.28),glass)
# Low service sheds and staged containers match the concept's varied apron use.
for x in [-25,-11,6,25]:
 box('PORT_SERVICE_SHED',(x,-8.3,1.95),(2.7,1.35,1.34),white)
 box('PORT_SHED_ROOF',(x,-8.3,2.67),(2.85,1.5,.10),edge)
 for xx in [x-.85,x-.4,x+.05]:box('PORT_SHED_WINDOW',(xx,-8.986,2.1),(.28,.02,.32),glass)
 box('PORT_SHED_DOOR',(x+.85,-8.986,1.77),(.46,.02,.96),deep)
# Relocate the affected old promenade furniture behind the new stacking yard.
bpy.context.view_layer.update();I=D.matrix_world.inverted();relocations=[];right_tree_index=0
for suffix in ['001','003','006','009','011','014','019','022','027','032','035','040','043']:
 trunk=s.objects['SF_TREE_TRUNK.'+suffix];p=sum((I@trunk.matrix_world@v.co for v in trunk.data.vertices),Vector())/len(trunk.data.vertices)
 # Old trees close to the hall move to a clear outer terminal border instead.
 target=Vector((p.x,1.95,p.z)) if p.x<8 else Vector((29.2,-1.5-1.15*right_tree_index,p.z))
 if p.x>=8:right_tree_index+=1
 shift=D.matrix_world.to_3x3()@(target-p)
 for prefix in ['SF_TREE_TRUNK.','SF_TREE_CROWN.']:
  o=s.objects[prefix+suffix];m=o.matrix_world.copy();m.translation+=shift;o.matrix_world=m
  relocations.append(o.name)
for name,x in [('DT_TRUCK_1',-8.5),('NA_PARKED_TRUCK',12)]:
 o=s.objects[name];points=[I@ch.matrix_world@v.co for ch in o.children_recursive if ch.type=='MESH'for v in ch.data.vertices]
 p=Vector(((min(v.x for v in points)+max(v.x for v in points))/2,(min(v.y for v in points)+max(v.y for v in points))/2,min(v.z for v in points)))
 m=o.matrix_world.copy();m.translation+=D.matrix_world.to_3x3()@(Vector((x,-13.8,1.31))-p);o.matrix_world=m;relocations.append(name)
# Original unsupported gray yard proxies are superseded by the modeled terminal.
for o in s.objects:
 if o.name.startswith('CN_YARD_STACK_')or o.name=='CN_YARD_ROAD':o.hide_render=True;o.hide_viewport=True
 if o.name in ['DT_GARDEN_ROCK.004','DT_GARDEN_ROCK.007','DT_GARDEN_ROCK.009','DT_GARDEN_ROCK.014']:o.hide_render=True;o.hide_viewport=True
# Reuse the old waterfront bollards on the terminal's east return wall.
for index,o in enumerate(sorted([o for o in s.objects if o.name.startswith('NA_QUAY_BOLLARD')],key=lambda o:o.name)):
 pts=[I@o.matrix_world@v.co for v in o.data.vertices];p=Vector(((min(v.x for v in pts)+max(v.x for v in pts))/2,(min(v.y for v in pts)+max(v.y for v in pts))/2,min(v.z for v in pts)))
 m=o.matrix_world.copy();m.translation+=D.matrix_world.to_3x3()@(Vector((29.75,-3-2*index,1.31))-p);o.matrix_world=m;relocations.append(o.name)
# Return the remaining decorative stones to the landscaped side of the promenade.
for index,suffix in enumerate(['001','010','011','016','019']):
 o=s.objects['DT_GARDEN_ROCK.'+suffix];pts=[I@o.matrix_world@v.co for v in o.data.vertices];p=Vector(((min(v.x for v in pts)+max(v.x for v in pts))/2,(min(v.y for v in pts)+max(v.y for v in pts))/2,min(v.z for v in pts)))
 m=o.matrix_world.copy();m.translation+=D.matrix_world.to_3x3()@(Vector((-25+index*.48,4.8,1.25))-p);o.matrix_world=m;relocations.append(o.name)
# Apron tile joints and loading-bay outlines add the fine density of the concept.
for x in range(-28,31):box('PORT_APRON_JOINT',(x,-6.65,1.284),(.012,16.6,.005),edge)
for x in [-25,-22,-19,-14.5,-11.5,-8.5,-4,-1,2,6.5,9.5,12.5,17,20,23]:
 for y in [-4.75,1.05]:box('PORT_BAY_LINE',(x,y,1.29),(2.65,.025,.008),yellow)
sys.path.insert(0,str(R/'scripts'))
from harbor_water import build_harbor_water
water_report=build_harbor_water(s,D)
s['cn_port_revision']='Front terminal with relocated original rig; camera unchanged; provisional berth offset holds through f252 and rejoins source by f360'
s.frame_set(0);bpy.ops.wm.save_as_mainfile(filepath=str(out))
(R/'delivery.json').write_text(json.dumps({'file':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'delta_layout':list(delta),'container_count':count,'cranes':3,'quay_size':[58,16.7],'relocated_promenade_objects':relocations,'water':water_report,'status':'Pending verification'},indent=2));print('BUILT',out,count)
