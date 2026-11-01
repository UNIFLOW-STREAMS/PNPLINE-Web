"""Independent camera contracts, dense motion measurements and scoped clearance.

Blender --background --factory-startup SOURCE --python verify_camera.py -- --baseline
Blender --background --factory-startup CANDIDATE --python verify_camera.py

The baseline cache and candidate report are tied to file hashes. No blend is saved.
Motion/roll/composition measurements are review evidence, not arbitrary quality gates.
"""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix, Quaternion, Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / 'review'
SOURCE = ROOT.parent / 'cn-port-layout-v001/master-cn-port-layout-v001.blend'
SOURCE_HASH = '053f302410863ce487a9fdbd0cf4b4c83dded3577c0a02e38ac7c0a6951f3174'
CACHE = REVIEW / 'source-camera-contract.json'
STEP = 0.125
END = 360
DENSE_END = 364
BOUNDARIES = [72, 96, 144, 156, 216, 252, 288, 360]
ACTOR_ROOTS = {'A02_SHIP', 'A01_CONTAINER', 'W01_NEW_PALLET', 'P01_SPREADER',
               'CR_SLEW_JIB', 'CR_TROLLEY_CARRIAGE', 'CR_SUSPENSION_HEAD'}


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def matrix_values(matrix):
    return [v for row in matrix for v in row]


def ease(t):
    t = min(1.0, max(0.0, t))
    return t * t * t * (10 + t * (-15 + 6 * t))


def beneath(obj, names):
    while obj:
        if obj.name in names:
            return True
        obj = obj.parent
    return False


def set_frame(scene, frame):
    whole = math.floor(frame)
    scene.frame_set(whole, subframe=frame - whole)


def action_fingerprints():
    result = {}
    for action in bpy.data.actions:
        bags = []
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    curves = []
                    for fc in bag.fcurves:
                        curves.append([fc.data_path, fc.array_index, fc.extrapolation,
                                       [[list(k.co), list(k.handle_left), list(k.handle_right),
                                         k.interpolation, k.handle_left_type, k.handle_right_type]
                                        for k in fc.keyframe_points]])
                    bags.append([bag.slot_handle, curves])
        result[action.name] = digest(bags)
    return result


def optics(camera):
    data = camera.data
    return [data.lens, data.shift_x, data.shift_y, data.ortho_scale,
            data.sensor_width, data.sensor_height, data.clip_start, data.clip_end,
            data.type, data.sensor_fit, data.dof.use_dof]


def scene_contract(scene):
    return {'frame_start': scene.frame_start, 'frame_end': scene.frame_end,
            'fps': scene.render.fps, 'fps_base': scene.render.fps_base,
            'markers': sorted([m.frame, m.name, m.camera.name if m.camera else None]
                              for m in scene.timeline_markers)}


def camera_row(scene, frame, layout_up):
    cam = scene.camera
    cm = cam.matrix_world.copy()
    target = scene.objects['CAM_LOOK_TARGET'].matrix_world.translation.copy()
    q = cm.to_quaternion().normalized()
    ship = scene.objects['A02_SHIP']
    source_ship_matrix = ship.matrix_world.copy()
    support = scene.objects.get('PORT_SHIP_WATERLINE_CORRECTION')
    if support and beneath(ship, {support.name}):
        source_ship_matrix = support.matrix_world.inverted() @ source_ship_matrix
    ship_up = (source_ship_matrix.to_3x3() @ Vector((0, 0, 1))).normalized()
    reference_up = layout_up.lerp(ship_up, ease((frame - 156) / 132)).normalized()
    right = q @ Vector((1, 0, 0))
    up = q @ Vector((0, 1, 0))
    horizontal = reference_up.dot(right)
    vertical = reference_up.dot(up)
    roll = math.degrees(math.atan2(horizontal, vertical))
    ship_center = ship.matrix_world @ Vector((0, 0, 2))
    screen = world_to_camera_view(scene, cam, ship_center)
    return {'frame': frame, 'eye': list(cm.translation), 'q': list(q),
            'target': list(target), 'roll_degrees': roll,
            'up_projection_length': math.hypot(horizontal, vertical),
            'ship_screen': list(screen)}


def percentile(values, percentile_value):
    if not values:
        return 0.0
    ordered = sorted(values)
    position = (len(ordered) - 1) * percentile_value / 100
    lo = math.floor(position)
    hi = math.ceil(position)
    return ordered[lo] * (hi - position) + ordered[hi] * (position - lo) if lo != hi else ordered[lo]


