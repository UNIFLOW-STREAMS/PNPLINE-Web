import bpy
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / 's5-integration-v001/master-s5-integration-v001.blend'
OUTPUT = ROOT / 'master-previz-s1-s7-2x-v001.blend'
RECORD = ROOT / 'render-record.json'

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def save(record):
    RECORD.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf8')

s = bpy.context.scene
if '--prepare' in sys.argv:
    assert Path(bpy.data.filepath).resolve() == SOURCE.resolve()
    assert s.render.fps == 12 and s.render.fps_base == 1
    assert (s.frame_start, s.frame_end) == (0, 1392)
    record = {'status': 'prepared', 'source': str(SOURCE), 'source_sha256': digest(SOURCE),
              'scene': s.name, 'camera': s.camera.name, 'original_fps': 12,
              'output_fps': 24, 'speed_multiplier': 2, 'frame_start': 0, 'frame_end': 1392,
              'frame_count': 1393, 'duration_seconds': 1393 / 24,
              'markers': {m.name: m.frame for m in s.timeline_markers},
              'blender_version': bpy.app.version_string, 'resolution': [960, 540],
              'images': []}
    (ROOT / 'frames').mkdir(parents=True, exist_ok=True)
    s.render.fps = 24
    s.render.fps_base = 1
    s.render.engine = 'BLENDER_WORKBENCH'
    s.render.resolution_x = 960
    s.render.resolution_y = 540
    s.render.resolution_percentage = 100
    s.render.use_border = False
    s.render.use_crop_to_border = False
    s.render.film_transparent = False
    s.render.image_settings.file_format = 'PNG'
    s.render.image_settings.color_mode = 'RGB'
    s.render.filepath = str(ROOT / 'frames') + '/'
    s.use_preview_range = False
    s.frame_step = 1
    s.sync_mode = 'FRAME_DROP'
    s.display.shading.light = 'STUDIO'
    s.display.shading.color_type = 'MATERIAL'
    s.display.shading.show_shadows = True
    s.display.shading.show_cavity = True
    s.display.shading.background_type = 'WORLD'
    s.world.color = (.18, .18, .18)
    s.frame_set(0)
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces.active.region_3d.view_perspective = 'CAMERA'
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT))
    record['output_blend'] = str(OUTPUT)
    record['output_blend_sha256'] = digest(OUTPUT)
    save(record)
    print('PREPARED', OUTPUT, flush=True)
else:
    assert Path(bpy.data.filepath).resolve() == OUTPUT.resolve()
    record = json.loads(RECORD.read_text(encoding='utf8'))
    assert digest(SOURCE) == record['source_sha256']
    assert s.render.fps == 24 and s.render.fps_base == 1
    record['status'] = 'rendering'
    record['script_sha256'] = digest(__file__)
    started = time.time()
    save(record)
    for frame in range(0, 1393):
        s.frame_set(frame)
        path = ROOT / 'frames' / f'{frame:04d}.png'
        s.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        record['images'].append({'frame': frame, 'sha256': digest(path)})
        if frame % 24 == 0 or frame == 1392:
            record['render_elapsed_seconds'] = time.time() - started
            save(record)
            print('PROGRESS', frame + 1, '/ 1393', flush=True)
    assert digest(SOURCE) == record['source_sha256'], 'Source changed during rendering'
    record['status'] = 'rendered'
    save(record)
    print('RENDER_COMPLETE', flush=True)
