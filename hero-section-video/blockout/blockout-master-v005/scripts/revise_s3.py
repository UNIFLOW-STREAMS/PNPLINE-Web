"""Reproducible, bounded S3-only patch on the user's saved v005 baseline."""
import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];S=bpy.context.scene
assert Path(bpy.data.filepath).resolve()==(R/'inputs/base-v005.blend').resolve()
assert hashlib.sha256((R/'inputs/base-v005.blend').read_bytes()).hexdigest()=='de03eca6e92f7c03ab967a44ed434531e5506536669a8383d69ac1bbf056ad0d'
base=json.loads((R/'review/baseline-full.json').read_text())['frames'];cam=S.camera;target=bpy.data.objects['CAM_LOOK_TARGET']
def local(f,key):return Matrix(base[f]['ship']).inverted()@(Matrix(base[f]['camera']).translation if key=='p' else Vector(base[f]['target']))
frames=[217,278,338,370,398,422,443,455]
points=[local(217,'p'),Vector((-25,-27,35)),Vector((-25,-27,35)),Vector((-27,-21,22)),Vector((-18,-23,13)),Vector((0,-23,12)),Vector((14,-20,13)),local(455,'p')]
targets=[local(217,'t'),Vector((0,0,5)),Vector((0,0,5)),Vector((5,0,1)),Vector((3,0,1)),Vector((0,0,1)),Vector((0,0,1)),local(455,'t')]
def derivatives(values,key):
 out=[local(217,key)-local(216,key)]
 for i in range(1,len(frames)-1):out.append(Vector((0,0,0)) if i in (1,2) else (values[i+1]-values[i-1])/(frames[i+1]-frames[i-1]))
 out.append(local(456,key)-local(455,key));return out
dp=derivatives(points,'p');dt=derivatives(targets,'t')
def evaluate(values,d,f):
 i=next(i for i in range(len(frames)-1) if frames[i]<=f<=frames[i+1]);span=frames[i+1]-frames[i];u=(f-frames[i])/span
 return (2*u**3-3*u*u+1)*values[i]+(u**3-2*u*u+u)*span*d[i]+(-2*u**3+3*u*u)*values[i+1]+(u**3-u*u)*span*d[i+1]
S.frame_set(217);prev=cam.rotation_quaternion.copy()
for f in range(218,455):
 S.frame_set(f);ship=bpy.data.objects['A02_SHIP'].matrix_world.copy();p=ship@evaluate(points,dp,f);t=ship@evaluate(targets,dt,f)
 up=ship.to_3x3()@Vector((0,0,1));z=(p-t).normalized();x=up.cross(z).normalized();y=z.cross(x).normalized();q=Matrix((x,y,z)).transposed().to_quaternion()
 if q.dot(prev)<0:q.negate()
 cam.location=p;cam.rotation_quaternion=q;target.location=t
 cam.keyframe_insert('location',frame=f);cam.keyframe_insert('rotation_quaternion',frame=f);target.keyframe_insert('location',frame=f);prev=q.copy()
for o in [cam,target]:
 for l in o.animation_data.action.layers:
  for st in l.strips:
   for bag in st.channelbags:
    for fc in bag.fcurves:
     for k in fc.keyframe_points:
      if 218<=k.co.x<=454:k.interpolation='LINEAR'
S['master_version']='v005';S.name='PNPLINE_MASTER_v005';S['camera_revision']='S3 bounded ship-relative camera, f218..454; S2/B23 and B34/S4 preserved'
S['generator']='scripts/revise_s3.py applied to inputs/base-v005.blend';S['source_basis']='User saved baseline SHA256 de03eca6e92f7c03ab967a44ed434531e5506536669a8383d69ac1bbf056ad0d; see report-s3-camera.md'
S['camera_guide_warning']='Preserved pre-revision CAMERA_PATH; use review/camera-path.png for current S3. Guides hidden in beauty.'
S.frame_set(216);S.use_preview_range=True;S.frame_preview_start=204;S.frame_preview_end=480
for screen in bpy.data.screens:
 for a in screen.areas:
  if a.type=='VIEW_3D':
   a.spaces.active.region_3d.view_perspective='CAMERA';a.spaces.active.overlay.show_overlays=False;a.spaces.active.shading.type='SOLID';a.spaces.active.shading.color_type='MATERIAL'
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
out=R/(args[0] if args else 'master-v005.blend')
if out.name=='master-v005.blend' and out.exists():
 allowed=['de03eca6e92f7c03ab967a44ed434531e5506536669a8383d69ac1bbf056ad0d']
 if (R/'review/last-written-hash.txt').exists():allowed.append((R/'review/last-written-hash.txt').read_text().strip())
 assert hashlib.sha256(out.read_bytes()).hexdigest() in allowed,'Saved file changed externally; preserve and investigate.'
bpy.ops.wm.save_as_mainfile(filepath=str(out))
if out.name=='master-v005.blend':(R/'review/last-written-hash.txt').write_text(hashlib.sha256(out.read_bytes()).hexdigest())
(R/'review/path-design.json').write_text(json.dumps({'frames':frames,'positions':[list(p) for p in points],'targets':[list(t) for t in targets],'position_derivatives':[list(v) for v in dp],'target_derivatives':[list(v) for v in dt],'space':'Evaluated ship-local Hermite, baked every frame; no edits outside f218..454'},indent=2))
