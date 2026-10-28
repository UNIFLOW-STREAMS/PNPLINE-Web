"""Rebuild both banks from explicit styleframe silhouette curves at f156."""
import bpy,math,json,sys
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path(__file__).resolve().parents[1];out=Path(sys.argv[sys.argv.index('--')+1]);assert not out.exists()
candidate=bpy.data.filepath;s=bpy.context.scene;s.frame_set(156)
bpy.ops.wm.open_mainfile(filepath=str(R/'review/layout-proposal-v021.blend'));s=bpy.context.scene;s.frame_set(156)
trees={o.name:[v.co.copy()for v in o.data.vertices]for o in s.objects if o.name.startswith(('SF_TREE_TRUNK','SF_TREE_CROWN'))and o.type=='MESH'}
towers={o.name:o.location.copy()for o in s.objects if o.type=='EMPTY'and o.name.startswith(('SF_HIGHRISE_','SF_SPHERE_TOWER','SF_OPEN_TOWER','SF_STEP_TOWER','SF_TALLEST_TOWER'))}
oldinner=[v.co.copy()for v in s.objects['SF_ISLAND_TOP'].data.vertices]
bpy.ops.wm.open_mainfile(filepath=candidate);s=bpy.context.scene;s.frame_set(156);D=s.objects['SF_CN_LAYOUT'];DI=D.matrix_world.inverted()
def uvpoint(px,py,z=1.25):
 cam=s.camera;fr=cam.data.view_frame(scene=s);xs=[v.x for v in fr];ys=[v.y for v in fr]
 v=Vector((min(xs)+(max(xs)-min(xs))*px/2048,max(ys)-(max(ys)-min(ys))*py/1156,fr[0].z))
 origin=DI@cam.matrix_world.translation;direction=DI.to_3x3()@cam.matrix_world.to_3x3()@v
 return origin+direction*((z-origin.z)/direction.z)
def bezier_path(start,segments):
 pts=[];a=Vector(start)
 for b,c,d in segments:
  b,c,d=map(Vector,(b,c,d))
  for j in range(40):
   t=j/40;q=a*(1-t)**3+b*3*(1-t)**2*t+c*3*(1-t)*t*t+d*t**3
   pts.append(uvpoint(q.x,q.y))
  a=d
 return pts
inner_segments=[
 ((620,590),(715,618),(830,618)),
 ((900,623),(970,620),(1020,605)),
 ((1080,586),(1135,549),(1185,548)),
 ((1220,544),(1250,548),(1265,540)),
 ((1280,530),(1250,526),(1225,525)),
 ((1180,517),(1090,513),(1050,513)),
 ((950,508),(840,505),(780,513)),
 ((700,522),(639,526),(629,548))]
outer_segments=[
 ((470,625),(490,651),(540,674)),
 ((610,699),(680,710),(750,710)),
 ((850,711),(970,713),(1040,694)),
 ((1115,673),(1170,655),(1230,634)),
 ((1300,616),(1370,604),(1370,574)),
 ((1370,543),(1310,524),(1260,522)),
 ((1160,507),(1090,502),(1010,505)),
 ((870,505),(720,500),(620,520)),
 ((550,533),(490,553),(479,583))]
rawinner=bezier_path((629,548),inner_segments);rawouter=bezier_path((479,583),outer_segments)
smooth='--smooth' in sys.argv
inner_controls=[(623,548),(630,580),(680,608),(760,626),(850,630),(950,625),(1040,608),(1120,575),(1185,546),(1235,540),(1270,542),(1280,532),(1250,518),(1190,516),(1050,512),(900,507),(780,512),(690,525)]
outer_controls=[(479,583),(480,630),(540,674),(650,702),(750,710),(900,711),(1040,694),(1150,660),(1230,634),(1320,610),(1380,580),(1370,550),(1310,524),(1260,522),(1100,502),(1010,505),(800,503),(620,520),(520,545)]
def periodic_bspline(controls):
 # Uniform cubic periodic B-spline: position, tangent and curvature are
 # continuous at every knot. No individually joined Bezier spans remain.
 result=[]
 for i in range(len(controls)):
  p0,p1,p2,p3=[Vector(controls[(i+j)%len(controls)])for j in [-1,0,1,2]]
  for k in range(24):
   t=k/24;q=(p0*(1-t)**3+p1*(3*t**3-6*t*t+4)+p2*(-3*t**3+3*t*t+3*t+1)+p3*t**3)/6
   result.append(uvpoint(q.x,q.y))
 return result
if smooth:rawinner=periodic_bspline(inner_controls);rawouter=periodic_bspline(outer_controls)
center=Vector((-5,23));N=512 if smooth else 256
def cross(a,b):return a.x*b.y-a.y*b.x
def intersect(poly,angle):
 dr=Vector((math.cos(angle),math.sin(angle)));hits=[]
 for av,bv in zip(poly,poly[1:]+poly[:1]):
  a=Vector(av[:2]);b=Vector(bv[:2]);e=b-a;den=cross(dr,e)
  if abs(den)<1e-8:continue
  t=cross(a-center,e)/den;u=cross(a-center,dr)/den
  if t>0 and -.00001<=u<=1.00001:hits.append(t)
 assert hits,(angle,'no radial crossing')
 return center+dr*max(hits)