def statistics(values, frames):
    if not values:
        return {'max': 0, 'p95': 0, 'rms': 0, 'peak_frame': None}
    index = max(range(len(values)), key=values.__getitem__)
    return {'max': values[index], 'p95': percentile(values, 95),
            'rms': math.sqrt(sum(x*x for x in values) / len(values)),
            'peak_frame': frames[index]}


def vector_derivative(vectors, dt):
    return [(b-a) / dt for a, b in zip(vectors, vectors[1:])]


def motion_metrics(rows, fps):
    dt = STEP / fps
    positions = [Vector(row['eye']) for row in rows]
    targets = [Vector(row['target']) for row in rows]
    qs = [Quaternion(row['q']).normalized() for row in rows]
    raw_sign_changes = []
    angular_velocity = []
    angular_steps = []
    for index, (a, b) in enumerate(zip(qs, qs[1:])):
        if a.dot(b) < 0:
            raw_sign_changes.append(rows[index+1]['frame'])
            b = -b
        change = (b @ a.inverted()).normalized()
        if change.w < 0:
            change = -change
        vector_length = math.sqrt(change.x*change.x + change.y*change.y + change.z*change.z)
        angle = 2*math.atan2(vector_length, change.w)
        axis = Vector((change.x, change.y, change.z))/vector_length if vector_length > 1e-12 else Vector((0, 0, 0))
        angular_steps.append(math.degrees(abs(angle)))
        angular_velocity.append(axis * (math.degrees(angle) / dt))
    velocity = vector_derivative(positions, dt)
    acceleration = vector_derivative(velocity, dt)
    jerk = vector_derivative(acceleration, dt)
    target_velocity = vector_derivative(targets, dt)
    angular_acceleration = vector_derivative(angular_velocity, dt)
    angular_jerk = vector_derivative(angular_acceleration, dt)
    arrays = {
        'eye_speed_m_per_s': (velocity, 1),
        'eye_acceleration_m_per_s2': (acceleration, 2),
        'eye_jerk_m_per_s3': (jerk, 3),
        'target_speed_m_per_s': (target_velocity, 1),
        'angular_speed_deg_per_s': (angular_velocity, 1),
        'angular_acceleration_deg_per_s2': (angular_acceleration, 2),
        'angular_jerk_deg_per_s3': (angular_jerk, 3),
    }
    magnitude = {name: ([v.length for v in vs], [r['frame'] for r in rows[skip:]])
                 for name, (vs, skip) in arrays.items()}
    summary = {name: statistics(values, frames) for name, (values, frames) in magnitude.items()}
    segments = {}
    for start, end in [(0, 72), (72, 144), (144, 156), (156, 216), (216, 288), (288, 360)]:
        key = f'{start}-{end}'
        segments[key] = {}
        for name, (values, frames) in magnitude.items():
            selected = [(v, f) for v, f in zip(values, frames) if start <= f <= end]
            segments[key][name] = statistics([v for v, f in selected], [f for v, f in selected])
    boundary = {}
    for center in BOUNDARIES:
        boundary[str(center)] = {}
        for name, (values, frames) in magnitude.items():
            selected = [(v, f) for v, f in zip(values, frames) if center-2 <= f <= center+2]
            boundary[str(center)][name] = statistics([v for v, f in selected], [f for v, f in selected])
    horizon = {}
    for start, end in [(0, 72), (72, 156), (156, 288), (288, 360)]:
        rs = [r for r in rows if start <= r['frame'] <= end]
        horizon[f'{start}-{end}'] = statistics([abs(r['roll_degrees']) for r in rs], [r['frame'] for r in rs])
        horizon[f'{start}-{end}']['minimum_reference_up_projection'] = min(r['up_projection_length'] for r in rs)
    tracking = [r for r in rows if 216 <= r['frame'] <= 360]
    result = {'sampling_frames': [0, DENSE_END], 'step_frames': STEP,
              'units': 'seconds use the saved scene fps; angular differences use shortest quaternion arcs',
              'summary': summary, 'segments': segments, 'boundary_neighborhoods_plus_minus_2_frames': boundary,
              'horizon_roll_relative_to_CN_then_ship_up': horizon,
              'quaternion_raw_sign_change_frames': raw_sign_changes,
              'maximum_shortest_rotation_step_degrees': max(angular_steps),
              'maximum_shortest_rotation_step_frame': rows[angular_steps.index(max(angular_steps))+1]['frame'],
              'ship_tracking_216_360': {
                  'behind_camera_frames': [r['frame'] for r in tracking if r['ship_screen'][2] <= 0],
                  'center_outside_image_frames': [r['frame'] for r in tracking if not (0 <= r['ship_screen'][0] <= 1 and 0 <= r['ship_screen'][1] <= 1)],
                  'center_bounds_xy': [[min(r['ship_screen'][i] for r in tracking), max(r['ship_screen'][i] for r in tracking)] for i in [0, 1]],
              }}
    return result


