"""Independent read-only integrated geometry/material/action/support checks."""
import bpy
import ast
import array
import json
import hashlib
import math
import statistics
import sys
from pathlib import Path
from collections import defaultdict,Counter
from mathutils import Vector,Matrix,Quaternion
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[1];REVIEW=ROOT/'review';BLOCKOUT=ROOT.parent
manifest=json.loads((REVIEW/'geometry-manifest.json').read_text())
us=json.loads((REVIEW/'geometry-us.json').read_text())
cn=json.loads((REVIEW/'geometry-cn.json').read_text())
candidate=Path(bpy.data.filepath)
assert candidate.name=='pnpline-cn-us-integrated-v001.blend',candidate
candidate_hash=hashlib.sha256(candidate.read_bytes()).hexdigest()

def import_functions(path,names):
    source=ast.parse(Path(path).read_text())
    exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef)and n.name in names],type_ignores=[]),str(path),'exec'),globals())

import_functions(ROOT/'scripts/audit_geometry.py',{'digest','simple','geometry','material_signature','matrix','rna_dependency'})
import_functions(BLOCKOUT/'cn-port-camera-v001/scripts/ship_support.py',{'ocean_tree','water_at','perimeter_points','ship_geometry','support_measure','mesh_tree','descendant'})
sys.path.insert(0,str(BLOCKOUT/'pacing-33s-v001/scripts'))
from timing import TimeMap
clock=TimeMap()

def action_signature(action):
    rows=[]
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fc in bag.fcurves:
                    rows.append((fc.data_path,fc.array_index,fc.extrapolation,
                                 [(list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation,k.handle_left_type,k.handle_right_type,k.easing)for k in fc.keyframe_points],
                                 [rna_dependency(m)for m in fc.modifiers]))
    return digest(rows)

# Read the accepted US file for immutable original action fingerprints.
bpy.ops.wm.open_mainfile(filepath=us['file']);s=bpy.context.scene;s.frame_set(0)
original_actions={a.name:action_signature(a)for a in bpy.data.actions}
bpy.ops.wm.open_mainfile(filepath=str(candidate));s=bpy.context.scene;s.frame_set(0)
geometry_cache={};current={}
for o in s.objects:
    if o.data and o.data.name not in geometry_cache:geometry_cache[o.data.name]=geometry(o.data)
    current[o.name]={'type':o.type,'parent':o.parent.name if o.parent else None,
                     'basis':matrix(o.matrix_basis),'parent_inverse':matrix(o.matrix_parent_inverse),
                     'world_f0':matrix(o.matrix_world),'geometry':geometry_cache.get(o.data.name)if o.data else None,
                     'materials':[m.name if m else None for m in o.data.materials]if o.data and hasattr(o.data,'materials')else [],
                     'hide_render':o.hide_render,'hide_viewport':o.hide_viewport,'hide_layer':o.hide_get(),
                     'constraints':[rna_dependency(c)for c in o.constraints],'modifiers':[rna_dependency(m)for m in o.modifiers]}

def numeric_error(a,b):
    if isinstance(a,(list,tuple))and isinstance(b,(list,tuple)):
        if len(a)!=len(b):return 1e99
        return max((numeric_error(x,y)for x,y in zip(a,b)),default=0)
    return abs(a-b)

def equal(field,a,b):
    return numeric_error(a,b)<.0001 if field in {'basis','parent_inverse','world_f0'}else a==b

allowed={n:set(d['fields'])for n,d in manifest['cn_common_deltas'].items()}
allowed.setdefault('CAM_MASTER',set()).add('parent')
allowed.setdefault('CAM_LOOK_TARGET',set()).add('parent')
fields=['type','parent','basis','parent_inverse','geometry','materials','hide_render','hide_viewport','hide_layer','constraints','modifiers']
us_missing=[];us_changes=[]
for name,old in us['objects'].items():
    now=current.get(name)
    if now is None:us_missing.append(name);continue
    for field in fields:
        if field not in allowed.get(name,set())and not equal(field,old[field],now[field]):
            us_changes.append({'name':name,'field':field,'before':old[field],'after':now[field]})

skipped={'PORT_CAMERA_RETARGET','PORT_CAMERA_TARGET_RETARGET'}
expected_new=set(manifest['cn_added_objects'])-skipped
cn_missing=sorted(expected_new-set(current));cn_changes=[]
for name in sorted(expected_new&set(current)):
    old=cn['objects'][name];now=current[name]
    check=['type','geometry','materials','hide_render','hide_viewport','constraints','modifiers','parent_inverse']
    if old['action']is None:check+=['basis','parent']
    for field in check:
        if not equal(field,old[field],now[field]):cn_changes.append({'name':name,'field':field,'expected':old[field],'actual':now[field]})
expected_static_errors=[]
for name,delta in manifest['cn_common_deltas'].items():
    if name in {'A01_CONTAINER','W01_NEW_PALLET','CAM_MASTER','CAM_LOOK_TARGET'}:continue
    for field,expected in delta['cn'].items():
        if field in current[name]and not equal(field,expected,current[name][field]):expected_static_errors.append({'name':name,'field':field})

