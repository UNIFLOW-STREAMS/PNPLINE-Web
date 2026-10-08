"""Evaluated motion, donor equivalence, temporal and optical continuity evidence."""
import bpy,sys,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R.parent/'s5-dock-test-v001/scripts'))
from kinematics import vehicle_state
candidate=bpy.data.filepath;cfg=json.loads((R/'config.json').read_text());dc=json.loads((R.parent/'s5-dock-test-v001/config.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(R.parent/'s5-dock-test-v001/master-with-s5-test-v001.blend'));s=bpy.data.scenes['S5_DOCK_TEST_v01'];bpy.context.window.scene=s;I=s.objects['S5T__US_FRAME'].matrix_world.inverted()
worst=0;donor=[]
for j in range(648*4,901*4):
 f=j/4;s.frame_set(j//4,subframe=(j%4)/4);st=vehicle_state(f,dc)
 for kind,n in [('trailer','A03_TRAILER'),('tractor','A03_TRACTOR')]:
  m=I@s.objects['S5T__'+n].matrix_world;worst=max(worst,(m.translation-Vector((*st[kind],0))).length,abs(math.atan2(math.sin(math.atan2(m[1][0],m[0][0])-st[kind+'_yaw']),math.cos(math.atan2(m[1][0],m[0][0])-st[kind+'_yaw']))))
 if f<=810:donor.append((f,(I@s.objects['S5T__A03_TRAILER'].matrix_world).copy()))
assert worst<.0001,('donor conversion',worst)
bpy.ops.wm.open_mainfile(filepath=candidate);s=bpy.data.scenes[cfg['scene']];bpy.context.window.scene=s;I=s.objects['US_FRAME'].matrix_world.inverted()
def at(n,f):s.frame_set(int(f),subframe=f%1);return I@s.objects[n].matrix_world
def qangle(a,b):
 q=a.to_quaternion().rotation_difference(b.to_quaternion());return math.degrees(2*math.atan2(math.sqrt(q.x*q.x+q.y*q.y+q.z*q.z),abs(q.w)))
metrics={'donor_logic_evaluated_equivalence_max':worst};errors=[];frames=[];boundary={}
for f in [719,720,721,809,810,811,842,849,850,889,890,891,899,900,901,923,924,925,947,948,949]:
 row={'frame':f,'objects':{}}
 for n in ['A03_TRACTOR','A03_TRAILER','A01_CONTAINER','W01_NEW_PALLET','W02_INBOUND_JACK','CAM_MASTER','CAM_LOOK_TARGET']:
  row['objects'][n]={'matrix':list(map(list,at(n,f)))}
 row['lens']=s.camera.data.lens;boundary[str(f)]=row
speedmax=0;rotationmax=0;steermax=0;camacc=0;camang=0;hitch=0;step_lens=0;framing=[]
for j in range(720*4,949*4):
 f=j/4;pm=at('A03_TRAILER',f-.25);m=at('A03_TRAILER',f);speed=(m.translation-pm.translation).length*4;speedmax=max(speedmax,speed);rotationmax=max(rotationmax,qangle(pm,m)*4)
 for o in s.objects:
  if o.name.startswith('A03_TRACTOR_WHEEL_1.65'):steermax=max(steermax,abs(math.degrees(o.rotation_euler.z)))
 hitch=max(hitch,(s.objects['TRACTOR_HITCH'].matrix_world.translation-s.objects['TRAILER_HITCH'].matrix_world.translation).length)
 c0=at('CAM_MASTER',f-.25);c1=at('CAM_MASTER',f);lens=s.camera.data.lens;c2=at('CAM_MASTER',f+.25)
 camacc=max(camacc,(c2.translation-2*c1.translation+c0.translation).length*16);camang=max(camang,qangle(c0,c1)*4);step_lens=max(step_lens,abs(s.camera.data.lens-lens)*4)
 if f%1==0:
  s.frame_set(int(f));parts=[s.objects[n] for n in ['TRACTOR_CAB','TRAILER_CHASSIS','A01_ROOF']];points=[world_to_camera_view(s,s.camera,o.matrix_world@Vector(v)) for o in parts for v in o.bound_box]
  bounds=[min(p.x for p in points),max(p.x for p in points),min(p.y for p in points),max(p.y for p in points)]
  framing.append({'frame':f,'truck_bounds':bounds})
 frames.append({'frame':f,'trailer':list(m.translation),'speed_m_per_frame':speed,'yaw':math.atan2(m[1][0],m[0][0])})
metrics.update(max_speed_m_per_frame=speedmax,max_body_degrees_per_frame=rotationmax,max_steering_deg=steermax,max_hitch_m=hitch,max_camera_accel_m_per_frame2=camacc,max_camera_rotation_deg_per_frame=camang,max_lens_mm_per_frame=step_lens)
for key,limit in [('max_body_degrees_per_frame',8),('max_steering_deg',60),('max_hitch_m',.002),('max_camera_rotation_deg_per_frame',8)]:
 if metrics[key]>=limit:errors.append([key,metrics[key],limit])
joins={}
for f in [720,900,948]:
 a=at('CAM_MASTER',f-.25);b=at('CAM_MASTER',f);c=at('CAM_MASTER',f+.25)
 joins[str(f)]={'camera_velocity_before':list((b.translation-a.translation)*4),'camera_velocity_after':list((c.translation-b.translation)*4),'rotation_before_deg_per_frame':qangle(a,b)*4,'rotation_after_deg_per_frame':qangle(b,c)*4}
 if ((c.translation-b.translation)-(b.translation-a.translation)).length*4>.15:errors.append(['camera_velocity_join',f])
out={'pass_all':not errors,'metrics':metrics,'errors':errors,'joins':joins,'framing':framing,'motion':frames,'candidate_sha256':hashlib.sha256(Path(candidate).read_bytes()).hexdigest()}
(R/'review/motion-audit.json').write_text(json.dumps(out,indent=2));(R/'boundary-states.json').write_text(json.dumps(boundary,indent=2));print(json.dumps({'metrics':metrics,'errors':errors,'joins':joins},indent=2));assert not errors

