"""Independently reopen both scenes and prove this is only a bounded camera edit."""
import bpy, hashlib, importlib.util, json
from pathlib import Path

R = Path(__file__).resolve().parents[1]
cfg = json.loads((R / 'config.json').read_text())
source = (R / cfg['source']).resolve()
output = R / cfg['output']
spec = importlib.util.spec_from_file_location('preservation', R.parent / 'curvature-rework-v001/scripts/audit_preservation.py')
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)

def capture(path):
    bpy.ops.wm.open_mainfile(filepath=str(path))
    data = helper.snap()
    scene = bpy.context.scene
    cam = scene.camera
    # Cache references; repeated scene-name lookups are expensive in this scene.
    physical = {n: scene.objects[n] for n in ('A02_SHIP', 'A01_CONTAINER', 'A03_TRAILER', 'US_FRAME', 'CV_WH_US_FRAME')}
    cameras = {}
    for f in list(range(211)) + list(range(350, 990)):
        scene.frame_set(f)
        cameras[f] = [v for row in cam.matrix_world for v in row] + [cam.data.lens, cam.data.shift_x, cam.data.shift_y]
    positions = {}
    for f in (235, 255, 275, 295, 315, 335, 467, 500, 526, 550, 565, 600):
        scene.frame_set(f)
        positions[f] = {n: [v for row in o.matrix_world for v in row] for n, o in physical.items()}
    return data, cameras, positions

assert hashlib.sha256(source.read_bytes()).hexdigest() == cfg['source_sha256']
before, before_cam, before_objects = capture(source)
after, after_cam, after_objects = capture(output)
differences = {
    'protected_objects': [n for n,v in before['objects'].items() if n != 'CAM_MASTER' and after['objects'].get(n) != v],
    'source_actions': [n for n,v in before['actions'].items() if after['actions'].get(n) != v],
    'geometry': before['geometry'] != after['geometry'],
    'materials': before['materials'] != after['materials'],
    'physical_transforms': before_objects != after_objects,
}
for k in ('world', 'timeline', 'camera', 'view'):
    differences[k] = before[k] != after[k]
extra = sorted(after['objects'].keys() - before['objects'].keys())
max_error = max(abs(a-b) for f in before_cam for a,b in zip(before_cam[f], after_cam[f]))
report = {
    'source_sha256': cfg['source_sha256'],
    'output_sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
    'source_object_count': len(before['objects']),
    'extra_objects': extra,
    'differences': differences,
    'outside_camera_frames_checked': len(before_cam),
    'outside_camera_max_error': max_error,
    'fps': bpy.context.scene.render.fps,
    'frame_count': bpy.context.scene.frame_end - bpy.context.scene.frame_start + 1,
}
report['passed'] = not any(differences.values()) and extra == ['S3_SHIP_FOLLOW_CAMERA'] and max_error < 0.0001 and report['fps'] == 30 and report['frame_count'] == 990
(R / 'review/preservation.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2), flush=True)
assert report['passed']