material_now={m.name:material_signature(m)for m in bpy.data.materials}
materials_missing=sorted(set(us['materials'])-set(material_now))
materials_changed=[n for n in set(us['materials'])&set(material_now)if us['materials'][n]['digest']!=material_now[n]['digest']]
new_material_errors=[n for n in manifest['cn_added_materials']if n not in material_now or cn['materials'][n]['digest']!=material_now[n]['digest']]
actions_now={a.name:action_signature(a)for a in bpy.data.actions if a.name in original_actions}
actions_missing=sorted(set(original_actions)-set(actions_now))
actions_changed=[n for n in set(original_actions)&set(actions_now)if original_actions[n]!=actions_now[n]]
deps=[o.name for o in bpy.data.objects if o.name.startswith('__CN_DEP__')]
unlinked_parents=[(o.name,o.parent.name)for o in s.objects if o.parent and o.parent.name not in s.objects]
unlinked_targets=[]
for o in s.objects:
    for c in list(o.constraints)+list(o.modifiers):
        for prop in c.bl_rna.properties:
            if prop.type=='POINTER':
                try:target=getattr(c,prop.identifier)
                except (AttributeError,RuntimeError):continue
                if isinstance(target,bpy.types.Object)and target.name not in s.objects:unlinked_targets.append((o.name,c.name,prop.identifier,target.name))

I=s.objects['SF_CN_LAYOUT'].matrix_world.inverted();water=ocean_tree(s,I);bottom,deck=ship_geometry(s)
env=[o for o in s.objects if o.type=='MESH'and not o.hide_render and(o.name=='CN_QUAY'or descendant(o,{'PORT_MODEL_ROOT'}))]
envtree,envnames=mesh_tree(env,I)
actors=[o for o in s.objects if o.type=='MESH'and not o.hide_render and descendant(o,{'A02_SHIP','A01_CONTAINER','W01_NEW_PALLET'})]
last=clock.output(360);support=[];collisions={}
times=sorted(set([i/2 for i in range(math.ceil(last*2)+1)]+[clock.output(f)for f in [0,24,48,72,120,156,180,216,252,272,300,336,360]]))
for index,t in enumerate(times):
    s.frame_set(int(t),subframe=t%1)
    measure=support_measure(I@s.objects['A02_SHIP'].matrix_world,bottom,deck,water)
    measure.update({'output_frame':t,'source_frame':clock.source(t)});support.append(measure)
    if abs(t-round(t))<1e-6:
        at,an=mesh_tree(actors,I)
        for a,b in at.overlap(envtree):collisions.setdefault(an[a]+' | '+envnames[b],[]).append(t)
    if index%100==0:print('VERIFY_SUPPORT',index,len(times),flush=True)

hashes_after={'us':hashlib.sha256(Path(us['file']).read_bytes()).hexdigest(),'cn':hashlib.sha256(Path(cn['file']).read_bytes()).hexdigest()}
checks={'all_US_original_objects_retained':not us_missing,'US_nonpatch_object_states_preserved':not us_changes,
        'all_selected_CN_objects_present':not cn_missing,'CN_new_static_geometry_states_exact':not cn_changes,
        'CN_common_static_patch_exact':not expected_static_errors,'all_US_materials_exact':not materials_missing and not materials_changed,
        'new_CN_materials_exact':not new_material_errors,'all_US_actions_exact':not actions_missing and not actions_changed,
        'no_duplicate_or_unresolved_object_dependencies':not deps and not unlinked_parents and not unlinked_targets,
        'retimed_hull_supported':min(r['min_immersion']for r in support)>.2,
        'retimed_deck_freeboard':min(r['min_deck_freeboard']for r in support)>.4,
        'moving_actors_clear_CN_terminal':not collisions,
        'source_files_unchanged':hashes_after=={k:manifest['source_hashes'][k]for k in ['us','cn']},
        'candidate_file_unchanged':hashlib.sha256(candidate.read_bytes()).hexdigest()==candidate_hash}
report={'file':str(candidate),'sha256':candidate_hash,'checks':checks,'original_US_count':len(us['objects']),
        'expected_CN_new_count':len(expected_new),'integrated_count':len(current),'US_missing':us_missing,
        'US_unexpected_changes':us_changes,'CN_missing':cn_missing,'CN_unexpected_changes':cn_changes,
        'CN_common_patch_errors':expected_static_errors,'US_materials_missing':materials_missing,'US_materials_changed':materials_changed,
        'new_CN_material_errors':new_material_errors,'US_actions_missing':actions_missing,'US_actions_changed':actions_changed,
        'duplicate_dependency_objects':deps,'unlinked_parents':unlinked_parents,'unlinked_targets':unlinked_targets,
        'support_samples':len(support),'support_output_range':[0,last],'min_hull_immersion':min(r['min_immersion']for r in support),
        'min_deck_freeboard':min(r['min_deck_freeboard']for r in support),'moving_actor_crossings':collisions,
        'support':support,'source_hashes_after':hashes_after,'read_only':True}
(REVIEW/'geometry-verification.json').write_text(json.dumps(report,indent=2))
print('GEOMETRY_VERIFY',json.dumps({k:v for k,v in report.items()if k not in {'support','US_unexpected_changes','CN_unexpected_changes'}}),flush=True)
assert all(checks.values()),checks
