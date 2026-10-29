"""Compare independently rebuilt complete scenes, including geometry and animation."""
import bpy,sys,json,hashlib,ast
from pathlib import Path
R=Path(__file__).resolve().parents[1]
args=sys.argv[sys.argv.index('--')+1:]; first=Path(args[0]); second=Path(args[1])
tree=ast.parse((R/'scripts/audit_preservation.py').read_text())
# Reuse the same material and RNA serializers as the preservation audit.
base=ast.parse((R.parent/'us-city-concept-v001/scripts/verify_preservation.py').read_text())
exec(compile(ast.Module(body=[n for n in base.body if isinstance(n,ast.FunctionDef) and n.name in ['digest','scalar','props','node_data']],type_ignores=[]),'helpers','exec'))
exec(compile((R.parent/'us-arrival-rework-v001/scripts/material_signature.py').read_text(),'material-signature','exec'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='action'],type_ignores=[]),'action-signature','exec'))
def custom(value):
 if isinstance(value,(str,int,float,bool)) or value is None:return value
 if hasattr(value,'items'):return {k:custom(v) for k,v in value.items()}
 if hasattr(value,'to_list'):return [custom(v) for v in value.to_list()]
 if hasattr(value,'name'):return value.name
 return [custom(v) for v in value]
def snapshot(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.frame_set(1)
 result={};materials={}
 for o in s.objects:
  d={'type':o.type,'parent':o.parent.name if o.parent else None,'basis':list(map(list,o.matrix_basis)),'inverse':list(map(list,o.matrix_parent_inverse)),'rotation':o.rotation_mode,'custom':custom(o),'visibility':[o.hide_render,o.hide_viewport],'constraints':[props(c) for c in o.constraints],'modifiers':[props(m) for m in o.modifiers]}
  d['action']=action(o.animation_data.action) if o.animation_data else None
  if o.type=='MESH':d['geometry']=[[list(v.co) for v in o.data.vertices],[[list(p.vertices),p.material_index,p.use_smooth] for p in o.data.polygons]]
  elif o.type in ['CAMERA','LIGHT','FONT']:d['data']=props(o.data,('animation_data',))
  elif o.type=='CURVE':d['curve']=[props(o.data),[[list(p.co) for p in sp.points] for sp in o.data.splines]]
  if o.data and o.data.animation_data:d['data_action']=action(o.data.animation_data.action)
  if hasattr(o.data,'materials'):
   d['materials']=[]
   for m in o.data.materials:
    if m:materials.setdefault(m.name,digest(node_data(m)));d['materials'].append(materials[m.name])
    else:d['materials'].append(None)
  result[o.name]=digest(d)
 return {'objects':result,'world':digest(node_data(s.world)),'timeline':[s.frame_start,s.frame_end,s.render.fps,sorted((m.name,m.frame) for m in s.timeline_markers)],'view':digest(props(s.view_settings)),'camera':s.camera.name}
a=snapshot(first);b=snapshot(second)
diff={k:([n for n in a[k].keys()|b[k].keys() if a[k].get(n)!=b[k].get(n)] if isinstance(a[k],dict) else a[k]!=b[k]) for k in a}
report={'first':str(first),'first_sha256':hashlib.sha256(first.read_bytes()).hexdigest(),'second':str(second),'second_sha256':hashlib.sha256(second.read_bytes()).hexdigest(),'objects':len(a['objects']),'differences':diff,'method':'Complete object geometry, hierarchy, actions, materials, data properties, custom properties, visibility, scene camera/timeline/world/view; binary .blend UUIDs need not match.'}
(R/'review/reproduction.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert not any(bool(v) for v in diff.values())
