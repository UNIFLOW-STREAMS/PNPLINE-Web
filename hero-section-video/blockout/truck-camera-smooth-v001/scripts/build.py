"""Smooth the truck-follow camera only, with a stable port-to-warehouse up frame."""
import bpy,hashlib,json,math,sys
import numpy as np
from pathlib import Path
from mathutils import Matrix,Vector,Quaternion

R=Path(__file__).resolve().parents[1];cfg=json.loads((R/'config.json').read_text())
source=(R/cfg['source']).resolve();out=R/cfg['output']
assert hashlib.sha256(source.read_bytes()).hexdigest()==cfg['source_sha256']
assert not out.exists()
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;cam=s.camera
assert not cam.constraints
info=json.loads((R/'review/inspection.json').read_text());rows=info['rows'];times=np.array([r['frame'] for r in rows])
portup=Vector(info['portup']);whup=Vector(info['whup'])

def ease(t):
    t=max(0,min(1,t));return t*t*t*(10+t*(-15+6*t))

def weight(f):
    a,b=cfg['window'];c,d=cfg['full_weight']
    return ease((f-a)/(c-a))*(1-ease((f-d)/(b-d)))

sigma=cfg['sigma_frames']/0.5
radius=math.ceil(sigma*4);kernel=np.exp(-.5*(np.arange(-radius,radius+1)/sigma)**2);kernel/=kernel.sum()
def filtered(key):
    values=np.array([r[key] for r in rows])
    if values.ndim==1:values=values[:,None]
    return np.column_stack([np.convolve(np.pad(values[:,i],(radius,radius),mode='edge'),kernel,mode='valid') for i in range(values.shape[1])])

smooth_eye=filtered('eye');smooth_front=filtered('forward');smooth_lens=filtered('lens')
def sample(array,f):return np.array([np.interp(f,times,array[:,i]) for i in range(array.shape[1])])
def camera_time(f):
    # Spread the fastest part of the turn without changing vehicle/door timing.
    u=max(0,min(1,(f-450)/150))
    return f-cfg['camera_delay_frames']*math.sin(math.pi*u)**2

def stable_up(f):
    a,b=cfg['reference_up_transition']
    return portup.lerp(whup,ease((f-a)/(b-a))).normalized()

def make_pose(f,original):
    w=weight(f);t=camera_time(f)
    eye=original.translation.lerp(Vector(sample(smooth_eye,t)),w)
    front=Vector(sample(smooth_front,t)).normalized();up=stable_up(f)
    right=front.cross(up).normalized();up=right.cross(front).normalized()
    level=Matrix((right,up,-front)).transposed().to_quaternion()
    q=original.to_quaternion().slerp(level,w)
    return Matrix.LocRotScale(eye,q,original.to_scale())

a,b=cfg['window'];ticks=[i/8 for i in range(a*8,b*8+1)]
records={};parent=cam.parent
for f in ticks:
    s.frame_set(int(f),subframe=f%1)
    records[f]=(cam.matrix_world.copy(),parent.matrix_world.copy())

basis=cam.matrix_basis.copy();inverse=cam.matrix_parent_inverse.copy()
layer=bpy.data.objects.new('S5_SMOOTH_CAMERA',None);s.collection.objects.link(layer)
layer.parent=parent;layer.rotation_mode='QUATERNION'
layer['role']='truck_camera_smoothing_only'
cam.parent=layer;cam.matrix_basis=basis;cam.matrix_parent_inverse=inverse
previous=None
for f in [0,a-1,*ticks,b+1,989]:
    correction=Matrix.Identity(4)
    if a<f<b:
        original,P=records[f];final=make_pose(f,original)
        correction=P.inverted()@final@original.inverted()@P
    layer.location=correction.translation;layer.rotation_quaternion=correction.to_quaternion()
    if previous and layer.rotation_quaternion.dot(previous)<0:layer.rotation_quaternion.negate()
    previous=layer.rotation_quaternion.copy()
    layer.keyframe_insert('location',frame=f);layer.keyframe_insert('rotation_quaternion',frame=f)
for l in layer.animation_data.action.layers:
    for st in l.strips:
        for bag in st.channelbags:
            for fc in bag.fcurves:
                for k in fc.keyframe_points:k.interpolation='LINEAR'

# Retain the projection and lens animation. No change to logistics or the33s clock.
s['truck_camera_revision']='v001: gaussian10f trajectory/forward smoothing;4f bounded lag; stable port/warehouse horizon'
s['truck_camera_modified_window']=f'{a}..{b}'
s.frame_set(526)
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(R/'review/build.json').write_text(json.dumps({'source_sha256':cfg['source_sha256'],'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'window':[a,b],'new_object':layer.name,'camera_only':True,'fps':s.render.fps,'frame_end':s.frame_end},indent=2))
print('SAVED',out)
