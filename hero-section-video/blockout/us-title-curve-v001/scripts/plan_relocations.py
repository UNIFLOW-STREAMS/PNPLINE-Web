import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.geometry import convex_hull_2d
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R.parent/'curvature-rework-v001/scripts'))
from mapping import surface,normal,CENTER
candidate=R/'pnpline-us-title-curve-v001.blend'
bpy.ops.wm.open_mainfile(filepath=str(R.parent/'us-city-density-v001/pnpline-us-city-density-v001.blend'))
s=bpy.context.scene;s.frame_set(349);U=s.objects['US_FRAME'];I=U.matrix_world.inverted()
with bpy.data.libraries.load(str(candidate),link=False)as(a,b):b.objects=['UST_LETTER_'+l for l in 'USA']
for o in b.objects:s.collection.objects.link(o);o.parent=U
for l in 'USA':
 for n in [f'UC_LETTER_{l}',f'UC_AR_LETTER_PLINTH_{l}',f'CV_FOUNDATION_LETTER_{l}']:s.objects[n].hide_render=True
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
def design(x,y):return(.8480480909*x+.5299192667*y-19.6070099,-.5299192667*x+.8480480909*y+6.6222191)
def params(p):
 d=p-CENTER;h=math.hypot(d.x,d.y);a=math.atan2(h,d.z)*140
 return(d.x/h*a,d.y/h*a)if h else(0,0)
def hull(v):
 v=[Vector(x)for x in v];return[list(v[i])for i in convex_hull_2d(v)]
def sat(a,b,gap=.20):
 for p in [a,b]:
  for q,r in zip(p,p[1:]+p[:1]):
   x,y=q[1]-r[1],r[0]-q[0];l=math.hypot(x,y)
   if l<1e-8:continue
   x/=l;y/=l;aa=[k[0]*x+k[1]*y for k in a];bb=[k[0]*x+k[1]*y for k in b]
   if max(aa)+gap<min(bb)or max(bb)+gap<min(aa):return False
 return True
def mesh(o):
 ev=o.evaluated_get(deps);me=ev.to_mesh();T=I@ev.matrix_world;v=[T@p.co for p in me.vertices];f=[tuple(p.vertices)for p in me.polygons];ev.to_mesh_clear();return v,f
def F(x,y,z):return Matrix.Translation(surface(x,y,z))@Vector((0,0,1)).rotation_difference(normal(x,y)).to_matrix().to_4x4()
rows=json.loads((R/'review/layout-source.json').read_text());coll=json.loads((R/'review/layout-collisions.json').read_text())['collision_roots']
moved=[k for k in coll if k!='US_FRAME'];footprints=[]
for r in rows:
 if r['name']in moved or 'LETTER'in r['name']:continue
 pts=[params(I@s.objects[n].matrix_world@Vector(p))for n in r['parts']for p in s.objects[n].bound_box if not s.objects[n].hide_render]
 if pts:footprints.append((r['name'],hull(pts)))
titlev=[];titlef=[]
for l in 'USA':
 v,f=mesh(s.objects['UST_LETTER_'+l]);k=len(titlev);titlev+=v;titlef.extend(tuple(i+k for i in p)for p in f)
title=BVHTree.FromPolygons(titlev,titlef)
ground=[]
for n in ['US_LAND_TERRACE','CE_NY_CURVED_LAND']:
 v,f=mesh(s.objects[n]);ground.append(BVHTree.FromPolygons(v,f))
roadnames=[r['name']for r in json.loads((R.parent/'us-city-density-v001/review/us-survey.json').read_text())['protected_road_port_objects']]
roadnames+= [o.name for o in s.objects if o.name.startswith('CE_STREET_FURNITURE')or o.name=='CE_NY_COAST_PROMENADE']
roadv=[];roadf=[]
for n in roadnames:
 o=s.objects[n]
 if o.hide_render or o.type not in {'MESH','CURVE','FONT'}:continue
 v,f=mesh(o);k=len(roadv);roadv+=v;roadf.extend(tuple(i+k for i in p)for p in f)
roads=BVHTree.FromPolygons(roadv,roadf)
preferred=[(-21,47),(-15,47),(-6,52),(3,51),(16,49),(-1,62),(-16,70),(-27,69)]
grid=[(x,y)for y in range(46,112,2)for x in range(-48,56,2)]
relocations=[]
for rootname in moved:
 root=s.objects[rootname];old=next(list(root[k])for k in('ce_anchor','cv_anchor','usd_anchor')if k in root);token=rootname.removesuffix('_ROOT')
 extras=[o.name for o in s.objects if o.name in {token+'_FOUNDATION',token+'_PLAZA'}]
 parts=[o for o in root.children_recursive if o.type=='MESH'and not o.hide_render]+[s.objects[n]for n in extras]
 vertices=[];faces=[]
 for o in parts:
  v,f=mesh(o);k=len(vertices);vertices+=v;faces.extend(tuple(i+k for i in p)for p in f)
 # Only the plan-view boundary can define an extreme after a rigid move.
 sourcepoly=hull([params(p)for p in vertices]);boundary=[surface(*p,old[2])for p in sourcepoly]
 print('FOOTPRINT',rootname,sourcepoly,flush=True)
 ordered=sorted(grid,key=lambda p:math.dist(design(*p),old[:2]))
 for dx,dy in preferred+ordered:
  x,y=design(dx,dy);D=F(x,y,old[2])@F(*old[:3]).inverted();poly=hull([params(D@p)for p in boundary])
  if any(sat(poly,p)for n,p in footprints):continue
  samples=poly+[(sum(p[0]for p in poly)/len(poly),sum(p[1]for p in poly)/len(poly))]
  for a,b in zip(poly,poly[1:]+poly[:1]):samples.extend((a[0]+(b[0]-a[0])*t/4,a[1]+(b[1]-a[1])*t/4)for t in range(1,4))
  good=True
  for px,py in samples:
   n=normal(px,py);origin=surface(px,py,70);hits=[g.ray_cast(origin,-n,90)[0]for g in ground];hs=[(h-CENTER).length-140 for h in hits if h is not None]
   if not hs or abs(max(hs)-.68)>.04 or roads.ray_cast(origin,-n,90)[0]is not None:good=False;break
  if not good:continue
  v=[D@p for p in vertices]
  candidate_tree=BVHTree.FromPolygons(v,faces)
  if title.overlap(candidate_tree)or roads.overlap(candidate_tree):continue
  relocations.append({'root':rootname,'design_xy':[dx,dy],'extras':extras});footprints.append((rootname,poly));print('PLACE',rootname,dx,dy,flush=True);break
 else:raise RuntimeError('No clear destination '+rootname)
(R/'scripts/relocations.json').write_text(json.dumps(relocations,indent=2))
