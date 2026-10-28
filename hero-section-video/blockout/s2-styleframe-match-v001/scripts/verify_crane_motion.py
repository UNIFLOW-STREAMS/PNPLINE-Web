import bpy,json,hashlib,math
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1];candidate=Path(bpy.data.filepath);ver=candidate.stem.rsplit('-',1)[-1];s=bpy.context.scene
cfg=json.loads((R/f'review/crane-integration-{ver}.json').read_text());allowed_actions=set(cfg['changed_original_actions'])
def actions():return {a.name:[[fc.data_path,fc.array_index,[[list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation]for k in fc.keyframe_points]]for l in a.layers for st in l.strips for bag in st.channelbags for fc in bag.fcurves]for a in bpy.data.actions}
def sample():
 result={};s=bpy.context.scene
 for f in range(72,s.frame_end+1):
  s.frame_set(f);result[f]={n:list(map(list,s.objects[n].matrix_world))for n in ['A01_CONTAINER','A02_SHIP','CAM_MASTER','CAM_LOOK_TARGET']}
 return result
aa=actions();after=sample();s.frame_set(156);D=s.objects['SF_CN_LAYOUT'];DI=D.matrix_world.inverted();DM=D.matrix_world
# Static architectural envelopes for conservative clearance checks.
arch=[]
for o in s.objects:
 if o.type=='EMPTY'and(o.get('role')in ['village_house','harbor_hall','masonry_infill']or o.name in ['DT_LEFT','DT_CENTER','DT_RIGHT','DT_FACADE']):
  ps=[DI@c.matrix_world@Vector(p)for c in o.children_recursive if c.type=='MESH'and not c.hide_render for p in c.bound_box]
  if ps:arch.append((o.name,Vector(tuple(min(p[i]for p in ps)for i in range(3))),Vector(tuple(max(p[i]for p in ps)for i in range(3)))))
rope_errors=[];collisions=[];camera_hits=[];max_endpoint=0;min_rope=100;max_frame_step=0;previous=None
cables=sorted([o for o in s.objects if o.name.startswith('CR_WORKING_CABLE')],key=lambda o:o.name)
locks=sorted([o for o in s.objects if o.name.startswith('CR_TWISTLOCK')],key=lambda o:o.name)
for step in range(313):
 f=step/2;s.frame_set(int(f),subframe=f%1);p=DI@s.objects['P01_SPREADER'].matrix_world.translation
 head=DI@s.objects['CR_SUSPENSION_HEAD'].matrix_world.translation
 # Measure the actual interpolated lock geometry, not an analytic easing curve:
 # the baked telescoping mechanism interpolates linearly between integer keys.
 hx=abs(locks[0].location.x);hy=abs(locks[0].location.y)
 if previous is not None:max_frame_step=max(max_frame_step,(p-previous).length)
 previous=p
 for (sx,sy),c,lock in zip([(-1,-1),(-1,1),(1,-1),(1,1)],cables,locks):
  ends=[DI@c.matrix_world@Vector((0,0,z))for z in [-.5,.5]]
  lower=DI@(lock.matrix_world@Vector((0,0,.205)))
  expected=[lower,head+Vector((-sx*hx,-sy*hy,-.02))]
  err=max((a-b).length for a,b in zip(ends,expected));max_endpoint=max(max_endpoint,err);min_rope=min(min_rope,(ends[1]-ends[0]).length)
  if err>.004:rope_errors.append([f,c.name,err])
 # Only released spreader moves across the village; loaded hero remains in its original slot.
 if f>=78:
  lo=p-Vector((hx+.08,hy+.08,.20));hi=p+Vector((hx+.08,hy+.08,.18))
  for name,a,b in arch:
   if all(lo[i]<b[i]and hi[i]>a[i]for i in range(3)):collisions.append([f,name])
 cp=DI@s.camera.matrix_world.translation
 for name,a,b in arch:
  if all(a[i]-.10<cp[i]<b[i]+.10 for i in range(3)):camera_hits.append([f,name])
s.frame_set(72);cargo=DI@s.objects['A01_CONTAINER'].matrix_world.translation;sp=DI@s.objects['P01_SPREADER'].matrix_world.translation;landing_gap=sp.z-cargo.z
bpy.ops.wm.open_mainfile(filepath=str(R/'review/crane-style-proposal-v019.blend'));ba=actions();before=sample()
diff={n:0.0 for n in ['A01_CONTAINER','A02_SHIP','CAM_MASTER','CAM_LOOK_TARGET']}
for f in before:
 for n in diff:diff[n]=max(diff[n],max(abs(before[f][n][i][j]-after[f][n][i][j])for i in range(4)for j in range(4)))
unexpected=[n for n in ba if n not in allowed_actions and ba[n]!=aa.get(n)]
checks={'landing_pose_and_voyage_f72_onward_preserved':diff['A01_CONTAINER']<.00001 and diff['A02_SHIP']<.00001,'camera_f72_onward_preserved':diff['CAM_MASTER']<.00001 and diff['CAM_LOOK_TARGET']<.00001,'only_authorized_original_actions_changed':not unexpected,'spreader_contacts_container_at_f72':abs(landing_gap-.89)<.00003,'cable_endpoints_connected':not rope_errors,'positive_hoist_clearance':min_rope>.15,'released_spreader_clears_architecture':not collisions,'S1_camera_outside_architecture':not camera_hits}
result={'file':str(candidate),'sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'checks':checks,'preserved_matrix_max_error':diff,'unexpected_action_changes':unexpected,'original_actions':len(ba),'new_actions':len(aa)-len(ba),'landing_frame':72,'landing_gap':landing_gap,'max_cable_endpoint_error':max_endpoint,'minimum_rope_length':min_rope,'max_half_frame_spreader_step':max_frame_step,'rope_errors':rope_errors[:30],'architectural_overlaps':collisions[:30],'camera_inside_buildings':camera_hits[:30],'sample_scope':'f0..156 half-frame mechanical/architectural checks; all integer frames f72..1392 protected actor and camera comparisons. Not a continuous-time physics proof.'}
(R/f'review/crane-motion-verified-{ver}.json').write_text(json.dumps(result,indent=2));print(json.dumps(result));assert all(checks.values())
