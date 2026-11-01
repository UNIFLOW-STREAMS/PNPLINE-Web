import bpy,sys,math,random,json
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];B=R.parents[1]/'blockout'
sys.path[:0]=[str(R/'scripts'),str(B/'curvature-rework-v001/scripts'),str(B/'cn-shanghai-density-v001/scripts')]
from mapping import graded,surface,normal,WAREHOUSE
from citykit import Batch
from buildingkit import building
from vegetationkit import tree,shrub
from truck_detail import add_details
S=bpy.context.scene;S.frame_set(900);U=S.objects['US_FRAME'];COL=bpy.data.collections.new('DSP_DISPATCH_DISTRICT');S.collection.children.link(COL)
M={};rng=random.Random(241)
palette={'brick':(.40,.135,.065),'cream':(.70,.66,.55),'stone':(.55,.53,.46),'glass':(.025,.065,.082),'metal':(.35,.40,.42),'dark':(.018,.026,.031),'roof':(.18,.20,.20),'green':(.035,.13,.065),'white':(.82,.81,.74),'wood':(.13,.075,.034),'cyan':(.006,.32,.49),'paving':(.57,.58,.54),'grass':(.14,.22,.075),'leaf1':(.09,.22,.045),'leaf2':(.18,.30,.07),'leaf3':(.055,.14,.035),'yellow':(.7,.44,.035),'soil':(.12,.095,.06)}
for k,c in palette.items():
 m=bpy.data.materials.new('DSP_'+k);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=.28 if k=='glass' else .36 if k in ['metal','cyan'] else .72
 if k=='metal':p.inputs['Metallic'].default_value=.8
 if k=='glass':p.inputs['Coat Weight'].default_value=.35
 if k in ['brick','stone','paving','roof']:
  n=m.node_tree.nodes;ln=m.node_tree.links;t=n.new('ShaderNodeTexNoise');t.inputs['Scale'].default_value=22 if k!='brick' else 38;t.inputs['Detail'].default_value=2
  tex=n.new('ShaderNodeTexCoord');ln.new(tex.outputs['Object'],t.inputs['Vector']);b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.14;b.inputs['Distance'].default_value=.018;ln.new(t.outputs['Fac'],b.inputs['Height']);ln.new(b.outputs['Normal'],p.inputs['Normal'])
 M[k]=m
M['asphalt']=bpy.data.materials.new('DSP_asphalt');M['asphalt'].diffuse_color=(.09,.11,.12,1);M['asphalt'].use_nodes=True
p=M['asphalt'].node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.09,.11,.12,1);p.inputs['Roughness'].default_value=.85
# Masonry courses use local metric coordinates on either vertical facade.
m=M['brick'];n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF');tc=n.new('ShaderNodeTexCoord');sep=n.new('ShaderNodeSeparateXYZ');l.new(tc.outputs['Object'],sep.inputs[0])
geo=n.new('ShaderNodeNewGeometry');tr=n.new('ShaderNodeVectorTransform');tr.vector_type='NORMAL';tr.convert_from='WORLD';tr.convert_to='OBJECT';l.new(geo.outputs['Normal'],tr.inputs[0]);ns=n.new('ShaderNodeSeparateXYZ');l.new(tr.outputs[0],ns.inputs[0])
ax=n.new('ShaderNodeMath');ax.operation='ABSOLUTE';ay=n.new('ShaderNodeMath');ay.operation='ABSOLUTE';l.new(ns.outputs['X'],ax.inputs[0]);l.new(ns.outputs['Y'],ay.inputs[0]);test=n.new('ShaderNodeMath');test.operation='GREATER_THAN';l.new(ax.outputs[0],test.inputs[0]);l.new(ay.outputs[0],test.inputs[1]);mix=n.new('ShaderNodeMixRGB');l.new(test.outputs[0],mix.inputs[0]);l.new(sep.outputs['X'],mix.inputs[1]);l.new(sep.outputs['Y'],mix.inputs[2]);comb=n.new('ShaderNodeCombineXYZ');l.new(mix.outputs[0],comb.inputs['X']);l.new(sep.outputs['Z'],comb.inputs['Y']);brick=n.new('ShaderNodeTexBrick');l.new(comb.outputs[0],brick.inputs[0]);brick.inputs['Scale'].default_value=1;brick.inputs['Brick Width'].default_value=.32;brick.inputs['Row Height'].default_value=.14;brick.inputs['Mortar Size'].default_value=.006;brick.inputs['Mortar Smooth'].default_value=.002;brick.inputs['Color1'].default_value=(.40,.135,.065,1);brick.inputs['Color2'].default_value=(.30,.08,.035,1);brick.inputs['Mortar'].default_value=(.28,.26,.22,1);l.new(brick.outputs['Color'],p.inputs['Base Color']);bm=n.new('ShaderNodeBump');bm.inputs['Strength'].default_value=.22;bm.inputs['Distance'].default_value=.009;l.new(brick.outputs['Fac'],bm.inputs['Height']);l.new(bm.outputs[0],p.inputs['Normal'])
def mesh(name,vs,fs,mat):
 d=bpy.data.meshes.new(name);d.from_pydata(vs,[],fs);d.materials.append(M[mat]);d.update();o=bpy.data.objects.new(name,d);COL.objects.link(o);o.parent=U;return o
