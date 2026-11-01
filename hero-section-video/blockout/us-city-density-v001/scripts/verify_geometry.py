"""Independent read-only US city placement, radial support and collision checks.

Uses the companion audit_preservation.py source snapshot; that audit owns all
original-state/action/material/motion checks. Never saves either blend file.
"""
import bpy,ast,array,json,hashlib,math,sys
from pathlib import Path
from collections import Counter,defaultdict
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'review';BLOCKOUT=ROOT.parent
SOURCE=BLOCKOUT/'cn-shanghai-density-v001/pnpline-cn-shanghai-density-v001.blend'
CANDIDATE=ROOT/'pnpline-us-city-density-v001.blend'
SHA='c0f7d784dbb67562614cfd46cc3a493418de6f6712db2aef2d8933fbee5672ce'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA
assert CANDIDATE.exists(),CANDIDATE
candidate_hash=hashlib.sha256(CANDIDATE.read_bytes()).hexdigest()
delivery=json.loads((ROOT/'delivery.json').read_text())
survey=json.loads((OUT/'us-survey.json').read_text())
before=json.loads((OUT/'preservation-source.json').read_text());assert before['sha256']==SHA
for file,names in [(BLOCKOUT/'cn-us-integrated-v001/scripts/audit_geometry.py',{'geometry','digest','simple'}),
                   (BLOCKOUT/'cn-shanghai-density-v001/scripts/survey_shanghai.py',{'hull','inside','edge_distance','segment_distance'})]:
 tree=ast.parse(file.read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in names],type_ignores=[]),str(file),'exec'),globals())
bpy.ops.wm.open_mainfile(filepath=str(CANDIDATE));s=bpy.context.scene;s.frame_set(349)
U=s.objects['US_FRAME'];I=U.matrix_world.inverted();C=Vector((0,0,-140));old=set(before['objects']);added=set(s.objects.keys())-old

def matrix(m):return [list(r)for r in m]
def visible(o):return o.type in {'MESH','CURVE','FONT'}and not o.hide_render and not o.hide_viewport and not o.hide_get()
def under(o,names):
 while o:
  if o.name in names:return True
  o=o.parent
 return False
def params(p):
 d=p-C;r=d.length;h=math.hypot(d.x,d.y);a=math.atan2(h,d.z)
 return [d.x/h*(a*140),d.y/h*(a*140),r-140]if h>1e-8 else [0,0,r-140]
def surface(x,y,h=.68):
 r=math.hypot(x,y);a=r/140;n=Vector((x/r*math.sin(a),y/r*math.sin(a),math.cos(a)))if r>1e-9 else Vector((0,0,1))
 return C+n*(140+h)
def bounds(vs):return ([min(v[i]for v in vs)for i in range(3)],[max(v[i]for v in vs)for i in range(3)])if vs else None
def boxhit(a,b):return a is not None and b is not None and all(a[0][i]<=b[1][i]and b[0][i]<=a[1][i]for i in range(3))
def mesh_data(o):
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();M=I@ev.matrix_world
 vs=[M@v.co for v in me.vertices];fs=[tuple(p.vertices)for p in me.polygons];ev.to_mesh_clear();return vs,fs
def combine(objects):
 vs=[];fs=[];names=[]
 for o in objects:
  if not visible(o):continue
  v,f=mesh_data(o);offset=len(vs);vs.extend(v);fs.extend(tuple(offset+i for i in p)for p in f);names.extend([o.name]*len(f))
 return {'vertices':vs,'faces':fs,'names':names,'tree':BVHTree.FromPolygons(vs,fs)if fs else None,'bounds':bounds(vs)}
def angle(a,b):return math.degrees(math.atan2(a.cross(b).length,a.dot(b)))

checks=[]
def check(name,ok,**detail):checks.append({'name':name,'pass':bool(ok),**detail})
terrain_names={r['name']for r in survey['terrain']}
protected_geometry=[]
for name in terrain_names|{'EARTH_CONTINUOUS_OCEAN'}:
 o=s.objects[name];src=before['objects'][name]
 now={'geometry':geometry(o.data),'matrix_world':matrix(o.matrix_world),'matrix_basis':matrix(o.matrix_basis),'parent':o.parent.name if o.parent else None,
      'hide_render':o.hide_render,'hide_viewport':o.hide_viewport}
 for k,v in now.items():
  if json.loads(json.dumps(v))!=src[k]:protected_geometry.append({'object':name,'field':k})
check('source_file_immutable',hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA)
check('terrain_and_ocean_exact',not protected_geometry,errors=protected_geometry)
check('additions_namespaced',all(n.startswith('USD_')for n in added),count=len(added))

