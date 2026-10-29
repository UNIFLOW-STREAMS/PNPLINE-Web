"""Compare new city, recolored crane, camera curves and complete saved preservation signatures."""
import bpy,json,hashlib,sys,ast
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
import verify_rework as v
def owned_snapshot():
 s=bpy.context.scene;s.frame_set(510);rows={}
 for o in s.objects:
  if not o.get('uc_owner') and not v.crane(o.name):continue
  d={'parent':o.parent.name if o.parent else None,'type':o.type,'matrix':list(map(list,o.matrix_world)),'visibility':[o.hide_render,o.hide_viewport],'materials':[v.node_data(m) if m else None for m in o.data.materials] if hasattr(o.data,'materials') else [],'modifiers':[v.props(m) for m in o.modifiers]}
  if o.type=='MESH':d.update(vertices=[list(x.co) for x in o.data.vertices],polygons=[[list(f.vertices),f.material_index,f.use_smooth] for f in o.data.polygons])
  if o.type=='CURVE':d.update(points=[[list(p.co) for p in sp.points] for sp in o.data.splines],bevel=o.data.bevel_depth)
  rows[o.name]=v.digest(d)
 # Curve keys include subframe motion, not just representative poses.
 for obj in [s.camera,s.camera.data,s.objects['CAM_LOOK_TARGET']]:
  ac=obj.animation_data.action
  rows[obj.name+'_ACTION']=v.digest([[fc.data_path,fc.array_index,[[list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation] for k in fc.keyframe_points]] for l in ac.layers for st in l.strips for bag in st.channelbags for fc in bag.fcurves])
 return rows
first=Path(bpy.data.filepath);a=owned_snapshot();sa=v.snap();other=Path(sys.argv[sys.argv.index('--')+1]);bpy.ops.wm.open_mainfile(filepath=str(other));b=owned_snapshot();sb=v.snap()
diff=sorted(n for n in a.keys()|b.keys() if a.get(n)!=b.get(n));protected=v.compare_snapshots(sa,sb)
report={'candidate_sha256':hashlib.sha256(first.read_bytes()).hexdigest(),'reproduction_sha256':hashlib.sha256(other.read_bytes()).hexdigest(),'entry_counts':[len(a),len(b)],'different':diff,'protected_differences':protected,'pass':not diff and not any(bool(x) for x in protected.values()),'binary_equality_required':False,'reason':'Saved metadata/path can differ. Geometry, materials, modifiers, world transforms and every camera/lens/target key must match.'}
(R/'review'/f'{first.stem}-reproduction.json').write_text(json.dumps(report,indent=2));print(json.dumps(report));assert report['pass']
