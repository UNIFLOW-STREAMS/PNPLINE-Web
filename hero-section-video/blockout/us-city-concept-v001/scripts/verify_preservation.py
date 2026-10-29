"""Compare saved candidate with immutable base; only allow individually listed hide flags."""
import bpy,json,hashlib,sys,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];candidate=Path(bpy.data.filepath);allow=json.loads((R/'allowed-changes.json').read_text())
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def scalar(x,depth=0):
 if isinstance(x,(str,int,float,bool)) or x is None:return x
 if isinstance(x,bpy.types.ID):return x.name
 if hasattr(x,'bl_rna'):return props(x,depth=depth+1) if depth<5 else {'rna_type':x.bl_rna.identifier}
 try:return [scalar(v,depth+1) for v in x]
 except:return type(x).__name__
def props(x,exclude=(),depth=0):
 d={}
 for p in x.bl_rna.properties:
  k=p.identifier
  if k in {'rna_type','id_data','session_uid',*exclude} or p.type=='COLLECTION':continue
  try:d[k]=scalar(getattr(x,k),depth)
  except:pass
 return d
def node_data(datablock):
 tree=datablock.node_tree
 return {'props':props(datablock),'nodes':[(n.name,n.type,props(n),[(i.name,scalar(i.default_value)) for i in n.inputs if hasattr(i,'default_value')]) for n in tree.nodes] if tree else [],'links':[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in tree.links] if tree else []}
def snapshot():
 s=bpy.context.scene;s.frame_set(156);objects={};meshes={};debug={}
 for o in s.objects:
  if o.get('uc_owner'):continue
  row={'type':o.type,'parent':o.parent.name if o.parent else None,'basis':list(map(list,o.matrix_basis)),'inverse':list(map(list,o.matrix_parent_inverse)),'data':o.data.name if o.data else None,'constraints':[props(c) for c in o.constraints],'modifiers':[props(m) for m in o.modifiers],'action':o.animation_data.action.name if o.animation_data and o.animation_data.action else None,'visibility':[o.hide_render,o.hide_viewport,o.hide_get()],'material_slots':[m.material.name if m.material else None for m in o.material_slots]}
  if o.name in allow['original_objects']:row.pop('visibility')
  if o.type=='CAMERA':row['camera']=props(o.data)
  if o.type=='LIGHT':row['light']=props(o.data)
  if o.type=='CURVE':row['curve']={'props':props(o.data),'splines':[[[list(p.co) for p in sp.points],[list(p.co) for p in sp.bezier_points]] for sp in o.data.splines]}
  objects[o.name]=digest(row)
  if o.name in ['CAM_MASTER','SF_BRIDGE_POST_1_18']:debug[o.name]=row
 for m in bpy.data.meshes:
  if m.name.startswith('UC_'):continue
  meshes[m.name]=digest({'v':[list(v.co) for v in m.vertices],'edges':[list(e.vertices) for e in m.edges],'polys':[[list(p.vertices),p.material_index,p.use_smooth] for p in m.polygons],'mats':[v.name if v else None for v in m.materials]})
 actions={ac.name:digest([[fc.data_path,fc.array_index,fc.extrapolation,[[list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation,k.handle_left_type,k.handle_right_type] for k in fc.keyframe_points],[props(m) for m in fc.modifiers]] for l in ac.layers for st in l.strips for bag in st.channelbags for fc in bag.fcurves]) for ac in bpy.data.actions}
 materials={}
 for m in bpy.data.materials:
  if m.name.startswith('UC_'):continue
  matrow=node_data(m)
  materials[m.name]=digest(matrow)
  if m.name=='navy':debug['navy']=matrow
 roots=[o for o in s.objects if not o.get('uc_owner') and (o.animation_data or o.constraints or o.name in ['US_FRAME','CN_FRAME','SF_CN_LAYOUT'])]
 sample_hash=hashlib.sha256();frames=sorted(set(range(s.frame_start,s.frame_end+1))|{b+j/8 for b in [72,96,216,456,510,532,578,583,600,648,720,776,842,890,900,960,1026,1090,1158,1200,1260,1391] for j in range(-8,9) if 0<=b+j/8<=1392})
 for f in ([] if '--diagnostic' in sys.argv else frames):
  s.frame_set(int(f),subframe=f%1)
  sample_hash.update(json.dumps([[o.name,list(map(list,o.matrix_world)),o.data.lens if o.type=='CAMERA' else None] for o in roots],separators=(',',':')).encode())
 return {'objects':objects,'meshes':meshes,'materials':materials,'actions':actions,'samples':sample_hash.hexdigest(),'sample_count':len(frames),'roots':[o.name for o in roots],'timeline':[s.frame_start,s.frame_end,s.render.fps,s.render.fps_base,sorted((m.name,m.frame) for m in s.timeline_markers)],'render':props(s.render,('filepath',)),'color':props(s.view_settings),'world':node_data(s.world) if s.world else None,'debug':debug}
after=snapshot();bpy.ops.wm.open_mainfile(filepath=str(R/'inputs/base.blend'));before=snapshot()
if '--diagnostic' in sys.argv:
 (R/'review/signature-diagnostic.json').write_text(json.dumps({'before':{k:before[k] for k in ['debug','render','color']},'after':{k:after[k] for k in ['debug','render','color']}},indent=2));sys.exit(0)
before.pop('debug');after.pop('debug')
checks={k:before[k]==after[k] for k in before};diff={k:[n for n in before[k].keys()|after[k].keys() if before[k].get(n)!=after[k].get(n)] for k in ['objects','meshes','materials','actions']}
report={'candidate':str(candidate),'sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'base_sha256':hashlib.sha256((R/'inputs/base.blend').read_bytes()).hexdigest(),'checks':checks,'differences':diff,'evaluated_roots':after['roots'],'sample_count':after['sample_count'],'limitations':'Data preservation plus evaluated transforms; new geometry collisions and image readability require separate gates.'}
(R/'review'/f'{candidate.stem}-preservation.json').write_text(json.dumps(report,indent=2));print(json.dumps({'checks':checks,'difference_counts':{k:len(v) for k,v in diff.items()},'samples':after['sample_count']}));assert all(checks.values())
