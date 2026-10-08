"""Read-only semantic signatures plus full-scene outside-window evaluations."""
import bpy,sys,json,argparse,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from preservation import capture,sha,action
p=argparse.ArgumentParser();p.add_argument('--scene',required=True);p.add_argument('--config',required=True);p.add_argument('--output',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);cfg=json.loads(Path(a.config).read_text(encoding='utf-8-sig'));s=bpy.data.scenes[a.scene];d=capture(s);excluded={'CAM_MASTER','CAM_LOOK_TARGET'};objs=sorted([o for o in s.objects if o.name not in excluded],key=lambda o:o.name);d['noncamera_frames']=[];d['join_subframes']=[]
for f in range(s.frame_start,s.frame_end+1):
 s.frame_set(f);d['noncamera_frames'].append(sha([[o.name,[list(r) for r in o.matrix_world]] for o in objs]))
for f in [cfg['edit_start']-1,cfg['edit_start']-.75,cfg['edit_start']-.5,cfg['edit_start']-.25,cfg['edit_start'],cfg['edit_end'],cfg['edit_end']+.25,cfg['edit_end']+.5,cfg['edit_end']+.75,cfg['edit_end']+1]:
 s.frame_set(math.floor(f),subframe=f%1);d['join_subframes'].append([f,sha([[o.name,[list(r) for r in o.matrix_world]] for o in s.objects]),s.camera.data.lens])
d['outside_keys']={};groups={'camera':['CAM_MASTER','CAM_LOOK_TARGET'],'support':['A03_TRACTOR','A03_TRAILER','A01_CONTAINER','W01_NEW_PALLET'],'hoist':['P02_SPREADER']+[f'P02_CABLE_{i}' for i in range(4)]};ends={'camera':cfg['edit_end'],'support':cfg.get('support_end',cfg['edit_end']),'hoist':666};d['group_frames']={};mutable=set()
for group,names in groups.items():
 members=sorted({x.name:x for n in names for x in [bpy.data.objects[n],*bpy.data.objects[n].children_recursive]}.values(),key=lambda o:o.name);mutable.update(o.name for o in members);d['group_frames'][group]=[]
 for o in [bpy.data.objects[n] for n in names]+([s.camera.data] if group=='camera' else []):
  d['outside_keys'][o.name]=[[path,index,[key for key in keys if key[0][0]<=cfg['edit_start'] or key[0][0]>=ends[group]]] for path,index,keys in action(o.animation_data)]
 for f in range(s.frame_start,s.frame_end+1):
  if cfg['edit_start']<f<ends[group]:continue
  s.frame_set(f);d['group_frames'][group].append([f,sha([[o.name,[list(r) for r in o.matrix_world]] for o in members])])
protected=sorted([o for o in s.objects if o.name not in mutable],key=lambda o:o.name);d['protected_environment_frames']=[]
for f in range(s.frame_start,s.frame_end+1):
 s.frame_set(f);d['protected_environment_frames'].append(sha([[o.name,[list(r) for r in o.matrix_world]] for o in protected]))
Path(a.output).write_text(json.dumps(d),encoding='utf8');print('CAPTURE',a.output,len(d['frames']))