def snapshot_source():
    scene = bpy.context.scene
    scene.frame_set(0)
    layout_up = (scene.objects['SF_CN_LAYOUT'].matrix_world.to_3x3() @ Vector((0, 0, 1))).normalized()
    allowed = {scene.camera.animation_data.action.name,
               scene.camera.data.animation_data.action.name,
               scene.objects['CAM_LOOK_TARGET'].animation_data.action.name}
    integer = []
    for frame in range(scene.frame_start, scene.frame_end + 1):
        scene.frame_set(frame)
        integer.append({'frame': frame, 'camera': matrix_values(scene.camera.matrix_world),
                        'target': matrix_values(scene.objects['CAM_LOOK_TARGET'].matrix_world),
                        'optics': optics(scene.camera)})
    dense = []
    for tick in range(DENSE_END*8+1):
        frame = tick / 8
        set_frame(scene, frame)
        dense.append(camera_row(scene, frame, layout_up))
        if tick % 720 == 0:
            print('BASELINE_DENSE', frame, flush=True)
    scene.frame_set(0)
    dw = scene.objects['SF_CN_LAYOUT'].matrix_world.to_3x3() @ Vector((14, -13.5, 0))
    return {'source': str(SOURCE), 'sha256': SOURCE_HASH,
            'scene_contract': scene_contract(scene), 'actions': action_fingerprints(),
            'allowed_camera_action_names': sorted(allowed), 'S1_translation_world': list(dw),
            'integer': integer, 'dense': dense,
            'metrics': motion_metrics(dense, scene.render.fps / scene.render.fps_base)}


class GeometryTree:
    def __init__(self, objects, dynamic=False):
        self.objects = objects
        self.geometry = []
        depsgraph = bpy.context.evaluated_depsgraph_get()
        for obj in objects:
            evaluated = obj.evaluated_get(depsgraph)
            mesh = evaluated.to_mesh()
            vs = [v.co.copy() for v in mesh.vertices]
            lo = [min(v[i] for v in vs) for i in range(3)] if vs else [0]*3
            hi = [max(v[i] for v in vs) for i in range(3)] if vs else [0]*3
            corners = [Vector((x, y, z)) for x in [lo[0], hi[0]]
                       for y in [lo[1], hi[1]] for z in [lo[2], hi[2]]]
            self.geometry.append((obj, vs, [tuple(p.vertices) for p in mesh.polygons], corners))
            evaluated.to_mesh_clear()
        self.tree = None
        self.names = []
        self.update()

    def update(self, query_bounds=None, nearest_point=None, nearest_limit=float('inf')):
        vertices = []
        polygons = []
        names = []
        for obj, local_vertices, local_polygons, corners in self.geometry:
            if obj.hide_render:
                continue
            matrix = obj.matrix_world
            if query_bounds is not None:
                world_corners = [matrix @ p for p in corners]
                lo = [min(p[i] for p in world_corners) for i in range(3)]
                hi = [max(p[i] for p in world_corners) for i in range(3)]
                overlap = all(hi[i]+1e-5 >= query_bounds[0][i] and lo[i]-1e-5 <= query_bounds[1][i]
                              for i in range(3))
                lower_bound = math.sqrt(sum(max(lo[i]-nearest_point[i], nearest_point[i]-hi[i], 0)**2
                                            for i in range(3)))
                if not overlap and lower_bound > nearest_limit+1e-4:
                    continue
            offset = len(vertices)
            vertices.extend(matrix @ v for v in local_vertices)
            polygons.extend(tuple(offset+i for i in p) for p in local_polygons)
            names.extend([obj.name] * len(local_polygons))
        self.tree = BVHTree.FromPolygons(vertices, polygons) if polygons else None
        self.names = names

    def ray(self, a, b):
        delta = b-a
        distance = delta.length
        if not self.tree or distance < 1e-8:
            return None
        hit, normal, index, length = self.tree.ray_cast(a, delta/distance, distance)
        return self.names[index] if hit is not None else None

    def nearest(self, point):
        if not self.tree:
            return None
        location, normal, index, distance = self.tree.find_nearest(point)
        if location is None:
            return None
        return self.names[index], distance


