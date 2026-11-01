"""Render disposable layout/hoist review cameras without saving the source blend.

Blender --background --factory-startup FILE --python render_review.py -- before|after [stills|motion|all]
"""
import bpy
import hashlib
import json
import sys
import time
from pathlib import Path
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[1]
args = sys.argv[sys.argv.index('--') + 1:]
label = args[0]
mode = args[1] if len(args) > 1 else 'all'
assert label in {'before', 'after'}
source = Path(bpy.data.filepath)
source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
scene = bpy.context.scene
original_camera = scene.camera
scene.frame_set(0)
layout = scene.objects['SF_CN_LAYOUT'].matrix_world.copy()
camera = bpy.data.objects.new('TEMP_PORT_REVIEW_CAMERA', original_camera.data.copy())
scene.collection.objects.link(camera)
scene.camera = camera
camera.data.dof.use_dof = False
camera.data.clip_end = 5000
scene.render.engine = 'BLENDER_WORKBENCH'
shading = scene.display.shading
shading.light = 'STUDIO'
shading.color_type = 'MATERIAL'
shading.show_shadows = True
shading.show_cavity = True
shading.cavity_type = 'BOTH'
shading.show_specular_highlight = True
shading.background_type = 'WORLD'
scene.render.resolution_percentage = 100
scene.render.use_border = False
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'
scene.render.fps = 12
scene.render.fps_base = 1
outputs = []
started = time.time()

def still(name, position, target, scale, resolution=(1600, 1000)):
    scene.frame_set(0)
    position, target = Vector(position), Vector(target)
    camera.matrix_world = layout @ Matrix.LocRotScale(
        position, (target - position).to_track_quat('-Z', 'Y'), Vector((1, 1, 1)))
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = scale
    camera.data.shift_x = 0
    camera.data.shift_y = 0
    scene.render.resolution_x, scene.render.resolution_y = resolution
    path = ROOT / 'review' / f'{label}-{name}.png'
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    outputs.append(str(path.relative_to(ROOT)))

if mode == 'fit':
    assert label == 'after', 'Fit comparison cameras from the final candidate only'
    inverse = layout.inverted()

    def beneath(obj, names):
        while obj:
            if obj.name in names:
                return True
            obj = obj.parent
        return False

    def points(objects):
        result = []
        for obj in objects:
            if obj.type not in {'MESH', 'CURVE', 'FONT'} or obj.hide_render:
                continue
            if 'WAVE' in obj.name.upper():
                continue
            ps = [inverse @ obj.matrix_world @ Vector(v) for v in obj.bound_box]
            if max(p.x for p in ps) - min(p.x for p in ps) > 90:
                continue
            result.extend(ps)
        return result

    full = points(o for o in scene.objects if beneath(o, {'SF_CN_LAYOUT', 'A02_SHIP', 'A01_CONTAINER', 'P01_SPREADER'}))
    port = points(o for o in scene.objects if beneath(o, {'PORT_MODEL_ROOT', 'PORT_CRANE_PLACEMENT', 'PORT_HOIST_PLACEMENT', 'A02_SHIP', 'A01_CONTAINER'}))
    assert full and port

    def fitted(ps, offset, padding=1.10):
        q = (-Vector(offset)).to_track_quat('-Z', 'Y')
        local = [q.inverted() @ p for p in ps]
        lo = Vector([min(p[i] for p in local) for i in range(3)])
        hi = Vector([max(p[i] for p in local) for i in range(3)])
        mid = (lo + hi) / 2
        position = q @ Vector((mid.x, mid.y, hi.z + 80))
        target = q @ Vector((mid.x, mid.y, lo.z))
        scale = max(hi.x - lo.x, (hi.y - lo.y) * 1.6) * padding
        return {'position': list(position), 'target': list(target), 'scale': scale}

    views = {'overview': fitted(full, (.40, -1, .72)),
             'port': fitted(port, (.36, -1, .76)),
             'top': fitted(port, (0, 0, 1))}
    (ROOT / 'review' / 'camera-framing.json').write_text(json.dumps({
        'source': str(source), 'sha256': source_hash, 'views': views,
        'purpose': 'Disposable identical comparison cameras; not saved to either master'
    }, indent=2), encoding='utf-8')

if mode in {'stills', 'all'}:
    framing_path = ROOT / 'review' / 'camera-framing.json'
    if framing_path.exists():
        views = json.loads(framing_path.read_text(encoding='utf-8'))['views']
        for name, spec in views.items():
            still(name, spec['position'], spec['target'], spec['scale'])
    else:
        still('overview', (15, -54, 44), (-3, 7, 7), 66)
        still('port', (4, -38, 25), (-3, -2.4, 4), 43)
        still('top', (-2.5, 0, 70), (-2.5, 0, 0), 50)

if mode in {'motion', 'all'}:
    folder = ROOT / 'review' / f'{label}-hoist-frames'
    folder.mkdir(exist_ok=True)
    scene.render.resolution_x = 800
    scene.render.resolution_y = 450
    offset = scene.objects.get('PORT_HOIST_PLACEMENT')
    translation = offset.matrix_world.translation.copy() if offset else Vector((0, 0, 0))
    frames = list(range(0, 157, 2))
    for frame in frames:
        scene.frame_set(frame)
        matrix = original_camera.matrix_world.copy()
        matrix.translation += translation
        camera.matrix_world = matrix
        for prop in ['type', 'lens', 'sensor_fit', 'sensor_width', 'sensor_height', 'shift_x', 'shift_y', 'ortho_scale']:
            setattr(camera.data, prop, getattr(original_camera.data, prop))
        scene.render.filepath = str(folder / f'f{frame:04d}.png')
        bpy.ops.render.render(write_still=True)
    outputs.append(str(folder.relative_to(ROOT)))
    (folder / 'metadata.json').write_text(json.dumps({
        'source': str(source), 'sha256': source_hash, 'frames': frames,
        'original_fps': 12, 'frame_step': 2, 'encode_fps': 6,
        'temporary_review_camera_world_offset': list(translation),
        'original_camera_saved': False
    }, indent=2), encoding='utf-8')

assert hashlib.sha256(source.read_bytes()).hexdigest() == source_hash
(ROOT / 'review' / f'{label}-{mode}-metadata.json').write_text(json.dumps({
    'source': str(source), 'sha256': source_hash, 'outputs': outputs,
    'elapsed_seconds': time.time() - started, 'camera': 'Temporary diagnostic camera; never saved',
}, indent=2), encoding='utf-8')
print('REVIEW_RENDER_DONE', label, mode, source_hash)
