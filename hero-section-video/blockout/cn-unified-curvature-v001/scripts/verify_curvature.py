"""Independent final spherical-ground/static-structure verification, read only."""
import bpy,bmesh,ast,array,hashlib,json,math,sys
from pathlib import Path
from collections import Counter,defaultdict
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'review';BLOCKOUT=ROOT.parent
SOURCE=BLOCKOUT/'cn-city-expansion-v001/pnpline-cn-city-expansion-v001.blend'
FILE=ROOT/'pnpline-cn-unified-curvature-v001.blend'
SHA='c9da20e19f2cf732245df77c178b1fa85dae00753884ea3c586327a63cbe75bb'
source_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest();assert source_hash==SHA
file_hash=hashlib.sha256(FILE.read_bytes()).hexdigest()
delivery=json.loads((ROOT/'delivery.json').read_text());assert delivery['sha256']==file_hash
survey=json.loads((OUT/'static-survey.json').read_text())['objects']
group_plan=json.loads((OUT/'static-original-clusters.json').read_text())
source_snapshot=json.loads((BLOCKOUT/'cn-city-expansion-v001/review/verification-candidate-snapshot.json').read_text())
assert source_snapshot['file_sha256']==SHA
defs=ast.parse((BLOCKOUT/'cn-us-integrated-v001/scripts/audit_geometry.py').read_text())
exec(compile(ast.Module(body=[n for n in defs.body if isinstance(n,ast.FunctionDef)and n.name in {'geometry','digest','simple','material_signature','rna_dependency'}],type_ignores=[]),'geometry_helpers','exec'),globals())
bpy.ops.wm.open_mainfile(filepath=str(FILE));s=bpy.context.scene;s.frame_set(0)
D=s.objects['SF_CN_LAYOUT'];I=D.matrix_world.inverted();ground=s.objects[delivery['ground']]
C=Vector(delivery['sphere']['center']);R=float(delivery['sphere']['radius'])

def coords(o):
 M=I@o.matrix_world
 if o.type=='MESH':return [M@v.co for v in o.data.vertices],[tuple(p.vertices)for p in o.data.polygons]
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
 vs=[M@v.co for v in me.vertices];fs=[tuple(p.vertices)for p in me.polygons];ev.to_mesh_clear();return vs,fs
def bounds(vs):return ([min(v[i]for v in vs)for i in range(3)],[max(v[i]for v in vs)for i in range(3)])
def overlap(a,b):return all(a[0][i]<=b[1][i]and b[0][i]<=a[1][i]for i in range(3))
def matrix_error(a,b):return max(abs(a[i][j]-b[i][j])for i in range(4)for j in range(4))
def visible(o):return not o.hide_render and not all(c.hide_render for c in o.users_collection)
def radius(p):return (p-C).length
def scalar_surface(x,y):return C.z+math.sqrt(R*R-(x-C.x)**2-(y-C.y)**2)
gv,gf=coords(ground);gtree=BVHTree.FromPolygons(gv,gf)
nt=int(ground['cnc_top_vertex_count']);nf=int(ground['cnc_top_face_count'])
bm=bmesh.new();bm.from_mesh(ground.data)
manifold=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True)
unseen=set(bm.verts);components=0
while unseen:
 components+=1;stack=[unseen.pop()]
 while stack:
  for edge in stack.pop().link_edges:
   for v in edge.verts:
    if v in unseen:unseen.remove(v);stack.append(v)
bm.free()
top_error=max(abs(radius(p)-R)for p in gv[:nt]);bottom_error=max(abs(radius(p)-ground['cnc_bottom_radius'])for p in gv[nt:])
normal_dots=[]
for polygon in ground.data.polygons[:nf]:
 p=sum((gv[i]for i in polygon.vertices),Vector())/len(polygon.vertices)
 normal=(I@ground.matrix_world).to_3x3()@polygon.normal
 normal_dots.append(normal.normalized().dot((p-C).normalized()))
ground_report={'object':ground.name,'vertices':len(gv),'faces':len(gf),'connected_components':components,
 'nonmanifold_edges':manifold,'euler_characteristic':len(ground.data.vertices)-len(ground.data.edges)+len(ground.data.polygons),
 'signed_volume':volume,'top_radius_max_error':top_error,'bottom_radius_max_error':bottom_error,
 'minimum_face_radial_normal_dot':min(normal_dots),'custom_normals':ground.data.has_custom_normals}

