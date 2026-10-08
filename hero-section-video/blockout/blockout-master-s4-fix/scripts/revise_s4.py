"""Bounded S4 camera patch. Review alternatives do not edit S3/S5 or master."""
import bpy,json,sys,hashlib,math
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
R=Path(__file__).resolve().parents[1];S=bpy.context.scene;C=S.camera;T=bpy.data.objects['CAM_LOOK_TARGET']
BASE_SHA='63e95f15f9ad5b223001021251982266ebe06957a297a5a03e72d732358df976'
assert Path(bpy.data.filepath).resolve()==(R/'inputs/base-s4.blend').resolve()
assert hashlib.sha256((R/'inputs/base-s4.blend').read_bytes()).hexdigest()==BASE_SHA
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['target']
mode=args[0]
assert mode in ['target','limited','final']
if mode=='final':
 approval=json.loads((R/'review/approval-s5-join.json').read_text(encoding='utf-8'))
 assert approval['approved'] and approval['camera_target_lens_frames']==[649,671] and approval['return_exact_at']==672
B=json.loads((R/'review/baseline-full.json').read_text(encoding='utf-8'))['frames']
U=bpy.data.objects['US_FRAME'].matrix_world.copy();inv=U.inverted()
def original(f,key):return inv@(Matrix(B[f]['camera']).translation if key=='p' else Vector(B[f]['target']))
frames=[457,480,499,522,555,582,608,632,648]
positions=[original(457,'p'),Vector((11,-25,22)),Vector((18,-38,28)),Vector((14,-14,15)),Vector((18,-10,16)),Vector((22,5,16)),Vector((11,26,16)),Vector((-3,32,16)),Vector((-4,32,16))]
targets=[original(457,'t'),Vector((-5,3,1.7)),Vector((12,12,2)),Vector((1,2,2)),Vector((1,3,3.5)),Vector((1,6,3.2)),Vector((2,9,3)),Vector((5,8,2.5)),Vector((6,8,2.5))]
lenses=[40,38,32,40,40,38,35,32,32]
if mode=='limited':
 frames=frames[:6]+[632];positions=positions[:6]+[original(632,'p')];targets=targets[:6]+[original(632,'t')];lenses=lenses[:6]+[B[632]['lens']]
def derivatives(values,key):
 out=[original(457,key)-original(456,key)]
 for i in range(1,len(frames)-1):out.append((values[i+1]-values[i-1])/(frames[i+1]-frames[i-1]))
 out.append((original(633,key)-original(632,key)) if mode=='limited' else (values[-1]-values[-2])/(frames[-1]-frames[-2]))
 return out
dp=derivatives(positions,'p');dt=derivatives(targets,'t')
def inherited_roll(f):
 m=Matrix(B[f]['camera']);p=m.translation;t=Vector(B[f]['target'])
 z=(p-t).normalized();x=(U.to_3x3()@Vector((0,0,1))).cross(z).normalized();y=z.cross(x).normalized()
 right=m.to_3x3()@Vector((1,0,0));return math.atan2(right.dot(y),right.dot(x))
roll_start=inherited_roll(457);roll_velocity=roll_start-inherited_roll(456)
def entry_roll(f):
 # Continue the inherited roll and its velocity; settle on US up at f480.
 # The previous camera's globe-up transition cannot be discarded in one frame.
 if f>=480:return 0.
 u=(f-457)/23
 return (2*u**3-3*u*u+1)*roll_start+(u**3-2*u*u+u)*23*roll_velocity
def evaluate(values,d,f):
 i=next(i for i in range(len(frames)-1) if frames[i]<=f<=frames[i+1]);span=frames[i+1]-frames[i];u=(f-frames[i])/span
 return (2*u**3-3*u*u+1)*values[i]+(u**3-2*u*u+u)*span*d[i]+(-2*u**3+3*u*u)*values[i+1]+(u**3-u*u)*span*d[i+1]
S.frame_set(457);prev=C.rotation_quaternion.copy();end=631 if mode=='limited' else 648
# Boundary lens keys prevent retimed S4 lens interpolation from leaking outside S4.
for f in [457,end+1]:
 C.data.lens=B[f]['lens'];C.data.keyframe_insert('lens',frame=f)
for f in range(458,end+1):
 S.frame_set(f);p=U@evaluate(positions,dp,f);t=U@evaluate(targets,dt,f)
 up=U.to_3x3()@Vector((0,0,1));z=(p-t).normalized();x=up.cross(z).normalized();y=z.cross(x).normalized();q=Matrix((x,y,z)).transposed().to_quaternion()
 q=q@Quaternion((0,0,1),entry_roll(f))
 if q.dot(prev)<0:q.negate()
 C.location=p;C.rotation_quaternion=q;T.location=t;C.data.lens=evaluate(lenses,[0]*len(lenses),f)
 C.keyframe_insert('location',frame=f);C.keyframe_insert('rotation_quaternion',frame=f);T.keyframe_insert('location',frame=f);C.data.keyframe_insert('lens',frame=f);prev=q.copy()
