"""China opening into the existing US camera stack, on the native 30fps clock.

Public API:
  times = capture_times(clock)          # source-CN frames, sampled on output grid
  cn = capture_cn(cn_scene, times)      # call while the CN source is loaded
  report = install_camera(us_scene, cn, clock)

The US camera/data actions, lens drivers and nested correction parents survive.
Only two inserted placement parents carry the splice and are identity from253.
"""
import hashlib
import math
from pathlib import Path

import bpy
from mathutils import Matrix, Quaternion, Vector

BLEND_START = 165.0
BLEND_END = 253.0
SAMPLE_STEP = 0.125


def _ease(t):
    t = max(0.0, min(1.0, t))
    return t*t*t*(10+t*(-15+6*t))


def _set_frame(scene, frame):
    whole = math.floor(frame)
    scene.frame_set(whole, subframe=frame-whole)


def _values(matrix):
    return [list(row) for row in matrix]


def capture_times(clock, step=SAMPLE_STEP):
    """Return CN frame times corresponding to a uniform native-US output grid."""
    count = round(BLEND_END/step)
    assert abs(count*step-BLEND_END) < 1e-8
    return [float(clock.source(i*step)) for i in range(count+1)]


def capture_cn(scene, times):
    """Capture evaluated CN camera/target world poses without changing the file."""
    source = Path(bpy.data.filepath)
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    saved_frame = scene.frame_current + scene.frame_subframe
    rows = []
    camera = scene.camera
    target = scene.objects['CAM_LOOK_TARGET']
    for frame in times:
        _set_frame(scene, float(frame))
        rows.append({'cn_frame': float(frame), 'camera': _values(camera.matrix_world),
                     'target': _values(target.matrix_world), 'lens': camera.data.lens,
                     'shift': [camera.data.shift_x, camera.data.shift_y]})
    _set_frame(scene, saved_frame)
    assert hashlib.sha256(source.read_bytes()).hexdigest() == source_hash
    return {'source': str(source), 'source_sha256': source_hash, 'samples': rows,
            'source_fps': scene.render.fps/scene.render.fps_base,
            'sample_semantics': 'CN frames from TimeMap.source(uniform US output frames)'}


def _blend_pose(cn, us, weight):
    if weight <= 0:
        return cn.copy()
    if weight >= 1:
        return us.copy()
    qa, qb = cn.to_quaternion(), us.to_quaternion()
    if qa.dot(qb) < 0:
        qb.negate()
    return Matrix.LocRotScale(cn.translation.lerp(us.translation, weight),
                              qa.slerp(qb, weight),
                              cn.to_scale().lerp(us.to_scale(), weight))


def _new_wrapper(scene, obj, name):
    assert scene.objects.get(name) is None, 'Camera splice was already installed'
    assert all(c.mute or c.influence == 0 for c in obj.constraints), 'Active object constraint requires a post-constraint splice'
    parent = obj.parent
    original_inverse = obj.matrix_parent_inverse.copy()
    original_basis = obj.matrix_basis.copy()
    wrapper = bpy.data.objects.new(name, None)
    scene.collection.objects.link(wrapper)
    wrapper.parent = parent
    wrapper.matrix_parent_inverse = Matrix.Identity(4)
    wrapper.rotation_mode = 'QUATERNION'
    wrapper['integration_role'] = 'China camera handoff into preserved US camera stack'
    wrapper['identity_from_output_frame'] = BLEND_END
    wrapper['blend_start_output_frame'] = BLEND_START
    obj.parent = wrapper
    obj.matrix_parent_inverse = original_inverse
    # Do not reassign/decompose obj.matrix_basis: original local channels remain exact.
    assert _values(obj.matrix_basis) == _values(original_basis), 'Parent insertion altered original local transform'
    return wrapper, {'before': parent.name if parent else None, 'after': wrapper.name,
                     'original_matrix_parent_inverse': _values(original_inverse),
                     'local_channels_unchanged': True}