old_plates=[r['object']for r in group_plan['replace_ground_objects']]+['CNX_CURVED_DISTRICT_LAND','CN_LAND_TERRACE']
visible_old=[n for n in old_plates if s.objects.get(n)and visible(s.objects[n])]
unified_visible=[o.name for o in s.objects if o.get('cnc_role')=='unified_spherical_ground'and visible(o)]

# The independently captured immutable-source donor is used only as a numerical
# reference; it is never appended into the scene or modified on disk.
ocean=s.objects['EARTH_CONTINUOUS_OCEAN'];OM=I@ocean.matrix_world
region=(-34.02,109.41,-62.12,39.42);protected=[]
for v in ocean.data.vertices:
 p=OM@v.co
 if not(region[0]<=p.x<=region[1]and region[2]<=p.y<=region[3]and p.z>-100):protected.append(v.co)
arr=array.array('f')
for p in protected:arr.extend(p)
protected_hash=hashlib.sha256(arr.tobytes()).hexdigest()
ocean_geo=geometry(ocean.data);old_ocean=source_snapshot['objects']['EARTH_CONTINUOUS_OCEAN']['geometry']
ocean_report={'protected_count':len(protected),'protected_hash':protected_hash,
 'expected_protected_hash':'2ec0790d241d6420ff76f3a271923743e83917eecc80e3da63836d14099013c7',
 'same_topology':ocean_geo['topology']==old_ocean['topology'],
 'same_smooth_flags':ocean_geo['smooth']==old_ocean['smooth'],
 'same_material_indices':ocean_geo['face_materials']==old_ocean['face_materials']}

cluster_data=[];rigidity_errors=[];normal_errors=[];ground_errors=[];geometry_errors=[];geom_cache={}
placements={r['id']:r for r in delivery['static_clusters']}
for group in group_plan['rigid_clusters']:
 row=placements[group['id']];names=[n for n in group['visible_geometry']if s.objects.get(n)and visible(s.objects[n])]
 if not names:continue
 first=names[0];oldM=Matrix(survey[first]['matrix']);newM=I@s.objects[first].matrix_world;delta=newM@oldM.inverted()
 anchor=Vector(group['anchor']);target=delta@anchor;up=(delta.to_3x3()@Vector((0,0,1))).normalized();expected=(target-C).normalized()
 angle=math.degrees(math.atan2(up.cross(expected).length,up.dot(expected)));per_error=0;vs=[];fs=[];face_names=[];oldvs=[];foot_candidates=[]
 for name in names:
  o=s.objects[name];oldmat=Matrix(survey[name]['matrix']);newmat=I@o.matrix_world
  per_error=max(per_error,matrix_error(newmat,delta@oldmat))
  if o.data and o.data.name not in geom_cache:geom_cache[o.data.name]=geometry(o.data)
  if geom_cache.get(o.data.name)!=source_snapshot['objects'][name]['geometry']:geometry_errors.append(name)
  ov,of=coords(o);offset=len(vs);vs.extend(ov);fs.extend(tuple(offset+i for i in f)for f in of);face_names.extend([name]*len(of))
  back=oldmat@newmat.inverted();oldpoints=[back@p for p in ov];oldvs.extend(oldpoints)
  if o.type=='MESH':foot_candidates.extend((p.z,q)for p,q in zip(oldpoints,ov))
 if not vs:continue
 low=min((z for z,p in foot_candidates),default=None)
 feet=[p for z,p in foot_candidates if z<=low+.025]if low is not None else []
 clearances=[radius(p)-R for p in feet]
 source_clearance=low-1.249988 if low is not None else None
 missing=0
 if not row['skip_ground_contact']:
  for p in feet:missing+=gtree.ray_cast(Vector((p.x,p.y,100)),Vector((0,0,-1)))[0]is None
 r={'id':group['id'],'category':group['category'],'normal_angle_degrees':angle,'rigid_matrix_error':per_error,
    'source_bottom_clearance':source_clearance,'minimum_bottom_clearance':min(clearances,default=None),
    'maximum_bottom_clearance':max(clearances,default=None),'ground_misses':missing,'pedestals':row['pedestals'],'skip_ground_contact':row['skip_ground_contact']}
 if angle>.01:normal_errors.append(r)
 if per_error>.0003:rigidity_errors.append(r)
 if not row['skip_ground_contact']and (missing or (clearances and min(clearances)<min(-.03,source_clearance-.015))):ground_errors.append(r)
 cluster_data.append({'record':r,'name':group['id'],'names':names,'bounds':bounds(vs),'tree':BVHTree.FromPolygons(vs,fs),
    'source_bounds':bounds(oldvs),'source_tree':BVHTree.FromPolygons(oldvs,fs),'face_names':face_names,'new':False})