if mode=='final':
 def old(f,key):return Matrix(B[f]['camera']).translation if key=='p' else Vector(B[f]['target'])
 endpoints={}
 for f in [647,648]:
  S.frame_set(f);endpoints[f]={'p':C.matrix_world.translation.copy(),'t':T.matrix_world.translation.copy()}
 delta={k:endpoints[648][k]-old(648,k) for k in ['p','t']}
 dv={k:endpoints[648][k]-endpoints[647][k]-(old(648,k)-old(647,k)) for k in ['p','t']}
 for f in range(649,672):
  u=(f-648)/24;h0=2*u**3-3*u*u+1;h1=u**3-2*u*u+u
  p=old(f,'p')+h0*delta['p']+h1*24*dv['p'];t=old(f,'t')+h0*delta['t']+h1*24*dv['t']
  z=(p-t).normalized();x=(U.to_3x3()@Vector((0,0,1))).cross(z).normalized();y=z.cross(x).normalized();q=Matrix((x,y,z)).transposed().to_quaternion()
  if q.dot(prev)<0:q.negate()
  C.location=p;C.rotation_quaternion=q;T.location=t;C.data.lens=B[f]['lens']-8*h0
  C.keyframe_insert('location',frame=f);C.keyframe_insert('rotation_quaternion',frame=f);T.keyframe_insert('location',frame=f);C.data.keyframe_insert('lens',frame=f);prev=q.copy()
 # Matching quaternion hemispheres also prevents a subframe interpolation flip.
 S.frame_set(672);assert C.rotation_quaternion.dot(prev)>0,'Quaternion sign mismatch at exact return'
 end=671
for o in [C,T,C.data]:
 for layer in o.animation_data.action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for fc in bag.fcurves:
     for k in fc.keyframe_points:
      if 457<=k.co.x<=end+1:k.interpolation='LINEAR'
S['s4_review_status']={'target':'REVIEW ONLY: target B45 awaits S5 join approval','limited':'LIMITED: fixed B45, K5 remains unmet','final':'S4 camera plus user-approved S5 f649..671 join; exact original at f672'}[mode]
S['s4_camera_source']='scripts/revise_s4.py '+mode+'; baseline '+BASE_SHA
S['camera_guide_warning']='Legacy CAMERA_PATH preserved; use review/camera-path.png for revised camera. Guides remain hidden.'
S.frame_set(456);S.use_preview_range=True;S.frame_preview_start=444 if mode=='final' else 456;S.frame_preview_end=696 if mode=='final' else 648
for screen in bpy.data.screens:
 for a in screen.areas:
  if a.type=='VIEW_3D':
   a.spaces.active.region_3d.view_perspective='CAMERA';a.spaces.active.overlay.show_overlays=False;a.spaces.active.shading.type='SOLID';a.spaces.active.shading.color_type='MATERIAL'
out=R/(args[1] if len(args)>1 else ('master-s4-fix.blend' if mode=='final' else f'review/candidate-{mode}.blend'))
assert out.resolve().is_relative_to(R.resolve()),'Output must stay in the user-designated version folder'
if out.name=='master-s4-fix.blend':
 assert mode=='final'
 allowed=[BASE_SHA]
 if (R/'review/last-written-hash.txt').exists():allowed.append((R/'review/last-written-hash.txt').read_text().strip())
 assert hashlib.sha256(out.read_bytes()).hexdigest() in allowed,'Master changed externally; preserve and investigate'
bpy.ops.wm.save_as_mainfile(filepath=str(out))
if out.name=='master-s4-fix.blend':(R/'review/last-written-hash.txt').write_text(hashlib.sha256(out.read_bytes()).hexdigest(),encoding='utf-8')
(R/'review'/f'path-{mode}.json').write_text(json.dumps({'frames':frames,'positions':[list(v) for v in positions],'targets':[list(v) for v in targets],'lenses':lenses,'dp':[list(v) for v in dp],'dt':[list(v) for v in dt],'entry_roll_degrees':math.degrees(roll_start),'entry_roll_velocity_degrees':math.degrees(roll_velocity),'entry_roll_settles_at':480,'space':'US_FRAME local cubic Hermite; position and aim differentiated, inherited roll released over f457..480; no per-state stop; lens smoothstep','changed_range':[458,end],'status':S['s4_review_status']},indent=2),encoding='utf-8')
