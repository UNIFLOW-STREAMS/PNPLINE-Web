import bpy,importlib.util,json,math,sys
from pathlib import Path
from mathutils import Matrix,Vector

R=Path(__file__).resolve().parents[1];OUT=R/'audit'
B=R.parents[1]/'blockout'
spec=importlib.util.spec_from_file_location('audit',B/'us-title-curve-v001/scripts/audit_preservation.py')
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
src=R/'inputs/before-dispatch.blend';dst=R/'candidate.blend'
source_sha=a.sha(src)
before=a.snapshot(src);s=bpy.context.scene;names=a.motion_names(s)
a.minimize_scene(s,names);bm=a.capture_motion(s,names)
print('SOURCE_MOTION_DONE',len(names),flush=True)
after=a.snapshot(dst);s=bpy.context.scene
added=sorted(set(after['objects'])-set(before['objects']))
all_geos=[s.objects[n] for n in added if s.objects[n].type in {'MESH','CURVE','FONT'} and a.visible(s.objects[n])]
dynamic_geos=[o for o in all_geos if a.under(o,{'A04_PRIMARY','A05_SECONDARY'})]
geos=[o for o in all_geos if o not in dynamic_geos]
tree,poly_names=a.combine(geos)
dynamic_tree=a.GeometryTree(dynamic_geos) if dynamic_geos else None
print('NEW_GEOMETRY_BVH_DONE',len(geos),len(poly_names),flush=True)
a.minimize_scene(s,names,[o.name for o in dynamic_geos]);am=a.capture_motion(s,names)
print('CANDIDATE_MOTION_DONE',flush=True)
allowed={f'E12_DESTINATION_{i}':{'hide_render','hide_viewport'} for i in range(4)}
allowed.update({n:{'hide_render','hide_viewport'} for n in ['E11_ROUTE_1','E11_ROUTE_-1','A05_WAIT_MERGE','CV_SUPPORT_A05_WAIT_MERGE']})
changes=[];errors=[];hidden_caches=[]
def chain_unchanged(name):
 while name:
  x=before['objects'].get(name);y=after['objects'].get(name)
  if not x or not y:return False
  if any(x[k]!=y[k] for k in ['parent','matrix_basis','matrix_parent_inverse','animation','constraints','drivers']):return False
  name=x['parent']
 return True
for name,old in before['objects'].items():
 new=after['objects'].get(name)
 if not new:errors.append([name,'removed']);continue
 fields=[k for k in old if old[k]!=new[k]]
 if 'matrix_world' in fields and new['hide_viewport'] and chain_unchanged(name):
  fields.remove('matrix_world');hidden_caches.append(name)
 if fields:changes.append([name,fields])
 for field in fields:
  if field not in allowed.get(name,set()):errors.append([name,field])
collection_errors=[]
for n,old in before['collections'].items():
 new=after['collections'].get(n)
 if new is None:collection_errors.append([n,'missing']);continue
 for k in ['hide_render','hide_viewport']:
  if old[k]!=new[k]:collection_errors.append([n,k])
 for k in ['objects','children']:
  if not set(old[k])<=set(new[k]):collection_errors.append([n,'removed_'+k])
motion_errors={n:max(a.error(x,y) for x,y in zip(bm['objects'][n],am['objects'][n])) for n in names}
scene_errors={k:[v,after['scene'][k]] for k,v in before['scene'].items() if v!=after['scene'][k]}
mat_errors=[n for n,v in before['materials'].items() if after['materials'].get(n)!=v]
camera_hits={};target_hits={};nearest={'distance':1e30};previous=None
for f in range(990):
 s.frame_set(f);cam=s.objects['CAM_MASTER'];eye=cam.matrix_world.translation.copy()
 if dynamic_tree:dynamic_tree.update()
 if tree:
  corners=[cam.matrix_world@(p*(cam.data.clip_start/abs(p.z))) for p in cam.data.view_frame(scene=s)]
  segments=[('near',eye,p) for p in corners]+[('near_edge',corners[i],corners[(i+1)%4]) for i in range(4)]
  if previous is not None:segments.append(('swept_eye',previous,eye))
  for kind,p,q in segments:
   d=q-p;ln=d.length
   if ln<1e-9:continue
   hit,nor,index,dist=tree.ray_cast(p,d/ln,ln)
   if hit is not None:camera_hits.setdefault(kind+' | '+poly_names[index],[]).append(f)
   if dynamic_tree:
    dn=dynamic_tree.ray(p,q)
    if dn is not None:camera_hits.setdefault(kind+' | '+dn,[]).append(f)
  p,nor,index,dist=tree.find_nearest(eye)
  if p is not None and dist<nearest['distance']:nearest={'distance':dist,'frame':f,'object':poly_names[index]}
  if f>=870 and 'CAM_LOOK_TARGET' in s.objects:
   target=s.objects['CAM_LOOK_TARGET'].matrix_world.translation;d=target-eye;ln=d.length
   hit,nor,index,dist=tree.ray_cast(eye,d/ln,ln)
   if hit is not None:target_hits.setdefault(poly_names[index],[]).append(f)
 previous=eye
checks={
 'source_file_immutable':a.sha(src)==source_sha,
 'original_objects_preserved_except_declared_proxy_and_road_visibility':not errors,
 'all_original_materials_exact':not mat_errors,
 'all_actions_exact':before['actions']==after['actions'],
 'all_990_frame_motion_exact':all(v==0 for v in motion_errors.values()),
 'all_990_frame_camera_optics_exact':bm['optics']==am['optics'],
 'timeline_markers_camera_render_contract_exact':not scene_errors,
 'all_new_objects_DSP_owned':all(n.startswith('DSP_') for n in added),
 'original_collections_preserved':not collection_errors,
 'new_geometry_clear_of_camera_sweep_and_near_plane':not camera_hits,
 'candidate_unchanged_during_audit':a.sha(dst)==after['sha256']}
report=dict(checks=checks,passed=all(checks.values()),source_sha256=source_sha,result_sha256=after['sha256'],
 original_objects=len(before['objects']),actions=len(before['actions']),tracked_objects=len(names),frames=990,
 max_motion_error=max(motion_errors.values()),forbidden_changes=errors,scene_errors=scene_errors,
 allowed_object_changes=changes,hidden_transform_cache_exceptions=hidden_caches,
 added_objects=added,material_errors=mat_errors,collection_errors=collection_errors,
 motion_errors=motion_errors,camera_crossings=camera_hits,nearest_camera_new_geometry=nearest,
 target_occlusions_S7=target_hits,
 scope='Read-only full original object/action/material snapshots and native 0-989 evaluated transforms/optics; camera swept eye and near-plane edges against actual added evaluated geometry. New A04/A05 detail descendants are updated dynamically. Target ray occlusions are composition diagnostics, not automatic failures.')
(OUT/'preservation-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('PRESERVATION_RESULT',json.dumps(checks),flush=True)
print('FORBIDDEN',json.dumps(errors),'NEAREST',json.dumps(nearest),'TARGET_HITS',json.dumps(target_hits),flush=True)
assert report['passed'],'See audit/preservation-verification.json'
