import bpy,json,hashlib,sys,ast
from pathlib import Path
R=Path(__file__).resolve().parents[1]
helpers=ast.parse((R/'scripts/verify_preservation.py').read_text())
exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n,ast.FunctionDef) and n.name in ['scalar','props','node_data']],type_ignores=[]),'stable-signatures','exec'))
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True).encode()).hexdigest()
def snap():
 s=bpy.context.scene;s.frame_set(510);rows={}
 for o in s.objects:
  if not o.get('uc_owner'):continue
  d={'parent':o.parent.name if o.parent else None,'type':o.type,'matrix':list(map(list,o.matrix_world)),'visibility':[o.hide_render,o.hide_viewport],'materials':[node_data(m) if m else None for m in o.data.materials] if hasattr(o.data,'materials') else [],'modifiers':[props(m) for m in o.modifiers]}
  if o.type=='MESH':d.update(v=[list(v.co) for v in o.data.vertices],f=[[list(f.vertices),f.material_index,f.use_smooth] for f in o.data.polygons])
  if o.type=='CURVE':d.update(p=[[list(v.co) for v in sp.points] for sp in o.data.splines],bevel=o.data.bevel_depth)
  rows[o.name]=digest(d)
 return rows
first=Path(bpy.data.filepath);a=snap();other=R/'review/reproduction-v004.blend';bpy.ops.wm.open_mainfile(filepath=str(other));b=snap()
diff=[n for n in a.keys()|b.keys() if a.get(n)!=b.get(n)]
report={'candidate_sha256':hashlib.sha256(first.read_bytes()).hexdigest(),'reproduction_sha256':hashlib.sha256(other.read_bytes()).hexdigest(),'owned_count':[len(a),len(b)],'different':diff,'pass':not diff,'binary_equality_required':False,'reason':'Blend save metadata/path may differ; geometry, materials assignments and world matrices must reproduce exactly.'}
(R/'review/reproduction-comparison.json').write_text(json.dumps(report,indent=2));print(json.dumps(report));assert not diff
