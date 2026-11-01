"""Independent, read-only preservation and new-terrain clearance verification.

Run Blender --background --factory-startup --python this.py. Never saves a blend.
"""
import bpy, ast, array, hashlib, json, math, sys, time
from pathlib import Path
from collections import defaultdict,Counter
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'review';BLOCKOUT=ROOT.parent
SOURCE=BLOCKOUT/'cn-us-integrated-v001/pnpline-cn-us-integrated-v001.blend'
CANDIDATE=ROOT/'pnpline-cn-city-expansion-v001.blend'
args=sys.argv[sys.argv.index('--')+1:]if '--'in sys.argv else []
capture_only='--capture-source'in args
if args and not capture_only:CANDIDATE=Path(args[0])
if not capture_only:assert CANDIDATE.exists(),CANDIDATE
source_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
assert source_hash=='1aee6c14eb4140614ffa650141eed3ada783c416397fbb938a5105a8df70a7d8'
candidate_hash=hashlib.sha256(CANDIDATE.read_bytes()).hexdigest()if not capture_only else None

def load_functions(path,names):
    tree=ast.parse(Path(path).read_text())
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in names],type_ignores=[]),str(path),'exec'),globals())
load_functions(BLOCKOUT/'cn-us-integrated-v001/scripts/audit_geometry.py',{'digest','matrix','simple','geometry','material_signature','rna_dependency'})

def animation_signature(a):
    if not a:return None
    curves=[]
    for layer in a.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for f in bag.fcurves:
                    curves.append((bag.slot_handle,f.data_path,f.array_index,f.extrapolation,
                        [(list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation,k.handle_left_type,k.handle_right_type,k.easing)for k in f.keyframe_points],
                        [rna_dependency(m)for m in f.modifiers]))
    return digest(curves)

def drivers(o):
    if not o.animation_data:return []
    return [(f.data_path,f.array_index,f.driver.expression,f.driver.type,
        [(v.name,v.type,[(t.id.name if t.id else None,t.data_path,t.bone_target,t.transform_type,t.transform_space)for t in v.targets])for v in f.driver.variables])for f in o.animation_data.drivers]

def snapshot(path,label):
    bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.frame_set(0)
    data_cache={};objects={}
    for o in s.objects:
        if o.data and o.data.name not in data_cache:data_cache[o.data.name]=geometry(o.data)if o.type in {'MESH','CURVE','FONT'}else rna_dependency(o.data)if o.type in {'CAMERA','LIGHT'}else None
        objects[o.name]={'type':o.type,'parent':o.parent.name if o.parent else None,
            'basis':matrix(o.matrix_basis),'parent_inverse':matrix(o.matrix_parent_inverse),'world_f0':matrix(o.matrix_world),
            'data':o.data.name if o.data else None,'geometry':data_cache.get(o.data.name)if o.data else None,
            'materials':[m.name if m else None for m in o.data.materials]if o.data and hasattr(o.data,'materials')else [],
            'hide_render':o.hide_render,'hide_viewport':o.hide_viewport,'hide_layer':o.hide_get(),
            'display_type':o.display_type,'collections':sorted(c.name for c in o.users_collection),
            'constraints':[rna_dependency(c)for c in o.constraints],'modifiers':[rna_dependency(m)for m in o.modifiers],
            'action':o.animation_data.action.name if o.animation_data and o.animation_data.action else None,
            'drivers':drivers(o),'properties':{k:simple(v)for k,v in o.items()}}
    result={'file':str(path),'file_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'objects':objects,'actions':{a.name:animation_signature(a)for a in bpy.data.actions},
            'materials':{m.name:material_signature(m)['digest']for m in bpy.data.materials},
            'scene':{'camera':s.camera.name,'fps':s.render.fps,'fps_base':s.render.fps_base,'start':s.frame_start,'end':s.frame_end},
            'collections':{c.name:{'hide_render':c.hide_render,'hide_viewport':c.hide_viewport,'children':sorted(x.name for x in c.children),'objects':sorted(o.name for o in c.objects)}for c in bpy.data.collections}}
    names=[s.camera.name,'CAM_LOOK_TARGET','A02_SHIP','A01_CONTAINER','W01_NEW_PALLET','P01_SPREADER']
    names=[n for n in names if n in s.objects]
    result['motion']={n:[]for n in names};result['optics']=[]
    for f in range(990):
        s.frame_set(f)
        for n in names:result['motion'][n].append(matrix(s.objects[n].matrix_world))
        c=s.camera.data;result['optics'].append([c.lens,c.shift_x,c.shift_y,c.clip_start,c.clip_end,c.sensor_width,c.sensor_height])
    s.frame_set(0)
    result=json.loads(json.dumps(result))
    (OUT/f'verification-{label}-snapshot.json').write_text(json.dumps(result,separators=(',',':')),encoding='utf-8')
    print('SNAPSHOT',label,len(objects),flush=True)
    return result

