"""Read-only matched-semantic-time animation/rig survey for CN/US integration."""
import bpy
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT/'review'
sys.path.insert(0, str(ROOT.parent/'pacing-33s-v001/scripts'))
from timing import TimeMap, CONFIG

LABEL = sys.argv[sys.argv.index('--')+1]
assert LABEL in {'cn', 'us'}
FILE = Path(bpy.data.filepath)
EXPECTED = {'cn': '19f68c0ccc16c18693df685b47d632d98dd1289cb4f19f744f11e1507e7e0864',
            'us': '3d011d3191df487a44bd96ddce803a436a5ca3f891f91b512550c52f91f001c8'}
sha = hashlib.sha256(FILE.read_bytes()).hexdigest()
assert sha == EXPECTED[LABEL], (LABEL, sha)
clock = TimeMap()
scene = bpy.context.scene
scene.frame_set(0)

def action_data(ad):
    if not ad or not ad.action:
        return None
    action = ad.action
    handle = ad.action_slot.handle
    data = []
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                if bag.slot_handle != handle:
                    continue
                for fc in bag.fcurves:
                    keys = [[*k.co, k.interpolation] for k in fc.keyframe_points]
                    data.append({'path': fc.data_path, 'index': fc.array_index,
                                 'count': len(keys), 'range': [keys[0][0], keys[-1][0]] if keys else [],
                                 'sha256': hashlib.sha256(json.dumps(keys).encode()).hexdigest(),
                                 'extrapolation': fc.extrapolation,
                                 'modifiers': [m.type for m in fc.modifiers]})
    return {'name': action.name, 'slot_handle': handle,
            'slot_identifier': ad.action_slot.identifier, 'curves': data,
            'nla_count': len(ad.nla_tracks)}

def matrix(matrix):
    return [list(row) for row in matrix]

names = {o.name for o in scene.objects if o.animation_data and (o.animation_data.action or o.animation_data.drivers)}
names.update(o.name for o in scene.objects if o.type == 'CAMERA' or o.name in {
    'CN_FRAME', 'SF_CN_LAYOUT', 'US_FRAME', 'CV_WH_US_FRAME', 'WH_FRAME', 'EARTH',
    'A02_SHIP', 'A01_CONTAINER', 'W01_NEW_PALLET', 'P01_SPREADER', 'CAM_LOOK_TARGET',
    'CR_COMPACT_GANTRY', 'CR_SLEW_JIB', 'CR_TROLLEY_CARRIAGE', 'CR_SUSPENSION_HEAD',
    'PORT_CRANE_PLACEMENT', 'PORT_HOIST_PLACEMENT', 'PORT_BERTH_PLACEMENT',
    'PORT_SHIP_WATERLINE_CORRECTION', 'PORT_CAMERA_RETARGET', 'PORT_CAMERA_TARGET_RETARGET'})
for name in list(names):
    parent = scene.objects[name].parent
    while parent:
        names.add(parent.name)
        parent = parent.parent
objects = {}
for name in sorted(names):
    o = scene.objects[name]
    objects[name] = {'type': o.type, 'parent': o.parent.name if o.parent else None,
                     'action': action_data(o.animation_data),
                     'constraints': [{'type': c.type, 'name': c.name,
                                      'target': c.target.name if hasattr(c, 'target') and c.target else None,
                                      'influence': c.influence, 'mute': c.mute} for c in o.constraints],
                     'matrix_parent_inverse': matrix(o.matrix_parent_inverse),
                     'drivers': [{'path': fc.data_path, 'index': fc.array_index,
                                  'expression': fc.driver.expression} for fc in o.animation_data.drivers] if o.animation_data else []}

source_frames = sorted(set([0, 36, 72, 84, 88, 96, 100, 138, 144, 145, 156, 170, 180,
                           192, 216, 228, 240, 252, 264, 276, 288, 300, 320, 340, 360,
                           400, 408, 440, 456, 480, 500, 510, 532, 555, 599, 632, 648,
                           672, 810, 811, 842, 849, 890, 900, 948, 966, 1020, 1090,
                           1158, 1200, 1261, 1392] +
                          [clock.source(f) for f in [165, 190, 200, 210, 220, 230, 235, 243, 250, 260, 274.5, 300, 315, 330, 350, 366, 440, 465, 620]]))
samples = []
for source_frame in source_frames:
    output_frame = clock.output(source_frame)
    frame = source_frame if LABEL == 'cn' else output_frame
    scene.frame_set(int(frame), subframe=frame % 1)
    samples.append({'cn_frame': source_frame, 'us_frame': output_frame, 'evaluated_frame': frame,
                    'camera': matrix(scene.camera.matrix_world),
                    'lens': scene.camera.data.lens,
                    'shift': [scene.camera.data.shift_x, scene.camera.data.shift_y],
                    'objects': {n: {'world': matrix(scene.objects[n].matrix_world),
                                    'hide_render': scene.objects[n].hide_render} for n in sorted(names)}})

result = {'label': LABEL, 'file': str(FILE), 'sha256': sha,
          'timeline': {'start': scene.frame_start, 'end': scene.frame_end,
                       'fps': scene.render.fps, 'fps_base': scene.render.fps_base,
                       'markers': [[m.name, m.frame] for m in scene.timeline_markers]},
          'objects': objects, 'camera_data_action': action_data(scene.camera.data.animation_data),
          'camera_data_drivers': [{'path': fc.data_path, 'index': fc.array_index,
                                  'expression': fc.driver.expression,
                                  'targets': [[t.id.name if t.id else None, t.data_path] for v in fc.driver.variables for t in v.targets]}
                                 for fc in scene.camera.data.animation_data.drivers] if scene.camera.data.animation_data else [],
          'samples': samples,
          'mapping': {'script': str(ROOT.parent/'pacing-33s-v001/scripts/timing.py'),
                      'sections': CONFIG['sections'], 'anchors': CONFIG['anchors'],
                      'camera_overlap': [{'output_frame': f, 'cn_frame': clock.source(f)}
                                         for f in [165, 190, 200, 210, 220, 230, 235, 243, 250, 260, 274.5, 315, 330, 350, 366]],
                      'cn_camera_keyframes': [{'cn_frame': f, 'output_frame': clock.output(f)}
                                              for f in [0, 72, 84, 96, 144, 145, 156, 180, 216, 252, 276, 288, 300, 320, 340, 360, 408, 456]]}}
REVIEW.mkdir(parents=True, exist_ok=True)
(REVIEW/f'animation-source-{LABEL}.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
assert hashlib.sha256(FILE.read_bytes()).hexdigest() == sha
print('ANIMATION_SOURCE', LABEL, len(objects), len(samples), result['timeline'], flush=True)
