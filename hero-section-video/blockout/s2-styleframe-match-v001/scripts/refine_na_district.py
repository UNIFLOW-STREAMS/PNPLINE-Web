"""Editable low-rise waterfront district, based on the locked NA crop.
Run on v014; changes are limited to static district props.
"""
import bpy,math,random,ast,json,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(156)
OUT=Path(sys.argv[sys.argv.index('--')+1]);assert not OUT.exists()
version=OUT.stem.rsplit('-',1)[-1]
D=s.objects['SF_CN_LAYOUT'];DM=D.matrix_world.copy();DI=DM.inverted()
col=bpy.data.collections.new('NA_WATERFRONT_DISTRICT');s.collection.children.link(col)
def tag(o):o['na_district_owner']='na-v015';return o
t=ast.parse((R/'scripts/build_layout_proposal.py').read_text())
exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name in {'empty','mesh','box','tube','lathe','sphere','uvpoint','pxwidth'}],type_ignores=[]),'geometry helpers','exec'))
M={k:bpy.data.materials['SF_'+k]for k in ['stone','cream','roof','white','red','blue','navy','silver','green','bark']}
def mat(n,c,rough=.7):
 m=bpy.data.materials.new('NA_'+n);m.diffuse_color=(*c,1);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*c,1);bs.inputs['Roughness'].default_value=rough;return m
walls=[mat('PLASTER_IVORY',(.66,.62,.50)),mat('PLASTER_WARM',(.57,.49,.37)),mat('PLASTER_PALE',(.76,.72,.62)),mat('GREY_BRICK',(.36,.38,.35))]
tile=mat('CHARCOAL_TILES',(.045,.052,.050));ridge=mat('TILE_EDGES',(.12,.14,.13));wood=mat('TIMBER',(.22,.065,.027));glass=mat('DARK_WINDOWS',(.032,.075,.072),.3)
grass=mat('GARDEN',(.13,.23,.055));paving=mat('PAVING',(.52,.53,.48));greens=[mat('LEAVES_'+str(i),c)for i,c in enumerate([(.12,.22,.04),(.22,.30,.075),(.08,.15,.025)])]
hidden=[]
for o in list(s.objects):
 if o.name in ['SF_HISTORIC_2','SF_HISTORIC_3','SF_SMALL_VEHICLE_2'] or (o.type=='EMPTY' and o.name.startswith('SF_LOW_ROOFS_')) or (o.name.startswith('SF_SMALL_TIRE.') and int(o.name.rsplit('.',1)[1])>=8):
  for q in [o]+list(o.children_recursive):
   if q.name not in hidden:q.hide_render=True;q.hide_set(True);hidden.append(q.name)
land=s.objects['SF_FRONT_LAND'];LI=land.matrix_world.inverted();down=(LI.to_3x3()@DM.to_3x3()@Vector((0,0,-1))).normalized()
def onland(x,y):
 return land.ray_cast(LI@(DM@Vector((x,y,4))),down)[0]
