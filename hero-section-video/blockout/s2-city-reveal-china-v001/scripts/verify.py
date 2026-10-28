"""Explicit camera interval exception; all original non-camera data/poses protected."""
import bpy,sys,json,hashlib,importlib.util,numpy as np,math,argparse
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('oldpres',R.parent/'cn-city-proxy-v001/scripts/preservation.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
p=argparse.ArgumentParser();p.add_argument('--candidate',required=True);p.add_argument('--output',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
base=R/'inputs/base.blend';candidate=Path(a.candidate)
bpy.ops.wm.open_mainfile(filepath=str(base));names=sorted(bpy.context.scene.objects.keys());cnames=['CAM_MASTER','CAM_LOOK_TARGET'];others=[n for n in names if n not in cnames]
actions={bpy.data.objects[n].animation_data.action.name for n in cnames}
def camera_signature(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;cs={}
 for n in cnames:
  o=s.objects[n];cs[n]=[]
  for layer in o.animation_data.action.layers:
   for strip in layer.strips:
    for bag in strip.channelbags:
     for fc in bag.fcurves:
      ks=[]
      for k in fc.keyframe_points:
       # Only keyed value/handles in the authorized open interval can vary.
       if 97<k.co.x<215 and fc.data_path in ['location','rotation_quaternion']:ks.append([float(k.co.x),'allowed'])
       else:ks.append([list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation,k.handle_left_type,k.handle_right_type])
      cs[n].append([fc.data_path,fc.array_index,ks,[old.rna(m) for m in fc.modifiers]])
 mats=[];outside=[];title_states=[];title=[o for o in s.objects if o.get('s2_reveal_owner')];initial=None
 for f in np.arange(0,1392.001,.25):
  s.frame_set(int(f),subframe=float(f%1));row=[list(map(list,s.objects[n].matrix_world)) for n in cnames]
  mats.append(row)
  if not 97<f<215:outside.append(old.digest(row))
  sig=old.digest([[o.name,list(map(list,o.matrix_world)),o.hide_render,o.hide_viewport,o.hide_get()] for o in title])
  if initial is None:initial=sig
  if sig!=initial:title_states.append(float(f))
 return cs,np.array(mats),outside,title_states
_,b,bf,_=old.snapshot(base,others);_,v,vf,city_static=old.snapshot(candidate,others)
for snap in [b,v]:
 for n in actions:snap['actions'].pop(n,None)
 snap['collections'].pop('S2_CHINA_TITLE_V001',None)
differences=[k for k in b if b[k]!=v[k]]
bc,bm,bo,_=camera_signature(base);vc,vm,vo,ts=camera_signature(candidate)
delta=np.max(np.abs(bm-vm),axis=(1,2,3));changed=np.where(delta>0)[0]/4
boundary={}
for f in [96,97,215,216]:
 idx=f*4
 boundary[f]={'max_pose_delta':float(delta[idx]),'velocity_delta':float(np.max(np.abs((vm[idx+1]-vm[idx-1])-(bm[idx+1]-bm[idx-1])))*2)}
added=sorted(set(bpy.context.scene.objects.keys())-set(names));unowned=[n for n in added if bpy.data.objects[n].get('s2_reveal_owner')!='s2-city-reveal-china-v001']
result={'original_count':len(names),'protected_non_camera':len(others),'frame_step':.25,'samples':len(bf),'data_differences':differences,'non_camera_pose_failures':sum(x!=y for x,y in zip(bf,vf)),'protected_camera_key_signature_equal':bc==vc,'outside_camera_equal':bo==vo,'city_static_errors':city_static,'title_static_error_frames':ts,'changed_camera_frames':[float(changed[0]),float(changed[-1])] if len(changed) else [],'boundary':boundary,'added':added,'unowned':unowned,'base_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256(candidate.read_bytes()).hexdigest()}
result['pass_all']=not differences and bf==vf and bc==vc and bo==vo and not city_static and not ts and not unowned
Path(a.output).write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if differences:(R/'review/preservation-debug.json').write_text(json.dumps({'base':{k:b[k] for k in differences},'candidate':{k:v[k] for k in differences}},indent=2,default=str))
if not result['pass_all']:raise SystemExit(1)