# Sites are rooted assemblies. Rooting may be explicit in delivery or inferred
# from the generated geometry hierarchy, to avoid trusting planned rectangles.
records=[]
for field in ['replacements','sites','tree_sites']:
 for record in delivery.get(field,[]):
  if isinstance(record,str):record={'root':record}
  root=record.get('root')or record.get('new_root')
  if not root or root not in s.objects:continue
  r=dict(record);r['root']=root;r['role']='replacement'if field=='replacements'else'tree'if field=='tree_sites'else'building'
  records.append(r)
record_roots={r['root']for r in records}
for o in s.objects:
 if o.name not in added or o.type!='EMPTY'or o.name in record_roots:continue
 if any(visible(ch)for ch in o.children):
  records.append({'root':o.name,'role':'generated','objects':[ch.name for ch in o.children_recursive]});record_roots.add(o.name)
height_records=delivery.get('height_changes',[]);relocation_records=delivery.get('relocations',[])
original_changed_roots=set()
for record in height_records+relocation_records:
 root=record.get('root')or record.get('name')
 if root and root in s.objects:
  original_changed_roots.add(root)
  r=dict(record);r['root']=root;r['role']='height_change'if record in height_records else'relocated';records.append(r)
# Reconcile with actual original group transforms if delivery omits a wrapper.
for group in survey['groups']:
 name=group['root'];o=s.objects.get(name)
 if not o or name in original_changed_roots:continue
 source=before['objects'][name]
 if matrix(o.matrix_basis)!=source['matrix_basis']and any(visible(ch)for ch in o.children_recursive):
  original_changed_roots.add(name);records.append({'root':name,'role':'changed_original'})

ground=combine([s.objects[n]for n in terrain_names if n!='US_YARD_ROAD'])
roads=combine([s.objects[r['name']]for r in survey['protected_road_port_objects']if r['name']in s.objects])
groups=[];orientation=[];contact_rows=[];contact_errors=[];road_errors=[];water_errors=[];heights=[];dimension_errors=[];seen_roots=set()
for record in records:
 rootname=record['root']
 if rootname in seen_roots:continue
 seen_roots.add(rootname);root=s.objects[rootname]
 names=set(record.get('objects',[]))|{o.name for o in root.children_recursive}|{rootname}
 foundation=record.get('foundation')or record.get('support')
 if foundation and isinstance(foundation,str):names.add(foundation)
 # Build manifests may list multiple generated foundation pieces.
 names.update(record.get('foundations',[]))
 objs=[s.objects[n]for n in names if n in s.objects and visible(s.objects[n])]
 geo=combine(objs)
 if not geo['tree']:continue
 M=I@root.matrix_world;pp=[params(p)for p in geo['vertices']];foot=hull(pp)
 g={'id':rootname,'role':record['role'],'objects':[o.name for o in objs],'geo':geo,'footprint_parameter':foot};groups.append(g)
 normal=(M.translation-C).normalized();up=(M.to_3x3()@Vector((0,0,1))).normalized()
 # Old CV wrappers are transforms around a remote pivot, not tangent base frames.
 if not rootname.startswith('CV_'):
  orientation.append({'root':rootname,'up_error_deg':angle(up,normal),'point_local':list(M.translation)})
 relative=[M.inverted()@p for p in geo['vertices']]
 heights.append({'root':rootname,'role':record['role'],'radial_height_above_land':max(p[2]for p in pp)-.68,
     'root_local_bounds':bounds(relative),'anchor_parameter':params(M.translation)})
 if record.get('size') and len(record['size'])==3 and record['role']in {'replacement','building'}:
  structural=[p for o in objs if o.name!=foundation for p in mesh_data(o)[0]]
  local=[M.inverted()@p for p in structural];bb=bounds(local);size=[bb[1][i]-bb[0][i]for i in range(3)]
  target=record['size'];heights[-1].update({'measured_dimensions':size,'declared_dimensions':target})
  # Ordinary facade variants fit inside a nominal envelope and may have slightly
  # lower rooftop equipment. Only the two requested heroes have exact total H.
  hero=record.get('kind')in {'empire','onewtc'}
  if size[0]>target[0]+.03 or size[1]>target[1]+.03 or size[2]>target[2]+.08 or (hero and abs(size[2]-target[2])>.08):
   dimension_errors.append({'root':rootname,'measured':size,'declared':target})
 if record['role']in {'height_change','changed_original'}:continue
 samples=[]
 for a,b in zip(foot,foot[1:]+foot[:1]):
  n=max(1,math.ceil(math.dist(a,b)/.16))
  samples.extend([(a[0]+(b[0]-a[0])*j/n,a[1]+(b[1]-a[1])*j/n)for j in range(n)])
 base=record.get('anchor_parameter')or record.get('target_anchor_parameter')or params(M.translation);samples.append(base[:2])
 missing=[];road_hits=[]
 for x,y in samples:
  p=surface(x,y);n=(p-C).normalized();hit=ground['tree'].ray_cast(p+n*20,-n,30)[0]
  if hit is None:missing.append([x,y])
  if roads['tree']:
   h,no,index,dist=roads['tree'].ray_cast(p+n*80,-n,85)
   if h is not None:road_hits.append({'point_parameter':[x,y],'object':roads['names'][index]})
 if missing:water_errors.append({'root':rootname,'missing_ground_samples':missing})
 if road_hits:road_errors.append({'root':rootname,'protected_footprint_hits':road_hits})
 if foundation and foundation in s.objects:
  fv,_=mesh_data(s.objects[foundation]);n=len(fv)//2;low=fv[n:];high=fv[:n];gaps=[];top=[]
  for collection,out in [(low,gaps),(high,top)]:
   for p in collection:
    normal=(p-C).normalized();hit=ground['tree'].ray_cast(C+normal*170,-normal,40)[0]
    out.append((p-C).length-(hit-C).length if hit is not None else None)
  row={'root':rootname,'foundation':foundation,'bottom_points':len(low),'min_bottom_gap':min((v for v in gaps if v is not None),default=None),
       'max_bottom_gap':max((v for v in gaps if v is not None),default=None),'min_top_clearance':min((v for v in top if v is not None),default=None),'missing_ground':gaps.count(None)+top.count(None)}
  contact_rows.append(row)
  if row['missing_ground'] or (row['max_bottom_gap']or 0)>.015 or (row['min_top_clearance']or 0)<-.01:contact_errors.append(row)
 else:
  low=sorted(geo['vertices'],key=lambda p:(p-C).length)[:12];gaps=[]
  for p in low:
   n=(p-C).normalized();hit=ground['tree'].ray_cast(C+n*170,-n,40)[0]
   if hit is not None:gaps.append((p-C).length-(hit-C).length)
  row={'root':rootname,'minimum_base_clearance':min(gaps,default=None),'role':record['role']};contact_rows.append(row)
  if not gaps or min(gaps)>.12:contact_errors.append(row)
