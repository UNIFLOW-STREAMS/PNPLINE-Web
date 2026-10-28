"""Author the C-front historic waterfront district using editable geometry."""
import bpy,math,random,json,sys,ast
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(156)
OUT=Path(sys.argv[sys.argv.index('--')+1]);assert not OUT.exists()
D=s.objects['SF_CN_LAYOUT'];DM=D.matrix_world.copy();DI=DM.inverted()
col=bpy.data.collections.new('C_FRONT_HISTORIC_DISTRICT');s.collection.children.link(col)
def tag(o):o['district_owner']='c-front-v012';return o
# Reuse only the explicitly listed, side-effect-free construction definitions.
tree=ast.parse((R/'scripts/build_layout_proposal.py').read_text())
names={'empty','mesh','box','tube','lathe','sphere','uvpoint','pxwidth'}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),'<geometry helpers>','exec'))
M={k:bpy.data.materials['SF_'+k]for k in ['stone','cream','roof','white','red','blue','navy','silver','green','bark']}
def material(name,color,rough=.72):
 m=bpy.data.materials.new('DT_'+name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;return m
M['paving']=material('PAVING',(.53,.53,.45));M['grass']=material('GRASS',(.13,.22,.065));M['glass']=material('GLASS',(.035,.10,.115),.25)
greens=[material('FOLIAGE_'+str(i),c)for i,c in enumerate([(.12,.22,.055),(.20,.28,.085),(.075,.16,.03),(.28,.31,.10)])]
rockmat=material('ROCK',(.36,.36,.29));tilemat=material('CHARCOAL_TILE',(.025,.037,.04),.65)
hidden=[];footprints=[]
oldroots=['SF_STONE_LEFT','SF_STONE_LEFT_REAR','SF_STONE_CENTER','SF_STONE_FACADE','SF_STONE_RIGHT','SF_GARDEN_PAVILION','SF_HISTORIC_0','SF_HISTORIC_1']
for name in oldroots:
 o=s.objects[name]
 for ob in [o]+list(o.children_recursive):ob.hide_render=True;ob.hide_set(True);hidden.append(ob.name)
# Replace the two static foreground props with articulated miniature trucks.
for o in s.objects:
 if o.name in ['SF_SMALL_VEHICLE_0','SF_SMALL_VEHICLE_1'] or (o.name.startswith('SF_SMALL_TIRE') and int(o.name.rsplit('.',1)[1] if '.'in o.name else 0)<8):
  o.hide_render=True;o.hide_set(True);hidden.append(o.name)
def archpanel(name,x,y,z,w,h,parent):
 r=w/2;spring=h-r;vs=[(x-r,y,z),(x+r,y,z)]+[(x+r*math.cos(t*math.pi/16),y,z+spring+r*math.sin(t*math.pi/16))for t in range(17)]
 mesh(name,vs,[tuple(range(len(vs)))],M['glass'],parent)
 pts=[(x-r,y-.02,z),(x-r,y-.02,z+spring)]+[(x+r*math.cos(t*math.pi/16),y-.02,z+spring+r*math.sin(t*math.pi/16))for t in range(16,-1,-1)]+[(x+r,y-.02,z)]
 tube(name+'_ARCH',pts,.035,M['cream'],parent)
 box(name+'_SILL',(x,y-.055,z-.035),(w+.11,.14,.07),M['cream'],parent)
 tube(name+'_MULLION',[(x,y-.03,z),(x,y-.03,z+h-.05)],.014,M['cream'],parent)
def dome(name,root,xy,z,r):
 cx,cy=xy;drum=.72*r
 lathe('DT_'+name+'_DRUM',(cx,cy,z),[(0,r*.89),(.07,r*.97),(drum-.07,r*.88),(drum,r)],M['stone'],root,16)
 for j in range(8):
  a=j*math.tau/8;frame=empty('DT_'+name+'_DRUM_WINDOW_FRAME',root,(cx+math.sin(a)*r*.9,cy-math.cos(a)*r*.9,z+.16*r));frame.rotation_euler.z=a
  archpanel('DT_'+name+'_DRUM_WINDOW',0,-.015,0,r*.32,drum*.66,frame)
 rings=[(0,r*1.04),(.07*r,r*1.05)]+[(r*1.15*math.sin(t*math.pi/2),r*math.cos(t*math.pi/2))for t in [j/18 for j in range(1,19)]]
 lathe('DT_'+name+'_DOME',(cx,cy,z+drum),rings,M['cream'],root,64)
 for j in range(12):
  a=j*math.tau/12;pts=[(cx+r*math.cos(t*math.pi/2)*math.cos(a),cy+r*math.cos(t*math.pi/2)*math.sin(a),z+drum+r*1.15*math.sin(t*math.pi/2)+.012)for t in [k/20 for k in range(21)]]
  tube('DT_'+name+'_DOME_RIB',pts,.018,M['stone'],root)
 lathe('DT_'+name+'_FINIAL',(cx,cy,z+drum+r*1.15),[(0,.10),(.1,.09),(.28,.035),(.46,.01)],M['stone'],root,16)
def classical(name,oldname,h,domed=False):
 old=s.objects[oldname];root=empty('DT_'+name,D,tuple(old.location));body=s.objects[oldname+'_body'];vs=[v.co for v in body.data.vertices];w=max(p.x for p in vs)-min(p.x for p in vs);d=max(p.y for p in vs)-min(p.y for p in vs)
 box('DT_'+name+'_BODY',(0,0,h/2),(w,d,h),M['stone'],root)
 # Shallow wings and a raised middle bay give a stepped, historic silhouette.
 for sign in [-1,1]:box('DT_'+name+'_CORNER',(sign*(w/2-.27),-.10,h/2),(.54,d+.20,h+.12),M['cream'],root)
 for z,t in [(0,.18),(.25,.12),(1.10,.10),(2.13,.10),(3.16,.10),(h,.17)]:
  if z<=h:box('DT_'+name+'_CORNICE',(0,0,z),(w+.25,d+.25,t),M['cream'],root)
 bays=max(4,round(w/.62));step=(w-.5)/(bays-1)
 for i in range(bays):
  x=-w/2+.25+i*step
  for floor in range(max(2,int(h/.92))):
   z=.28+floor*.92
   if z+.68<h:archpanel('DT_'+name+'_WINDOW',x,-d/2-.015,z,.28,.62,root)
  box('DT_'+name+'_PILASTER',(x+step*.43,-d/2-.08,h*.53),(.075,.15,h*.86),M['cream'],root)
  box('DT_'+name+'_CAPITAL',(x+step*.43,-d/2-.09,h-.20),(.15,.19,.12),M['cream'],root)
 # Side facades remain articulated when the camera moves.
 for sign in [-1,1]:
  side=empty('DT_'+name+'_SIDE',root,(sign*w/2,0,0));side.rotation_euler.z=sign*math.pi/2
  for xx in [-d*.30,0,d*.30]:
   for floor in range(max(2,int(h/.92))):
    z=.28+floor*.92
    if z+.68<h:archpanel('DT_'+name+'_SIDE_WINDOW',xx,-.025,z,.28,.62,side)
 # Door surround, entry steps, entablature and balustraded roof terrace.
 archpanel('DT_'+name+'_ENTRANCE',0,-d/2-.10,.08,.55,.92,root)
 for j in range(3):box('DT_'+name+'_ENTRY_STEP',(0,-d/2-.20-j*.12,.07-j*.02),(.85+j*.18,.22,.09),M['cream'],root)
 for yy in [-d/2,d/2]:
  box('DT_'+name+'_PARAPET_BASE',(0,yy,h+.08),(w+.18,.12,.12),M['cream'],root)
  box('DT_'+name+'_PARAPET_RAIL',(0,yy,h+.40),(w+.18,.11,.10),M['cream'],root)
  for i in range(max(6,int(w/.24))):box('DT_'+name+'_BALUSTER',(-w/2+i*w/(max(6,int(w/.24))-1),yy,h+.25),(.055,.065,.28),M['stone'],root)
 if domed:dome(name,root,(w*(.27 if name=='LEFT' else .10),-d*.18 if name=='LEFT' else 0),h+.15,min(w*.22,d*.42))
 else:
  box('DT_'+name+'_ROOF_PAVILION',(w*.20,.05,h+.28),(w*.36,d*.48,.55),M['stone'],root)
  box('DT_'+name+'_ROOF_CAP',(w*.20,.05,h+.60),(w*.40,d*.52,.12),M['cream'],root)
 footprints.append((root.location.x,root.location.y,w/2+.20,d/2+.28))
 return root
classical('LEFT','SF_STONE_LEFT',4.1,True);classical('LEFT_REAR','SF_STONE_LEFT_REAR',3.2)
classical('CENTER','SF_STONE_CENTER',4.1,True);classical('FACADE','SF_STONE_FACADE',3.5);classical('RIGHT','SF_STONE_RIGHT',2.8)
# Eight-sided pavilion: stone steps, red columns, layered upturned roof.
pc=s.objects['SF_GARDEN_PAVILION'].location.copy();pav=empty('DT_PAVILION',D,pc)
for j in range(3):lathe('DT_PAVILION_STEP',(0,0,j*.10),[(0,1.55-j*.13),(.10,1.55-j*.13)],M['cream'],pav,8)
for j in range(8):
 a=j*math.tau/8;x,y=1.08*math.cos(a),1.08*math.sin(a)
 lathe('DT_PAVILION_COLUMN',(x,y,.30),[(0,.10),(1.62,.085),(1.72,.13)],M['red'],pav,16)
 lathe('DT_PAVILION_COLUMN_BASE',(x,y,.30),[(0,.15),(.12,.13)],M['stone'],pav,16)
 a2=(j+1)*math.tau/8;tube('DT_PAVILION_BEAM',[(x,y,2.0),(1.08*math.cos(a2),1.08*math.sin(a2),2.0)],.085,M['red'],pav)
def pagoda_roof(name,z,r,height):
 vs=[];N=64;profile=[(1,.24),(.90,.04),(.68,.16),(.42,.42),(.16,.82),(.02,1)]
 for radius,h in profile:
  for j in range(N):
   a=j*math.tau/N;poly=math.cos(math.pi/8)/math.cos((a%(math.pi/4))-math.pi/8);up=.12*(.5+.5*math.cos(8*a))*(radius**5)
   vs.append((r*radius*poly*math.cos(a),r*radius*poly*math.sin(a),z+height*h+up))
 faces=[(i*N+j,i*N+(j+1)%N,(i+1)*N+(j+1)%N,(i+1)*N+j)for i in range(len(profile)-1)for j in range(N)]
 o=mesh(name,vs,faces,tilemat,pav);o['sides']=8
 for j in range(N):tube(name+'_TILE_SEAM',[vs[i*N+j]for i in range(len(profile))],.013,M['roof'],pav)
 for j in range(8):
  a=j*math.tau/8;tube(name+'_RIDGE',[vs[i*N+j*8]for i in range(len(profile))],.035,M['silver'],pav)
 return o
pagoda_roof('DT_PAVILION_ROOF_LOWER',1.85,1.68,.62);pagoda_roof('DT_PAVILION_ROOF_UPPER',2.27,1.82,1.12)
lathe('DT_PAVILION_FINIAL',(0,0,3.39),[(0,.09),(.16,.08),(.31,.015)],M['roof'],pav,16)
# Compact traditional hall with two dark tiled eaves, curved ends and red trim.
tr=s.objects['SF_HISTORIC_0'].location.copy();tr.y+=.40;traditional=empty('DT_TRADITIONAL',D,tr)
box('DT_TRADITIONAL_WALL',(0,0,1.05),(2.55,1.85,2.10),M['stone'],traditional)
def gable(name,z,w,d,h):
 vs=[]
 for x in [-w/2,w/2]:
  for y,zz in [(-d*.62,.20),(-d*.46,0),(0,h),(d*.46,0),(d*.62,.20)]:vs.append((x,y,z+zz))
 mesh(name,vs,[(j,j+1,j+6,j+5)for j in range(4)],tilemat,traditional)
 for j in range(37):
  x=-w/2+j*w/36;tube(name+'_TILE',[(x,-d*.62,z+.21),(x,-d*.46,z+.02),(x,0,z+h+.02),(x,d*.46,z+.02),(x,d*.62,z+.21)],.022,M['roof'],traditional)
 tube(name+'_RIDGE',[(-w*.60,0,z+h+.20),(-w/2,0,z+h),(w/2,0,z+h),(w*.60,0,z+h+.20)],.05,M['silver'],traditional)
 for yy in [-d*.46,d*.46]:box(name+'_RED_FASCIA',(0,yy,z-.06),(w,.10,.12),M['red'],traditional)
gable('DT_TRADITIONAL_LOWER_ROOF',1.50,2.98,2.05,.58);gable('DT_TRADITIONAL_UPPER_ROOF',2.55,2.73,1.90,.65)
for j in [-1,0,1]:
 box('DT_TRADITIONAL_ENTRY',(j*.60,-.94,.66),(.42,.035,1.12),M['roof'],traditional)
 for dx in [-.24,.24]:box('DT_TRADITIONAL_DOOR_POST',(j*.60+dx,-.97,.68),(.055,.07,1.20),M['red'],traditional)
 box('DT_TRADITIONAL_LINTEL',(j*.60,-.97,1.28),(.54,.08,.07),M['red'],traditional)
 for dx in [-.12,0,.12]:tube('DT_TRADITIONAL_LATTICE',[(j*.60+dx,-.97,.12),(j*.60+dx,-.97,1.20)],.016,M['stone'],traditional)
footprints.append((tr.x,tr.y,1.65,1.30))
# A smaller rear roof fills the corner without obscuring the stone landmark.
rear=s.objects['SF_HISTORIC_1'].location.copy();small=empty('DT_TRADITIONAL_REAR',D,rear)
box('DT_TRADITIONAL_REAR_WALL',(0,0,.72),(1.65,1.2,1.44),M['stone'],small)
saved=traditional;traditional=small;gable('DT_TRADITIONAL_REAR_ROOF',1.40,1.95,1.48,.55);traditional=saved
footprints.append((rear.x,rear.y,1.05,.85))
land=s.objects['SF_FRONT_LAND']
def onland(p):
 world=DM@Vector((p.x,p.y,4));inv=land.matrix_world.inverted();hit,*_=land.ray_cast(inv@world,(inv.to_3x3()@(DM.to_3x3()@Vector((0,0,-1)))).normalized())
 return hit
def free(p):
 if any(abs(p.x-x)<w and abs(p.y-y)<d for x,y,w,d in footprints):return False
 return onland(p)
# Reserve actual clear parking space before placing any vegetation.
parking=[]
for n,(px,py,length) in enumerate([(604,902,1.25),(846,910,1.65)]):
 candidates=sorted([(xx,yy)for xx in range(px-70,px+41,10)for yy in range(py-30,py+21,5)],key=lambda v:(v[0]-px)**2+(v[1]-py)**2)
 for xx,yy in candidates:
  p=uvpoint(xx,yy);p.z=1.25
  if all(free(p+Vector((dx,dy,0)))for dx in [-length*.58,0,length*.58]for dy in [-.45,.45]):
   parking.append(p);footprints.append((p.x,p.y,length*.85,1.05));break
 else:raise RuntimeError('No safe parking space for truck '+str(n))
for o in s.objects:
 if o.name.startswith(('SF_TREE_TRUNK','SF_TREE_CROWN')) and o.type=='MESH':
  p=sum((v.co for v in o.data.vertices),Vector())/len(o.data.vertices)
  if any(abs(p.x-q.x)<1.45 and abs(p.y-q.y)<1.0 for q in parking):
   o.hide_render=True;o.hide_set(True);hidden.append(o.name)
def path_strip(name,a,b,width):
 axis=b-a;side=Vector((-axis.y,axis.x,0)).normalized()*width/2;vs=[];faces=[];count=max(2,int(axis.length/.18))
 for j in range(count):
  p=a.lerp(b,j/count);q=a.lerp(b,(j+1)/count);corners=[p-side,p+side,q+side,q-side]
  if all(onland(v)for v in corners):
   k=len(vs);vs.extend([tuple(v)for v in corners]);faces.append((k,k+1,k+2,k+3))
 mesh(name,vs,faces,M['paving'])
 for j in range(max(2,int(axis.length/.45))):
  p=a.lerp(b,j/max(2,int(axis.length/.45)))
  if onland(p-side) and onland(p+side):tube('DT_PATH_JOINT',[tuple(p-side),tuple(p+side)],.008,M['stone'])
front=uvpoint(609,918);front.z=1.28;entry=pc+Vector((0,-1.6,.035));path_strip('DT_GARDEN_PATH',entry,front,.73)
for xy in [(440,884),(710,908),(581,857)]:
 b=uvpoint(*xy);b.z=1.29;path_strip('DT_GARDEN_PATH_BRANCH',front.lerp(entry,.45),b,.56)
rng=random.Random(12028)
for j,(dx,dy,rx,ry)in enumerate([(-2.0,-1.2,.7,1.1),(1.8,-1.3,.7,1.0),(-.6,-3.0,.7,.55),(1.6,-3.6,.85,.5)]):
 p=pc+Vector((dx,dy,.018))
 if not free(p):continue
 pts=[(p.x+rx*math.cos(a*math.tau/48),p.y+ry*math.sin(a*math.tau/48),1.275)for a in range(48)]
 mesh('DT_GARDEN_LAWN',pts,[tuple(range(48))],M['grass']);tube('DT_GARDEN_STONE_BORDER',pts,.055,M['cream'],closed=True)
# Diverse clustered crowns and shrubs replace empty paving with garden mass.
tree_count=0;shrub_count=0;attempt=0
while tree_count<16 and attempt<500:
 attempt+=1;px=rng.uniform(370,840);py=rng.uniform(788,946);p=uvpoint(px,py);p.z=1.28
 if not free(p) or (p-pc).length<1.85:continue
 if 460<px<620 and 800<py<885:continue
 # Reserve the central approach to keep the pavilion readable.
 if abs(p.x-front.x)<.50 and min(front.y,entry.y)<p.y<max(front.y,entry.y):continue
 h=rng.uniform(.65,1.05);lathe('DT_TREE_TRUNK',p,[(0,.045),(h,.025)],M['bark'],D,8)
 for j in range(5):
  a=j*2.399;q=p+Vector((math.cos(a)*.23,math.sin(a)*.23,h+.22+(j%2)*.18))
  sphere('DT_TREE_CROWN',q,rng.uniform(.22,.32),greens[(tree_count+j)%4])
 tree_count+=1
for j in range(140):
 p=uvpoint(rng.uniform(385,835),rng.uniform(801,918));p.z=1.32
 if not free(p) or (p-pc).length<1.7:continue
 if abs(p.x-front.x)<.45:continue
 sphere('DT_SHRUB',p+Vector((0,0,.16)),rng.uniform(.14,.28),greens[j%4]);shrub_count+=1
 if j%3==0:
  rock=lathe('DT_GARDEN_ROCK',p+Vector((.18,.12,.02)),[(0,.13),(.13,.15),(.22,.06)],rockmat,D,6);rock.rotation_euler.z=rng.random()*math.tau
# Street edge, smaller paving joints and wrought-iron-style lamps.
a=uvpoint(350,962);b=uvpoint(938,962);a.z=b.z=1.28;path_strip('DT_WATERFRONT_WALK',a,b,.62)
for xy in [(422,923),(662,941),(858,933)]:
 p=uvpoint(*xy);p.z=1.3
 if free(p):
  lathe('DT_STREET_LAMP',p,[(0,.07),(.12,.055),(1.15,.035)],M['roof'],D,12)
  sphere('DT_STREET_LAMP_GLASS',p+Vector((0,0,1.18)),.105,M['cream'])
def truck(n,px,py,length=1.45):
 p=parking[n];root=empty('DT_TRUCK_'+str(n),D,p);root.rotation_euler.z=-.10
 box(f'DT_TRUCK_{n}_CHASSIS',(0,0,.24),(length,.58,.16),M['navy'],root)
 box(f'DT_TRUCK_{n}_LOAD',(-.20,0,.70),(length*.64,.61,.72),M['cream'] if n==1 else M['blue'],root)
 box(f'DT_TRUCK_{n}_STRIPE',(-.20,-.313,.63),(length*.64,.022,.22),M['blue'],root)
 box(f'DT_TRUCK_{n}_CAB',(length*.36,0,.55),(length*.30,.60,.62),M['blue'],root)
 box(f'DT_TRUCK_{n}_WINDSCREEN',(length*.515,0,.69),(.02,.48,.25),M['glass'],root)
 for side in [-1,1]:
  box('DT_TRUCK_SIDE_WINDOW',(length*.36,side*.306,.72),(length*.22,.02,.21),M['glass'],root)
  for xx in [-length*.31,length*.35]:
   wheel=lathe('DT_TRUCK_WHEEL',(0,0,0),[(-.065,.16),(.065,.16)],M['roof'],root,16);wheel.location=(xx,side*.33,.16);wheel.rotation_euler.x=math.pi/2
  box('DT_TRUCK_HEADLIGHT',(length*.53,side*.19,.43),(.025,.10,.10),M['cream'],root)
 box('DT_TRUCK_GRILLE',(length*.53,0,.39),(.025,.22,.09),M['silver'],root)
truck(0,604,902,1.25);truck(1,846,922,1.65)
for screen in bpy.data.screens:
 for ar in screen.areas:
  if ar.type=='VIEW_3D':ar.spaces.active.shading.type='SOLID';ar.spaces.active.shading.color_type='MATERIAL'
bpy.context.view_layer.update();s.frame_set(156)
version=OUT.stem.rsplit('-',1)[-1]
(R/f'review/c-district-build-{version}.json').write_text(json.dumps({'source':bpy.data.filepath,'output':str(OUT),'hidden_original_objects':hidden,'new_objects':[o.name for o in col.objects],'tree_count':tree_count,'shrub_count':shrub_count,'parking':[list(p)for p in parking],'assumptions':['Unseen rear facades use the same stone vocabulary','Garden planting is deterministic authored detail, not exact botanical reconstruction'],'scope':'C-front architecture, pavilion, garden, two parked miniature vehicles; no camera, typography, cloud, waterway or actor animation edits'},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT));print('DISTRICT',len(col.objects),'trees',tree_count,'shrubs',shrub_count)
