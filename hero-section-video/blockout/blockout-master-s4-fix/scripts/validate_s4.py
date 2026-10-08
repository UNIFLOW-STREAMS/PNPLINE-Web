import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scene_evidence import capture
from s4_metrics import sample
from camera_math import orientation_degrees
R=Path(__file__).resolve().parents[1];S=bpy.context.scene;C=S.camera;T=bpy.data.objects['CAM_LOOK_TARGET'];U=bpy.data.objects['US_FRAME'].matrix_world.copy()
label=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'target'
A=capture();B=json.loads((R/'review/baseline-full.json').read_text(encoding='utf-8'));(R/'review'/f'states-{label}.json').write_text(json.dumps(A,default=str),encoding='utf-8')
changes={k:[f for f in range(1393) if A['frames'][f][k]!=B['frames'][f][k]] for k in ['camera','target','lens','noncamera']}
meshes=[o for o in S.objects if o.type=='MESH' and o.name!='EARTH_CONTINUOUS_OCEAN' and not o.name.startswith('WAKE_') and not o.hide_render and not all(c.hide_render for c in o.users_collection)]
boxes={o.name:([min(v[i] for v in o.bound_box) for i in range(3)],[max(v[i] for v in o.bound_box) for i in range(3)]) for o in meshes}
rows=[];hits=[];prev=None
stop=684 if label=='final' else 648
for i in range(452*4,stop*4+1):
 f=i/4;S.frame_set(int(f),subframe=f-int(f));p=C.matrix_world.translation.copy();q=C.matrix_world.to_quaternion();t=T.matrix_world.translation.copy()
 row={'frame':f,'p':list(p),'q':list(q),'t':list(t),'lens':C.data.lens,'globe_clearance':p.length-S['radius'],'us_camera':list(U.inverted()@p)}
 if prev:row.update(speed=(p-prev[0]).length*4,angular_speed=orientation_degrees(q,prev[1])*4,target_speed=(t-prev[2]).length*4)
 rows.append(row);prev=(p,q,t)
 for o in meshes:
  v=o.matrix_world.inverted()@p;lo,hi=boxes[o.name];scale=o.matrix_world.to_scale();margin=[.12/max(abs(scale[j]),1e-8) for j in range(3)]
  if all(lo[j]-margin[j]<v[j]<hi[j]+margin[j] for j in range(3)):hits.append({'frame':f,'object':o.name})
observations=[sample(f) for f in range(490,stop+1)]
boundaries={}
for f in [456,648,672]:
 d={}
 for tag,state in [('before',B['frames']),('after',A['frames'])]:
  m=[Matrix(state[k]['camera']) for k in [f-1,f,f+1]];ts=[Vector(state[k]['target']) for k in [f-1,f,f+1]]
  d[tag]={'position':list(m[1].translation),'quaternion':list(m[1].to_quaternion()),'target':list(ts[1]),'lens':state[f]['lens'],'incoming_velocity':list(m[1].translation-m[0].translation),'outgoing_velocity':list(m[2].translation-m[1].translation),'incoming_target_velocity':list(ts[1]-ts[0]),'outgoing_target_velocity':list(ts[2]-ts[1]),'incoming_angle':math.degrees(m[0].to_quaternion().rotation_difference(m[1].to_quaternion()).angle),'outgoing_angle':math.degrees(m[1].to_quaternion().rotation_difference(m[2].to_quaternion()).angle)}
 boundaries[str(f)]=d
# Numerical proposals only: no S5 animation keys or scene state are edited.
def xyz(state,f,key):return Matrix(state[f]['camera']).translation if key=='p' else Vector(state[f]['target'])
delta={key:xyz(A['frames'],648,key)-xyz(B['frames'],648,key) for key in ['p','t']}
dv={key:(xyz(A['frames'],648,key)-xyz(A['frames'],647,key))-(xyz(B['frames'],648,key)-xyz(B['frames'],647,key)) for key in ['p','t']}
proposals=[]
for length in [12,16,20,24,28,32,36,40]:
 poses=[];quats=[]
 for f in range(647,648+length+2):
  if f<=648:p=xyz(A['frames'],f,'p');t=xyz(A['frames'],f,'t')
  elif f>=648+length:p=xyz(B['frames'],f,'p');t=xyz(B['frames'],f,'t')
  else:
   u=(f-648)/length;h0=2*u**3-3*u*u+1;h1=u**3-2*u*u+u
   p=xyz(B['frames'],f,'p')+h0*delta['p']+h1*length*dv['p'];t=xyz(B['frames'],f,'t')+h0*delta['t']+h1*length*dv['t']
  z=(p-t).normalized();x=(U.to_3x3()@Vector((0,0,1))).cross(z).normalized();y=z.cross(x).normalized();poses.append(p);quats.append(Matrix((x,y,z)).transposed().to_quaternion())
 proposals.append({'frames':[649,648+length-1],'return_exact_at':648+length,'duration_to_exact_seconds':length/12,'max_step':max((poses[i]-poses[i-1]).length for i in range(1,len(poses))),'max_acceleration':max((poses[i+1]-2*poses[i]+poses[i-1]).length for i in range(1,len(poses)-1)),'max_angle':max(math.degrees(quats[i].rotation_difference(quats[i-1]).angle) for i in range(1,len(quats)))})
result={'changes':changes,'boundaries':boundaries,'quarter_frames':rows,'obb_hits':hits,'observations':observations,'join_proposals':proposals,'delta_at_648':{'position_world':list(delta['p']),'position_m':delta['p'].length,'target_world':list(delta['t']),'target_m':delta['t'].length,'lens_mm':A['frames'][648]['lens']-B['frames'][648]['lens']},'limitations':'Quarter-frame point+0.12m OBB check is not continuous swept-volume proof; weighted rays are finite, not pixel segmentation. '+('S5 f649..671 is user approved and applied, exact original at f672; join_proposals retains the numerical alternatives.' if label=='final' else 'S5 proposal computed numerically only, NOT applied and NOT visually approved.')}
(R/'review'/f'validation-{label}.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('CHANGES',{k:([min(v),max(v),len(v)] if v else []) for k,v in changes.items()});print('OBB',len(hits),'max_speed',max(r.get('speed',0) for r in rows),'max_angle',max(r.get('angular_speed',0) for r in rows));print('JOIN',json.dumps(proposals));print('DELTA',result['delta_at_648'])
assert not hits,hits[:10]
assert max(r.get('speed',0) for r in rows)<2.5
assert max(r.get('angular_speed',0) for r in rows)<8