print('SITES',len(groups),'ground_failures',len(water_errors),'road_failures',len(road_errors),'contact_failures',len(contact_errors),flush=True)

# Triangle intersections between different assemblies and retained source meshes.
changed_names=set(o.name for root in original_changed_roots for o in [s.objects[root]]+list(s.objects[root].children_recursive))
all_objects=[s.objects[n]for n in added|changed_names if n in s.objects and visible(s.objects[n])]
allnew=combine(all_objects);collisions=[];inherited=[];paving_contacts=[];baseline_candidates=[]
moving={'A02_SHIP','A01_CONTAINER','W01_NEW_PALLET','P01_SPREADER','A03_TRAILER','A03_TRACTOR','A04_PRIMARY','A05_SECONDARY','W08_LAST_LOAD'}
excluded=terrain_names|{'EARTH_CONTINUOUS_OCEAN','SF_BASIN_WATER_SURFACE','CNC_UNIFIED_GROUND'}
for name in sorted(old-changed_names):
 o=s.objects.get(name)
 if not o or not visible(o) or name in excluded or under(o,moving):continue
 b=bounds([I@o.matrix_world@Vector(p)for p in o.bound_box])
 if not boxhit(b,allnew['bounds']):continue
 vs,fs=mesh_data(o)
 if not vs or not fs:continue
 pairs=BVHTree.FromPolygons(vs,fs).overlap(allnew['tree'])
 hits=Counter(allnew['names'][j]for i,j in pairs)
 for other,count in hits.items():
  row={'a':name,'b':other,'triangle_pairs':count}
  if name.startswith(('CV_FOUNDATION_','CE_'))and any(token in name for token in ('FOUNDATION','PLAZA')):paving_contacts.append(row)
  elif other in old:baseline_candidates.append(row)
  else:collisions.append(row)
inter_site=[]
for index,a in enumerate(groups):
 for b in groups[index+1:]:
  if not boxhit(a['geo']['bounds'],b['geo']['bounds']):continue
  pairs=a['geo']['tree'].overlap(b['geo']['tree'])
  for (an,bn),count in Counter((a['geo']['names'][i],b['geo']['names'][j])for i,j in pairs).items():
   row={'a':an,'b':bn,'sites':[a['id'],b['id']],'triangle_pairs':count}
   if an in old and bn in old:baseline_candidates.append(row)
   else:inter_site.append(row)

