"""Bounded, zero-phase micro smoothing; preserve the accepted camera route."""
import bpy,hashlib,json,math
import numpy as np
from pathlib import Path
from mathutils import Matrix,Quaternion,Vector
R=Path(__file__).resolve().parents[1];cfg=json.loads((R/'config.json').read_text())
source=(R/cfg['source']).resolve();out=R/cfg['output']
assert hashlib.sha256(source.read_bytes()).hexdigest()==cfg['source_sha256']
assert not out.exists()
data=json.loads((R/'review/inspection.json').read_text());assert data['sha256']==cfg['source_sha256']
rows=data['rows'];times=np.array([r['frame'] for r in rows])
sigma=cfg['sigma_frames']*8;radius=math.ceil(4*sigma)
kernel=np.exp(-.5*(np.arange(-radius,radius+1)/sigma)**2);kernel/=kernel.sum()
def filtered(key):
 v=np.array([r[key] for r in rows]);return np.column_stack([np.convolve(np.pad(v[:,i],(radius,radius),mode='edge'),kernel,mode='valid') for i in range(v.shape[1])])
eyes=filtered('eye');quats=filtered('q');quats/=np.linalg.norm(quats,axis=1)[:,None]
def sample(v,f):return [float(np.interp(f,times,v[:,i])) for i in range(v.shape[1])]
def ease(t):
 t=max(0,min(1,t));return t*t*t*(10+t*(-15+6*t))

bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;cam=s.camera;parent=cam.parent
a,b=cfg['window'];ticks=[i/8 for i in range(a*8,b*8+1)];records={}
for f in ticks:
 s.frame_set(int(f),subframe=f%1);records[f]=(cam.matrix_world.copy(),parent.matrix_world.copy())
basis=cam.matrix_basis.copy();inverse=cam.matrix_parent_inverse.copy()
layer=bpy.data.objects.new('S4_CAMERA_MICRO_SMOOTH',None);s.collection.objects.link(layer)
layer.parent=parent;layer.rotation_mode='QUATERNION';cam.parent=layer;cam.matrix_parent_inverse=inverse
# Parenting does not alter local transform channels. Do not assign matrix_basis:
# its decomposition would round unchanged rotation/scale outside this window.
last=None;position_delta=[];rotation_delta=[]
for f in [0,a-1,*ticks,b+1,989]:
 C=Matrix.Identity(4)
 if a<f<b:
  old,P=records[f];w=ease((f-a)/cfg['blend_frames'])*ease((b-f)/cfg['blend_frames'])
  eye=old.translation.lerp(Vector(sample(eyes,f)),w)
  q=old.to_quaternion().slerp(Quaternion(sample(quats,f)).normalized(),w)
  desired=Matrix.LocRotScale(eye,q,old.to_scale());C=P.inverted()@desired@old.inverted()@P
  position_delta.append((eye-old.translation).length)
  rotation_delta.append(math.degrees(old.to_quaternion().rotation_difference(q).angle))
 layer.location=C.translation;layer.rotation_quaternion=C.to_quaternion()
 if last and layer.rotation_quaternion.dot(last)<0:layer.rotation_quaternion.negate()
 last=layer.rotation_quaternion.copy()
 layer.keyframe_insert('location',frame=f);layer.keyframe_insert('rotation_quaternion',frame=f)
for l in layer.animation_data.action.layers:
 for st in l.strips:
  for bag in st.channelbags:
   for fc in bag.fcurves:
    for k in fc.keyframe_points:k.interpolation='LINEAR'
layer['window']='f330..f366 only';layer['filter']='symmetric Gaussian sigma2f; quintic6f boundaries; unchanged lens/shift/timing'
s.frame_set(350);bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(R/'review/build.json').write_text(json.dumps({'source_sha256':cfg['source_sha256'],'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
 'window':[a,b],'max_position_correction':max(position_delta),'max_rotation_correction_degrees':max(rotation_delta)},indent=2))
