"""Read-only exact-water-mask and radial footprint survey of current Shanghai."""
import bpy,ast,array,json,hashlib,math
from pathlib import Path
from collections import Counter,defaultdict
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'review';OUT.mkdir(exist_ok=True)
SOURCE=ROOT.parent/'cn-unified-curvature-v001/pnpline-cn-unified-curvature-v001.blend'
SHA='f0f07fcbbd00f9f3c2d3402092684e6326610ffcf65678a33490ad5d86f4b978'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA
previous=json.loads((SOURCE.parent/'delivery.json').read_text());C=Vector(previous['sphere']['center']);R=previous['sphere']['radius']
groups=json.loads((SOURCE.parent/'review/static-original-clusters.json').read_text())['rigid_clusters']
placements={r['id']:r for r in previous['static_clusters']}
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.context.scene;s.frame_set(0);D=s.objects['SF_CN_LAYOUT'];I=D.matrix_world.inverted()
defs=ast.parse((ROOT.parent/'cn-us-integrated-v001/scripts/audit_geometry.py').read_text())
exec(compile(ast.Module(body=[n for n in defs.body if isinstance(n,ast.FunctionDef)and n.name in {'geometry','digest','simple','material_signature'}],type_ignores=[]),'helpers','exec'),globals())

def vec(p):return [float(v)for v in p]
def mat(M):return [list(r)for r in M]
def box(points):return {'min':[min(v[i]for v in points)for i in range(3)],'max':[max(v[i]for v in points)for i in range(3)]}
def localmesh(o):
 T=I@o.matrix_world
 if o.type=='MESH':return [T@v.co for v in o.data.vertices],[tuple(p.vertices)for p in o.data.polygons]
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();vs=[T@v.co for v in me.vertices];fs=[tuple(p.vertices)for p in me.polygons];ev.to_mesh_clear();return vs,fs
def radial(p):return C+(p-C).normalized()*R
def hull(points):
 points=sorted(set((round(p[0],6),round(p[1],6))for p in points))
 if len(points)<=2:return points
 def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
 lower=[];upper=[]
 for p in points:
  while len(lower)>1 and cross(lower[-2],lower[-1],p)<=0:lower.pop()
  lower.append(p)
 for p in reversed(points):
  while len(upper)>1 and cross(upper[-2],upper[-1],p)<=0:upper.pop()
  upper.append(p)
 return lower[:-1]+upper[:-1]
def inside(p,poly):
 x,y=p;hit=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a[1]>y)!=(b[1]>y)and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:hit=not hit
 return hit
def segment_distance(p,a,b):
 dx=b[0]-a[0];dy=b[1]-a[1];length=dx*dx+dy*dy
 t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/length))if length else 0
 return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
def edge_distance(p,poly):return min(segment_distance(p,a,b)for a,b in zip(poly,poly[1:]+poly[:1]))
def area(poly):return sum(a[0]*b[1]-b[0]*a[1]for a,b in zip(poly,poly[1:]+poly[:1]))*.5

water=s.objects['SF_BASIN_WATER_SURFACE'];wv,wf=localmesh(water);wt=BVHTree.FromPolygons(wv,wf)
edges=Counter(tuple(sorted((a,b)))for f in wf for a,b in zip(f,f[1:]+f[:1]));adj=defaultdict(list)
for (a,b),count in edges.items():
 if count==1:adj[a].append(b);adj[b].append(a)
assert all(len(v)==2 for v in adj.values()),Counter(len(v)for v in adj.values())
unseen=set(adj);loops=[]
while unseen:
 start=next(iter(unseen));current=start;last=None;indices=[]
 while current not in indices:
  indices.append(current);unseen.discard(current);following=next(v for v in adj[current]if v!=last);last,current=current,following
 loops.append([vec(wv[i])for i in indices])
loops.sort(key=lambda p:abs(area(p)),reverse=True)
assert len(loops)==2,len(loops)
outer=[[p[0],p[1]]for p in loops[0]];island=[[p[0],p[1]]for p in loops[1]]
water_related=['SF_BASIN_WATER_SURFACE','SF_ISLAND_EDGE_CURVED','DT_WATERFRONT_WALK','WB_STONE_ARCH_BRIDGE']
protected={}
for name in water_related:
 o=s.objects[name]
 protected[name]={'type':o.type,'parent':o.parent.name if o.parent else None,'basis':mat(o.matrix_basis),'parent_inverse':mat(o.matrix_parent_inverse),'world':mat(o.matrix_world),
  'geometry':geometry(o.data)if o.data else None,'materials':[m.name for m in o.data.materials]if o.data and hasattr(o.data,'materials')else [],
  'hide_render':o.hide_render,'hide_viewport':o.hide_viewport}
water_materials={m.name:material_signature(m)for m in water.data.materials}