def rect(x,y,w,d,a=0):
 return [Vector((x+u*math.cos(a)-v*math.sin(a),y+u*math.sin(a)+v*math.cos(a)))for u,v in [(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]]
def overlap(a,b,gap=0):
 for poly in (a,b):
  for j,p in enumerate(poly):
   e=poly[(j+1)%len(poly)]-p;axis=Vector((-e.y,e.x)).normalized();aa=[p.dot(axis)for p in a];bb=[p.dot(axis)for p in b]
   if max(aa)+gap<min(bb) or max(bb)+gap<min(aa):return False
 return True
obstacles=[];footprints=[];trees=[]
# Protect the previously authored C district and crane's low-level members.
for name in ['DT_LEFT','DT_LEFT_REAR','DT_CENTER','DT_FACADE','DT_RIGHT','DT_PAVILION','DT_TRADITIONAL','DT_TRADITIONAL_REAR']:
 o=s.objects.get(name)
 if not o:continue
 pts=[DI@ch.matrix_world@Vector(v)for ch in o.children_recursive if ch.type=='MESH' for v in ch.bound_box]
 if pts:
  x0,x1=min(p.x for p in pts),max(p.x for p in pts);y0,y1=min(p.y for p in pts),max(p.y for p in pts);obstacles.append(rect((x0+x1)/2,(y0+y1)/2,x1-x0+.15,y1-y0+.15))
for x in [-3.5,2]:
 for y in [5,12]:obstacles.append(rect(x,y,1.6,2.0 if y==5 else 3.2))
def free(poly,gap=.12):
 samples=list(poly)+[(poly[j]+poly[(j+1)%4])/2 for j in range(4)]+[sum(poly,Vector((0,0)))/4]
 return all(onland(p.x,p.y)for p in samples) and not any(overlap(poly,b,gap)for b in obstacles+[f['polygon']for f in footprints])
def roof(n,root,w,d,z,h,hip=False):
 if not hip:
  # Dense village houses have pitched gables, distinct from the two hipped halls.
  profile=[(-d*.62,z+.13),(-d*.46,z+.02),(0,z+h),(d*.46,z+.02),(d*.62,z+.13)]
  vs=[(x,y,zz)for x in [-w*.58,w*.58]for y,zz in profile]
  mesh(n+'_ROOF',vs,[(j,j+1,j+6,j+5)for j in range(4)],tile,root)
  for x in [-w/2,w/2]:mesh(n+'_GABLE',[(x,-d/2,z),(x,d/2,z),(x,0,z+h-.02)],[(0,1,2)],walls[2],root)
  for j in range(max(14,int(w/.065))):
   x=-w*.58+j*w*1.16/(max(14,int(w/.065))-1);tube(n+'_TILE',[(x,y,zz+.012)for y,zz in profile],.013,ridge,root)
  tube(n+'_RIDGE',[(-w*.64,0,z+h+.11),(-w*.48,0,z+h+.025),(w*.48,0,z+h+.025),(w*.64,0,z+h+.11)],.035,ridge,root)
  for x in [-w*.58,w*.58]:tube(n+'_GABLE_EDGE',[(x,y,zz+.02)for y,zz in profile],.026,ridge,root)
  return
 # Four rings, eaves rise at corners; hip shoulders narrow to a short ridge.
 rings=[(w*.58,d*.62,z+.17),(w*.49,d*.47,z+.04),(w*.40,d*.22,z+h*.66),(w*(.28 if hip else .49),.015,z+h)]
 vs=[]
 for xx,yy,zz in rings:vs.extend([(-xx,-yy,zz),(xx,-yy,zz),(xx,yy,zz),(-xx,yy,zz)])
 fs=[(i*4+j,i*4+(j+1)%4,(i+1)*4+(j+1)%4,(i+1)*4+j)for i in range(3)for j in range(4)]+[(12,13,14,15)]
 o=mesh(n+'_ROOF',vs,fs,tile,root)
 for sign in [-1,1]:
  for j in range(max(12,int(w/.075))):
   u=-1+2*j/(max(12,int(w/.075))-1)
   tube(n+'_TILE',[(xx*u,sign*yy,zz+.012)for xx,yy,zz in rings],.012,ridge,root)
  tube(n+'_EAVE',[(-w*.58,sign*d*.62,z+.18),(-w*.42,sign*d*.62,z+.06),(w*.42,sign*d*.62,z+.06),(w*.58,sign*d*.62,z+.18)],.027,ridge,root)
 for side in [-1,1]:
  tube(n+'_HIP',[(side*xx,yy,zz+.018)for xx,yy,zz in rings],.025,ridge,root)
  tube(n+'_HIP',[(side*xx,-yy,zz+.018)for xx,yy,zz in rings],.025,ridge,root)
 xx=rings[-1][0];tube(n+'_RIDGE',[(-xx-.13,0,z+h+.15),(-xx,0,z+h+.035),(xx,0,z+h+.035),(xx+.13,0,z+h+.15)],.035,ridge,root)
 return o
def window(n,root,x,y,z,w,h):
 box(n+'_GLASS',(x,y,z),(w,.025,h),glass,root)
 for xx in [-w/2,0,w/2]:box(n+'_FRAME',(x+xx,y-.025,z),(.027,.035,h+.06),wood,root)
 for zz in [-h/2,0,h/2]:box(n+'_FRAME',(x,y-.025,z+zz),(w+.06,.035,.026),wood,root)
def house(n,x,y,w,d,h,a=0,hall=False,tone=0):
 p=rect(x,y,w*1.20,d*1.28,a);assert free(p,.04),n
 root=empty(n,D,(x,y,1.25));root.rotation_euler.z=a;root['role']='harbor_hall' if hall else 'village_house'
 root['footprint']=[v for q in p for v in q];root['wall_height']=h
 box(n+'_PLINTH',(0,0,.07),(w+.10,d+.10,.14),M['stone'],root)
 box(n+'_WALL',(0,0,h/2+.07),(w,d,h),walls[tone],root)
 for side in [-1,1]:box(n+'_CORNER',(side*(w/2-.04),-d/2-.035,h/2),(.075,.065,h),M['cream'] if hall else wood,root)
 stories=2 if hall or h>1.6 else 1
 for level in range(stories):
  z=.45+level*h/stories
  for xx in [-w*.28,w*.28]:window(n,root,xx,-d/2-.018,z,w*.22,.42 if not hall else .60)
  if hall:
   box(n+'_BELT',(0,0,(level+1)*h/stories),(w+.12,d+.12,.095),wood,root)
   for xx in [-w*.40,0,w*.40]:box(n+'_PILASTER',(xx,-d/2-.05,h/2),(.075,.09,h),M['cream'],root)
 # Entry and stone step.
 box(n+'_DOOR',(0,-d/2-.024,.39),(.27 if not hall else .42,.04,.72),wood,root)
 box(n+'_STEP',(0,-d/2-.10,.065),(.47 if not hall else .68,.20,.13),M['stone'],root)
 # Side windows are real pieces, visible on oblique camera frames.
 for sign in [-1,1]:
  fr=empty(n+'_SIDE',root,(sign*w/2,0,0));fr.rotation_euler.z=sign*math.pi/2
  for level in range(stories):
   for xx in [-d*.24,d*.24]:window(n,fr,xx,-.018,.5+level*h/stories,.25,.40 if not hall else .55)
 if not hall and int(n.rsplit('_',1)[-1])%9==4:
  box(n+'_FLAT_ROOF',(0,0,h+.08),(w+.06,d+.06,.12),M['stone'],root)
  for y in [-d/2,d/2]:box(n+'_PARAPET',(0,y,h+.23),(w+.08,.09,.30),walls[tone],root)
  for x in [-w/2,w/2]:box(n+'_PARAPET',(x,0,h+.23),(.09,d+.08,.30),walls[tone],root)
  box(n+'_ROOFTOP_ROOM',(-w*.18,d*.12,h+.32),(w*.38,d*.40,.42),walls[tone],root)
 else:roof(n,root,w,d,h+.05,.46 if not hall else .70,hall)
 if hall:
  for sign in [-1,1]:
   for yy in [-d*.40,d*.40]:lathe(n+'_EAVE_POST',(sign*w*.44,yy,0),[(0,.05),(h,.05)],wood,root,8)
 footprints.append({'name':n,'polygon':p,'role':root['role']});return root
# Two prominent tiled port buildings on the right, a stepped pair as in reference.
for n,x,y,w,d,h in [('NA_HALL_REAR',8.9,5.25,2.25,1.85,2.85),('NA_HALL_FRONT',11.7,3.95,2.45,1.95,2.6)]:
 offsets=sorted([(dx*.2,dy*.2)for dx in range(-8,9)for dy in range(-8,9)],key=lambda q:q[0]**2+q[1]**2)
 for dx,dy in offsets:
  if free(rect(x+dx,y+dy,w*1.20,d*1.28),.04):house(n,x+dx,y+dy,w,d,h,hall=True,tone=1);break
 else:raise RuntimeError('No grounded site for '+n)
# Maintain a waterfront service street and a clear route between crane posts.
obstacles.append(rect(7.8,1.65,12.2,1.35))
# Screen-organized candidates become fixed local-space geometry, never camera followers.
rng=random.Random(151028);candidates=[]
for row,yy in enumerate([654,685,716,747,778]):
 for j in range(14):
  xx=902+j*43+(row%2)*20
  candidates.append((xx,yy+rng.uniform(-3,3)))
# Smaller buildings follow the narrow right bend up to NA.
candidates += [(x,y)for y in [577,604,630]for x in [1390,1434,1478,1522]]
candidates += [(x+(j%2)*14,y)for j,y in enumerate(range(634,806,17))for x in range(930,1530,23)]
for xx,yy in candidates:
 p=uvpoint(xx,yy);w=rng.uniform(1.00,1.25);d=rng.uniform(1.04,1.34);h=rng.uniform(.70,1.08);a=rng.choice([0,0,math.pi/2])
 poly=rect(p.x,p.y,w*1.20,d*1.28,a)
 if not free(poly,.09):continue
 house('NA_HOUSE_%02d'%sum(f['role']=='village_house'for f in footprints),p.x,p.y,w,d,h,a,tone=rng.randrange(4))
 if sum(f['role']=='village_house'for f in footprints)>=44:break
# Three restrained flat-roof masonry infills amongst the gabled village.
for i,(xx,yy)in enumerate([(1280,648),(1410,619),(1370,688)]):
 p=uvpoint(xx,yy);w,d=1.05,.90;poly=rect(p.x,p.y,w+.18,d+.18)
 if not free(poly,.12):continue
 root=empty('NA_MASONRY_'+str(i),D,p);root['role']='masonry_infill';root['footprint']=[v for q in poly for v in q]
 box('NA_MASONRY_WALL',(0,0,.98),(w,d,1.96),walls[2],root)
 for z in [.52,1.25]:
  for x in [-.3,.3]:window('NA_MASONRY_WINDOW',root,x,-d/2-.02,z,.20,.36)
 for y in [-d/2,d/2]:box('NA_MASONRY_PARAPET',(0,y,2.05),(w+.10,.10,.20),M['cream'],root)
 footprints.append({'name':root.name,'polygon':poly,'role':'masonry_infill'})
# Remove old lollipop trees only where the new district footprint occupies them.
for o in s.objects:
 if o.type=='MESH' and o.name.startswith(('SF_TREE_TRUNK','SF_TREE_CROWN')) and not o.hide_render:
  p=DI@o.matrix_world@(sum((v.co for v in o.data.vertices),Vector())/len(o.data.vertices))
  if any(overlap(rect(p.x,p.y,.6,.6),f['polygon'])for f in footprints):o.hide_render=True;o.hide_set(True);hidden.append(o.name)
# Plant small groups in the alleys and on the waterside, leaving building entrances open.
for i in range(240):
 px=rng.uniform(990,1630);py=rng.uniform(595,790);p=uvpoint(px,py);poly=rect(p.x,p.y,.65,.65)
 if not free(poly,.16) or any((p-q).length<.65 for q in trees):continue
 h=rng.uniform(.42,.70);root=empty('NA_TREE',D,p);root['role']='tree'
 lathe('NA_TREE_TRUNK',(0,0,0),[(0,.045),(h,.028)],M['bark'],root,8)
 for j in range(4):
  a=j*2.4;sphere('NA_TREE_CROWN',(math.cos(a)*.15,math.sin(a)*.15,h+.10+(j%2)*.13),.22,greens[i%3],root)
 trees.append(p)
 if len(trees)>=32:break
# A detailed blue/cream truck on the right service street.
root=empty('NA_PARKED_TRUCK',D,(11.7,1.55,1.25));root['role']='parked_truck'
box('NA_TRUCK_CHASSIS',(0,0,.24),(1.65,.62,.16),M['navy'],root)
box('NA_TRUCK_LOAD',(-.22,0,.70),(1.04,.65,.76),M['cream'],root)
box('NA_TRUCK_STRIPE',(-.22,-.332,.67),(1.04,.018,.36),M['blue'],root)
box('NA_TRUCK_CAB',(.61,0,.55),(.48,.62,.65),M['blue'],root)
box('NA_TRUCK_WINDSCREEN',(.86,0,.70),(.025,.51,.28),glass,root)
for sign in [-1,1]:
 box('NA_TRUCK_WINDOW',(.61,sign*.319,.73),(.32,.02,.23),glass,root)
 for x in [-.5,.59]:
  o=lathe('NA_TRUCK_WHEEL',(0,0,0),[(-.075,.17),(.075,.17)],M['roof'],root,16);o.location=(x,sign*.35,.17);o.rotation_euler.x=math.pi/2
 box('NA_TRUCK_LIGHT',(.875,sign*.2,.43),(.025,.1,.11),M['white'],root)
# Thin street paving and regularly spaced bollards sit wholly on the existing land.
for x in [7.0,8.5,10,11.5,13]:
 if onland(x,.80):lathe('NA_QUAY_BOLLARD',(x,.80,1.25),[(0,.06),(.26,.05),(.29,.08)],wood,D,12)
for x in [6.5,10.0,13.5]:
 if onland(x,2.15):
  lathe('NA_STREET_LAMP',(x,2.15,1.25),[(0,.065),(.12,.045),(1.4,.025)],M['roof'],D,12);sphere('NA_LAMP_GLOBE',(x,2.15,2.68),.10,M['cream'])
for f in footprints:f['polygon']=[list(p)for p in f['polygon']]
bpy.context.view_layer.update()
record={'source':bpy.data.filepath,'output':str(OUT),'hidden_original_objects':hidden,'footprints':footprints,'trees':len(trees),'new_objects':[o.name for o in col.objects],'scope':'NA static village, paired harbor halls, right parked truck and plants. Existing C district, camera, title, clouds, water and all actor animations preserved.'}
(R/f'review/na-district-build-{version}.json').write_text(json.dumps(record,indent=2))
s.frame_set(156)
for screen in bpy.data.screens:
 for ar in screen.areas:
  if ar.type=='VIEW_3D':ar.spaces.active.region_3d.view_perspective='CAMERA';ar.spaces.active.shading.type='MATERIAL'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT));print('NA_BUILD',len(footprints),'buildings',len(trees),'trees',len(col.objects),'objects')