print('RIGID_CLUSTERS_CHECKED',len(cluster_data),flush=True)

district_normal_errors=[]
for site in delivery['districts']['sites']:
 root=s.objects[site['root']];T=I@root.matrix_world;p=T.translation;up=(T.to_3x3()@Vector((0,0,1))).normalized()
 expected=(p-C).normalized();angle=math.degrees(math.atan2(up.cross(expected).length,up.dot(expected)))
 if angle>.01:district_normal_errors.append({'name':site['name'],'angle_degrees':angle})
 vs=[];fs=[];face_names=[]
 for o in root.children_recursive:
  if o.type not in {'MESH','CURVE','FONT'}or not visible(o):continue
  ov,of=coords(o);n=len(vs);vs.extend(ov);fs.extend(tuple(n+i for i in f)for f in of);face_names.extend([o.name]*len(of))
 if vs:cluster_data.append({'name':site['name'],'bounds':bounds(vs),'tree':BVHTree.FromPolygons(vs,fs),'face_names':face_names,'new':True})

foundations=[];foundation_errors=[]
pedestal_names={n for row in delivery['static_clusters']for n in row['pedestals']}
pedestal_names|={o.name for o in s.objects if o.name.startswith('CNX_')and o.type=='MESH'and (o.name.endswith('_FOUNDATION')or o.name.endswith('_TERRACE'))}
for name in sorted(pedestal_names):
 o=s.objects[name];verts,faces=coords(o);half=len(verts)//2
 if len(verts)%2 or half<4:foundation_errors.append({'name':name,'error':'Unexpected support topology'});continue
 top=verts[:half];bottom=verts[half:];values=[];top_clear=[];miss=0
 for a,b in zip(bottom,bottom[1:]+bottom[:1]):
  for t in [0,.25,.5,.75]:
   p=a.lerp(b,t);hit=gtree.ray_cast(Vector((p.x,p.y,100)),Vector((0,0,-1)))[0]
   if hit:values.append(p.z-hit.z)
   else:miss+=1
 for p in top:
  hit=gtree.ray_cast(Vector((p.x,p.y,100)),Vector((0,0,-1)))[0]
  if hit:top_clear.append(p.z-hit.z)
 record={'name':name,'samples':len(values),'misses':miss,'max_skirt_gap':max(values,default=None),'min_top_clearance':min(top_clear,default=None)}
 # Old originals intentionally have embedded base geometry; pedestal tops may
 # meet/bury into that old base. Only a floating skirt is a new support defect.
 if miss or max(values,default=0)>.025:foundation_errors.append(record)
 foundations.append(record)

conflicts=[];baseline_contacts=[];landscape_contacts=[];broad=0
for i,a in enumerate(cluster_data):
 for b in cluster_data[i+1:]:
  if not overlap(a['bounds'],b['bounds']):continue
  broad+=1;pairs=a['tree'].overlap(b['tree'])
  if not pairs:continue
  mesh_pairs=sorted(set((a['face_names'][x],b['face_names'][y])for x,y in pairs))
  row={'a':a['name'],'b':b['name'],'triangle_crossings':len(pairs),'mesh_pairs':mesh_pairs}
  if not a['new']and not b['new']and overlap(a['source_bounds'],b['source_bounds'])and a['source_tree'].overlap(b['source_tree']):baseline_contacts.append(row)
  elif all((x.endswith('_paving')and 'WALL_HILLS'in y)or(y.endswith('_paving')and 'WALL_HILLS'in x)for x,y in mesh_pairs):landscape_contacts.append(row)
  else:conflicts.append(row)
print('CLUSTER_COLLISIONS_COMPLETE',len(conflicts),flush=True)

hill_edges=[];hill_errors=[]
for o in s.objects:
 if not o.name.startswith('CNX_BJ_WALL_HILLS')or o.type!='MESH' or not visible(o):continue
 vs,fs=coords(o);edge_count=Counter(tuple(sorted((a,b)))for face in fs for a,b in zip(face,face[1:]+face[:1]))
 ids=set(i for edge,count in edge_count.items()if count==1 and (vs[edge[0]]-vs[edge[1]]).length>1e-6 for i in edge)
 gaps=[];miss=0
 for i in ids:
  p=vs[i];hit=gtree.ray_cast(Vector((p.x,p.y,100)),Vector((0,0,-1)))[0]
  if hit:gaps.append(p.z-hit.z)
  else:miss+=1
 row={'name':o.name,'edge_vertices':len(ids),'misses':miss,'max_gap':max(gaps,default=None),'min_gap':min(gaps,default=None)}
 if miss or max(gaps,default=0)>.025:hill_errors.append(row)
 hill_edges.append(row)

