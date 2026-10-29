"""Protect source geometry/actions and untouched regional objects independently of transforms."""
import bpy,ast,json,hashlib,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];candidate=Path(bpy.data.filepath)
base=ast.parse((R.parent/'us-city-concept-v001/scripts/verify_preservation.py').read_text())
exec(compile(ast.Module(body=[n for n in base.body if isinstance(n,ast.FunctionDef) and n.name in ['digest','scalar','props','node_data']],type_ignores=[]),'helpers','exec'))
exec(compile((R.parent/'us-arrival-rework-v001/scripts/material_signature.py').read_text(),'material-signature','exec'))
def action(a):
 if not a:return None
 return digest([[fc.data_path,fc.array_index,fc.extrapolation,[[list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation,k.handle_left_type,k.handle_right_type] for k in fc.keyframe_points],[props(m) for m in fc.modifiers]] for l in a.layers for st in l.strips for bag in st.channelbags for fc in bag.fcurves])
def snap():
 s=bpy.context.scene;s.frame_set(1);objects={};geometry={};actions={};materials={}
 for o in s.objects:
  d={'type':o.type,'parent':o.parent.name if o.parent else None,'inverse':list(map(list,o.matrix_parent_inverse)),'basis':list(map(list,o.matrix_basis)),'constraints':[props(c) for c in o.constraints],'modifiers':[props(m) for m in o.modifiers],'visibility':[o.hide_render,o.hide_viewport]}
  actions[o.name]=action(o.animation_data.action) if o.animation_data else None
  d['action']=actions[o.name]
  if o.type=='MESH':d['mesh']={'v':[list(v.co) for v in o.data.vertices],'f':[[list(p.vertices),p.material_index,p.use_smooth] for p in o.data.polygons]};geometry[o.name]=digest(d['mesh'])
  elif o.type=='CURVE':d['curve']=[props(o.data),[[list(p.co) for p in sp.points] for sp in o.data.splines]]
  elif o.type in ['CAMERA','LIGHT','FONT']:
   d['data']=props(o.data,('animation_data',))
   if o.data.animation_data:d['data_action']=action(o.data.animation_data.action)
  if hasattr(o.data,'materials'):
   d['materials']=[]
   for m in o.data.materials:
    if m:materials.setdefault(m.name,digest(node_data(m)));d['materials'].append(materials[m.name])
    else:d['materials'].append(None)
  objects[o.name]=digest(d)
 camera=[]
 for f in [1,120,240,360,380]:
  s.frame_set(f);camera.append(list(map(list,s.objects['CAM_MASTER'].matrix_world)))
 return {'objects':objects,'geometry':geometry,'actions':actions,'materials':materials,'early_camera':camera,'world':digest(node_data(s.world)),'timeline':[s.frame_start,s.frame_end,s.render.fps,s.render.fps_base,sorted((m.name,m.frame) for m in s.timeline_markers)],'camera':s.camera.name,'view':digest(props(s.view_settings))}
if __name__=='__main__':
 manifest=json.loads((R/'review'/f'{candidate.stem}-build.json').read_text());allowed=set(manifest['modified']+manifest['removed'])
 rigid={n for g in manifest['groups'] for n in g['members']}
 after=snap();bpy.ops.wm.open_mainfile(filepath=str(R/'inputs/warehouse-v008.blend'));before=snap()
 diff={'protected_objects':[n for n,v in before['objects'].items() if n not in allowed and after['objects'].get(n)!=v], 'rigid_meshes':[n for n in rigid if n in before['geometry'] and before['geometry'][n]!=after['geometry'].get(n)],'source_actions':[n for n,v in before['actions'].items() if n not in manifest['removed'] and after['actions'].get(n)!=v], 'source_materials':[n for n,v in before['materials'].items() if after['materials'].get(n)!=v]}
 for k in ['early_camera','world','timeline','camera','view']:diff[k]=before[k]!=after[k]
 report={'candidate_sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'protected_objects':len(before['objects'])-len(allowed),'rigid_meshes':len(rigid&before['geometry'].keys()),'source_action_objects':len(before['actions']),'differences':diff}
 (R/'review'/f'{candidate.stem}-preservation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert not any(bool(v) for v in diff.values())
