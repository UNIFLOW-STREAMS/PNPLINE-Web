"""Measure the new shot and ensure the unedited projection/lens is preserved."""
import bpy, json, math, hashlib
from pathlib import Path
from mathutils import Vector
R = Path(__file__).resolve().parents[1]
candidate = Path(bpy.data.filepath)
s = bpy.context.scene
c = s.camera

def projection_snapshot():
    action = c.data.animation_data.action
    keys = [(fc.data_path, fc.array_index, [(list(k.co), list(k.handle_left), list(k.handle_right), k.interpolation) for k in fc.keyframe_points]) for layer in action.layers for strip in layer.strips for bag in strip.channelbags for fc in bag.fcurves]
    outside = {}
    for f in [0, 408, 439, 439.5, 440, 648, 648.5, 649, 672, 900, 1392]:
        s.frame_set(int(f), subframe=f % 1)
        outside[f] = (c.data.lens, c.data.shift_x, c.data.shift_y)
    return keys, outside

after = projection_snapshot()
side_angles = {}
for f in [500, 504]:
    s.frame_set(f)
    p = s.objects['A02_SHIP'].matrix_world.inverted() @ c.matrix_world.translation
    side_angles[f] = math.degrees(math.atan2(abs(p.x), abs(p.y)))
segments = []
for start, end in [(440, 500), (504, 596), (596, 648)]:
    points = []
    for f in range(start, end + 1):
        s.frame_set(f)
        points.append(c.matrix_world.translation.copy())
    length = sum((b-a).length for a,b in zip(points, points[1:]))
    chord = (points[-1]-points[0]).length
    segments.append({'frames': [start, end], 'length': length, 'chord': chord, 'ratio': length/chord})
turns = []; pitch = []; roll = []; previous = None
for half in range(878, 1301):
    f = half/2
    s.frame_set(int(f), subframe=f % 1)
    q = c.matrix_world.to_quaternion()
    if previous is not None:
        angle = math.degrees(previous.rotation_difference(q).angle)
        turns.append((min(angle, 360-angle)*2, f))
    previous = q
    if 440 <= f <= 504:
        front = q @ Vector((0,0,-1)); right = q @ Vector((1,0,0))
        lr = front.cross(Vector((0,0,1))).normalized(); lu = lr.cross(front).normalized()
        pitch.append(math.degrees(math.asin(max(-1, min(1, front.z)))))
        roll.append(math.degrees(math.atan2(right.dot(lu), right.dot(lr))))
result = {'candidate_sha256': hashlib.sha256(candidate.read_bytes()).hexdigest(),
          'ship_broadside_error_degrees': side_angles, 'straight_segments': segments,
          'max_rotation_degrees_per_frame_half_frame_sampled': max(turns),
          'entry_pitch_span_degrees': max(pitch)-min(pitch),
          'entry_roll_span_degrees': max(roll)-min(roll)}
bpy.ops.wm.open_mainfile(filepath=str(R.parent/'curvature-rework-v001/candidate-curvature-v004.blend'))
s = bpy.context.scene; c = s.camera
before = projection_snapshot()
result['focal_length_action_unchanged'] = after[0] == before[0]
result['max_projection_error_outside_window'] = max(abs(a-b) for f in before[1] for a,b in zip(after[1][f], before[1][f]))
(R/'review'/f'{candidate.stem}-side-audit.json').write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
assert result['focal_length_action_unchanged']
assert result['max_projection_error_outside_window'] < 1e-6
assert result['entry_pitch_span_degrees'] < .02 and result['entry_roll_span_degrees'] < .02
assert max(turns)[0] < 2
