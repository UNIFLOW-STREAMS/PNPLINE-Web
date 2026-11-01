"""Retarget the accepted China camera staging to the expanded harbor.

Original animation actions/optics remain on their objects. Correction parents
carry the new camera placement and become identity at the source-route handoff.
"""
import bpy
import hashlib
import json
import math
import sys
from pathlib import Path
import numpy as np
from mathutils import Matrix, Quaternion, Vector

R = Path(__file__).resolve().parents[1]
SOURCE = R.parent / 'cn-port-layout-v001/master-cn-port-layout-v001.blend'
SOURCE_SHA = '053f302410863ce487a9fdbd0cf4b4c83dded3577c0a02e38ac7c0a6951f3174'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_SHA
if Path(bpy.data.filepath) != SOURCE:
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
s = bpy.context.scene
sys.path.insert(0, str(R / 'scripts'))
from fix_port_normals import fix_port_normals
normal_report = fix_port_normals(s)
cam = s.camera
target = s.objects['CAM_LOOK_TARGET']
layout = s.objects['SF_CN_LAYOUT']
s.frame_set(0)
D = layout.matrix_world.copy()
up_cn = (D.to_3x3() @ Vector((0, 0, 1))).normalized()
delta = D.to_3x3() @ Vector((14, -13.5, 0))
city_shift = D.to_3x3() @ Vector((3, -4.5, 0))
STEP = .125
times = np.arange(0, 364 + STEP, STEP)
source = []
for f in times:
    s.frame_set(int(f), subframe=float(f % 1))
    source.append({'C': cam.matrix_world.copy(), 'T': target.matrix_world.copy(),
                   'ship': s.objects['A02_SHIP'].matrix_world.copy(),
                   'berth': s.objects['PORT_BERTH_PLACEMENT'].matrix_world.copy()})

sys.path.insert(0, str(R / 'scripts'))
from ship_support import build_ship_support
ship_helper, ship_report = build_ship_support(s, layout)

def ease(t):
    t = max(0., min(1., t))
    return t*t*t*(10+t*(-15+6*t))

def view(eye, aim, up):
    z = (eye-aim).normalized()
    x = up.cross(z).normalized()
    assert x.length > .9, 'Degenerate camera up'
    y = z.cross(x).normalized()
    return Matrix((x, y, z)).transposed().to_quaternion()

eyes = []
aims = []
ups = []
for f, old in zip(times, source):
    s.frame_set(int(f), subframe=float(f % 1))
    p = old['C'].translation
    t = old['T'].translation
    reveal = ease((f-72)/72)
    voyage = ease((f-156)/132)
    handoff = 1-ease((f-320)/40)
    source_ship = old['ship'].translation-old['berth'].translation
    ship_delta = s.objects['A02_SHIP'].matrix_world.translation-source_ship
    shift = delta.lerp(city_shift, reveal).lerp(ship_delta, voyage)
    shift *= handoff
    scale = 1 + .27*reveal*(1-voyage)
    eyes.append(list(p+shift+(p-t)*(scale-1)))
    aims.append(list(t+shift))
    ship_up = (old['ship'].to_3x3() @ Vector((0, 0, 1))).normalized()
    up = up_cn.lerp(ship_up, ease((f-156)/132)).normalized()
    ups.append(up)

def gaussian(values, sigma_frames=1.75):
    values = np.array(values)
    sigma = sigma_frames/STEP
    radius = int(math.ceil(4*sigma))
    kernel = np.exp(-.5*(np.arange(-radius,radius+1)/sigma)**2)
    kernel /= kernel.sum()
    return np.column_stack([np.convolve(np.pad(values[:,i], (radius,radius), mode='edge'),
                                        kernel, mode='valid') for i in range(values.shape[1])])

smooth_eyes = gaussian(eyes)
smooth_aims = gaussian(aims)
poses = []
last = None
for i, (f, old) in enumerate(zip(times, source)):
    weight = ease((f-72)/12)*(1-ease((f-344)/16))
    eye = Vector(eyes[i]).lerp(Vector(smooth_eyes[i]), weight)
    aim = Vector(aims[i]).lerp(Vector(smooth_aims[i]), weight)
    if f <= 72:
        q = old['C'].to_quaternion()
    else:
        q = view(eye, aim, ups[i])
        # Retain the source orientation residual while joining its moving
        # globe horizon. This prevents a forced roll reset at the handoff.
        raw = view(old['C'].translation, old['T'].translation, ups[i])
        residual = raw.rotation_difference(old['C'].to_quaternion())
        if residual.w < 0:
            residual.negate()
        q = q @ Quaternion((1,0,0,0)).slerp(residual, ease((f-276)/84))
    if f >= 360:
        eye = old['C'].translation.copy()
        aim = old['T'].translation.copy()
        q = old['C'].to_quaternion()
    if last is not None and last.dot(q) < 0:
        q.negate()
    last = q.copy()
    poses.append((eye, aim, q))

# Symmetric quaternion filtering removes local roll noise without phase lag.
filtered_q = gaussian([list(p[2]) for p in poses], 1.0)
for i, (f, old) in enumerate(zip(times, source)):
    w = ease((f-72)/12)*(1-ease((f-344)/16))
    eye, aim, q = poses[i]
    q = q.slerp(Quaternion(filtered_q[i]).normalized(), w)
    poses[i] = (eye, aim, q)

