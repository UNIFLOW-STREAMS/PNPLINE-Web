"""Read-only US geometry, spherical parameter-space and protected-area survey."""
import bpy,ast,array,json,hashlib,math,re,sys
from pathlib import Path
from collections import Counter,defaultdict
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'review';OUT.mkdir(parents=True,exist_ok=True)
SOURCE=ROOT.parent/'cn-shanghai-density-v001/pnpline-cn-shanghai-density-v001.blend'
SHA='c0f7d784dbb67562614cfd46cc3a493418de6f6712db2aef2d8933fbee5672ce'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA
sys.path.insert(0,str(ROOT.parent/'curvature-rework-v001/scripts'))
from mapping import surface,normal,CENTER
defs=ast.parse((ROOT.parent/'cn-shanghai-density-v001/scripts/survey_shanghai.py').read_text())
exec(compile(ast.Module(body=[n for n in defs.body if isinstance(n,ast.FunctionDef)and n.name in {'hull','inside','segment_distance','edge_distance','area'}],type_ignores=[]),'footprint_helpers','exec'),globals())
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.context.scene;s.frame_set(349)
U=s.objects['US_FRAME'];I=U.matrix_world.inverted();C=CENTER

def mat(m):return [list(r)for r in m]
def vec(v):return [float(x)for x in v]
def under(o,names):
 while o:
  if o.name in names:return True
  o=o.parent
 return False
def visible(o):return o.type in {'MESH','CURVE','FONT'} and not o.hide_render and not o.hide_viewport and not o.hide_get()
def params(p):
 d=p-C;r=d.length;h=math.hypot(d.x,d.y);a=math.atan2(h,d.z)
 return [d.x/h*(a*140),d.y/h*(a*140),r-140]if h>1e-8 else [0,0,r-140]
def bounds(vs):return {'min':[min(v[i]for v in vs)for i in range(3)],'max':[max(v[i]for v in vs)for i in range(3)]}if vs else None
def mesh(o):
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();M=I@ev.matrix_world
 v=[M@p.co for p in me.vertices];f=[tuple(p.vertices)for p in me.polygons];ev.to_mesh_clear();return v,f
def member_list(root):return [root]+list(root.children_recursive)
def category(root):
 n=root.name
 if 'CENTRAL_TOWER'in n:return 'empire_state'
 if 'GLASS_TOWER'in n or 'WTC'in n or 'WORLD_TRADE'in n:return 'one_world_trade'
 if root.get('ce_role')=='building_root':return 'expansion_building'
 if n.startswith('CV_UC_BLOCK_'):return 'original_building'
 if 'CIVIC'in n:return 'civic'
 if 'LETTER'in n:return 'title'
 if 'LIBERTY'in n:return 'liberty'
 return 'other_static'

us=[o for o in s.objects if under(o,{'US_FRAME'})]
roots=[o for o in us if o.type=='EMPTY'and(o.get('ce_role')=='building_root' or o.get('cv_anchor')is not None)]
cache={};groups=[];seen=set()
for root in roots:
 members=[o for o in member_list(root)if visible(o)]
 if not members:continue
 vs=[];mnames=[]
 for o in members:
  if o.name not in cache:cache[o.name]=mesh(o)
  vs.extend(cache[o.name][0]);mnames.append(o.name);seen.add(o.name)
 pp=[params(p)for p in vs];fo=hull(pp)
 anchor=root.get('ce_anchor')or root.get('cv_anchor')
 if anchor:
  anchor=list(anchor);point=surface(anchor[0],anchor[1],.96 if root.get('ce_anchor')is not None else .8)
 else:
  point=sum(vs,Vector())/len(vs);anchor=params(point)
 groups.append({'root':root.name,'parent':root.parent.name if root.parent else None,'category':category(root),'members':mnames,
    'all_descendants':[o.name for o in member_list(root)],'anchor_parameter':anchor,'ground_point_local':vec(point),
    'normal_local':vec((point-C).normalized()),'matrix_world':mat(root.matrix_world),'matrix_us':mat(I@root.matrix_world),
    'bounds_local':bounds(vs),'bounds_parameter':bounds(pp),'footprint_parameter':fo,
    'height_above_surface':max(p[2]for p in pp)-.68,'radial_range':[min(p[2]for p in pp),max(p[2]for p in pp)]})