def geometry_scope(scene):
    dynamic = []
    static = []
    for obj in scene.objects:
        if obj.type != 'MESH':
            continue
        if any(token in obj.name.upper() for token in ['WATER', 'OCEAN', 'WAVE', 'CAMERA_PATH', 'ROUTE_GUIDE']):
            continue
        if beneath(obj, ACTOR_ROOTS) or obj.name.startswith('CR_WORKING_CABLE'):
            dynamic.append(obj)
        elif not obj.hide_render and (beneath(obj, {'CN_FRAME', 'PORT_MODEL_ROOT'}) or obj.name == 'CN_QUAY'):
            static.append(obj)
    return static, dynamic


def projected_group(scene, objects):
    points = []
    for obj in objects:
        for corner in obj.bound_box:
            points.append(world_to_camera_view(scene, scene.camera, obj.matrix_world @ Vector(corner)))
    front = [p for p in points if p.z > 0]
    if not points:
        return {'object_count': 0}
    bounds = [[min(p[i] for p in front), max(p[i] for p in front)] for i in [0, 1]] if front else None
    return {'object_count': len(objects), 'point_count': len(points),
            'behind_point_count': len(points)-len(front), 'bounds_xy': bounds,
            'all_bounding_corners_in_frame': all(p.z > 0 and 0 <= p.x <= 1 and 0 <= p.y <= 1 for p in points)}