if capture_only:
    snapshot(SOURCE,'source')
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==source_hash
    sys.exit(0)
cache=OUT/'verification-source-snapshot.json'
before=json.loads(cache.read_text())if cache.exists()else None
if before is None or before.get('file_sha256')!=source_hash:before=snapshot(SOURCE,'source')
after=snapshot(CANDIDATE,'candidate');s=bpy.context.scene
old=set(before['objects']);now=set(after['objects']);added=sorted(now-old)
changes=[]
allowed_waves={'SF_OCEAN_WAVE.'+x for x in ['001','003','004','009','016','027','029','030','031']}
visibility_changes=[]
hidden_wave_transform_cache=[]
for name in sorted(old&now):
    for field,value in before['objects'][name].items():
        new_value=after['objects'][name][field]
        if name in allowed_waves and field=='world_f0'and after['objects'][name]['hide_viewport']:
            obj=after['objects'][name]
            # Blender does not evaluate matrix_world for viewport-disabled IDs.
            # Verify the preserved static authored hierarchy instead of its
            # unevaluated identity cache; this changes no scene state.
            if not obj['action']and not obj['constraints']and not obj['drivers']:
                parent=after['objects'][obj['parent']]['world_f0']if obj['parent']else Matrix.Identity(4)
                composed=matrix(Matrix(parent)@Matrix(obj['parent_inverse'])@Matrix(obj['basis']))
                if composed==value:
                    if new_value!=value:hidden_wave_transform_cache.append(name)
                    new_value=composed
        if value!=new_value:
            row={'object':name,'field':field,'before':value,'after':new_value}
            if name in allowed_waves and field in {'hide_render','hide_viewport','hide_layer'}and new_value is True:visibility_changes.append(row)
            else:changes.append(row)
action_errors=[n for n,v in before['actions'].items()if after['actions'].get(n)!=v]
mat_errors=[n for n,v in before['materials'].items()if after['materials'].get(n)!=v]
def error(a,b):
    if isinstance(a,list):return max((error(x,y)for x,y in zip(a,b)),default=0)if len(a)==len(b)else 1e99
    return abs(a-b)
motion_errors={n:max(error(a,b)for a,b in zip(v,after['motion'][n]))for n,v in before['motion'].items()}
collection_errors=[]
for n,orig in before['collections'].items():
    cur=after['collections'].get(n)
    if not cur:collection_errors.append({'collection':n,'field':'missing'});continue
    for f in ['hide_render','hide_viewport']:
        if cur[f]!=orig[f]:collection_errors.append({'collection':n,'field':f})
    for f in ['children','objects']:
        if not set(orig[f])<=set(cur[f]):collection_errors.append({'collection':n,'field':'removed '+f})

I=s.objects['SF_CN_LAYOUT'].matrix_world.inverted()
def bbox(points):return ([min(p[i]for p in points)for i in range(3)],[max(p[i]for p in points)for i in range(3)])
def boxhit(a,b,pad=0):return all(a[0][i]<=b[1][i]+pad and b[0][i]<=a[1][i]+pad for i in range(3))
def mesh_data(o):
    m=I@o.matrix_world;ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
    vs=[m@v.co for v in me.vertices];fs=[tuple(p.vertices)for p in me.polygons]
    ev.to_mesh_clear();return vs,fs
def combine(objects):
    vs=[];fs=[];names=[];boxes={}
    for o in objects:
        ov,of=mesh_data(o)
        if not ov:continue
        boxes[o.name]=bbox(ov);n=len(vs);vs.extend(ov);fs.extend(tuple(n+i for i in f)for f in of);names.extend([o.name]*len(of))
    return BVHTree.FromPolygons(vs,fs),names,bbox(vs),boxes
newmeshes=[s.objects[n]for n in added if s.objects[n].type in {'MESH','CURVE','FONT'}and not s.objects[n].hide_render]
newtree,facenames,newbounds,newboxes=combine(newmeshes)
print('ADDED BVH',len(newmeshes),len(facenames),flush=True)

