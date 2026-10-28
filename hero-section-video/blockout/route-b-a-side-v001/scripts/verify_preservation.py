import bpy,json,ast,hashlib,sys
import numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];candidate=Path(bpy.data.filepath);label=sys.argv[sys.argv.index('--')+1];is_city=label.startswith('city');cfg=json.loads((R/'route-config.json').read_text())
tree=ast.parse((R.parent/'s2-styleframe-match-v001/scripts/verify_title_water.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in {'digest','actions','objects'}],type_ignores=[]),'<pure helpers>','exec'))
def snapshot():
 s=bpy.context.scene;s.frame_set(156);data={'objects':objects(),'actions':actions(),'timeline':[s.frame_start,s.frame_end,s.render.fps,s.render.fps_base,sorted((m.name,m.frame)for m in s.timeline_markers)],'lens':{p:getattr(s.camera.data,p)for p in ['lens','sensor_width','sensor_height','sensor_fit','shift_x','shift_y','clip_start','clip_end']},'geometry':{o.name:digest([[list(v.co)for v in o.data.vertices],[list(p.vertices)for p in o.data.polygons]])for o in s.objects if o.type=='MESH'},'camera':[],'ship':[],'cargo':[],'spreader':[]}
 for f in range(1393):
  s.frame_set(f)
  for key,n in [('camera','CAM_MASTER'),('ship','A02_SHIP'),('cargo','A01_CONTAINER'),('spreader','P01_SPREADER')]:data[key].append(np.array(s.objects[n].matrix_world))
 return data
out=snapshot();bpy.ops.wm.open_mainfile(filepath=str(R/'inputs/base.blend'));base=snapshot()
if is_city:
 allowed={'CN_FRAME','CR_COMPACT_GANTRY','P01_SPREADER','CAM_MASTER','CAM_LOOK_TARGET','CR_SLEW_JIB','CR_TROLLEY_CARRIAGE','CR_SUSPENSION_HEAD',*[n for n in base['objects']if n.startswith('CR_WORKING_CABLE')]}
else:allowed=set(cfg['regional_roots'])|{'B_US_RIGID_TRANSFER','A02_SHIP','A01_CONTAINER','CAM_MASTER','CAM_LOOK_TARGET','SHIP_ROUTE','CAMERA_PATH'}
diffs=[n for n in base['objects'].keys()|out['objects'].keys()if base['objects'].get(n)!=out['objects'].get(n)];unexpected=[n for n in diffs if n not in allowed]
gdiff=[n for n in base['geometry'].keys()|out['geometry'].keys()if base['geometry'].get(n)!=out['geometry'].get(n)]
local_old=np.load(R/'review/current-local-samples.npz');local_new=np.load(R/'review'/f'{label}-local-samples.npz');us_error=float(np.max(abs(local_old['us']-local_new['us'])));load_error=float(np.max(abs(local_old['cargo']-local_new['cargo'])))
after=340 if is_city else 456;T=Matrix.Identity(4)if is_city else Matrix(cfg['rigid_transfer']);T=np.array(T)
camera_error=max(float(np.max(abs(out['camera'][f]-T@base['camera'][f])))for f in range(after,1393))
ship_error=max(float(np.max(abs(out['ship'][f]-T@base['ship'][f])))for f in range(0 if is_city else 510,1393))
cargo_error=max(float(np.max(abs(out['cargo'][f]-T@base['cargo'][f])))for f in range(0 if is_city else 510,1393))
s1_error=max(float(np.max(abs(out['camera'][f]-base['camera'][f])))for f in range(97))if not is_city else None
checks={'only_authorized_object_changes':not unexpected,'all_mesh_geometry_unchanged':not gdiff,'timeline_markers_fps_preserved':out['timeline']==base['timeline'],'camera_optics_preserved':out['lens']==base['lens'],'US_local_roots_all_integer_and_boundary_samples_preserved':us_error<.0002,'cargo_on_ship_relative_pose_preserved':load_error<.0002,'later_camera_preserved_in_US_frame':camera_error<.0002,'docked_ship_preserved_in_US_frame':ship_error<.0002,'US_cargo_handoff_preserved':cargo_error<.0002,'source_hash_unchanged':hashlib.sha256(Path(json.loads((R/'inputs/manifest.json').read_text())['source']).read_bytes()).hexdigest()==json.loads((R/'inputs/manifest.json').read_text())['source_sha256']}
if not is_city:checks['S1_camera_unchanged']=s1_error<.0002
report={'file':str(candidate),'sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'checks':checks,'changed_objects':diffs,'unexpected_objects':unexpected,'geometry_changes':gdiff,'US_local_max_error':us_error,'cargo_relative_error':load_error,'later_camera_error':camera_error,'docked_ship_error':ship_error,'US_cargo_error':cargo_error,'S1_camera_error':s1_error,'method':'All source mesh vertices/faces and protected object transforms, parent/material/visibility; all-frame regional root evaluation plus quarter-frame joins; unchanged child geometry/local matrices together with action signatures checked separately.'}
# Existing actions on unchanged objects must still be linked and identical.
changed_actions=[]
for o in bpy.context.scene.objects:
 if o.name not in allowed and o.animation_data and o.animation_data.action:
  n=o.animation_data.action.name
  if base['actions'].get(n)!=out['actions'].get(n):changed_actions.append(n)
checks['protected_actions_preserved']=not changed_actions;report['unexpected_actions']=changed_actions
(R/'review'/f'{label}-preservation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report));assert all(checks.values()),checks