angles=[math.tau*i/N for i in range(N)]
inner=[intersect(rawinner,a)for a in angles];outer=[intersect(rawouter,a)for a in angles]
oldcoast=[v.co.copy()for v in list(s.objects['SF_FRONT_LAND'].data.vertices)[:len(s.objects['SF_FRONT_LAND'].data.vertices)//2]]
coast=[intersect(oldcoast,a)for a in angles]
for i in range(N):
 dr=(outer[i]-center).normalized()
 if (coast[i]-center).length<(outer[i]-center).length+.7:coast[i]=outer[i]+dr*.7
def update_mesh(name,vs,faces):
 o=s.objects[name];data=bpy.data.meshes.new(name+'_traced');data.from_pydata(vs,[],faces);data.update()
 for mat in o.data.materials:data.materials.append(mat)
 o.data=data
def ring3(poly,z):return [(p.x,p.y,z if not callable(z)else z(p))for p in poly]
quads=[(i,(i+1)%N,N+(i+1)%N,N+i)for i in range(N)]
update_mesh('SF_BASIN_WATER_SURFACE',ring3(outer,.92)+ring3(inner,.92),quads)
update_mesh('SF_FRONT_LAND',ring3(coast,1.25)+ring3(outer,1.25),quads)
update_mesh('SF_COAST_FOLDED_FACE',ring3(coast,1.25)+ring3(coast,lambda p:math.sqrt(max(1,140**2-p.x*p.x-p.y*p.y))-140-.05),quads)
update_mesh('SF_BASIN_OUTER_WALL',ring3(outer,1.25)+ring3(outer,-.2),quads)
update_mesh('SF_ISLAND_WALL',ring3(inner,1.25)+ring3(inner,.1),quads)
vs=[Vector(p)for p in ring3(inner,1.25)];lookup={tuple(p):i for i,p in enumerate(vs)}
tris=tessellate_polygon([vs]);faces=[[v if isinstance(v,int)else lookup[tuple(v)]for v in tri]for tri in tris]
update_mesh('SF_ISLAND_TOP',vs,faces)
curve=s.objects['SF_ISLAND_EDGE'].data;curve.splines.clear();sp=curve.splines.new('POLY');sp.points.add(N-1);sp.use_cyclic_u=True
for v,p in zip(sp.points,inner):v.co=(p.x,p.y,1.28,1)
moved_trees=[]
for name,vs in trees.items():
 o=s.objects[name];c=sum(vs,Vector())/len(vs)
 dist,j=min(((Vector((c.x-p.x,c.y-p.y)).length,j)for j,p in enumerate(oldinner)))
 delta=Vector()
 if dist<.9:
  oldp=oldinner[j];a=math.atan2(c.y-center.y,c.x-center.x);p=intersect(rawinner,a)
  # Small inward margin under the trunk; the original randomized bank offset
  # is retained along its tangent rather than leaving trees over water.
  p-= (p-center).normalized()*.24;delta=Vector((p.x-c.x,p.y-c.y,0));moved_trees.append(name)
 for v,oldv in zip(o.data.vertices,vs):v.co=oldv+delta
 o.data.update()
def inside(p,poly):
 hit=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if(a.y>p.y)!=(b.y>p.y)and p.x<(b.x-a.x)*(p.y-a.y)/(b.y-a.y)+a.x:hit=not hit
 return hit
moved_towers={}
for name,oldpos in towers.items():
 root=s.objects[name];root.location=oldpos;bpy.context.view_layer.update()
 feet=[]
 for o in root.children_recursive:
  if o.type=='MESH':feet += [DI@o.matrix_world@v.co for v in o.data.vertices if (DI@o.matrix_world@v.co).z<1.48]
 shift=0
 while feet and not all(inside(Vector((p.x,p.y+shift)),inner)for p in feet):
  shift+=.05
  assert shift<7,(name,'cannot support tower on island')
 if shift:root.location.y+=shift;moved_towers[name]=shift
if smooth:
 common=max([moved_towers.get('SF_HIGHRISE_'+str(j),0)for j in range(8,14)])+.05
 for j in range(8,14):
  name='SF_HIGHRISE_'+str(j);s.objects[name].location=towers[name]+Vector((0,common,0));moved_towers[name]=common
bpy.context.view_layer.update();ver=out.stem.rsplit('-',1)[-1]
report={'source':candidate,'output':str(out),'method':'One periodic cubic B-spline per bank, C2 continuous at all knots, projected through unchanged f156 camera'if smooth else 'Explicit cubic Bezier silhouette tracing','inner_segments':inner_segments,'outer_segments':outer_segments,'inner_bspline_controls':inner_controls if smooth else None,'outer_bspline_controls':outer_controls if smooth else None,'trees_following_bank':moved_trees,'tower_ground_adjustments':moved_towers,'ground_ring_samples':N}
(R/f'review/title-arc-{ver}-config.json').write_text((R/f"review/title-arc-{Path(candidate).stem.rsplit('-',1)[-1]}-config.json").read_text())
(R/f'review/basin-trace-{ver}.json').write_text(json.dumps(report,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(out))
