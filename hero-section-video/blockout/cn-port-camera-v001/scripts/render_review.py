"""Render the scene's actual camera without saving changes to its source blend.

Blender --background FILE --python render_review.py -- reference --frames 0,24,72
Blender --background FILE --python render_review.py -- after --motion 0:400:2
"""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('label')
selection = parser.add_mutually_exclusive_group(required=True)
selection.add_argument('--frames')
selection.add_argument('--motion', help='Inclusive START:END:STEP')
parser.add_argument('--width', type=int, default=800)
parser.add_argument('--height', type=int, default=450)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
assert args.label.replace('-', '').replace('_', '').isalnum()
if args.frames:
    frames = [int(x) for x in args.frames.split(',')]
else:
    start, end, step = (int(x) for x in args.motion.split(':'))
    assert step > 0 and end >= start
    frames = list(range(start, end + 1, step))
assert frames and len(set(frames)) == len(frames)

scene = bpy.context.scene
source = Path(bpy.data.filepath)
source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
camera = scene.camera
assert camera is not None
native_fps = scene.render.fps / scene.render.fps_base
folder = ROOT / 'review' / f'{args.label}-frames'
folder.mkdir(parents=True, exist_ok=True)
scene.render.engine = 'BLENDER_WORKBENCH'
shading = scene.display.shading
shading.light = 'STUDIO'
shading.color_type = 'MATERIAL'
shading.show_shadows = False
shading.show_cavity = True
shading.cavity_type = 'BOTH'
shading.show_specular_highlight = True
shading.background_type = 'WORLD'
scene.render.resolution_percentage = 100
scene.render.resolution_x = args.width
scene.render.resolution_y = args.height
scene.render.use_border = False
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'
started = time.time()
poses = []
for frame in frames:
    scene.frame_set(frame)
    assert scene.camera == camera
    poses.append({'frame': frame, 'world': [list(row) for row in camera.matrix_world],
                  'lens': camera.data.lens, 'type': camera.data.type,
                  'shift_x': camera.data.shift_x, 'shift_y': camera.data.shift_y})
    scene.render.filepath = str(folder / f'f{frame:04d}.png')
    bpy.ops.render.render(write_still=True)
assert hashlib.sha256(source.read_bytes()).hexdigest() == source_hash
metadata = {'source': str(source), 'sha256': source_hash, 'frames': frames,
            'native_fps': native_fps, 'camera': camera.name, 'actual_scene_camera': True,
            'camera_poses': poses, 'source_saved': False,
            'preview_lighting': 'Workbench STUDIO, cavity BOTH, specular; cast shadows disabled to avoid below-horizon preview artifacts. Production Cycles lighting is unchanged.',
            'width': args.width, 'height': args.height,
            'elapsed_seconds': time.time() - started}
(folder / 'metadata.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
print('NATIVE_CAMERA_REVIEW_DONE', args.label, source_hash, flush=True)
