"""Independent, read-only Shanghai density and exact-waterway verification.

Blender --background --factory-startup --python this.py
Requires the shared, hash-bound review/preservation-source.json baseline from
audit_preservation.py; no duplicate motion or full preservation sweep is run.
Never saves any blend and never edits the protected source.
"""
import bpy, ast, array, hashlib, json, math, sys, time
from pathlib import Path
from collections import Counter, defaultdict
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'review'; BLOCKOUT=ROOT.parent
OUT.mkdir(exist_ok=True)
SOURCE=BLOCKOUT/'cn-unified-curvature-v001/pnpline-cn-unified-curvature-v001.blend'
CANDIDATE=ROOT/'pnpline-cn-shanghai-density-v001.blend'
SOURCE_SHA='f0f07fcbbd00f9f3c2d3402092684e6326610ffcf65678a33490ad5d86f4b978'
source_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
assert source_hash==SOURCE_SHA,source_hash

def load_functions(path,names):
    tree=ast.parse(Path(path).read_text())
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(path),'exec'),globals())

load_functions(BLOCKOUT/'cn-us-integrated-v001/scripts/audit_geometry.py',{'digest','matrix','simple','geometry','material_signature','rna_dependency'})
load_functions(ROOT/'scripts/survey_shanghai.py',{'hull','inside','segment_distance','edge_distance','area'})

assert CANDIDATE.exists(),CANDIDATE
candidate_hash=hashlib.sha256(CANDIDATE.read_bytes()).hexdigest()
delivery=json.loads((ROOT/'delivery.json').read_text())
survey=json.loads((OUT/'shanghai-survey.json').read_text())
prior=json.loads((SOURCE.parent/'delivery.json').read_text())
C=Vector(prior['sphere']['center']);R=prior['sphere']['radius']
cache=OUT/'preservation-source.json'
assert cache.exists(), 'Run audit_preservation.py -- --capture-source first.'
before=json.loads(cache.read_text())
assert before['sha256']==SOURCE_SHA
# Blender keeps mesh and curve namespaces separate. Use the preservation
# snapshot's (ID type, data name) cache; name-only legacy snapshots can confuse
# the mesh SF_ISLAND_EDGE with the same-named curve datablock.
field_alias={'matrix_basis':'basis','matrix_parent_inverse':'parent_inverse','matrix_world':'world_f0'}
before['objects']={n:{field_alias.get(k,k):v for k,v in r.items()} for n,r in before['objects'].items()}
bpy.ops.wm.open_mainfile(filepath=str(CANDIDATE))
s=bpy.context.scene;s.frame_set(0);D=s.objects['SF_CN_LAYOUT'];I=D.matrix_world.inverted()
after={'objects':{o.name:None for o in s.objects}}

def numerror(a,b):
    if isinstance(a,list):return max((numerror(x,y) for x,y in zip(a,b)),default=0) if len(a)==len(b) else 1e99
    return abs(a-b)

old=set(before['objects']);now=set(after['objects']);added=sorted(now-old)
aliases={'matrix_basis':'basis','matrix_world':'world_f0','world':'world_f0','basis':'basis'}
declared=delivery.get('allowed_original_changes',{})

def descendants(root):return [o for o in s.objects if under(o,{root})]
def under(o,names):
    while o:
        if o.name in names:return True
        o=o.parent
    return False
def visible(o):return o.type in {'MESH','CURVE','FONT'} and not o.hide_render and not o.hide_viewport and not o.hide_get()
def mesh_data(o):
    ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();M=I@ev.matrix_world
    vs=[M@v.co for v in me.vertices];fs=[tuple(p.vertices) for p in me.polygons]
    ev.to_mesh_clear();return vs,fs
def bbox(vs):return ([min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)])
def boxhit(a,b,pad=0):return all(a[0][i]<=b[1][i]+pad and b[0][i]<=a[1][i]+pad for i in range(3))
def combine(objects):
    vs=[];fs=[];names=[]
    for o in objects:
        ov,of=mesh_data(o);offset=len(vs);vs.extend(ov);fs.extend(tuple(offset+i for i in f) for f in of);names.extend([o.name]*len(of))
    return {'vertices':vs,'faces':fs,'names':names,'tree':BVHTree.FromPolygons(vs,fs) if fs else None,'bounds':bbox(vs) if vs else None}