groups.sort(key=lambda r:r['root'])

terrain=[];grounds=[]
for name in ['US_LAND_TERRACE','US_QUAY','US_YARD_ROAD','CE_NY_CURVED_LAND','CE_SF_CURVED_ISLAND','CE_CHICAGO_CURVED_LAND']:
 o=s.objects.get(name)
 if not o:continue
 vs,fs=mesh(o);pp=[params(p)for p in vs]
 row={'name':name,'parent':o.parent.name if o.parent else None,'matrix_us':mat(I@o.matrix_world),'bounds_local':bounds(vs),
  'bounds_parameter':bounds(pp),'vertices':len(vs),'polygons':len(fs),'radial_range':[min(p[2]for p in pp),max(p[2]for p in pp)]}
 # Keep upper surface boundary to distinguish neighboring spherical plates and port.
 threshold=.60 if 'QUAY'not in name and 'ROAD'not in name else -100
 edges=Counter(tuple(sorted((a,b)))for f in fs if all(pp[i][2]>threshold for i in f)for a,b in zip(f,f[1:]+f[:1]))
 boundary=sorted(set(i for e,n in edges.items()if n==1 for i in e))
 adj=defaultdict(list)
 for (a,b),count in edges.items():
  if count==1:adj[a].append(b);adj[b].append(a)
 loops=[];unseen=set(adj)
 if all(len(v)==2 for v in adj.values()):
  while unseen:
   start=next(iter(unseen));current=start;last=None;indices=[]
   while current not in indices:
    indices.append(current);unseen.discard(current);following=next(v for v in adj[current]if v!=last);last,current=current,following
   loops.append([pp[i][:2]for i in indices])
 row['boundary_parameter_points']=[pp[i][:2]for i in boundary];row['boundary_loops_parameter']=loops;row['footprint_hull_parameter']=hull(pp)
 terrain.append(row)
 if name not in {'US_YARD_ROAD'}:grounds.append((name,BVHTree.FromPolygons(vs,fs)))

protected=[]
protect_tokens=('STREET','AVENUE','ROAD','RAIL','SIDEWALK','ASPHALT','MARKS','BRIDGE','QUAY','WAREHOUSE','DOCK','OUTBOUND','PORT')
for o in us:
 if not visible(o):continue
 if o.name in {r['name']for r in terrain}:continue
 role=str(o.get('pt_role',''))
 if not(o.name.startswith(('PT_','CV_FOUNDATION_WAREHOUSE'))or any(t in o.name for t in protect_tokens)or under(o,{'E08_WAREHOUSE'})):continue
 if o.name not in cache:cache[o.name]=mesh(o)
 vs,fs=cache[o.name]
 if not vs:continue
 pp=[params(p)for p in vs]
 protected.append({'name':o.name,'parent':o.parent.name if o.parent else None,'role':role or 'road_port_logistics','bounds_local':bounds(vs),
   'bounds_parameter':bounds(pp),'footprint_parameter':hull(pp)})

# Unwrapped architectural objects (if any) are explicit instead of silently omitted.
loose=[]
for o in us:
 if visible(o)and o.name not in seen and o.name.startswith(('UC_BLOCK_','UC_CENTRAL','UC_GLASS','CE_')) and not any(t in o.name for t in protect_tokens):
  if o.name not in cache:cache[o.name]=mesh(o)
  vv,_=cache[o.name];loose.append({'name':o.name,'parent':o.parent.name if o.parent else None,'bounds_parameter':bounds([params(p)for p in vv])})

frame_objects={n:{'parent':s.objects[n].parent.name if s.objects[n].parent else None,'world':mat(s.objects[n].matrix_world),'basis':mat(s.objects[n].matrix_basis),
 'type':s.objects[n].type,'action':s.objects[n].animation_data.action.name if s.objects[n].animation_data and s.objects[n].animation_data.action else None}for n in ['US_FRAME','UC_CITY_DISTRICT']if n in s.objects}