def gp(x,y,z=.71):return graded(Vector((x,y,z)))
def frame(x,y):
 p=gp(x,y);dx=(gp(x+.02,y)-gp(x-.02,y)).normalized();dy=(gp(x,y+.02)-gp(x,y-.02));n=dx.cross(dy).normalized();dy=n.cross(dx).normalized();return Matrix.Translation(p)@Matrix((dx,dy,n)).transposed().to_4x4()
def root(name,x,y,yaw=0):
 o=bpy.data.objects.new(name,None);COL.objects.link(o);o.parent=U;o.matrix_basis=frame(x,y)@Matrix.Rotation(yaw,4,'Z');return o
def patch(name,x0,x1,y0,y1,mat,z=.71,step=1):
 nx=max(1,math.ceil((x1-x0)/step));ny=max(1,math.ceil((y1-y0)/step));vs=[gp(x0+(x1-x0)*i/nx,y0+(y1-y0)*j/ny,z) for i in range(nx+1) for j in range(ny+1)];fs=[]
 for i in range(nx):
  for j in range(ny):a=i*(ny+1)+j;fs.append((a,a+ny+1,a+ny+2,a+1))
 return mesh(name,vs,fs,mat)
# Continuous graded apron/neighborhood surface, supported to the existing sphere.
patch('DSP_CONTINUOUS_GROUND',78,113,5.6,55,'paving',.66,.4)
patch('DSP_WATERFRONT_PROMENADE',40,78,5.8,11.5,'paving',.70,.45)
patch('DSP_WAREHOUSE_SIDE_GARDEN',41,77,12,20,'grass',.75,.4)
patch('DSP_GARDEN_WALK',41,77,15.5,16.5,'cream',.79,.4)
edge=[(78+35*i/50,5.6) for i in range(51)]+[(113,5.6+49.4*i/65) for i in range(1,66)]+[(113-35*i/50,55) for i in range(1,51)]+[(78,55-49.4*i/65) for i in range(1,66)]
vs=[];fs=[]
for x,y in edge:vs.extend([gp(x,y,.66),surface(x,y,.45)])
for i in range(len(edge)):j=(i+1)%len(edge);fs.append((2*i,2*j,2*j+1,2*i+1))
mesh('DSP_GROUND_EDGE',vs,fs,'stone')
sites=[(84,14,6,5,4.5,0),(92,12,6.5,5.5,6.2,1),(100,9.5,6,5,4.5,2),(108,9,6,5,5.9,3),(84,44,6,5,4.4,1),(92,46,6,5.5,6.1,0),(100,49,6,5,6.2,3),(108,50,6,5,4.5,2)]
for i,(x,y,w,d,h,v) in enumerate(sites):
 yaw=math.pi if y<29 else 0;p=root('DSP_B%02d_ROOT'%i,x,y,yaw);building(Batch,'DSP_B%02d'%i,p,COL,M,w,d,h,v)
 # foundation follows the locally rigid building, extended down to curved ground.
 F=p.matrix_basis;corners=[(-w/2-.35,-d/2-.35),(w/2+.35,-d/2-.35),(w/2+.35,d/2+.35),(-w/2-.35,d/2+.35)]
 vs=[F@Vector((a,b,.08)) for a,b in corners];vs += [F@Vector((a,b,-.6)) for a,b in corners]
 mesh('DSP_B%02d_FOUNDATION'%i,vs,[(0,1,2,3)]+[(i,(i+1)%4,(i+1)%4+4,i+4) for i in range(4)],'stone')
for i in range(4):
 o=S.objects.get('E12_DESTINATION_'+str(i))
 if o:o.hide_render=True;o.hide_viewport=True
def road(x,branch):
 u=max(0,min(1,(x-85)/22));return 29+branch*12*u*u*(3-2*u)

# Replace the two coincident source ribbons with one welded visual surface.
# The center paths and .74 contact elevation remain identical to the source.
for name in ['E11_ROUTE_1','E11_ROUTE_-1','A05_WAIT_MERGE','CV_SUPPORT_A05_WAIT_MERGE']:
 S.objects[name].hide_render=True;S.objects[name].hide_viewport=True
def halfwidth(x):return 1.9*math.sqrt(1+((road(x+.01,1)-road(x-.01,1))/.02)**2)
a,b=85.,99.
for _ in range(50):
 mid=(a+b)/2
 if road(mid,1)-29<halfwidth(mid):a=mid
 else:b=mid
split=(a+b)/2
def stripgrid(name,x0,x1,bounds,cols=12,z=.74,mat='asphalt'):
 nx=math.ceil((x1-x0)/.18);vs=[];fs=[]
 for i in range(nx+1):
  x=x0+(x1-x0)*i/nx;lo,hi=bounds(x)
  vs.extend(gp(x,lo+(hi-lo)*j/cols,z) for j in range(cols+1))
 for i in range(nx):
  for j in range(cols):
   k=i*(cols+1)+j;fs.append((k,k+cols+1,k+cols+2,k+1))
 ob=mesh(name,vs,fs,mat)
 for f in ob.data.polygons:f.use_smooth=True
 return ob
stripgrid('DSP_ROAD_STEM',70,split,lambda x:(road(x,-1)-halfwidth(x),road(x,1)+halfwidth(x)),24)
for branch in [-1,1]:stripgrid('DSP_ROAD_BRANCH_'+str(branch),split,110.2,lambda x,b=branch:(road(x,b)-halfwidth(x),road(x,b)+halfwidth(x)))
def ribbon(name,pts,width,mat,z):
 vs=[]
 for i,(x,y) in enumerate(pts):
  a=Vector(pts[max(0,i-1)]);b=Vector(pts[min(len(pts)-1,i+1)]);t=(b-a).normalized();side=Vector((-t.y,t.x))*width/2
  for sg in [-1,1]:vs.append(gp(x+side.x*sg,y+side.y*sg,z))
 return mesh(name,vs,[(i,i+2,i+3,i+1) for i in range(0,len(vs)-2,2)],mat)
for branch in [-1,1]:
 # Edges/sidewalk remain outside original road width (1.9 half width).
 pts=[(x,road(x,branch)) for x in [82+i*.25 for i in range(117)]]
 for side in [-1,1]:
  if (branch==1 and side==-1) or (branch==-1 and side==1):start=44
  else:start=0
  offs=[]
  for i,(x,y) in enumerate(pts):
   a=Vector(pts[max(0,i-1)]);b=Vector(pts[min(len(pts)-1,i+1)]);t=(b-a).normalized();offs.append((x-t.y*side*2.45,y+t.x*side*2.45))
  ribbon('DSP_SIDEWALK_%s_%s'%(branch,side),offs[start:],1.0,'cream',.84)
  curb=[]
  for i,(x,y) in enumerate(pts):
   a=Vector(pts[max(0,i-1)]);b=Vector(pts[min(len(pts)-1,i+1)]);t=(b-a).normalized();curb.append((x-t.y*side*1.98,y+t.x*side*1.98))
  ribbon('DSP_CURB_%s_%s'%(branch,side),curb[start:],.12,'white',.87)
 for a in range(83,109,3):
  if a<86 and branch==1:continue
  ribbon('DSP_LANE_%s_%s'%(branch,a),[(a+i*.1,road(a+i*.1,branch))for i in range(11)],.055,'white',.785)
 # narrow edge markings inside shoulder
 for side in [-1,1]:
  if side==-branch:continue
  ribbon('DSP_EDGE_LINE_%s_%s'%(branch,side),[(x,y+side*halfwidth(x)*.88)for x,y in pts],.055,'white',.785)
# Triangular planted median, growing gradually beyond fork clearance.
stripgrid('DSP_RAIN_GARDEN',93.4,111.2,lambda x:(road(x,-1)+3.12,road(x,1)-3.12),40,.81,'grass')
occupied=[(x,y,w/2+.65,d/2+.65)for x,y,w,d,h,v in sites]
def safe(x,y,r=.8):
 if any(abs(x-a)<w+r and abs(y-b)<d+r for a,b,w,d in occupied):return False
 if min(abs(y-road(x,b)) for b in [-1,1])<3.0+r:return False
 return True
trees=[]
for x in [79.5+i*2.9 for i in range(12)]:
 for y in [6.8,19,39,53.3]:
  yy=y+rng.uniform(-.3,.3)
  if safe(x,yy):trees.append((x,yy))
for x,y in [(87.7,12),(96,10),(104,9),(87.6,45),(96,48),(104,50),(102,26),(106,32),(110,26),(99,30)]:
 if safe(x,y):trees.append((x,y))
for x in [42+i*2.7 for i in range(14)]:trees.append((x,9.0+rng.uniform(-.3,.3)))
for x,y in [(80,14),(87,22),(91,22),(95,20),(99,18),(103,15),(107,14),(110,14),(81,43),(88,38),(92,38),(97,41),(101,44),(105,45),(110,45),(103,29),(108,23),(109,36),(101,33)]:
 if safe(x,y,.55):trees.append((x,y))
for x,y in [(98,27),(100,25),(102,23),(104,25),(106,27),(108,29),(110,32),(104,34),(106,36),(110,38)]:
 if safe(x,y,.9):trees.append((x,y))
for i,(x,y) in enumerate(trees):
 p=root('DSP_TREE_%03d'%i,x,y);tree(Batch,'DSP_TREE_%03d'%i,p,COL,M,seed=100+i,height=rng.uniform(2.4,3.5))
 # square planter around tree foot
 b=Batch('DSP_TREEBED_%03d'%i,p,COL,M);b.box('soil',(0,0,.04),(1.3,1.3,.08));b.finish()
for i in range(240):
 x=rng.uniform(92,111);y=rng.uniform(18,40)
 if y<road(x,-1)+3.3 or y>road(x,1)-3.3:continue
 p=root('DSP_SHRUB_%03d'%i,x,y);shrub(Batch,'DSP_SHRUB_%03d'%i,p,COL,M,seed=i,width=rng.uniform(.35,.85),height=rng.uniform(.2,.45))