def radial(p):return C+(p-C).normalized()*R
def angle(a,b):return math.degrees(math.atan2(a.cross(b).length,a.dot(b)))

protected_roots={'SF_BASIN_WATER_SURFACE','SF_ISLAND_EDGE_CURVED','DT_WATERFRONT_WALK','WB_STONE_ARCH_BRIDGE','SF_SPHERE_TOWER','CNC_UNIFIED_GROUND','EARTH_CONTINUOUS_OCEAN'}
protected_names=sorted(o.name for o in s.objects if under(o,protected_roots))
protected_errors=[]
for name in protected_names:
    o=s.objects[name];b=before['objects'][name]
    current={'parent':o.parent.name if o.parent else None,'basis':matrix(o.matrix_basis),'parent_inverse':matrix(o.matrix_parent_inverse),'world_f0':matrix(o.matrix_world),
      'geometry':geometry(o.data) if o.type in {'MESH','CURVE','FONT'} else None,'materials':[m.name if m else None for m in o.data.materials] if o.data and hasattr(o.data,'materials') else [],
      'hide_render':o.hide_render,'hide_viewport':o.hide_viewport,'hide_layer':o.hide_get()}
    current=json.loads(json.dumps(current))
    for field,value in current.items():
        if value!=b[field]:protected_errors.append({'object':name,'field':field})

report={'candidate':str(CANDIDATE),'candidate_sha256':candidate_hash,'source':str(SOURCE),'source_sha256':source_hash,
    'original_objects':len(old),'added_objects':len(added),'missing_objects':sorted(old-now),'unexpected_added_names':[n for n in added if not n.startswith('SHD_')],
    'allowed_original_changes':declared,
    'preservation_owner':'audit_preservation.py / review/preservation-verification.json: complete original state, actions, materials and all 990 frames. This report does not repeat that sweep.',
    'protected_waterway':{'checked_objects':protected_names,'errors':protected_errors,'water_native_vertices':survey['water']['native_vertex_count'],'water_native_faces':survey['water']['face_count']},
    'checks':[]}
def check(name,ok,**details):report['checks'].append({'name':name,'pass':bool(ok),**details})
check('source_file_immutable',hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SOURCE_SHA)
check('original_object_set_preserved',not report['missing_objects'])
check('new_objects_namespaced',not report['unexpected_added_names'],count=len(added))
check('water_banks_bridge_pearl_terrain_exact',not protected_errors,count=len(protected_names))

# Work in actual evaluated local geometry, independent of planned rectangles.
water=combine([s.objects['SF_BASIN_WATER_SURFACE']]);ground=combine([s.objects['CNC_UNIFIED_GROUND']])
groups=[]
for rec in delivery['sites']:
    groups.append({'id':rec['name'],'kind':rec['kind'],'role':'building','root':rec['root'],'anchor':rec['anchor'],
       'objects':rec['objects']+[rec['foundation']],'foundation':rec['foundation']})
for rec in delivery['tree_sites']:
    groups.append({'id':rec['root'],'kind':'tree','role':'tree','root':rec['root'],'anchor':rec['anchor'],'objects':rec['objects']})
for rec in delivery['hero_changes']+delivery.get('relocations',[]):
    groups.append({'id':rec['root'],'kind':'original_tower','role':'hero' if rec in delivery['hero_changes'] else 'relocated',
       'root':rec['root'],'anchor':rec['target_anchor'][:2],
       'objects':rec['members']+([rec['foundation']] if rec.get('foundation') else []),'foundation':rec.get('foundation')})

