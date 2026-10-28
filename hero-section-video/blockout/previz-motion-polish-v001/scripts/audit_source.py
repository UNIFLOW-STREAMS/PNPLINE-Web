"""Read-only input comparison and motion diagnosis; no .blend saving."""
import bpy, json, hashlib, struct, math, numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1]
B=R.parent
(R/'review').mkdir(parents=True,exist_ok=True)
(R/'inputs').mkdir(exist_ok=True)
sources={'reported':B/'s5-integration-v001/review/reproduced.blend',
         'storyboard':B.parent/'storyboard/s5-sync-v001/master/source-current.blend',
         'current':B/'s5-integration-v001/master-s5-integration-v001.blend',
         'double':B/'previz-s1-s7-2x-v001/master-previz-s1-s7-2x-v001.blend'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def curves(action):return [fc for l in action.layers for st in l.strips for bag in st.channelbags for fc in bag.fcurves]
def curve_hash(fc):
 h=hashlib.sha256()
 for k in fc.keyframe_points:
  h.update(struct.pack('6d',*k.co,*k.handle_left,*k.handle_right))
  h.update(str((k.interpolation,k.handle_left_type,k.handle_right_type,k.easing)).encode())
 return h.hexdigest()
records={}; base=None; selected=None
for label,path in sources.items():
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.frame_set(0)
 names=sorted(o.name for o in s.objects)
 actions={a.name:[{'path':f.data_path,'index':f.array_index,'count':len(f.keyframe_points),'hash':curve_hash(f),'interpolation':sorted(set(k.interpolation for k in f.keyframe_points))} for f in curves(a)] for a in bpy.data.actions}
 geo={o.name:hashlib.sha256(np.asarray([v.co[:] for v in o.data.vertices],dtype=np.float64).tobytes()+str([list(p.vertices) for p in o.data.polygons]).encode()).hexdigest() for o in s.objects if o.type=='MESH'}
 inventory={o.name:{'parent':o.parent.name if o.parent else None,'action':o.animation_data.action.name if o.animation_data and o.animation_data.action else None,'constraints':[c.type for c in o.constraints],'drivers':len(o.animation_data.drivers) if o.animation_data else 0,'nla':len(o.animation_data.nla_tracks) if o.animation_data else 0,'rotation_mode':o.rotation_mode} for o in s.objects}
 states=np.zeros((1393,len(names),4,4),dtype=np.float64);lens=[]
 for f in range(1393):
  s.frame_set(f);states[f]=np.asarray([s.objects[n].matrix_world[:] for n in names]);lens.append(s.camera.data.lens)
 rec={'path':str(path),'sha256':sha(path),'scene':s.name,'camera':s.camera.name,'fps':s.render.fps,'fps_base':s.render.fps_base,'range':[s.frame_start,s.frame_end],'markers':{m.name:m.frame for m in s.timeline_markers},'objects':inventory,'geometry':geo,'actions':actions,'evaluated_hash':hashlib.sha256(states.tobytes()).hexdigest(),'lens':lens}
 if base is None:base=(states.copy(),rec)
 else:
  rec['difference_from_reported']={'matrices_max':float(np.max(np.abs(states-base[0]))),'lens_max':float(np.max(np.abs(np.array(lens)-base[1]['lens']))),'actions_equal':actions==base[1]['actions'],'geometry_equal':geo==base[1]['geometry'],'objects_equal':inventory==base[1]['objects'],'markers_equal':rec['markers']==base[1]['markers']}
 if label=='current':
  selected=(states,rec)
  np.savez_compressed(R/'review/source-states.npz',matrices=states,names=np.array(names),lens=np.array(lens))
  animated={}
  for o in list(s.objects)+[s.camera.data]:
   if not o.animation_data or not o.animation_data.action:continue
   fs=curves(o.animation_data.action)
   animated[o.name]={'action':o.animation_data.action.name,'curves':[{'path':fc.data_path,'index':fc.array_index,'count':len(fc.keyframe_points),'keys':[[round(k.co.x,4),round(k.co.y,5),k.interpolation] for k in fc.keyframe_points] if len(fc.keyframe_points)<90 else [[round(fc.keyframe_points[0].co.x,4),round(fc.keyframe_points[-1].co.x,4)]]} for fc in fs]}
  (R/'review/animated-inventory.json').write_text(json.dumps(animated,indent=2),encoding='utf8')
 records[label]=rec
 print('AUDIT',label,rec.get('difference_from_reported',{}),flush=True)
(R/'review/source-comparison.json').write_text(json.dumps(records,indent=2),encoding='utf8')
states,rec=selected; names=sorted(rec['objects']); cam=names.index(rec['camera']);xyz=states[:,cam,:3,3];velocity=np.linalg.norm(np.diff(xyz,axis=0),axis=1)
segments=[0,96,216,456,648,900,1200,1392];pacing=[]
for i,(a,b) in enumerate(zip(segments,segments[1:]),1):
 v=velocity[a:b]
 pacing.append({'segment':'S'+str(i),'source_range':[a,b],'duration_at_24fps':(b-a)/24,'camera_speed_m_per_frame':{'min':float(min(v)),'max':float(max(v)),'mean':float(np.mean(v))},'near_still_frames':[a+int(j) for j in np.where(v<.015)[0]],'camera_distance':float(v.sum())})
out={'segments':pacing,'camera_boundary_speeds':{str(f):[float(v) for v in velocity[max(0,f-3):f+3]] for f in segments[1:-1]},'source_sha256':rec['sha256']}
(R/'pacing-audit.json').write_text(json.dumps(out,indent=2),encoding='utf8');print('PACING',json.dumps(out),flush=True)