# Detect original visible architecture versus additions; terrain contact and covered
# decorative sea ornaments are reviewed separately, since those are intentional.
excluded={'EARTH_CONTINUOUS_OCEAN','SF_FRONT_LAND','SF_COAST_FOLDED_FACE','SF_ISLAND_TOP','SF_ISLAND_WALL','SF_ISLAND_EDGE','SF_BASIN_WATER_SURFACE'}
static_conflicts=[];allowed_ground_contacts=[];checked_static=0
moving_names={'A02_SHIP','A01_CONTAINER','W01_NEW_PALLET','P01_SPREADER'}
def under(o,names):
    while o:
        if o.name in names:return True
        o=o.parent
    return False
for n in sorted(old):
    o=s.objects[n]
    if o.type not in {'MESH','CURVE','FONT'}or o.hide_render or o.hide_viewport or o.hide_get()or n in excluded or n.startswith('SF_OCEAN_WAVE')or under(o,moving_names):continue
    b=bbox([I@o.matrix_world@Vector(v)for v in o.bound_box])
    if not boxhit(b,newbounds):continue
    vs,fs=mesh_data(o)
    if not vs:continue
    checked_static+=1;tree=BVHTree.FromPolygons(vs,fs)
    collisions=tree.overlap(newtree)
    if collisions:
        counts=Counter(facenames[j]for i,j in collisions)
        row={'source':n,'new_objects':dict(counts)}
        if n in {'CN_QUAY','SF_CHINA_GOLD_H','SF_CHINA_GOLD_I'}and set(counts)=={'CNX_CURVED_DISTRICT_LAND'}:
            allowed_ground_contacts.append(row)
        else:static_conflicts.append(row)

camera_hits=[];actor_hits=[];actor_near=0
actor_children={n:[o for o in s.objects if o.type in {'MESH','CURVE','FONT'}and under(o,{n})and not o.hide_render]for n in moving_names if n in s.objects}
previous_camera=None
for f in range(990):
    s.frame_set(f);cam=s.camera;M=I@cam.matrix_world;eye=M.translation
    corners=[M@(p*(cam.data.clip_start/-p.z))for p in cam.data.view_frame(scene=s)]
    segments=[(eye,c)for c in corners]+[(corners[i],corners[(i+1)%4])for i in range(4)]
    if previous_camera is not None:segments.append((previous_camera,eye))
    for a,b in segments:
        direction=b-a;length=direction.length
        if length<1e-8:continue
        hit,normal,face,dist=newtree.ray_cast(a,direction.normalized(),length)
        if hit is not None:camera_hits.append({'frame':f,'object':facenames[face],'point':list(hit)});break
    previous_camera=eye.copy()
    for name,children in actor_children.items():
        points=[I@o.matrix_world@Vector(v)for o in children for v in o.bound_box]
        if not points or not boxhit(bbox(points),newbounds):continue
        actor_near+=1;tree,names,bb,boxes=combine(children);pairs=tree.overlap(newtree)
        if pairs:actor_hits.append({'frame':f,'actor':name,'objects':dict(Counter(facenames[j]for i,j in pairs))})
s.frame_set(0)

# Fitted foundation bottoms should meet the actual tessellated land, and the
# horizontal tangent top should remain above it at the architectural footprint.
terrain_obj=s.objects.get('CNX_CURVED_DISTRICT_LAND')
foundation_records=[];foundation_errors=[]
if terrain_obj:
    tv,tf=mesh_data(terrain_obj);terrain_tree=BVHTree.FromPolygons(tv,tf)
    for o in newmeshes:
        if not(o.name.endswith('_FOUNDATION')or o.name.endswith('_TERRACE'))or len(o.data.vertices)<8 or len(o.data.vertices)%2:continue
        m=I@o.matrix_world;v=[m@p.co for p in o.data.vertices];half=len(v)//2;row={'name':o.name,'corners':[]}
        for top,bottom in zip(v[:half],v[half:]):
            p,normal,face,dist=terrain_tree.ray_cast(Vector((bottom.x,bottom.y,100)),Vector((0,0,-1)))
            row['corners'].append({'xy':[bottom.x,bottom.y],'terrain_z':p.z if p else None,
                'bottom_gap':bottom.z-p.z if p else None,'top_clearance':top.z-p.z if p else None})
        missing=any(c['terrain_z']is None for c in row['corners'])
        gaps=[c['bottom_gap']for c in row['corners']if c['bottom_gap']is not None]
        clearance=[c['top_clearance']for c in row['corners']if c['top_clearance']is not None]
        edge_gaps=[]
        for a,b in zip(v[half:],v[half+1:]+v[half:half+1]):
            for t in [.2,.4,.6,.8]:
                q=a.lerp(b,t);p=terrain_tree.ray_cast(Vector((q.x,q.y,100)),Vector((0,0,-1)))[0]
                if p:edge_gaps.append(q.z-p.z)
        row.update({'missing_land':missing,'max_bottom_gap':max(gaps,default=None),'min_top_clearance':min(clearance,default=None)})
        row['max_skirt_edge_gap']=max(edge_gaps,default=None)
        if missing or max(gaps+edge_gaps,default=0)>.08 or min(clearance,default=0)<-.10:foundation_errors.append(row)
        foundation_records.append(row)

