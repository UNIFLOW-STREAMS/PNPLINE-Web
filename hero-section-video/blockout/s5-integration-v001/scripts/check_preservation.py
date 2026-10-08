import bpy,sys,json,argparse,hashlib,numpy as np
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--base',required=True);p.add_argument('--output',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
candidate=bpy.data.filepath;R=Path(a.output);names=sorted(bpy.context.scene.objects.keys());frames=np.arange(0,1392.01,.25)
def snapshot(path):
 bpy.ops.wm.open_mainfile(filepath=path);s=bpy.data.scenes['PNPLINE_MASTER_v005'];bpy.context.window.scene=s
 meta={};matrices=np.empty((len(frames),len(names),4,4),dtype=np.float32)
 for n in names:
  o=s.objects[n];meta[n]={'parent':o.parent.name if o.parent else None,'rotation_mode':o.rotation_mode,'scale':tuple(o.scale),'ids':{k:o[k] for k in ['asset_id','instance_id'] if k in o},'mesh':hashlib.sha256(repr(([tuple(v.co) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])).encode()).hexdigest() if o.type=='MESH' else None}
 lenses=[]
 for i,f in enumerate(frames):
  s.frame_set(int(f),subframe=float(f%1));matrices[i]=[list(map(list,s.objects[n].matrix_world)) for n in names];lenses.append(s.camera.data.lens)
 return meta,matrices,np.array(lenses),{m.name:m.frame for m in s.timeline_markers}
bm,b,bl,markers=snapshot(str(Path(a.base).resolve()));cm,c,cl,newmarkers=snapshot(candidate)
approved_scales={'DOCK_BRIDGE':(1,1.34/1.48),'A01_DOOR_LEFT_LEAF':(2,1.43/1.5),'A01_DOOR_RIGHT_LEAF':(2,1.43/1.5)}
for n,(axis,factor) in approved_scales.items():
 expected=list(bm[n]['scale']);expected[axis]*=factor
 assert max(abs(x-y) for x,y in zip(expected,cm[n]['scale']))<1e-6,(n,'approved scale')
 cm[n]['scale']=bm[n]['scale']
assert bm==cm,'Unapproved geometry/hierarchy/IDs differ';assert markers==newmarkers
s=bpy.context.scene;hinges=set()
for n in ['A01_DOOR_L','A01_DOOR_R']:hinges|={n}|{o.name for o in s.objects[n].children_recursive}
wheels={n for n in names if n.startswith('A03') and '_WHEEL_' in n}
changed={'A03_TRAILER','A03_TRACTOR','A01_CONTAINER','W01_NEW_PALLET','CAM_MASTER','CAM_LOOK_TARGET'}
for n in list(changed):changed|={o.name for o in s.objects[n].children_recursive}
errors=[];worst={}
for j,n in enumerate(names):
 mask=np.ones(len(frames),dtype=bool)
 if n in hinges or n=='DOCK_BRIDGE':continue
 if n in wheels:mask=frames<=720
 elif n in changed:mask=(frames<=720)|(frames>=948)
 delta=float(np.max(np.abs(c[mask,j]-b[mask,j])));worst[n]=delta
 if delta>.0001:errors.append((n,delta))
mask=(frames<=720)|(frames>=948);lensdelta=float(max(abs(cl[mask]-bl[mask])))
out={'pass_all':not errors and lensdelta<.0001,'samples':len(frames),'step':.25,'matrix_max':max(worst.values()),'lens_max':lensdelta,'errors':errors,'geometry_hierarchy_ids_equal':True,'markers_equal':True,'exceptions':{'approved_global_hinges_and_children':sorted(hinges),'wheel_rolling_phase_and_support_after720':sorted(wheels)},'base_sha256':hashlib.sha256(Path(a.base).read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256(Path(candidate).read_bytes()).hexdigest()}
out['geometry_hierarchy_ids_equal_except_approved_scales']=out.pop('geometry_hierarchy_ids_equal');out['exceptions']['approved_bridge']={'width':1.34,'center_z':1.88};out['exceptions']['approved_door_leaf']={'height':1.43,'center_z_delta':.035}
for n in ['A01_DOOR_L','A01_DOOR_R']:assert abs(s.objects[n].location.x+1.65)<1e-6
for n in ['A01_DOOR_LEFT_LEAF','A01_DOOR_RIGHT_LEAF']:assert abs(s.objects[n].location.z-.035)<1e-6
assert abs(s.objects['DOCK_BRIDGE'].location.z-1.88)<1e-6
R.write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));assert out['pass_all']