def originally_under(name,root):
 while name and name in source_snapshot['objects']:
  if name==root:return True
  name=source_snapshot['objects'][name]['parent']
 return False
us_names=[n for n in source_snapshot['objects']if originally_under(n,'US_FRAME')]
us_errors=[];us_materials=set()
for name in us_names:
 old=source_snapshot['objects'][name];o=s.objects.get(name)
 if o is None:us_errors.append({'name':name,'field':'missing'});continue
 if o.data and o.data.name not in geom_cache:geom_cache[o.data.name]=rna_dependency(o.data)if o.type in {'CAMERA','LIGHT'}else geometry(o.data)
 now={'geometry':geom_cache.get(o.data.name)if o.data else None,'parent':o.parent.name if o.parent else None,
      'materials':[m.name if m else None for m in o.data.materials]if o.data and hasattr(o.data,'materials')else [],
      'hide_render':o.hide_render,'hide_viewport':o.hide_viewport,'basis':[list(r)for r in o.matrix_basis],
      'parent_inverse':[list(r)for r in o.matrix_parent_inverse]}
 for field,value in now.items():
  if value!=old[field]:us_errors.append({'name':name,'field':field})
 us_materials.update(n for n in old['materials']if n)
us_mat_errors=[name for name in us_materials if not bpy.data.materials.get(name)or material_signature(bpy.data.materials[name])['digest']!=source_snapshot['materials'][name]]

checks={'single_visible_unified_ground':unified_visible==[ground.name],'no_old_ground_plate_visible':not visible_old,
 'single_connected_closed_manifold':components==1 and manifold==0 and ground_report['euler_characteristic']==2 and volume>0,
 'true_spherical_radius':max(top_error,bottom_error)<.0001,'top_faces_radial_outward':min(normal_dots)>.99998,
 'far_and_US_ocean_vertices_exact':len(protected)==18589 and protected_hash==ocean_report['expected_protected_hash'],
 'ocean_topology_shading_material_indices_exact':all(ocean_report[k]for k in ['same_topology','same_smooth_flags','same_material_indices']),
 'original_structure_geometry_rigid':not geometry_errors and not rigidity_errors,
 'original_clusters_radial':not normal_errors,'district_structures_radial':not district_normal_errors,
 'original_structure_ground_support':not ground_errors,'pedestals_contact_ground':not foundation_errors,
 'hill_park_edge_contacts_ground':not hill_errors,'US_static_objects_and_materials_preserved':not us_errors and not us_mat_errors,
 'no_introduced_structure_collisions':not conflicts,
 'source_file_immutable':hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA,'candidate_file_immutable':hashlib.sha256(FILE.read_bytes()).hexdigest()==file_hash}
report={'candidate':str(FILE),'candidate_sha256':file_hash,'source_sha256':SHA,'checks':checks,
 'ground':ground_report,'visible_old_plates':visible_old,'ocean':ocean_report,
 'original_cluster_records':[d['record']for d in cluster_data if not d['new']],
 'normal_errors':normal_errors,'district_normal_errors':district_normal_errors,'rigidity_errors':rigidity_errors,
 'original_geometry_errors':sorted(set(geometry_errors)),'ground_errors':ground_errors,'foundations':foundations,'foundation_errors':foundation_errors,
 'collision_broadphase_pairs':broad,'introduced_collisions':conflicts,'preexisting_contacts':baseline_contacts,'landscape_contacts':landscape_contacts,
 'hill_edges':hill_edges,'hill_errors':hill_errors,'US_protected_count':len(us_names),'US_object_errors':us_errors,'US_material_errors':us_mat_errors,
 'notes':['Camera and moving actors are verified independently by animation_audit.','Original embedded foot offsets are retained; added sinking beyond source clearance is rejected.']}
(OUT/'curvature-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('CURVATURE_VERIFICATION',json.dumps({'checks':checks,'ground':ground_report,'counts':{'original_groups':len(placements),'district_sites':len(delivery['districts']['sites']),'supports':len(foundations)}}),flush=True)
