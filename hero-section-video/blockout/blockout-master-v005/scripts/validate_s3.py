import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scene_evidence import capture
from s3_metrics import sample
R=Path(__file__).resolve().parents[1];S=bpy.context.scene;cam=S.camera
data=capture();(R/'review/states-after.json').write_text(json.dumps(data,default=str))
base=json.loads((R/'review/baseline-full.json').read_text());changed={k:[f for f in range(1393) if base['frames'][f][k]!=data['frames'][f][k]] for k in ['camera','target','lens','noncamera']}
meshes=[o for o in S.objects if o.type=='MESH' and o.name!='EARTH_CONTINUOUS_OCEAN' and not o.name.startswith('WAKE_')]
boxes={o.name:([min(v[i] for v in o.bound_box) for i in range(3)],[max(v[i] for v in o.bound_box) for i in range(3)]) for o in meshes}
rows=[];hits=[];prev=None
for i in range(208*4,468*4+1):
 f=i/4;S.frame_set(int(f),subframe=f-int(f));p=cam.matrix_world.translation.copy();q=cam.matrix_world.to_quaternion();t=bpy.data.objects['CAM_LOOK_TARGET'].matrix_world.translation.copy();ship=bpy.data.objects['A02_SHIP'].matrix_world.copy();local=ship.inverted()@p
 up=ship.to_3x3()@Vector((0,0,1));forward=cam.matrix_world.to_3x3()@Vector((0,0,-1));right=cam.matrix_world.to_3x3()@Vector((1,0,0))
 row={'frame':f,'position':list(p),'quaternion':list(q),'target':list(t),'ship_local_camera':list(local),'globe_clearance':p.length-S['radius'],'right_up_dot':right.dot(up.normalized()),'up_forward_abs_dot':abs(forward.dot(up.normalized()))}
 if prev:row.update(step_per_frame=(p-prev[0]).length*4,angle_deg_per_frame=math.degrees(q.rotation_difference(prev[1]).angle)*4,target_step_per_frame=(t-prev[2]).length*4)
 rows.append(row);prev=(p,q,t)
 for o in meshes:
  if o.hide_render or all(c.hide_render for c in o.users_collection):continue
  v=o.matrix_world.inverted()@p;lo,hi=boxes[o.name];scale=o.matrix_world.to_scale();margin=[.12/max(abs(scale[j]),1e-8) for j in range(3)]
  if all(lo[j]-margin[j]<v[j]<hi[j]+margin[j] for j in range(3)):hits.append({'frame':f,'object':o.name})
observations=[sample(f) for f in range(216,457)];boundaries={}
for f in [216,456]:
 item={}
 for name,states in [('before',base['frames']),('after',data['frames'])]:
  m=[Matrix(states[k]['camera']) for k in [f-1,f,f+1]];ts=[Vector(states[k]['target']) for k in [f-1,f,f+1]]
  item[name]={'position':list(m[1].translation),'quaternion':list(m[1].to_quaternion()),'target':list(ts[1]),'lens':states[f]['lens'],'incoming_velocity':list(m[1].translation-m[0].translation),'outgoing_velocity':list(m[2].translation-m[1].translation),'incoming_target_velocity':list(ts[1]-ts[0]),'outgoing_target_velocity':list(ts[2]-ts[1]),'incoming_angle':math.degrees(m[0].to_quaternion().rotation_difference(m[1].to_quaternion()).angle),'outgoing_angle':math.degrees(m[1].to_quaternion().rotation_difference(m[2].to_quaternion()).angle)}
 boundaries[f]=item
result={'changed_frames':changed,'boundaries':boundaries,'observations':observations,'key_frames':[216,278,330,380,422,450],'quarter_frame_samples':rows,'obb_hits':hits,'limitations':'Ship bounds include occluded mesh vertices; not visible area. Camera point plus 0.12m vs OBBs, not exact continuous swept-volume collision. Curvature is analytic sphere silhouette, ignoring coastal occlusion.'}
(R/'camera-before-after.json').write_text(json.dumps(result,indent=2))
print('CHANGED', {k:([min(v),max(v),len(v)] if v else []) for k,v in changed.items()});print('OBB hits',len(hits),'max step',max(r.get('step_per_frame',0) for r in rows),'max angle',max(r.get('angle_deg_per_frame',0) for r in rows),'min globe clearance',min(r['globe_clearance'] for r in rows))
print('OBS',json.dumps([o for o in observations if o['frame'] in [216,278,330,380,398,422,450,456]]))
assert not hits,hits[:10]