# Connected, closed generated components have unambiguous signed-volume normals.
normal_errors=[];closed_count=0;open_count=0;seen=set()
for o in newmeshes:
    if o.type!='MESH'or o.data.name in seen:continue
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
        ec=Counter();volume=0
        origin=me.vertices[faces[0].vertices[0]].co
        for p in faces:
            ids=list(p.vertices)
            for a,b in zip(ids,ids[1:]+ids[:1]):ec[tuple(sorted((a,b)))]+=1
            a=me.vertices[ids[0]].co-origin
            for j in range(1,len(ids)-1):
                b=me.vertices[ids[j]].co-origin;c=me.vertices[ids[j+1]].co-origin
                volume+=a.dot(b.cross(c))/6
        if all(v==2 for v in ec.values()):
            closed_count+=1
            if volume < -1e-7:normal_errors.append({'object':o.name,'faces':len(faces),'signed_volume':volume})
        else:open_count+=1

checks={'source_all_18311_objects_retained':not(old-now),'all_original_fields_exact_except_documented_wave_visibility':not changes,
        'all_original_actions_exact':not action_errors,'all_original_materials_exact':not mat_errors,
        'all_original_collections_retained':not collection_errors,'camera_and_actor_matrices_990_frames_exact':max(motion_errors.values())==0,
        'camera_optics_990_frames_exact':before['optics']==after['optics'],'scene_timing_camera_exact':before['scene']==after['scene'],
        'all_added_objects_CNX_prefix':all(n.startswith('CNX_')for n in added),'new_geometry_clear_camera_sweeps':not camera_hits,
        'new_geometry_clear_moving_actors':not actor_hits,'new_geometry_clear_original_visible_architecture':not static_conflicts,
        'foundations_contact_terrain':not foundation_errors,'closed_new_components_outward':not normal_errors,
        'source_file_unchanged':hashlib.sha256(SOURCE.read_bytes()).hexdigest()==source_hash,
        'candidate_file_unchanged':hashlib.sha256(CANDIDATE.read_bytes()).hexdigest()==candidate_hash}
report={'source':str(SOURCE),'source_sha256':source_hash,'candidate':str(CANDIDATE),'candidate_sha256':candidate_hash,'checks':checks,
        'source_count':len(old),'candidate_count':len(now),'added_count':len(added),'added_names':added,
        'missing':sorted(old-now),'original_changes':changes,'changed_actions':action_errors,'changed_materials':mat_errors,
        'documented_wave_visibility_changes':visibility_changes,'allowed_ground_contacts':allowed_ground_contacts,
        'hidden_wave_unevaluated_world_cache_verified_from_authored_hierarchy':hidden_wave_transform_cache,
        'collection_errors':collection_errors,'matrix_errors':motion_errors,'added_bounds_local':newbounds,
        'camera_hits':camera_hits,'moving_actor_hits':actor_hits,'actor_broadphase_candidates':actor_near,
        'original_architecture_checked':checked_static,'original_architecture_conflicts':static_conflicts,
        'foundation_records':foundation_records,'foundation_errors':foundation_errors,
        'closed_components':closed_count,'open_components':open_count,'inward_closed_components':normal_errors,
        'new_object_bounds':newboxes,
        'new_root_metadata':{n:{k:simple(v)for k,v in s.objects[n].items()}for n in added if s.objects[n].type=='EMPTY'and len(s.objects[n].keys())}}
(OUT/'expansion-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('VERIFICATION_RESULT',json.dumps({'checks':checks,'counts':[len(old),len(now),len(added)],'motion_errors':motion_errors,'conflicts':len(static_conflicts)}),flush=True)
