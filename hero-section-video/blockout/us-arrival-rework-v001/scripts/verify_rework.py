"""Scoped replacement for camera-invariant comparison; old verifier is untouched."""
import bpy,sys,json,hashlib,ast,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R.parent/'us-city-concept-v001'
helpers=ast.parse((D/'scripts/verify_preservation.py').read_text())
exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n,ast.FunctionDef) and n.name in ['digest','scalar','props','node_data']],type_ignores=[]),'old-signature-helpers','exec'))
exec(compile((R/'scripts/material_signature.py').read_text(),'material-signature','exec'))
cfg=json.loads((R/'scene-config.json').read_text());start,end=cfg['camera_interval']
def crane(n):return n.startswith(('P02_LEG','P02_BOOM')) or n in ['P02_TROLLEY','P02_SPREADER_FRAME']
def snap():
 s=bpy.context.scene;s.frame_set(156);obs={}
 for o in s.objects:
  if o.get('uc_owner'):continue
  row={'type':o.type,'parent':o.parent.name if o.parent else None,'inverse':list(map(list,o.matrix_parent_inverse)),'constraints':[props(c) for c in o.constraints],'modifiers':[props(m) for m in o.modifiers],'visibility':[o.hide_render,o.hide_viewport,o.hide_get()]}
  if o.name not in ['CAM_MASTER','CAM_LOOK_TARGET']:row.update(basis=list(map(list,o.matrix_basis)),action=o.animation_data.action.name if o.animation_data and o.animation_data.action else None)
  if o.type=='MESH':
   row['mesh']={'v':[list(v.co) for v in o.data.vertices],'f':[[list(p.vertices),p.use_smooth] for p in o.data.polygons]}
   if not crane(o.name):row['materials']=[[m.name if m else None for m in o.data.materials],[p.material_index for p in o.data.polygons]]
  if o.type=='CURVE':row['curve']=[props(o.data),[[list(p.co) for p in sp.points] for sp in o.data.splines]]
  if o.type=='LIGHT':row['light']=props(o.data)
  if o.type=='CAMERA':row['camera']=props(o.data,('animation_data',))
  obs[o.name]=digest(row)
 acts={ac.name:digest([[fc.data_path,fc.array_index,fc.extrapolation,[[list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation,k.handle_left_type,k.handle_right_type] for k in fc.keyframe_points],[props(m) for m in fc.modifiers]] for l in ac.layers for st in l.strips for bag in st.channelbags for fc in bag.fcurves]) for ac in bpy.data.actions if not ac.name.startswith('AR_')}
 mats={m.name:digest(node_data(m)) for m in bpy.data.materials if not m.name.startswith('AR_')}
 return {'objects':obs,'actions':acts,'materials':mats,'world':node_data(s.world),'timeline':[s.frame_start,s.frame_end,s.render.fps,s.render.fps_base,sorted((m.name,m.frame) for m in s.timeline_markers)],'render':props(s.render,('filepath',)),'color':props(s.view_settings)}
def samples():
 s=bpy.context.scene;roots=[o for o in s.objects if not o.get('uc_owner') and (o.animation_data or o.constraints or o.name in ['US_FRAME','CN_FRAME'])]
 frames=sorted(set(range(1393))|{b+j/8 for b in [300,420,468,528,456,510,532,600,648,720,900,1200] for j in range(-8,9)})
 values={};camera=[]
 for f in frames:
  s.frame_set(int(f),subframe=f%1)
  values[str(f)]={o.name:[float(v) for row in o.matrix_world for v in row]+([o.data.lens] if o.type=='CAMERA' else []) for o in roots if o.name not in ['CAM_MASTER','CAM_LOOK_TARGET'] or not start<f<end}
  c=s.objects['CAM_MASTER'];camera.append({'frame':f,'p':list(c.matrix_world.translation),'q':list(c.matrix_world.to_quaternion()),'lens':c.data.lens})
 return values,camera
def compare_snapshots(before,after):
 return {k:([n for n in before[k].keys()|after[k].keys() if before[k].get(n)!=after[k].get(n)] if isinstance(before[k],dict) else before[k]!=after[k]) for k in before}
def compare_evaluations(bv,av):
 errors=[];maximum=0
 for f,rs in bv.items():
  for n,vals in rs.items():
   other=av.get(f,{}).get(n)
   err=max(abs(x-y) for x,y in zip(vals,other)) if other and len(vals)==len(other) else 999
   maximum=max(maximum,err)
   if err>2e-5:errors.append({'f':f,'object':n,'error':err})
 return errors,maximum
def main():
 file=Path(bpy.data.filepath);after=snap();av,ac=samples();bpy.ops.wm.open_mainfile(filepath=str(R/cfg['input']));before=snap();bv,bc=samples()
 diff=compare_snapshots(before,after);errors,maximum=compare_evaluations(bv,av)
 report={'candidate_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'base_sha256':hashlib.sha256((R/cfg['input']).read_bytes()).hexdigest(),'differences':diff,'evaluation_errors':errors,'maximum_evaluation_error':maximum,'frames':len(bv),'camera_exception_open_interval':[start,end],'camera_all_outside_and_all_protected_roots_checked':True}
 (R/'review'/f'{file.stem}-preservation.json').write_text(json.dumps(report,indent=2));(R/'review'/f'{file.stem}-camera-samples.json').write_text(json.dumps({'before':bc,'after':ac}))
 print('DIFF',json.dumps(diff),'EVAL_ERRORS',len(errors),'MAX',maximum)
 assert not any(bool(v) for v in diff.values()) and not errors
if __name__=='__main__':main()
