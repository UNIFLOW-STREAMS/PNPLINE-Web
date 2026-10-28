import bpy,ast,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];candidate=Path(bpy.data.filepath)
tree=ast.parse((R.parent/'s2-styleframe-match-v001/scripts/verify_title_water.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in {'digest','objects','actions'}],type_ignores=[]),'helpers','exec'))
affected={'A01_CONTAINER','W01_NEW_PALLET','P01_SPREADER'}|{o.name for o in bpy.context.scene.objects if o.name.startswith('CR_WORKING_CABLE')}
def snapshot():
 s=bpy.context.scene;s.frame_set(156);rows={}
 for n in affected:
  a=s.objects[n].animation_data
  for l in a.action.layers:
   for st in l.strips:
    for b in st.channelbags:
     if b.slot_handle!=a.action_slot.handle:continue
     for fc in b.fcurves:
      rows[n+'|'+fc.data_path+'|'+str(fc.array_index)]=[fc.evaluate(i/8)for i in range(576,11137)]
 return {'objects':objects(),'actions':actions(),'links':{o.name:o.animation_data.action.name for o in s.objects if o.animation_data and o.animation_data.action},'late':rows,'visibility':{o.name:[o.hide_render,o.hide_viewport,o.hide_get()]for o in s.objects},'timeline':[s.frame_start,s.frame_end,s.render.fps,s.render.fps_base,sorted((m.name,m.frame)for m in s.timeline_markers)]}
a=snapshot();bpy.ops.wm.open_mainfile(filepath=str(R/'inputs/base.blend'));b=snapshot()
allowed_actions={v for n,v in b['links'].items()if n in affected}
changed_actions=[n for n in a['actions'].keys()|b['actions'].keys()if a['actions'].get(n)!=b['actions'].get(n)]
err=max(abs(v-w)for k,vs in a['late'].items()for v,w in zip(vs,b['late'][k]))
checks={'all_objects_geometry_and_f156_transforms_unchanged':a['objects']==b['objects'],'only_approved_animated_roots_changed':not(set(changed_actions)-allowed_actions),'action_links_exact':a['links']==b['links'],'all_f72_plus_curves_exact_at_eighth_frames':err==0,'visibility_exact':a['visibility']==b['visibility'],'timeline_exact':a['timeline']==b['timeline'],'source_hash_intact':hashlib.sha256((R/'inputs/base.blend').read_bytes()).hexdigest()=='c21292bb055930d745ad37e9a3f4f732743043d5528429c030b9f366ff6e1942'}
r={'file':str(candidate),'sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'checks':checks,'changed_actions':changed_actions,'max_after_landing_error':err,'camera_note':'Both camera and target excluded from allowed changed actions; therefore camera unchanged for entire animation.'}
(R/'review/scope.json').write_text(json.dumps(r,indent=2));print(r);assert all(checks.values())