records=[];all_objects={}
for group in groups:
 vs=[];members=[]
 for name in group['visible_geometry']:
  o=s.objects[name]
  if o.hide_render:continue
  v,f=localmesh(o);vs.extend(v);members.append(name)
  all_objects[name]={'bounds':box(v),'matrix_local':mat(I@o.matrix_world),'parent':o.parent.name if o.parent else None}
 if not vs:continue
 a=placements[group['id']]['target_anchor'];foot=hull([radial(p)for p in vs])
 r={'id':group['id'],'category':group['category'],'members':members,'roots':placements[group['id']]['roots'],
    'ground_anchor':a,'normal':placements[group['id']]['target_normal'],'bounds':box(vs),
    'radial_footprint_xy':foot,'footprint_bounds':[min(p[0]for p in foot),max(p[0]for p in foot),min(p[1]for p in foot),max(p[1]for p in foot)],
    'height_from_radial_ground':max((p-C).length-R for p in vs)}
 records.append(r)
selected=[r for r in records if r['id'].startswith(('SF_HIGHRISE_','SF_SPHERE_TOWER','SF_OPEN_TOWER','SF_STEP_TOWER','SF_TALLEST_TOWER','DT_LEFT','DT_CENTER','DT_FACADE','DT_RIGHT','DT_PAVILION','DT_TRADITIONAL','NA_HOUSE','NA_HALL','SF_CHINA_'))]
architecture=[r for r in records if r['category']not in {'tree','shrub','rock','floating_cloud','bollard','fender','port_lamp','street_lamp'}]
def occupied(p,margin=.22):
 for r in architecture:
  x0,x1,y0,y1=r['footprint_bounds']
  if not(x0-margin<=p[0]<=x1+margin and y0-margin<=p[1]<=y1+margin):continue
  poly=r['radial_footprint_xy']
  if inside(p,poly)or edge_distance(p,poly)<margin:return True
 return False
def water_hit(x,y):return wt.ray_cast(Vector((x,y,100)),Vector((0,0,-1)))[0]is not None
zones={'island':[-14,8,17,29],'bund':[-27,-4,2.1,14.2],'oldtown':[-9.5,13.5,2.1,16.5]}
free={}
for zone,(x0,x1,y0,y1)in zones.items():
 points=[];x=x0
 while x<=x1:
  y=y0
  while y<=y1:
   p=(x,y)
   if (zone!='island'or(inside(p,island)and edge_distance(p,island)>.55))and not water_hit(x,y)and not occupied(p):
    corners=[(x+sx*.5,y+sy*.4)for sx in [-1,1]for sy in [-1,1]]
    if all(not water_hit(*q)and not occupied(q,.18)and(zone!='island'or inside(q,island))for q in corners):points.append([round(x,3),round(y,3)])
   y+=.5
  x+=.5
 free[zone]=points
report={'source':str(SOURCE),'sha256':SHA,'sphere':previous['sphere'],'frame':0,
 'water':{'object':water.name,'bounds':box(wv),'loops':loops,'outer_boundary_xy':outer,'dry_island_boundary_xy':island,
          'outer_area_xy':abs(area(outer)),'dry_island_area_xy':abs(area(island)),'water_area_xy':abs(area(outer))-abs(area(island)),
          'geometry':geometry(water.data),'native_vertex_count':len(water.data.vertices),'face_count':len(water.data.polygons),'matrix_local':mat(I@water.matrix_world)},
 'protected_waterway_objects':protected,'protected_water_materials':water_materials,
 'selected_architecture':selected,'all_rigid_cluster_footprints':records,'objects':all_objects,
 'candidate_fill_samples_for_1m_by_0_8m_footprints':free,
 'notes':['Water surface/loop vertices, topology, matrix, visibility and materials must stay exact.',
 'Use actual water BVH as forbidden mask for every building/tree footprint; do not enlarge/fill the island or regenerate river.',
 'Radial footprint hulls include full existing architecture, including title letters; these are conservative masks.',
 'Sample points are proposed footprint centres, not final placements; preserve street gaps and run final3D collision tests.',
 'Original port lies below y1.7; keep front/Bund additions y>=2.1. Oriental Pearl must retain its existing scale.']}
(OUT/'shanghai-survey.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('SHANGHAI_SURVEY '+json.dumps({'water':{k:report['water'][k]for k in ['bounds','outer_area_xy','dry_island_area_xy','water_area_xy','native_vertex_count','face_count']},
 'loop_sizes':[len(p)for p in loops],'free_samples':{k:len(v)for k,v in free.items()},
 'heroes':[{k:r[k]for k in ['id','ground_anchor','footprint_bounds','height_from_radial_ground']}for r in selected if r['id']in ['SF_SPHERE_TOWER','SF_OPEN_TOWER','SF_STEP_TOWER','SF_TALLEST_TOWER']]},indent=2),flush=True)
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA
