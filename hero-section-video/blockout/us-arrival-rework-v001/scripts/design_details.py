"""Arrival-facing civic placement and differentiated, static architectural details."""
import ast,math,re
from pathlib import Path
import bpy
from mathutils import Vector,Matrix

def apply(cfg,solid):
 s=bpy.context.scene;city=s.objects['UC_CITY_DISTRICT'];u=s.objects['US_FRAME']
 # Reuse the existing deterministic geometry helpers without executing the city builder.
 source=Path(__file__).resolve().parents[2]/'us-city-concept-v001/scripts/build_city.py'
 tree=ast.parse(source.read_text())
 ns=dict(bpy=bpy,math=math,Vector=Vector,U=u,city=city,owner='us-city-concept-v001',cols={c.name:c for c in bpy.data.collections})
 names={'own','mesh','box','cylinder','beam','line','batch_boxes'}
 exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(source),'exec'),ns)
 mesh,box,cylinder,beam,line=[ns[n] for n in ['mesh','box','cylinder','beam','line']]
 mats=bpy.data.materials;ivory=mats['UC_IVORY'];stone=mats['UC_LIMESTONE'];metal=mats['UC_SILVER'];patina=mats['UC_VERDIGRIS'];dark=mats['UC_WINDOWS']
 civic=bpy.data.objects.new('UC_AR_CIVIC_GROUP',None);ns['own'](civic,'CIVIC_AND_BRIDGE',u)
 civic.matrix_local=Matrix.Translation(Vector(cfg['civic_anchor']))@Matrix.Scale(cfg['civic_scale'],4)@Matrix.Translation(Vector((-29,-41,-.7)))
 for o in list(s.objects):
  if o.name.startswith('UC_CIVIC') or (o.parent==u and o.name.startswith('UC_TREE') and o.type=='MESH' and sum(v.co.x for v in o.data.vertices)/max(1,len(o.data.vertices))>22):o.parent=civic
  if o.name.startswith(('UC_CIVIC_DOME','UC_CIVIC_LANTERN','UC_CIVIC_FINIAL')):o.location.z+=1.5
  if o.name=='UC_CIVIC_DRUM':
   for v in o.data.vertices:v.co.z=4.95+(v.co.z-4.95)*(2.6/1.1)
 footprint=[civic.matrix_local@Vector((x,y,.68)) for x,y in [(22,33.3),(36,33.3),(36,48.7),(22,48.7)]]
 solid('UC_AR_CIVIC_FOUNDATION',[(p.x,p.y) for p in footprint],-18,footprint[0].z,stone,u)
 # Lower shore terrace breaks the exposed quay into two grounded levels.
 cx,cy,cz=cfg['civic_anchor'];lower=[(p.x+(-1.0 if p.x<cx else 1.0),p.y+(-1.0 if p.y<cy else 1.0)) for p in footprint]
 solid('UC_AR_CIVIC_LOWER_TERRACE',lower,-18,cz-1.6,stone,u)
 # A pediment, deep portico cornice and dome drum rhythm distinguish the civic building.
 mesh('UC_AR_CIVIC_PEDIMENT',[(x,y,z) for y in [39.75,40.25] for x,z in [(25.9,5.15),(32.1,5.15),(29,6.45)]],[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)],ivory,'CIVIC_AND_BRIDGE',civic,.035)
 box('UC_AR_CIVIC_PORTICO',(29,40.0,5.05),(6.5,1.25,.28),ivory,'CIVIC_AND_BRIDGE',civic)
 for i in range(20):
  a=2*math.pi*i/20
  cylinder('UC_AR_CIVIC_DRUM_COLUMN',(29+2.12*math.cos(a),43+2.12*math.sin(a),6.4),.065,2.3,ivory,'CIVIC_AND_BRIDGE',civic,n=10)
 for x in [21.78,36.22]:
  for y in [41.1,42.05,43,43.95,44.9]:
   for z in [2.0,3.65]:
    box('UC_AR_CIVIC_SIDE_WINDOW',(x,y,z),(.035,.42,.82),dark,'CIVIC_AND_BRIDGE',civic,0)
    box('UC_AR_CIVIC_SIDE_LINTEL',(x-.02,y,z+.48),(.12,.59,.12),ivory,'CIVIC_AND_BRIDGE',civic,0)
 # Small additional edge roundover is independent of the original baked letter contour.
 for ch in 'USA':
  o=s.objects['UC_LETTER_'+ch];m=o.modifiers.new('Arrival silver edge roundover','BEVEL');m.width=.045;m.segments=3;m.limit_method='ANGLE';m.angle_limit=.5
 # Existing window lines used an approximate taper and lay inside the actual glass hull.
 # Place the existing lines on the exact piecewise facade profile with a small standoff.
 def radius(z):
  levels=[(.7,2.5),(2,2.4),(18,1.65),(21,1.)]
  for (za,ra),(zb,rb) in zip(levels,levels[1:]):
   if z<=zb:return ra+(rb-ra)*(z-za)/(zb-za)
  return 1.
 for o in s.objects:
  if o.name.startswith('UC_GLASS_SPIRE_FLOOR'):
   pts=o.data.splines[0].points;z=pts[0].co.z;r=radius(z)+.025
   for p,(a,b) in zip(pts,[(-1,-1),(1,-1),(1,1),(-1,1),(-1,-1)]):p.co=(10+a*r,44+b*r,z,1)
  elif o.name.startswith('UC_GLASS_SPIRE_MULLION'):
   sp=o.data.splines[0];first=sp.points[0].co.copy();t=(first.x-10)/2.5;side=-1 if first.y<44 else 1
   sp.points.add(2)
   for p,z in zip(sp.points,[.7,2,18,21]):r=radius(z)+.035;p.co=(10+t*r,44+side*r,z,1)
 # Diagonal facets and a crown are distinct from the limestone tower's vertical setbacks.
 for side in [-1,1]:
  for za,zb,sgn in [(2,10,-1),(10,18,1),(18,21,-1)]:
   ra,rb=radius(za)+.06,radius(zb)+.06
   line('UC_AR_GLASS_DIAGRID',[(20+sgn*ra,44+side*ra,za),(20-sgn*rb,44+side*rb,zb)],.055,metal,'SKYLINE',city)
 cylinder('UC_AR_GLASS_CROWN',(20,44,21.2),1.05,.32,metal,'SKYLINE',city,n=32)
 # Four authored roof silhouettes on the front street: mansards, pediments, water tanks.
 for idx,name in enumerate(['UC_BLOCK_00_00','UC_BLOCK_00_02','UC_BLOCK_00_04','UC_BLOCK_01_01','UC_BLOCK_01_03','UC_BLOCK_01_06']):
  previous_objects=set(s.objects)
  o=s.objects[name];vs=[v.co for v in o.data.vertices];x=(min(v.x for v in vs)+max(v.x for v in vs))/2;y=(min(v.y for v in vs)+max(v.y for v in vs))/2
  w=max(v.x for v in vs)-min(v.x for v in vs);d=max(v.y for v in vs)-min(v.y for v in vs);z=max(v.z for v in vs)
  if idx%3!=2:
   pts=[(x+a*w*.53,y+b*d*.53,z+.12) for a,b in [(-1,-1),(1,-1),(1,1),(-1,1)]]+[(x+a*w*.32,y+b*d*.32,z+1.0) for a,b in [(-1,-1),(1,-1),(1,1),(-1,1)]]
   mesh('UC_AR_MANSARD',pts,[(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],patina if idx%2==0 else dark,'URBAN_BLOCKS',city,.02)
   for xx in [x-w*.22,x+w*.22]:
    box('UC_AR_DORMER',(xx,y-d*.43,z+.57),(.46,.30,.6),ivory,'URBAN_BLOCKS',city)
    box('UC_AR_DORMER_GLASS',(xx,y-d*.50-.01,z+.55),(.26,.03,.37),dark,'URBAN_BLOCKS',city,0)
  else:
   cylinder('UC_AR_WATER_TANK',(x,y,z+1.1),.53,1.1,stone,'URBAN_BLOCKS',city,n=16)
   cylinder('UC_AR_TANK_CAP',(x,y,z+1.75),.60,.25,metal,'URBAN_BLOCKS',city,r2=0,n=16)
   for a,b in [(-1,-1),(1,-1),(1,1),(-1,1)]:beam('UC_AR_TANK_STILT',(x+a*.34,y+b*.34,z+.12),(x+a*.34,y+b*.34,z+.65),.07,metal,'URBAN_BLOCKS',city)
  # Pilasters and rounded entrance heads create actual depth on the front stone facades.
  for xx in [x-w*.46,x+w*.46]:box('UC_AR_PILASTER',(xx,y-d/2-.07,(.7+z)/2),(.14,.18,z-.7),ivory,'URBAN_BLOCKS',city,.015)
  box('UC_AR_ENTRY_RECESS',(x,y-d/2-.08,1.25),(.65,.05,1.0),dark,'URBAN_BLOCKS',city,0)
  for j in range(9):
   a,b=math.pi*j/9,math.pi*(j+1)/9
   beam('UC_AR_ENTRY_ARCH',(x+.39*math.cos(a),y-d/2-.16,1.65+.39*math.sin(a)),(x+.39*math.cos(b),y-d/2-.16,1.65+.39*math.sin(b)),.12,ivory,'URBAN_BLOCKS',city)
  for detail in set(s.objects)-previous_objects:detail['ar_source_block']=name
 # Bring the left/central low-rise street onto its own lower waterfront terrace.
 # The right-hand blocks remain behind the protected truck route.
 fronts={f'UC_BLOCK_00_{i:02}' for i in range(7)}
 for o in list(s.objects):
  if any(o.name==name or o.name.startswith(name+'_') for name in fronts) or o.get('ar_source_block') in fronts:o.location+=Vector(cfg['front_row_shift'])
 solid('UC_AR_FRONT_STREET_TERRACE',[(-26.5,17.5),(3.6,17.5),(3.6,22),(-26.5,22)],-40,-.92,stone,city)
 bpy.context.view_layer.update()
