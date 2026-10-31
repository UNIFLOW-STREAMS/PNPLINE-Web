import bpy,importlib.util,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];B=R.parents[1]/'blockout'
spec=importlib.util.spec_from_file_location('audit',B/'us-title-curve-v001/scripts/audit_preservation.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
src=Path(json.loads((R/'review/survey.json').read_text())['file']);dst=R/'pnpline-hero-material-v001.blend'
before=a.snapshot(src);s=bpy.context.scene;names=a.motion_names(s);a.minimize_scene(s,names);bm=a.capture_motion(s,names)
after=a.snapshot(dst);s=bpy.context.scene;a.minimize_scene(s,names);am=a.capture_motion(s,names)
changes=[];errors=[]
for name,old in before['objects'].items():
 new=after['objects'].get(name)
 if not new:errors.append([name,'removed']);continue
 fields=[k for k in old if old[k]!=new[k]]
 if fields:changes.append([name,fields])
 allowed={'materials'}
 if old['type']=='LIGHT':allowed|={'geometry'}
 for field in fields:
  if field not in allowed:errors.append([name,field])
scene_errors={k:[v,after['scene'][k]] for k,v in before['scene'].items() if k!='resolution' and v!=after['scene'][k]}
added=set(after['objects'])-set(before['objects']);motion_errors={n:max(a.error(x,y) for x,y in zip(bm['objects'][n],am['objects'][n])) for n in names}
checks={'source_unchanged':a.sha(src)==json.loads((R/'review/survey.json').read_text())['sha256'],'all_original_nonmaterial_geometry_hierarchy_visibility_constraints_drivers_exact':not errors,'all_actions_exact':before['actions']==after['actions'],'all_990_frame_motion_exact':all(v==0 for v in motion_errors.values()),'all_990_frame_camera_optics_exact':bm['optics']==am['optics'],'timeline_markers_camera_exact':not scene_errors,'only_lights_added':all(after['objects'][n]['type']=='LIGHT' and n.startswith('LD_') for n in added),'time_mapping_exact':(src.parent/'time-map.json').read_bytes()==(R/'time-map.json').read_bytes()}
report=dict(checks=checks,passed=all(checks.values()),source_sha256=a.sha(src),result_sha256=a.sha(dst),objects=len(before['objects']),actions=len(before['actions']),tracked_objects=len(names),frames=990,max_motion_error=max(motion_errors.values()),forbidden_changes=errors,scene_errors=scene_errors,allowed_object_changes=changes,new_lights=sorted(added),material_changes=[n for n,v in before['materials'].items() if after['materials'].get(n)!=v])
(R/'review/preservation-verification.json').write_text(json.dumps(report,indent=2));print('VERIFIED',json.dumps(checks),flush=True)