def install_camera(scene, captured, clock):
    """Install a C2 weighted world-pose splice, preserving every US action/optic."""
    assert scene.render.fps == 30 and scene.frame_start == 0 and scene.frame_end == 989
    camera = scene.camera
    target = scene.objects['CAM_LOOK_TARGET']
    original_camera_parent = camera.parent
    original_target_parent = target.parent
    frames = []
    records = []
    for cn in captured['samples']:
        frame = float(clock.output(cn['cn_frame']))
        nearest_grid = round(frame/SAMPLE_STEP)*SAMPLE_STEP
        if abs(frame-nearest_grid) < 1e-6:
            frame = nearest_grid
        assert 0 <= frame <= BLEND_END+1e-6
        _set_frame(scene, frame)
        records.append({'camera': camera.matrix_world.copy(), 'target': target.matrix_world.copy(),
                        'camera_parent': original_camera_parent.matrix_world.copy() if original_camera_parent else Matrix.Identity(4),
                        'target_parent': original_target_parent.matrix_world.copy() if original_target_parent else Matrix.Identity(4),
                        'cn_camera': Matrix(cn['camera']), 'cn_target': Matrix(cn['target']),
                        'optics': [camera.data.lens, camera.data.shift_x, camera.data.shift_y]})
        frames.append(frame)
    assert frames[0] == 0 and abs(frames[-1]-BLEND_END) < 1e-6
    assert all(abs(b-a-SAMPLE_STEP) < 1e-6 for a,b in zip(frames, frames[1:])), 'Incomplete capture grid'
    layers = {}
    parents_changed = {}
    for key, obj, name in [('camera', camera, 'INTEGRATED_CN_CAMERA'),
                           ('target', target, 'INTEGRATED_CN_CAMERA_TARGET')]:
        layers[key], parents_changed[obj.name] = _new_wrapper(scene, obj, name)
    previous = {}
    for frame, record in zip(frames, records):
        weight = _ease((frame-BLEND_START)/(BLEND_END-BLEND_START))
        for key, layer in layers.items():
            correction = Matrix.Identity(4)
            if frame < BLEND_END:
                desired = _blend_pose(record['cn_'+key], record[key], weight)
                parent = record[key+'_parent']
                correction = parent.inverted() @ desired @ record[key].inverted() @ parent
            layer.location = correction.translation
            q = correction.to_quaternion()
            if key in previous and previous[key].dot(q) < 0:
                q.negate()
            previous[key] = q.copy()
            layer.rotation_quaternion = q
            layer.scale = correction.to_scale()
            for path in ['location', 'rotation_quaternion', 'scale']:
                layer.keyframe_insert(path, frame=frame)
    for key, layer in layers.items():
        layer.location = (0, 0, 0)
        layer.rotation_quaternion = (1, 0, 0, 0)
        layer.scale = (1, 1, 1)
        for path in ['location', 'rotation_quaternion', 'scale']:
            layer.keyframe_insert(path, frame=989)
        for action_layer in layer.animation_data.action.layers:
            for strip in action_layer.strips:
                for bag in strip.channelbags:
                    for curve in bag.fcurves:
                        curve.extrapolation = 'CONSTANT'
                        for k in curve.keyframe_points:
                            k.interpolation = 'LINEAR'
    _set_frame(scene, BLEND_END)
    final_error = max(abs(a-b) for a,b in zip(
        [v for row in camera.matrix_world for v in row],
        [v for row in records[-1]['camera'] for v in row]))
    assert final_error < 1e-6, ('Camera identity handoff differs', final_error)
    return {'method': 'Evaluated world-pose blend carried by conjugated placement parents',
            'cn_source_sha256': captured['source_sha256'],
            'cn_exact_output_window': [0, BLEND_START],
            'blend_output_window': [BLEND_START, BLEND_END],
            'blend_cn_equivalent_window': [clock.source(BLEND_START), clock.source(BLEND_END)],
            'us_exact_from_output_frame': BLEND_END,
            'sample_step_output_frames': SAMPLE_STEP, 'sample_count': len(frames),
            'easing': 'quintic smoothstep, zero first/second weight derivatives at both boundaries',
            'orientation': 'shortest-arc quaternion blend with continuous helper quaternion signs',
            'modified_original_parents': parents_changed,
            'new_helpers': [o.name for o in layers.values()],
            'original_actions_modified': False, 'camera_data_or_lens_drivers_modified': False,
            'camera_identity_handoff_max_matrix_error': final_error}