for i in range(76):
 x=42+(i//4)*1.8;y=[13,14.4,17.6,19][i%4]+rng.uniform(-.16,.16)
 p=root('DSP_SIDE_GARDEN_%03d'%i,x,y);shrub(Batch,'DSP_SIDE_GARDEN_%03d'%i,p,COL,M,seed=600+i,width=rng.uniform(.5,.9),height=rng.uniform(.24,.42))
# Waterfront paving joints, benches and shore stones carry the concept into
# the existing uninterrupted waterfront without changing its coastline.
for x in range(41,79,2):ribbon('DSP_PROMENADE_JOINT_%s'%x,[(x,5.9),(x,11.4)],.018,'stone',.73)
for i,x in enumerate(range(43,78,6)):
 p=root('DSP_PROMENADE_FURNITURE_%02d'%i,x,7.0);b=Batch('DSP_PROMENADE_%02d'%i,p,COL,M)
 for sy in [-.15,0,.15]:b.box('wood',(0,sy,.43),(1.25,.12,.07))
 for sx in [-.45,.45]:b.box('dark',(sx,0,.2),(.07,.4,.4))
 b.rod('dark',(1,0,0),(1,0,2.6),.04,8);b.box('dark',(1,0,2.6),(.3,.22,.13));b.finish()
for i in range(150):
 x=40+i*.48;y=4.95+rng.uniform(-.32,.18);p=root('DSP_SHORE_%03d'%i,x,y);b=Batch('DSP_SHORE_%03d'%i,p,COL,M);b.ellipsoid('stone',(0,0,-.14),(rng.uniform(.18,.4),rng.uniform(.19,.36),rng.uniform(.2,.35)),7,4);b.finish()
# Edge lamps, benches and drainage, kept away from truck lane.
for i,x in enumerate([82,88,95,102,109]):
 for branch in [-1,1]:
  y=road(x,branch)+branch*3.2;p=root('DSP_STREET_%s_%s'%(i,branch),x,y);b=Batch('DSP_STREET_%s_%s'%(i,branch),p,COL,M)
  b.rod('dark',(0,0,0),(0,0,2.6),.045,8);b.box('dark',(0,0,2.62),(.32,.22,.12));b.box('white',(0,0,2.55),(.24,.15,.025))
  b.box('dark',(.3,0,.02),(.38,.65,.04))
  for j in range(7):b.box('metal',(.3,-.27+j*.09,.045),(.34,.026,.02))
  b.finish()
# Fine warehouse panel battens, roof seams and outlet details follow existing rigid frame.
p=bpy.data.objects.new('DSP_WAREHOUSE_DETAIL_ROOT',None);COL.objects.link(p);p.parent=U;p.matrix_basis=WAREHOUSE;b=Batch('DSP_WH',p,COL,M)
for y in [31.7+i*.28 for i in range(26)]:b.box('metal',(68.185,y,6.55),(.025,.025,9.1))
for y in [26.8+i*.28 for i in range(17)]:b.box('metal',(68.265,y,8.45),(.025,.025,5.5))
for x in [36.2+i*.7 for i in range(46)]:b.box('metal',(x,37.9,11.625),(.025,2.7,.025))
for x in [41,49,57,65]:
 b.box('white',(x,38,11.85),(1.4,1.3,.42));b.box('metal',(x,38,12.08),(1.2,1.1,.06))
 for j in range(8):b.box('dark',(x-.5+j*.14,37.33,11.85),(.04,.025,.27))
b.finish()
# Apron panel seams: flush surface strips; no vehicle-contact elevation change.
p=bpy.data.objects.new('DSP_APRON_ROOT',None);COL.objects.link(p);p.parent=U;p.matrix_basis=WAREHOUSE;b=Batch('DSP_APRON',p,COL,M)
for x in [69,72,75,78,81]:b.box('stone',(x,30,.766),(.018,13.7,.008))
for y in [24,27,30,33,36]:b.box('stone',(75,y,.766),(13.7,.018,.008))
b.finish()
add_details(S,COL,M)
for o in COL.objects:o['dispatch_owner']='us-dispatch-model-v001'
S.frame_set(989);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(R/'candidate.blend'))
(R/'review/build.json').write_text(json.dumps(dict(buildings=sites,trees=trees,new_objects=len(COL.objects),hidden_proxies=['E12_DESTINATION_'+str(i)for i in range(4)],replaced_road_surfaces=['E11_ROUTE_1','E11_ROUTE_-1','A05_WAIT_MERGE','CV_SUPPORT_A05_WAIT_MERGE']),indent=2))
print('BUILT',len(COL.objects),flush=True)