water_errors=[];orientation=[];contacts=[];contact_errors=[];hero_metrics=[]
for g in groups:
    objs=[s.objects[n] for n in g['objects'] if n in s.objects and visible(s.objects[n])]
    data=combine(objs);g['geo']=data
    if not data['vertices']:continue
    g['footprint']=hull([radial(p) for p in data['vertices']])
    samples=[]
    for a,b in zip(g['footprint'],g['footprint'][1:]+g['footprint'][:1]):
        n=max(1,math.ceil(math.dist(a,b)/.12))
        samples.extend([(a[0]+(b[0]-a[0])*j/n,a[1]+(b[1]-a[1])*j/n) for j in range(n)])
    samples.append(tuple(g['anchor']))
    hits=[]
    for x,y in samples:
        p=water['tree'].ray_cast(Vector((x,y,60)),Vector((0,0,-1)))[0]
        if p is not None:hits.append([x,y,p.z])
    if hits:water_errors.append({'site':g['id'],'role':g['role'],'water_footprint_samples':hits})
    root=s.objects[g['root']];m=I@root.matrix_world;up=m.to_3x3()@Vector((0,0,1));normal=(m.translation-C).normalized()
    orientation.append({'root':root.name,'up_error_deg':angle(up.normalized(),normal),'anchor':list(m.translation),'root_surface_offset':(m.translation-C).length-R})
    if g['role']=='hero':
        oldrow=next(r for r in survey['selected_architecture'] if r['id']==g['id'])
        original_matrix=I@Matrix(before['objects'][g['root']]['world_f0'])
        scale_ratios=[m.to_3x3().col[i].length/original_matrix.to_3x3().col[i].length for i in range(3)]
        declared_hero=next(r for r in delivery['hero_changes'] if r['root']==g['id'])
        hero_metrics.append({'root':g['id'],'old_height':oldrow['height_from_radial_ground'],
          'new_height':max((p-C).length-R for p in data['vertices']),'radial_footprint':g['footprint'],
          'axis_scale_ratios':scale_ratios,'declared_scale':[declared_hero['scale_xy'],declared_hero['scale_xy'],declared_hero['scale_z']]})
    if g.get('foundation'):
        o=s.objects[g['foundation']];pts,_=mesh_data(o);n=len(pts)//2;bottom=pts[n:];top=pts[:n]
        gaps=[];top_clear=[]
        for p in bottom:
            direction=(p-C).normalized();hit=ground['tree'].ray_cast(C+direction*(R+5),-direction)[0]
            if hit is not None:gaps.append((p-C).length-(hit-C).length)
            else:gaps.append(None)
        for p in top:
            direction=(p-C).normalized();hit=ground['tree'].ray_cast(C+direction*(R+5),-direction)[0]
            if hit is not None:top_clear.append((p-C).length-(hit-C).length)
        row={'site':g['id'],'foundation':o.name,'bottom_points':len(bottom),'min_bottom_gap':min((x for x in gaps if x is not None),default=None),
          'max_bottom_gap':max((x for x in gaps if x is not None),default=None),'min_top_clearance':min(top_clear,default=None),'missing_land':gaps.count(None)}
        contacts.append(row)
        if row['missing_land'] or (row['max_bottom_gap'] or 0)>.012 or (row['min_top_clearance'] or 0)<-.005:contact_errors.append(row)
    else:
        # Tree roots have a small planned soil embed/gap; relocated original towers
        # retain their source base offset and have no new skirt.
        low=sorted(data['vertices'],key=lambda p:(p-C).length)[:8]
        gaps=[]
        for p in low:
            direction=(p-C).normalized();hit=ground['tree'].ray_cast(C+direction*(R+5),-direction)[0]
            if hit is not None:gaps.append((p-C).length-(hit-C).length)
        row={'site':g['id'],'minimum_base_clearance':min(gaps,default=None),'role':g['role']};contacts.append(row)
        if not gaps or min(gaps)>.08:contact_errors.append(row)
print('SITE_GEOMETRY',len(groups),'water_failures',len(water_errors),'contact_failures',len(contact_errors),flush=True)

changed_members={n for rec in delivery['hero_changes']+delivery.get('relocations',[]) for n in rec['members']}
geometry_objects=[s.objects[n] for n in set(added)|changed_members]
geometry_objects=[o for o in geometry_objects if visible(o)]
allnew=combine(geometry_objects)
source_contacts=[];paving_contacts=[];old_checked=0
excluded={'EARTH_CONTINUOUS_OCEAN','CNC_UNIFIED_GROUND','SF_BASIN_WATER_SURFACE'}
moving={'A02_SHIP','A01_CONTAINER','W01_NEW_PALLET','P01_SPREADER'}
for name in sorted(old-changed_members):
    o=s.objects[name]
    if not visible(o) or name in excluded or name.startswith('SF_OCEAN_WAVE') or under(o,moving):continue
    b=bbox([I@o.matrix_world@Vector(p) for p in o.bound_box])
    if not boxhit(b,allnew['bounds']):continue
    v,f=mesh_data(o)
    if not v or not f:continue
    old_checked+=1;pairs=BVHTree.FromPolygons(v,f).overlap(allnew['tree'])
    if not pairs:continue
    hits=dict(Counter(allnew['names'][j] for i,j in pairs));row={'original':name,'added_or_changed':hits}
    if name.startswith('CNC_SUPPORT_') or any(t in name for t in ('PROMENADE','WALK','ROAD','PAVING','LAWN')):paving_contacts.append(row)
    else:source_contacts.append(row)