# Match the incoming closeup velocity and acceleration instead of inheriting
# the original abrupt stop at f72. A quintic bridge has shared first/second
# derivatives with both the preserved closeup and the filtered pullback.
def quintic(y0, v0, a0, y1, v1, a1, u, duration):
    c0, c1, c2 = y0, v0*duration, a0*(duration*duration*.5)
    b0 = y1-c0-c1-c2
    b1 = v1*duration-c1-2*c2
    b2 = a1*(duration*duration)-2*c2
    c3 = 10*b0-4*b1+.5*b2
    c4 = -15*b0+7*b1-b2
    c5 = 6*b0-3*b1+.5*b2
    return c0+u*(c1+u*(c2+u*(c3+u*(c4+u*c5))))

a, b = int(72/STEP), int(84/STEP)
q0 = poses[a][2].copy()
def log_rotation(q):
    residual = q0.rotation_difference(q)
    if residual.w < 0:
        residual.negate()
    xyz = Vector((residual.x,residual.y,residual.z))
    length = xyz.length
    return xyz*(2*math.atan2(length,residual.w)/length) if length > 1e-10 else Vector((0,0,0))
values = [[p[0].copy() for p in poses], [p[1].copy() for p in poses],
          [log_rotation(p[2]) for p in poses]]
bridged = []
for vs in values:
    # Half-frame secants suppress float noise while measuring the preserved
    # linear-key motion on the left and the filtered curve on the right.
    h = 4
    dt = h*STEP
    v0 = (3*vs[a]-4*vs[a-h]+vs[a-2*h])/(2*dt)
    a0 = (vs[a]-2*vs[a-h]+vs[a-2*h])/(dt*dt)
    v1 = (vs[b+h]-vs[b-h])/(2*dt)
    a1 = (vs[b+h]-2*vs[b]+vs[b-h])/(dt*dt)
    bridged.append([quintic(vs[a],v0,a0,vs[b],v1,a1,(i-a)/(b-a),12.) for i in range(a,b+1)])
for i in range(a+1,b):
    rv = bridged[2][i-a]
    q = q0 @ (Quaternion(rv.normalized(),rv.length) if rv.length > 1e-8 else Quaternion())
    poses[i] = (bridged[0][i-a],bridged[1][i-a],q)

def new_parent(name, obj):
    assert obj.parent is None
    layer = bpy.data.objects.new(name, None)
    s.collection.objects.link(layer)
    layer.rotation_mode = 'QUATERNION'
    obj.parent = layer
    return layer

camera_layer = new_parent('PORT_CAMERA_RETARGET', cam)
target_layer = new_parent('PORT_CAMERA_TARGET_RETARGET', target)
previous = None
for i, (f, old) in enumerate(zip(times, source)):
    if f > 360:
        continue
    eye, aim, q = poses[i]
    desired = Matrix.LocRotScale(eye, q, old['C'].to_scale())
    correction = desired @ old['C'].inverted() if f < 360 else Matrix.Identity(4)
    camera_layer.location = correction.translation
    cq = correction.to_quaternion()
    if previous is not None and previous.dot(cq) < 0:
        cq.negate()
    previous = cq.copy()
    camera_layer.rotation_quaternion = cq
    target_layer.location = aim-old['T'].translation if f < 360 else Vector((0,0,0))
    camera_layer.keyframe_insert('location', frame=float(f))
    camera_layer.keyframe_insert('rotation_quaternion', frame=float(f))
    target_layer.keyframe_insert('location', frame=float(f))
for layer in [camera_layer, target_layer]:
    for action_layer in layer.animation_data.action.layers:
        for strip in action_layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    curve.extrapolation = 'CONSTANT'
                    for key in curve.keyframe_points:
                        key.interpolation = 'LINEAR'

camera_layer['intent'] = 'Original closeup/reveal/departure staging retargeted; CN/sphere up; zero-phase smoothing'
camera_layer['identity_from_frame'] = 360
s['cn_port_camera_revision'] = 'Preserved S1 shot via berth translation; wider city reveal; smooth departure; original route exact from f360'
s.frame_set(156)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.region_3d.view_perspective = 'CAMERA'
out = R / 'master-cn-port-camera-v001.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(out), compress=True)
report = {'source': str(SOURCE), 'source_sha256': SOURCE_SHA, 'file': str(out),
          'sha256': hashlib.sha256(out.read_bytes()).hexdigest(),
          'camera_scope': [0,360], 'source_actions_rewritten': False,
          'optics_changed': False, 'sample_step': STEP,
          'city_translation_layout': [3,-4.5,0], 'city_distance_factor': 1.27,
          'closeup_pullback_C2_bridge': [72,84],
          'eye_target_filter_sigma_frames': 1.75, 'orientation_filter_sigma_frames': 1.,
          'ship_support': ship_report, 'port_normals': normal_report,
          'status': 'Pending independent camera and visual checks'}
(R / 'delivery.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('BUILT_CAMERA', report['sha256'], flush=True)