# Closed-component signed volume of generated meshes only; source windings are preserved.
normal_errors=[];closed_count=0;open_count=0;seen=set()
for o in all_objects:
 if o.name not in added or o.type!='MESH'or o.data.name in seen:continue
 seen.add(o.data.name);me=o.data;parents=list(range(len(me.vertices)))
 def find(a):
  while parents[a]!=a:parents[a]=parents[parents[a]];a=parents[a]
  return a
 for edge in me.edges:
  a,b=edge.vertices;ra,rb=find(a),find(b)
  if ra!=rb:parents[rb]=ra
 components=defaultdict(list)
 for face in me.polygons:
  if face.vertices:components[find(face.vertices[0])].append(face)
 for faces in components.values():
  ec=Counter();volume=0;origin=me.vertices[faces[0].vertices[0]].co
  for face in faces:
   ids=list(face.vertices)
   for a,b in zip(ids,ids[1:]+ids[:1]):ec[tuple(sorted((a,b)))]+=1
   p=me.vertices[ids[0]].co-origin
   for j in range(1,len(ids)-1):volume+=p.dot((me.vertices[ids[j]].co-origin).cross(me.vertices[ids[j+1]].co-origin))/6
  if all(v==2 for v in ec.values()):
   closed_count+=1
   if volume< -1e-8:normal_errors.append({'object':o.name,'signed_volume':volume,'faces':len(faces)})
  else:open_count+=1

if baseline_candidates:
 bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.context.scene;s.frame_set(349);I=s.objects['US_FRAME'].matrix_world.inverted();trees={}
 for row in baseline_candidates:
  for name in [row['a'],row['b']]:
   if name not in trees:
    vs,fs=mesh_data(s.objects[name]);trees[name]=BVHTree.FromPolygons(vs,fs)
  if trees[row['a']].overlap(trees[row['b']]):inherited.append(row)
  else:collisions.append(row)

check('all_visible_generated_sites_on_land',not water_errors,sites=len(groups))
check('declared_building_dimensions',not dimension_errors,errors=dimension_errors)
measured_heights={r['root']:r['radial_height_above_land']for r in heights}
height_errors=[{'root':r['root'],'measured':measured_heights.get(r['root']),'target':r['target_height']}for r in height_records
 if r['root']not in measured_heights or abs(measured_heights[r['root']]-r['target_height'])>.12]
check('rear_height_hierarchy_targets',not height_errors,errors=height_errors,count=len(height_records))
check('protected_roads_ports_clear_of_new_footprints',not road_errors)
check('radial_building_orientation',max((r['up_error_deg']for r in orientation),default=0)<.003,max_error_deg=max((r['up_error_deg']for r in orientation),default=0))
check('foundations_and_tree_bases_supported',not contact_errors,sites=len(contact_rows))
check('no_introduced_original_geometry_intersections',not collisions,inherited_source_contacts=len(inherited))
check('no_new_inter_site_intersections',not inter_site)
check('new_closed_components_outward',not normal_errors,closed_components=closed_count,open_components=open_count)
check('candidate_unchanged_during_readonly_audit',hashlib.sha256(CANDIDATE.read_bytes()).hexdigest()==candidate_hash)
report={'candidate':str(CANDIDATE),'candidate_sha256':candidate_hash,'source':str(SOURCE),'source_sha256':SHA,'pass':all(c['pass']for c in checks),'checks':checks,
 'scope':'Geometry/support/radial/normals/road footprint checks; preservation and990-frame camera/actor clearance owned by audit_preservation.py.',
 'source_object_count':len(old),'added_object_count':len(added),'site_count':len(groups),
 'sites':[{k:v for k,v in g.items()if k!='geo'}for g in groups],'orientation':orientation,'heights':heights,
 'contacts':contact_rows,'contact_errors':contact_errors,'missing_land_errors':water_errors,'road_footprint_errors':road_errors,
 'collisions':{'introduced_vs_original':collisions,'inter_site':inter_site,'inherited_original_contacts':inherited,'paving_contacts':paving_contacts},
 'normals':{'errors':normal_errors,'closed_components':closed_count,'open_components':open_count}}
probe=OUT/'wtc-placement-probe.json'
if probe.exists():
 data=json.loads(probe.read_text())
 report['baseline_context']={'original_glass_tower_contacts':data.get('original_glass_contacts',{}),
  'note':'The original glass tower crossed retained streets and the maneuver yard. Replacement relocation is checked independently against these unchanged surfaces.'}
(OUT/'geometry-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA
print('US_GEOMETRY_REPORT',json.dumps({'hash':candidate_hash,'pass':report['pass'],'checks':checks}),flush=True)