inter_site=[];broadphase=0
for index,a in enumerate(groups):
    if not a['geo']['tree']:continue
    for b in groups[index+1:]:
        if not b['geo']['tree'] or not boxhit(a['geo']['bounds'],b['geo']['bounds']):continue
        broadphase+=1;pairs=a['geo']['tree'].overlap(b['geo']['tree'])
        if pairs:inter_site.append({'a':a['id'],'b':b['id'],'roles':[a['role'],b['role']],
          'pairs':dict(Counter(a['geo']['names'][i]+' | '+b['geo']['names'][j] for i,j in pairs))})
print('COLLISIONS',len(source_contacts),len(inter_site),'original_checked',old_checked,flush=True)

# Signed volume for every independent closed component catches inverted batches.
normal_errors=[];closed_count=0;open_count=0;degenerate=[];seen=set()
for o in geometry_objects:
    if o.type!='MESH' or o.name not in added or o.data.name in seen:continue
    seen.add(o.data.name);me=o.data;n=len(me.vertices);parent=list(range(n))
    def find(a):
        while parent[a]!=a:parent[a]=parent[parent[a]];a=parent[a]
        return a
    for edge in me.edges:
        a,b=edge.vertices;ra,rb=find(a),find(b)
        if ra!=rb:parent[rb]=ra
    components=defaultdict(list)
    for p in me.polygons:
        if p.vertices:components[find(p.vertices[0])].append(p)
    for faces in components.values():
        ec=Counter();volume=0;origin=me.vertices[faces[0].vertices[0]].co
        for p in faces:
            ids=list(p.vertices)
            for a,b in zip(ids,ids[1:]+ids[:1]):ec[tuple(sorted((a,b)))]+=1
            a=me.vertices[ids[0]].co-origin
            for j in range(1,len(ids)-1):volume+=a.dot((me.vertices[ids[j]].co-origin).cross(me.vertices[ids[j+1]].co-origin))/6
        if all(v==2 for v in ec.values()):
            closed_count+=1
            if volume < -1e-8:normal_errors.append({'object':o.name,'faces':len(faces),'signed_volume':volume})
        else:open_count+=1

report.update({'sites':[{k:v for k,v in g.items() if k!='geo'} for g in groups], 'water_footprint_errors':water_errors,
 'orientation':orientation,'contacts':contacts,'contact_errors':contact_errors,'hero_metrics':hero_metrics,
 'collisions':{'original_vs_new_or_changed':source_contacts,'inter_site':inter_site,'retained_paving_contacts':paving_contacts,'original_objects_checked':old_checked,'inter_site_broadphase_pairs':broadphase},
 'normals':{'errors':normal_errors,'closed_components':closed_count,'open_components':open_count}})
check('new_and_edited_footprints_avoid_exact_water',not water_errors,sites=len(groups))
check('three_hero_scale_targets',len(hero_metrics)==3 and all(max(abs(a-b) for a,b in zip(r['axis_scale_ratios'],r['declared_scale']))<1e-5 for r in hero_metrics),metrics=hero_metrics)
check('structures_and_trees_radial',max((r['up_error_deg'] for r in orientation),default=0)<.002,max_error_deg=max((r['up_error_deg'] for r in orientation),default=0))
check('foundation_and_tree_ground_contact',not contact_errors,sites=len(contacts))
check('no_source_architecture_intersections',not source_contacts,checked_original_objects=old_checked)
check('no_inter_site_intersections',not inter_site,broadphase_pairs=broadphase)
check('generated_closed_components_outward',not normal_errors,closed_components=closed_count,open_components=open_count)
report['pass']=all(r['pass'] for r in report['checks'])
(OUT/'density-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('DENSITY_VERIFICATION',json.dumps({'hash':candidate_hash,'pass':report['pass'],'checks':report['checks']}),flush=True)
