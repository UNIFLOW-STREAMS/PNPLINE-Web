import bpy,ast,json,hashlib,numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1];candidate=Path(bpy.data.filepath)
tree=ast.parse((R.parent/'s2-styleframe-match-v001/scripts/verify_title_water.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in {'digest','objects','actions'}],type_ignores=[]),'helpers','exec'))
affected={'A01_CONTAINER','W01_NEW_PALLET','CAM_MASTER','CAM_LOOK_TARGET','P01_SPREADER','CR_SLEW_JIB','CR_TROLLEY_CARRIAGE','CR_SUSPENSION_HEAD'}|{o.name for o in bpy.context.scene.objects if o.name.startswith('CR_WORKING_CABLE')}
geometry=set(json.loads((R/'delivery.json').read_text())['changed_static_geometry'])
def under(o,n):
 while o:
  if o.name==n:return True
  o=o.parent
 return False
def moving(o):
 while o:
  if o.animation_data and o.animation_data.action:return True
  o=o.parent
 return False
def snapshot():
 s=bpy.context.scene;s.frame_set(156)
 r={'objects':objects(),'actions':actions(),'links':{o.name:o.animation_data.action.name for o in s.objects if o.animation_data and o.animation_data.action},'visibility':{o.name:[o.hide_render,o.hide_viewport,o.hide_get()]for o in s.objects},'timeline':[s.frame_start,s.frame_end,s.render.fps,s.render.fps_base,sorted((m.name,m.frame)for m in s.timeline_markers)]}
 names=sorted(o.name for o in s.objects if moving(o) and not any(under(o,n)for n in affected))
 h=hashlib.sha256();later=[]
 for f in range(s.frame_start,s.frame_end+1):
  s.frame_set(f);h.update(json.dumps([list(map(list,s.objects[n].matrix_world))for n in names]).encode())
  if f>=72:later.append([list(map(list,s.objects[n].matrix_world))for n in ['A01_CONTAINER','W01_NEW_PALLET','CAM_MASTER','CAM_LOOK_TARGET']]+[[[s.camera.data.lens]*4]*4])
 r['protected_digest']=h.hexdigest();r['later']=np.array(later);r['names']=names
 return r
a=snapshot();bpy.ops.wm.open_mainfile(filepath=str(R/'inputs/base.blend'));b=snapshot()
changed=[n for n in a['objects'].keys()|b['objects'].keys() if a['objects'].get(n)!=b['objects'].get(n)]
badlinks=[n for n in a['links'].keys()|b['links'].keys() if n not in affected and a['links'].get(n)!=b['links'].get(n)]
badactions=[n for n in {v for k,v in b['links'].items()if k not in affected}if a['actions'].get(n)!=b['actions'].get(n)]
error=float(np.max(np.abs(a['later']-b['later'])))
checks={'only_authorized_objects':not(set(changed)-affected-geometry),'protected_action_links':not badlinks,'protected_actions':not badactions,'all_frames_unaffected_world_matrices_exact':a['protected_digest']==b['protected_digest'],'landing_and_later_cargo_payload_camera_lens_preserved':error<.0001,'visibility_unchanged':a['visibility']==b['visibility'],'timeline_fps_unchanged':a['timeline']==b['timeline'],'baseline_hash':hashlib.sha256((R/'inputs/base.blend').read_bytes()).hexdigest()=='64a206b9104e6c8f0cd0f4c2232bcac8789df47bd2e06cc3207743a87d70ce98'}
report={'file':str(candidate),'sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'checks':checks,'changed_objects':changed,'unexpected':list(set(changed)-affected-geometry),'bad_actions':badactions,'bad_links':badlinks,'max_later_matrix_error':error,'protected_names':a['names']}
(R/'review/scope.json').write_text(json.dumps(report,indent=2));print('SCOPE',checks,error);assert all(checks.values())
