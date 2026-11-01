"""Read-only camera/shot survey of the harbor source; never save the blend."""
import bpy
import hashlib
import json
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
scene = bpy.context.scene
source = Path(bpy.data.filepath)
sha = hashlib.sha256(source.read_bytes()).hexdigest()
scene.frame_set(0)
layout = scene.objects['SF_CN_LAYOUT'].matrix_world.copy()
inverse = layout.inverted()

def curves(action, slot_handle):
    return [fc for layer in action.layers for strip in layer.strips
            for bag in strip.channelbags if bag.slot_handle == slot_handle for fc in bag.fcurves]

def action_summary(animation):
    if not animation or not animation.action:
        return None
    action = animation.action
    slot_handle = animation.action_slot.handle
    result = []
    for fc in curves(action, slot_handle):
        keys = fc.keyframe_points
        result.append({'path': fc.data_path, 'index': fc.array_index,
                       'count': len(keys), 'range': [keys[0].co.x, keys[-1].co.x] if keys else [],
                       'keys': [[*k.co, k.interpolation] for k in keys] if len(keys) < 90 else [],
                       'extrapolation': fc.extrapolation})
    return {'name': action.name, 'slot_handle': slot_handle,
            'slot_identifier': animation.action_slot.identifier, 'curves': result}

def constraints(obj):
    result = []
    for c in obj.constraints:
        d = {'name': c.name, 'type': c.type, 'influence': c.influence, 'mute': c.mute}
        for attr in ['target', 'track_axis', 'up_axis', 'use_target_z', 'owner_space', 'target_space']:
            if hasattr(c, attr):
                value = getattr(c, attr)
                d[attr] = value.name if hasattr(value, 'name') else value
        result.append(d)
    return result

names = [o.name for o in scene.objects if o.type == 'CAMERA' or o.name.startswith(('CAM_', 'S2_CAMERA', 'S3_CAMERA', 'S4_CAMERA'))]
for name in list(names):
    obj = scene.objects[name].parent
    while obj:
        if obj.name not in names:
            names.append(obj.name)
        obj = obj.parent
objects = {}
for name in names:
    obj = scene.objects[name]
    objects[name] = {'type': obj.type, 'parent': obj.parent.name if obj.parent else None,
                     'rotation_mode': obj.rotation_mode,
                     'constraints': constraints(obj),
                     'action': action_summary(obj.animation_data),
                     'basis': [list(r) for r in obj.matrix_basis],
                     'world': [list(r) for r in obj.matrix_world]}
    if obj.type == 'CAMERA':
        data = obj.data
        objects[name]['optics'] = {k: getattr(data, k) for k in ['type', 'lens', 'sensor_fit', 'sensor_width', 'sensor_height', 'shift_x', 'shift_y', 'clip_start', 'clip_end']}
        objects[name]['data_action'] = action_summary(data.animation_data)

samples = []
for frame in range(scene.frame_start, scene.frame_end + 1):
    scene.frame_set(frame)
    camera = scene.camera
    world = camera.matrix_world.copy()
    local = inverse @ world
    target = scene.objects.get('CAM_LOOK_TARGET')
    ship = scene.objects['A02_SHIP']
    samples.append({'frame': frame, 'position': list(world.translation),
                    'rotation': list(world.to_quaternion()),
                    'cn_position': list(local.translation),
                    'cn_forward': list((local.to_3x3() @ Vector((0, 0, -1))).normalized()),
                    'cn_up': list((local.to_3x3() @ Vector((0, 1, 0))).normalized()),
                    'target': list(target.matrix_world.translation) if target else None,
                    'cn_target': list(inverse @ target.matrix_world.translation) if target else None,
                    'ship': list(ship.matrix_world.translation),
                    'cn_ship': list(inverse @ ship.matrix_world.translation),
                    'ship_up': list((ship.matrix_world.to_3x3() @ Vector((0, 0, 1))).normalized()),
                    'lens': camera.data.lens,
                    'shift': [camera.data.shift_x, camera.data.shift_y]})

result = {'source': str(source), 'sha256': sha,
          'frame_range': [scene.frame_start, scene.frame_end],
          'fps': scene.render.fps, 'fps_base': scene.render.fps_base,
          'active_camera': scene.camera.name,
          'markers': [{'name': m.name, 'frame': m.frame, 'camera': m.camera.name if m.camera else None} for m in scene.timeline_markers],
          'scene_properties': {k: str(scene[k]) for k in scene.keys()},
          'layout_world': [list(r) for r in layout],
          'layout_up_world': list((layout.to_3x3() @ Vector((0, 0, 1))).normalized()),
          'camera_objects': objects, 'samples': samples}
(ROOT / 'review').mkdir(parents=True, exist_ok=True)
(ROOT / 'review/source-camera.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
assert hashlib.sha256(source.read_bytes()).hexdigest() == sha
print('SOURCE_CAMERA_SURVEY', json.dumps({k: result[k] for k in ['sha256', 'frame_range', 'fps', 'active_camera', 'markers', 'layout_up_world']}))
