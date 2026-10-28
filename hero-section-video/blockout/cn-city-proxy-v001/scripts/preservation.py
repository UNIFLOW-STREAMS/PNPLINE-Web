"""Compare original data and all-quarter-frame evaluated states, no S5 exceptions."""
import bpy,sys,json,hashlib,argparse,numpy as np
from pathlib import Path
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,default=str).encode()).hexdigest()
def props(o):return {k:v.to_list() if hasattr(v,'to_list') else v for k,v in o.items()}
def rna(o):
 d={}
 for p in o.bl_rna.properties:
  k=p.identifier
  if k in {'rna_type','name','name_full','id_data','session_uid'} or p.type in {'COLLECTION'}:continue
  try:
   v=getattr(o,k)
   if p.type=='POINTER':d[k]=v.name if isinstance(v,bpy.types.ID) else None
   elif p.is_array:d[k]=list(v)
   elif isinstance(v,(str,int,float,bool)) or v is None:d[k]=v
  except (AttributeError,TypeError):pass
 return d
def actions():
 out={}
 for a in bpy.data.actions:
  cs=[]
  for layer in a.layers:
   for strip in layer.strips:
    for bag in strip.channelbags:
     for fc in bag.fcurves:
      cs.append([fc.data_path,fc.array_index,[[list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation,k.handle_left_type,k.handle_right_type] for k in fc.keyframe_points], [rna(m) for m in fc.modifiers]])
  out[a.name]=digest(cs)
 return out
def snapshot(path,names=None,hide=(),frames=None):
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.frame_set(0)
 if names is None:names=sorted(s.objects.keys())
 objects={};meshes={};materials={}
 for n in names:
  o=s.objects[n];ad=o.animation_data
  objects[n]={'parent':o.parent.name if o.parent else None,'data':o.data.name if o.data else None,'props':props(o),'parent_inverse':list(map(list,o.matrix_parent_inverse)),'constraints':[rna(x) for x in o.constraints],'modifiers':[rna(x) for x in o.modifiers],'action':ad.action.name if ad and ad.action else None,'drivers':[x.data_path for x in ad.drivers] if ad else [],'hide':[o.hide_render,o.hide_viewport,o.hide_get()] if n not in hide else 'allowed_static_hide','rotation_mode':o.rotation_mode}
  if o.type=='MESH':
   m=o.data;meshes[m.name]=digest({'v':[list(v.co) for v in m.vertices],'p':[list(p.vertices) for p in m.polygons],'smooth':[p.use_smooth for p in m.polygons],'material_indices':[p.material_index for p in m.polygons],'materials':[x.name if x else None for x in m.materials],'shape_keys':m.shape_keys.name if m.shape_keys else None})
  elif o.type=='CURVE':meshes[o.data.name]=digest([[sp.type,[list(p.co) for p in sp.points],[list(p.co) for p in sp.bezier_points]] for sp in o.data.splines])
  elif o.type=='FONT':meshes[o.data.name]=digest(rna(o.data))
  if hasattr(o.data,'materials'):
   for m in o.data.materials:
    if not m:continue
    materials[m.name]=digest([rna(m),[[x.name,x.bl_idname,[(i.identifier,list(i.default_value) if hasattr(i.default_value,'__len__') and not isinstance(i.default_value,str) else i.default_value) for i in x.inputs if hasattr(i,'default_value')]] for x in m.node_tree.nodes] if m.node_tree else None])
 scene={'name':s.name,'props':{k:v for k,v in props(s).items() if not k.startswith('cn_proxy_')},'camera':s.camera.name,'fps':s.render.fps,'fps_base':s.render.fps_base,'range':[s.frame_start,s.frame_end],'markers':[(m.name,m.frame,m.camera.name if m.camera else None) for m in s.timeline_markers],'render':rna(s.render),'display':rna(s.display.shading),'color':rna(s.view_settings),'world':rna(s.world),'camera_data':{o.name:rna(o.data) for o in s.objects if o.type=='CAMERA'}}
 static={'objects':objects,'meshes':meshes,'materials':materials,'actions':actions(),'scene':scene,'collections':{c.name:[c.hide_render,c.hide_viewport] for c in bpy.data.collections if c.name!='CN_CITY_PROXY_V001'}}
 owned=[o for o in s.objects if o.get('cn_proxy_owner')]
 owned_initial={o.name:o.matrix_world.copy() for o in owned}
 frame_hash=[];static_errors=[]
 cameras=[o for o in s.objects if o.type=='CAMERA']
 for f in (np.arange(0,1392.001,.25) if frames is None else frames):
  s.frame_set(int(f),subframe=float(f%1));h=hashlib.sha256(np.array([list(map(list,s.objects[n].matrix_world)) for n in names],dtype=np.float32).tobytes())
  h.update(np.array([[o.data.lens,o.data.sensor_width,o.data.sensor_height,o.data.shift_x,o.data.shift_y,o.data.clip_start,o.data.clip_end] for o in cameras],dtype=np.float64).tobytes())
  h.update(bytes([v for n in names if n not in hide for v in (s.objects[n].hide_render,s.objects[n].hide_viewport,s.objects[n].hide_get())]))
  frame_hash.append(h.hexdigest())
  for o in owned:
   if o.matrix_world!=owned_initial[o.name] or o.hide_render or o.hide_viewport or o.hide_get():static_errors.append([float(f),o.name])
  for n in hide:
   if owned and not(s.objects[n].hide_render and s.objects[n].hide_get()):static_errors.append([float(f),'replacement visibility '+n])
 return names,static,frame_hash,static_errors
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--base',required=True);p.add_argument('--candidate',required=True);p.add_argument('--output',required=True);p.add_argument('--config',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
 c=json.loads(Path(a.config).read_text());names,b,bf,_=snapshot(a.base,hide=c['hide_original']);_,v,vf,static_errors=snapshot(a.candidate,names,c['hide_original'])
 differences=[k for k in b if b[k]!=v[k]];bad=[i*.25 for i,(x,y) in enumerate(zip(bf,vf)) if x!=y]
 added=sorted(set(bpy.context.scene.objects.keys())-set(names));unowned=[n for n in added if bpy.data.objects[n].get('cn_proxy_owner')!=c['owner']]
 result={'pass_all':not differences and not bad and not static_errors and not unowned,'samples':len(bf),'frame_step':.25,'original_count':len(names),'added_count':len(added),'added':added,'data_differences':differences,'evaluated_difference_frames':bad,'new_static_errors':static_errors[:20],'unowned_additions':unowned,'hide_allowlist':c['hide_original'],'base_sha256':hashlib.sha256(Path(a.base).read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256(Path(a.candidate).read_bytes()).hexdigest(),'exact_evaluation_digest':digest(vf),'comparison':'Exact float32 matrices, float64 camera scalars; no tolerance or inherited S5 exceptions'}
 Path(a.output).write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='added'},indent=2))
 if differences:
  Path(a.output).with_suffix('.debug.json').write_text(json.dumps({'base':{k:b[k] for k in differences},'candidate':{k:v[k] for k in differences}},indent=2,default=str))
 if not result['pass_all']:raise SystemExit(1)
