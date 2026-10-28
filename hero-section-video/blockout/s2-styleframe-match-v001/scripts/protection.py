"""Baseline-specific protection adapter. No allowed camera interval.

Original action keys/handles, camera data, root evaluation and unrelated data
remain protected. Only explicitly listed static visual objects can change.
Existing material datablocks stay immutable; replacement art must use copies.
Finite samples are not proof of continuous collision freedom.
"""
import bpy,json,hashlib,importlib.util,numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('preservation_helpers',R.parent/'cn-city-proxy-v001/scripts/preservation.py')
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
def digest(v):return old.digest(v)
def capture(frames=None):
 s=bpy.context.scene;s.frame_set(0)
 inventory=json.loads((R/'review/baseline-inventory.json').read_text())['objects']
 allow=set(json.loads((R/'allowed-changes.json').read_text())['visual_only_candidates'])
 assert not allow.intersection({'CAM_MASTER','CAM_LOOK_TARGET','A02_SHIP','A01_CONTAINER','CN_FRAME','US_FRAME','P01_TROLLEY','P01_SPREADER'})
 names=sorted(set(inventory)-allow);missing=[n for n in inventory if n not in s.objects]
 assert not missing,'Original objects removed: '+str(missing)
 states={};geometry={};material_names={}
 static_violations=[]
 for n in inventory:
  o=s.objects[n]
  if n in allow:
   if o.animation_data or o.constraints:static_violations.append(n)
   continue
  states[n]={'parent':o.parent.name if o.parent else None,'inverse':list(map(list,o.matrix_parent_inverse)),'data':o.data.name if o.data else None,'props':old.props(o),'constraints':[old.rna(c) for c in o.constraints],'modifiers':[old.rna(m) for m in o.modifiers],'rotation_mode':o.rotation_mode,'animation':old.rna(o.animation_data) if o.animation_data else None}
  if o.type=='MESH':
   m=o.data;geometry[n]=digest({'vertices':[list(v.co) for v in m.vertices],'polygons':[list(p.vertices) for p in m.polygons],'smooth':[p.use_smooth for p in m.polygons],'materials':[m.name if m else None for m in m.materials],'indices':[p.material_index for p in m.polygons]})
  elif o.type=='FONT':geometry[n]=digest(old.rna(o.data))
  elif o.type=='CURVE':geometry[n]=digest([[sp.type,[list(p.co) for p in sp.points],[list(p.co) for p in sp.bezier_points]] for sp in o.data.splines])
 original_materials={m[0] for v in inventory.values() for m in v['materials']}
 materials={}
 for n in sorted(original_materials):
  m=bpy.data.materials.get(n)
  if not m:materials[n]='MISSING';continue
  nodes=[[o.name,o.bl_idname,[(i.identifier,list(i.default_value) if hasattr(i.default_value,'__len__') and not isinstance(i.default_value,str) else i.default_value) for i in o.inputs if hasattr(i,'default_value')]] for o in m.node_tree.nodes] if m.node_tree else []
  links=[(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in m.node_tree.links] if m.node_tree else []
  materials[n]=digest([old.rna(m),nodes,links])
 cameras={o.name:old.rna(o.data) for o in s.objects if o.type=='CAMERA'}
 timeline={'fps':s.render.fps,'fps_base':s.render.fps_base,'start':s.frame_start,'end':s.frame_end,'camera':s.camera.name,'markers':[(m.name,m.frame,m.camera.name if m.camera else None) for m in s.timeline_markers],'radius':s.get('radius'),'events':s.get('events')}
 actions=old.actions();evals=[]
 for f in (np.arange(0,1392.001,.25) if frames is None else frames):
  s.frame_set(int(f),subframe=float(f%1));values=np.array([list(map(list,s.objects[n].matrix_world)) for n in names],dtype=np.float32)
  h=hashlib.sha256(values.tobytes())
  h.update(bytes(v for n in names for v in (s.objects[n].hide_render,s.objects[n].hide_viewport,s.objects[n].hide_get())))
  h.update(np.array([[o.data.lens,o.data.sensor_width,o.data.sensor_height,o.data.shift_x,o.data.shift_y,o.data.clip_start,o.data.clip_end] for o in s.objects if o.type=='CAMERA'],dtype=np.float64).tobytes())
  evals.append(h.hexdigest())
 return {'objects':states,'geometry':geometry,'materials':materials,'actions':actions,'cameras':cameras,'timeline':timeline,'evaluations':evals,'illegal_visual_animation':static_violations}
def changed(a,b):return [k for k in sorted(set(a)|set(b)) if a.get(k)!=b.get(k)]
if __name__=='__main__':
 import argparse,sys
 p=argparse.ArgumentParser();p.add_argument('--candidate',required=True);p.add_argument('--output',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
 bpy.ops.wm.open_mainfile(filepath=str(R/'inputs/base.blend'));base=capture()
 bpy.ops.wm.open_mainfile(filepath=str(Path(a.candidate).resolve()));candidate=capture()
 result={'baseline_sha256':hashlib.sha256((R/'inputs/base.blend').read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256(Path(a.candidate).read_bytes()).hexdigest(),'frame_step':.25,'samples':len(base['evaluations']),'differences':changed(base,candidate),'camera_whole_timeline_protected':True,'camera_interval_exceptions':[],'baseline_signature':digest(base),'candidate_signature':digest(candidate),'pass':not changed(base,candidate),'limits':'Snapshot schema and sampled evaluated state; not a geometry collision proof.'}
 Path(a.output).write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
 if not result['pass']:raise SystemExit(1)
