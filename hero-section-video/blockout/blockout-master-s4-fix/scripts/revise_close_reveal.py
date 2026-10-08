"""Local foreground-scale correction atop the latest saved S4 master.

Reproducible input is inputs/before-close-reveal.blend; only f458..521
camera, aim and focal length change. The previous approved later shot remains exact.
"""
import bpy,json,sys,hashlib,math
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
R=Path(__file__).resolve().parents[1];S=bpy.context.scene;C=S.camera;T=bpy.data.objects['CAM_LOOK_TARGET']
BASE_SHA='85c2431c6cb26060b768d38ce1d5e3a859c000d5ae6e72a75a47ab51cccd47de'
base=R/'inputs/before-close-reveal.blend'
assert Path(bpy.data.filepath).resolve()==base.resolve()
assert hashlib.sha256(base.read_bytes()).hexdigest()==BASE_SHA
B=json.loads((R/'review/close-reveal/before-states.json').read_text(encoding='utf-8'))['frames']
U=bpy.data.objects['US_FRAME'].matrix_world.copy();inv=U.inverted()
def old(f,key):return inv@(Matrix(B[f]['camera']).translation if key=='p' else Vector(B[f]['target']))
frames=[457,480,499,522]
positions=[old(457,'p'),Vector((0,-25,16)),Vector((0,-30,14)),old(522,'p')]
targets=[old(457,'t'),Vector((-4,2,2)),Vector((6,6,2)),old(522,'t')]
lenses=[B[457]['lens'],38,35,B[522]['lens']]
def derivatives(values,key):
 return [old(457,key)-old(456,key),*( (values[i+1]-values[i-1])/(frames[i+1]-frames[i-1]) for i in [1,2]),old(523,key)-old(522,key)]
dp=derivatives(positions,'p');dt=derivatives(targets,'t')
# Finish the inland aim at the reveal, then return toward the ship without
# overshooting the focal point to its right while the camera approaches.
dt[2].x=0.
def evaluate(values,d,f):
 i=next(i for i in range(3) if frames[i]<=f<=frames[i+1]);span=frames[i+1]-frames[i];u=(f-frames[i])/span
 return (2*u**3-3*u*u+1)*values[i]+(u**3-2*u*u+u)*span*d[i]+(-2*u**3+3*u*u)*values[i+1]+(u**3-u*u)*span*d[i+1]
def roll(f):
 m=Matrix(B[f]['camera']);z=(m.translation-Vector(B[f]['target'])).normalized()
 x=(U.to_3x3()@Vector((0,0,1))).cross(z).normalized();y=z.cross(x).normalized();right=m.to_3x3()@Vector((1,0,0))
 return math.atan2(right.dot(y),right.dot(x))
r0=roll(457);rv=r0-roll(456)
def entry_roll(f):
 if f>=480:return 0.
 u=(f-457)/23
 return (2*u**3-3*u*u+1)*r0+(u**3-2*u*u+u)*23*rv
S.frame_set(457);prev=C.rotation_quaternion.copy()
for f in range(458,522):
 S.frame_set(f);p=U@evaluate(positions,dp,f);t=U@evaluate(targets,dt,f)
 z=(p-t).normalized();x=(U.to_3x3()@Vector((0,0,1))).cross(z).normalized();y=z.cross(x).normalized()
 q=Matrix((x,y,z)).transposed().to_quaternion()@Quaternion((0,0,1),entry_roll(f))
 if q.dot(prev)<0:q.negate()
 C.location=p;C.rotation_quaternion=q;T.location=t;C.data.lens=evaluate(lenses,[0]*4,f)
 C.keyframe_insert('location',frame=f);C.keyframe_insert('rotation_quaternion',frame=f);T.keyframe_insert('location',frame=f);C.data.keyframe_insert('lens',frame=f);prev=q.copy()
S.frame_set(522);assert C.rotation_quaternion.dot(prev)>0,'Quaternion hemisphere at preserved join'
for o in [C,T,C.data]:
 for layer in o.animation_data.action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for fc in bag.fcurves:
     for k in fc.keyframe_points:
      if 458<=k.co.x<=521:k.interpolation='LINEAR'
S['s4_close_reveal_source']='scripts/revise_close_reveal.py; baseline '+BASE_SHA
S['s4_close_reveal_range']='f458..521; f522 onward preserved exactly'
S.frame_set(502)
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
out=R/(args[0] if args else 'review/close-reveal/candidate.blend')
assert out.resolve().is_relative_to(R.resolve())
if out.name=='master-s4-fix.blend':
 allowed=[BASE_SHA]
 stamp=R/'review/close-reveal/last-written-hash.txt'
 if stamp.exists():allowed.append(stamp.read_text(encoding='utf-8').strip())
 assert hashlib.sha256(out.read_bytes()).hexdigest() in allowed,'User changed master; preserve and investigate'
bpy.ops.wm.save_as_mainfile(filepath=str(out))
if out.name=='master-s4-fix.blend':stamp.write_text(hashlib.sha256(out.read_bytes()).hexdigest(),encoding='utf-8')
(R/'review/close-reveal/path.json').write_text(json.dumps({'frames':frames,'positions':[list(p) for p in positions],'targets':[list(t) for t in targets],'lenses':lenses,'changed':[458,521],'preserved_join':522,'entry_roll_degrees':math.degrees(r0)},indent=2),encoding='utf-8')