roots_info=[{'name':o.name,'parent':o.parent.name if o.parent else None,'children':len(o.children_recursive),'anchor':list(o.get('cv_anchor',o.get('ce_anchor',[])))}for o in us if o.type=='EMPTY']
primary=[r for r in groups if r['category']in {'empire_state','one_world_trade'}]
buildings=[r for r in groups if r['category']in {'original_building','expansion_building'}]
for r in primary:
 nearest=sorted(buildings,key=lambda b:math.dist(r['anchor_parameter'][:2],b['anchor_parameter'][:2]))[:12]
 r['nearest_buildings']=[{'root':b['root'],'anchor_parameter':b['anchor_parameter'],'distance':math.dist(r['anchor_parameter'][:2],b['anchor_parameter'][:2]),'height':b['height_above_surface']}for b in nearest]

# Low-cost 2m footprint candidate grid, protected by exact geometry-derived masks.
obstacles=[r['footprint_parameter']for r in groups if r['category']not in {'other_static'}]
obstacle_boxes=[(min(p[0]for p in poly),max(p[0]for p in poly),min(p[1]for p in poly),max(p[1]for p in poly))for poly in obstacles]
pv=[];pf=[]
for r in protected:
 vs,fs=cache[r['name']];offset=len(pv);pv.extend(vs);pf.extend(tuple(offset+i for i in f)for f in fs)
protected_tree=BVHTree.FromPolygons(pv,pf)
def occupied(p,margin=.22):
 for poly,b in zip(obstacles,obstacle_boxes):
  if b[0]-margin<=p[0]<=b[1]+margin and b[2]-margin<=p[1]<=b[3]+margin and(inside(p,poly)or edge_distance(p,poly)<margin):return True
 q=surface(*p,.68);n=(q-C).normalized()
 return protected_tree.ray_cast(q+n*80,-n,85)[0]is not None
def contact(x,y):
 p=surface(x,y,.68);n=(p-C).normalized();hits=[]
 for name,tree in grounds:
  q,no,ind,d=tree.ray_cast(p+n*30,-n,60)
  if q is not None:hits.append((d,name,vec(q)))
 return min(hits)if hits else None
free=[]
for x in range(-40,84,2):
 for y in range(-80,96,2):
  corners=[(x+sx,y+sy)for sx in [-1,1]for sy in [-1,1]]
  if any(occupied(p)for p in corners+[(x,y)]):continue
  hit=contact(x,y)
  if not hit or hit[1] in {'US_QUAY'}:continue
  if not all(contact(*p)for p in corners):continue
  free.append({'xy':[x,y],'terrain':hit[1]})

report={'source':str(SOURCE),'sha256':SHA,'frame':349,'coordinate_system':'US_FRAME local with exponential-map arc-distance XY parameters, inverse-mapped from actual evaluated geometry.',
 'sphere':{'center_local':vec(C),'ocean_radius':140,'main_city_top_radius':140.68,'expansion_building_base_radius':140.96,
  'mapping':'p = (0,0,-140) + (140+h)*(x/r*sin(r/140), y/r*sin(r/140), cos(r/140)); r=hypot(x,y). Local Cartesian XY differs from parameter XY.'},
 'frames':frame_objects,'root_inventory':roots_info,'groups':groups,'hero_candidates':primary,'terrain':terrain,'protected_road_port_objects':protected,
 'loose_architecture':loose,'free_2m_square_candidate_centers':free,
 'notes':['Candidate centers are overlapping choices, not final placements; actor/camera clearance is owned by animation audit.',
 'For enlarged original heroes move all children of their CV wrapper plus rebuild separate CV_FOUNDATION_<group>; wrapper origins are not their base anchor.',
 'US quay/warehouse are locally graded tangent surfaces, not a uniform sphere. Keep protected logistics objects and their underlying terrain unchanged.']}
(OUT/'us-survey.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA
print('SURVEY_READY',json.dumps({'groups':len(groups),'hero_candidates':[{k:r[k]for k in ['root','anchor_parameter','bounds_parameter','height_above_surface']}for r in primary],'terrain':[r['name']for r in terrain],'free_centers':len(free)}),flush=True)
