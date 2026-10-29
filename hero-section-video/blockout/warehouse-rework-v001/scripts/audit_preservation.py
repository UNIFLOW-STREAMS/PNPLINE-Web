import bpy,ast,sys,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];S=bpy.context.scene;candidate=Path(bpy.data.filepath)
tree=ast.parse((R.parent/'us-city-concept-v001/scripts/verify_preservation.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['digest','scalar','props','node_data']],type_ignores=[]),'signature-helpers','exec'))
exec(compile((R.parent/'us-arrival-rework-v001/scripts/material_signature.py').read_text(),'material-signature','exec'))
def allowed(n):
 return n.startswith(('WAREHOUSE_','RACK_','W01_NEW_PALLET','W01_STORED_PALLET','W02_','W04_','W05_','W06_','W07_','W08_','W09_','CH_','TABLE_LEG_','PACK_BOX_','LAST_BOX_')) or n in [x+s for x in ['INBOUND_WAIT','STORAGE','PICKING','PACKING','OUTBOUND_WAIT'] for s in ['_ZONE','_REVIEW_LABEL']]
def action(a):
 if not a:return None
 return digest([[fc.data_path,fc.array_index,fc.extrapolation,[[list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation,k.handle_left_type,k.handle_right_type] for k in fc.keyframe_points],[props(m) for m in fc.modifiers]] for l in a.layers for st in l.strips for bag in st.channelbags for fc in bag.fcurves])
def snap():
 s=bpy.context.scene;s.frame_set(1);result={};mats={};acts={}
 for o in s.objects:
  if allowed(o.name) or o.name.startswith('WH_'):continue
  d={'type':o.type,'parent':o.parent.name if o.parent else None,'inverse':list(map(list,o.matrix_parent_inverse)),'basis':list(map(list,o.matrix_basis)),'rotation_mode':o.rotation_mode,'constraints':[props(c) for c in o.constraints],'modifiers':[props(m) for m in o.modifiers],'visibility':[o.hide_render,o.hide_viewport]}
  if o.animation_data and o.animation_data.action:
   a=o.animation_data.action;acts.setdefault(a.name,action(a));d['action']=acts[a.name]
  if o.type=='MESH':d['mesh']={'v':[list(v.co) for v in o.data.vertices],'f':[[list(p.vertices),p.material_index,p.use_smooth] for p in o.data.polygons]}
  elif o.type=='CURVE':d['curve']=[props(o.data),[[list(p.co) for p in sp.points] for sp in o.data.splines]]
  elif o.type in ['CAMERA','LIGHT']:
   d['data']=props(o.data,('animation_data',))
   if o.data.animation_data:d['data_action']=action(o.data.animation_data.action)
  if hasattr(o.data,'materials'):
   d['materials']=[]
   for m in o.data.materials:
    if m:mats.setdefault(m.name,digest(node_data(m)));d['materials'].append(mats[m.name])
    else:d['materials'].append(None)
  result[o.name]=digest(d)
 return {'objects':result,'world':digest(node_data(s.world)),'timeline':[s.frame_start,s.frame_end,s.render.fps,s.render.fps_base,sorted((m.name,m.frame) for m in s.timeline_markers)],'camera':s.camera.name,'view':digest(props(s.view_settings))}
after=snap();bpy.ops.wm.open_mainfile(filepath=str(R/'inputs/arrival-v010.blend'));before=snap()
diff={k:([n for n in before[k].keys()|after[k].keys() if before[k].get(n)!=after[k].get(n)] if isinstance(before[k],dict) else before[k]!=after[k]) for k in before}
report={'candidate_sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256((R/'inputs/arrival-v010.blend').read_bytes()).hexdigest(),'protected_objects':len(before['objects']),'differences':diff,'scope':'Explicit warehouse object prefixes only; every other object, complete animation curves, camera/lens, hierarchy, mesh, material and timeline preserved.'}
(R/'review'/f'{candidate.stem}-preservation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert not any(bool(v) for v in diff.values())