def candidate_report(baseline):
    scene = bpy.context.scene
    candidate = Path(bpy.data.filepath)
    candidate_hash = file_hash(candidate)
    scene.frame_set(0)
    layout_up = (scene.objects['SF_CN_LAYOUT'].matrix_world.to_3x3() @ Vector((0, 0, 1))).normalized()
    now_actions = action_fingerprints()
    changed_actions = [name for name, value in baseline['actions'].items() if now_actions.get(name) != value]
    forbidden_actions = sorted(set(changed_actions)-set(baseline['allowed_camera_action_names']))
    integer_error = {'camera_360plus_max': 0.0, 'target_360plus_max': 0.0, 'camera_S1_translation_max': 0.0, 'target_S1_translation_max': 0.0}
    exact_camera = True
    exact_target = True
    optics_differences = []
    dw = baseline['S1_translation_world']
    for row in baseline['integer']:
        frame = row['frame']
        scene.frame_set(frame)
        camera = matrix_values(scene.camera.matrix_world)
        target = matrix_values(scene.objects['CAM_LOOK_TARGET'].matrix_world)
        if optics(scene.camera) != row['optics']:
            optics_differences.append(frame)
        if frame >= 360:
            exact_camera &= camera == row['camera']
            exact_target &= target == row['target']
            integer_error['camera_360plus_max'] = max(integer_error['camera_360plus_max'], max(abs(a-b) for a,b in zip(camera,row['camera'])))
            integer_error['target_360plus_max'] = max(integer_error['target_360plus_max'], max(abs(a-b) for a,b in zip(target,row['target'])))
        if frame <= 72:
            for key, values in [('camera', camera), ('target', target)]:
                expected = row[key].copy()
                for index in range(3):
                    expected[index*4+3] += dw[index]
                name = key+'_S1_translation_max'
                integer_error[name] = max(integer_error[name], max(abs(a-b) for a,b in zip(values,expected)))
    scene.frame_set(0)
    static_objects, dynamic_objects = geometry_scope(scene)
    print('GEOMETRY_SCOPE', len(static_objects), len(dynamic_objects), flush=True)
    static = GeometryTree(static_objects)
    moving = GeometryTree(dynamic_objects, dynamic=True)
    dense = []
    crossings = {}
    nearest = {'static': [float('inf'), None, None], 'moving': [float('inf'), None, None]}
    previous_eye = None
    max_s1_dense_eye = 0.0
    max_s1_dense_target = 0.0
    max_s1_dense_angle = 0.0
    framing = {}
    for tick in range(DENSE_END*8+1):
        frame = tick/8
        set_frame(scene, frame)
        row = camera_row(scene, frame, layout_up)
        dense.append(row)
        camera = scene.camera
        eye = camera.matrix_world.translation.copy()
        near_corners = []
        for corner in camera.data.view_frame(scene=scene):
            local = corner * (camera.data.clip_start / abs(corner.z))
            near_corners.append(camera.matrix_world @ local)
        rays = [('near_center', eye, sum(near_corners, Vector())/4)]
        rays.extend(('near_corner', eye, corner) for corner in near_corners)
        if previous_eye is not None:
            rays.append(('swept_eye', previous_eye, eye))
        ray_points = [p for kind, a, b in rays for p in [a, b]]
        query_bounds = ([min(p[i] for p in ray_points) for i in range(3)],
                        [max(p[i] for p in ray_points) for i in range(3)])
        moving.update(query_bounds, eye, nearest['moving'][0])
        previous_eye = eye
        for label, tree in [('static', static), ('moving', moving)]:
            for kind, a, b in rays:
                name = tree.ray(a, b)
                if name:
                    key = label+' | '+kind+' | '+name
                    crossings.setdefault(key, []).append(frame)
            near = tree.nearest(eye)
            if near and near[1] < nearest[label][0]:
                nearest[label] = [near[1], frame, near[0]]
        if frame <= 72:
            old = baseline['dense'][tick]
            expected_eye = Vector(old['eye']) + Vector(dw)
            expected_target = Vector(old['target']) + Vector(dw)
            max_s1_dense_eye = max(max_s1_dense_eye, (Vector(row['eye'])-expected_eye).length)
            max_s1_dense_target = max(max_s1_dense_target, (Vector(row['target'])-expected_target).length)
            qa, qb = Quaternion(row['q']), Quaternion(old['q'])
            dot = sum(a*b for a,b in zip(qa,qb))
            norm = math.sqrt(sum(a*a for a in qa)*sum(b*b for b in qb))
            max_s1_dense_angle = max(max_s1_dense_angle, 2*math.acos(min(1, abs(dot)/norm)))
        if frame in {144, 156, 180}:
            visible = [o for o in scene.objects if o.type == 'MESH' and not o.hide_render]
            framing[str(int(frame))] = {
                'title': projected_group(scene, [o for o in visible if o.name.startswith(('SF_CHINA_GOLD_', 'SF_CHINA_RED_'))]),
                'terminal': projected_group(scene, [o for o in visible if beneath(o, {'PORT_MODEL_ROOT'})]),
                'working_crane': projected_group(scene, [o for o in visible if beneath(o, {'PORT_CRANE_PLACEMENT', 'PORT_HOIST_PLACEMENT'})]),
                'ship': projected_group(scene, [o for o in visible if beneath(o, {'A02_SHIP'})]),
            }
        if tick % 480 == 0:
            print('CAMERA_DENSE', frame, 'collision_pairs', len(crossings), flush=True)
    metrics = motion_metrics(dense, scene.render.fps/scene.render.fps_base)
    for key, value in metrics['summary'].items():
        old = baseline['metrics']['summary'][key]
        value['source_max'] = old['max']
        value['source_p95'] = old['p95']
        value['max_ratio_to_source'] = value['max']/old['max'] if old['max'] > 1e-12 else None
    checks = {
        'all_source_actions_exact': not changed_actions,
        'non_camera_source_actions_exact': not forbidden_actions,
        'camera_all_frames_f360plus_exact': exact_camera,
        'target_all_frames_f360plus_exact': exact_target,
        'optics_all_integer_frames_exact': not optics_differences,
        'S1_integer_camera_target_rigid_translation_error_under_1e_minus_4': max(integer_error['camera_S1_translation_max'], integer_error['target_S1_translation_max']) < 1e-4,
        'S1_dense_camera_target_translation_error_under_1e_minus_4': max(max_s1_dense_eye, max_s1_dense_target) < 1e-4,
        'S1_dense_orientation_preserved': max_s1_dense_angle < 1e-4,
        'timeline_and_markers_preserved': scene_contract(scene) == baseline['scene_contract'],
    }
    report = {
        'file': str(candidate), 'sha256': candidate_hash, 'source_sha256': SOURCE_HASH,
        'contract_checks': checks, 'contracts_pass': all(checks.values()),
        'source_actions_changed': changed_actions, 'forbidden_actions_changed': forbidden_actions,
        'matrix_errors': integer_error,
        'S1_dense_errors': {'eye_position_m': max_s1_dense_eye, 'target_position_m': max_s1_dense_target,
                            'orientation_radians': max_s1_dense_angle},
        'optics_difference_frames': optics_differences,
        'motion_metrics': metrics,
        'geometry': {
            'static_mesh_count': len(static_objects), 'moving_mesh_count': len(dynamic_objects),
            'sample_count': len(dense), 'step_frames': STEP,
            'swept_eye_and_near_plane_rays_clear': not crossings,
            'crossings': {key: sorted(set(frames)) for key, frames in crossings.items()},
            'minimum_eye_surface_distance': nearest,
            'method': 'Triangle BVH: swept eye segments, eye-to-near-plane center/corners at every eighth frame. Static China solids and transformed China crane/ship/cargo meshes; evaluated mesh shape at frame0. Moving-object world AABBs conservatively reduce ray/closest-distance candidates.',
            'limits': 'Water/waves, global globe outside China, hidden objects and curve-only geometry are excluded. This is a finite sampled surface-crossing check, not a swept volume proof or arbitrary safety-radius gate.',
        },
        'composition': framing,
        'review_policy': 'Motion, acceleration, jerk, horizon roll and frame composition have measurements and source comparisons; they do not receive invented pass thresholds. Review these with rendered continuity footage. Raw quaternion sign changes are reported separately from shortest physical rotation.',
        'quality_review_needed': True,
    }
    assert file_hash(candidate) == candidate_hash, 'Candidate changed during verification'
    return report, dense


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--baseline', action='store_true')
    parser.add_argument('--extend-baseline', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    REVIEW.mkdir(parents=True, exist_ok=True)
    assert file_hash(SOURCE) == SOURCE_HASH, 'Unexpected source revision'
    candidate_path = Path(bpy.data.filepath)
    if args.extend_baseline:
        assert candidate_path.resolve() == SOURCE.resolve(), 'Baseline extension must load the source'
        snapshot = json.loads(CACHE.read_text(encoding='utf-8'))
        assert snapshot['sha256'] == SOURCE_HASH
        scene = bpy.context.scene
        scene.frame_set(0)
        layout_up = (scene.objects['SF_CN_LAYOUT'].matrix_world.to_3x3() @ Vector((0, 0, 1))).normalized()
        next_tick = round(snapshot['dense'][-1]['frame']*8)+1
        for tick in range(next_tick, DENSE_END*8+1):
            frame = tick/8
            set_frame(scene, frame)
            snapshot['dense'].append(camera_row(scene, frame, layout_up))
        snapshot['metrics'] = motion_metrics(snapshot['dense'], scene.render.fps/scene.render.fps_base)
        CACHE.write_text(json.dumps(snapshot, indent=2), encoding='utf-8')
        (REVIEW/'source-camera-metrics.json').write_text(json.dumps({'sha256': SOURCE_HASH, **snapshot['metrics']}, indent=2), encoding='utf-8')
        print('BASELINE_EXTENDED', snapshot['dense'][-1]['frame'])
        return
    if args.baseline:
        assert candidate_path.resolve() == SOURCE.resolve(), 'Baseline must load the source explicitly'
        snapshot = snapshot_source()
        CACHE.write_text(json.dumps(snapshot, indent=2), encoding='utf-8')
        (REVIEW/'source-camera-metrics.json').write_text(json.dumps({'sha256': SOURCE_HASH, **snapshot['metrics']}, indent=2), encoding='utf-8')
        assert file_hash(SOURCE) == SOURCE_HASH
        print('BASELINE_READY', CACHE)
        return
    assert candidate_path.resolve() != SOURCE.resolve(), 'Use --baseline for source measurements'
    baseline = json.loads(CACHE.read_text(encoding='utf-8'))
    assert baseline['sha256'] == SOURCE_HASH
    assert baseline['dense'][-1]['frame'] >= DENSE_END, 'Extend baseline through handoff-right neighborhood'
    report, dense = candidate_report(baseline)
    (REVIEW/'camera-verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    (REVIEW/'camera-dense-samples.json').write_text(json.dumps({'sha256': report['sha256'], 'rows': dense}, indent=2), encoding='utf-8')
    print('CAMERA_CONTRACTS', json.dumps(report['contract_checks']))
    print('CAMERA_GEOMETRY_CLEAR', report['geometry']['swept_eye_and_near_plane_rays_clear'])
    print('CAMERA_REVIEW_METRICS_READY', report['sha256'])
    assert report['contracts_pass'], 'Camera preservation contract failed; see camera-verification.json'


if __name__ == '__main__':
    main()
