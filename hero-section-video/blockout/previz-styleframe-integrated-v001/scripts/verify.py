import bpy,json,ast,hashlib,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];A=R.parent/'s2-styleframe-match-v001';candidate=R/'master-previz-styleframe-v001.blend'
tree=ast.parse((A/'scripts/verify_title_water.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in {'digest','actions','objects'}],type_ignores=[]),'<helpers>','exec'))
def snapshot(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.frame_set(156)
 animated=sorted(o.name for o in s.objects if o.animation_data or o.constraints)
 data={'objects':objects(),'actions':actions(),'timeline':[s.frame_start,s.frame_end,s.render.fps,s.render.fps_base,sorted((m.name,m.frame)for m in s.timeline_markers)],'animated_names':animated,'collections':{c.name:sorted(o.name for o in c.objects)for c in bpy.data.collections}}
 rows=[];protected={}
 # Every integer frame plus quarter-frame samples at segment/lift joins.
 frames=sorted(set(range(s.frame_start,s.frame_end+1))|{f+q for f in [70,71,72,73,94,95,96,97,98,99,213,214,215,216,217,454,455,456,457,646,647,648,649,650,670,671,672,673,900,901,902,903,910,911,912,913,1198,1199,1200,1201]for q in [.25,.5,.75]})
 for f in frames:
  s.frame_set(int(f),subframe=f%1)
  rows.append([f,s.camera.data.lens,*[[n,list(map(list,s.objects[n].matrix_world))]for n in animated]])
  if path==candidate or path.name=='master-s2-city-reveal-china-v001.blend':
   protected[f]={n:list(map(list,s.objects[n].matrix_world))for n in ['CAM_MASTER','CAM_LOOK_TARGET','A01_CONTAINER','A02_SHIP','A03_TRUCK','A04_PALLET']if n in s.objects}
 data['evaluated_hash']=digest(rows);data['sample_count']=len(frames);data['protected']=protected
 return data
out=snapshot(candidate);src=snapshot(R/'inputs/layout-proposal-v032.blend');base=snapshot(R.parent/'s2-city-reveal-china-v001/master-s2-city-reveal-china-v001.blend')
diffs=[n for n in src['objects'].keys()|out['objects'].keys()if src['objects'].get(n)!=out['objects'].get(n)]
basechanged=[n for n in base['objects']if out['objects'].get(n)!=base['objects'][n]]
unexpectedactions=[n for n in base['actions']if base['actions'][n]!=out['actions'].get(n)and not any(k in n for k in ['CAM_MASTER','CAM_LOOK_TARGET','A01_CONTAINER','P01_SPREADER'])]
errors={n:0 for n in base['protected'][0]}
for f,rows in base['protected'].items():
 for n,mat in rows.items():
  if n in ['CAM_MASTER','CAM_LOOK_TARGET']and (f<72 or 97<f<215):continue
  if n=='A01_CONTAINER'and f<72:continue
  errors[n]=max(errors[n],max(abs(mat[i][j]-out['protected'][f][n][i][j])for i in range(4)for j in range(4)))
checks={'v032_all_objects_identical':not diffs,'v032_all_actions_identical':out['actions']==src['actions'],'v032_all_evaluated_motion_identical':out['evaluated_hash']==src['evaluated_hash'],'v032_collections_identical':out['collections']==src['collections'],'full_S1_S7_timeline_preserved':out['timeline']==base['timeline']==src['timeline'],'base_nonapproved_actions_preserved':not unexpectedactions,'base_protected_actors_and_camera_ranges_preserved':max(errors.values())<1e-5,'S1_S7_all_markers_present':all(any(m[0]==n for m in out['timeline'][4])for n in ['S1','S2','S3','S4','S5','S6','S7'])}
report={'file':str(candidate),'sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'checks':checks,'source_object_count':len(src['objects']),'action_count':len(out['actions']),'evaluated_samples':out['sample_count'],'source_differences':diffs,'base_changed_objects':basechanged,'unexpected_action_changes':unexpectedactions,'protected_transform_errors':errors,'timeline':out['timeline'],'scope':'Exact object geometry/visibility/parent/material assignment, actions and collections against current saved v032; all animated/constrained objects evaluated at every integer frame plus quarter-frame boundary samples. Protected primary actors compared to latest base master.'}
(R/'review/integration-verified.json').write_text(json.dumps(report,indent=2));print(json.dumps(report));assert all(checks.values())
