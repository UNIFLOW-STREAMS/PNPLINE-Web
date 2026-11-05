"""Reproducible Cycles/OptiX production render; never writes the adopted source."""
import argparse, bpy, hashlib, json, os, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for name in ('audit', 'review', 'frames', 'assets'):
    (ROOT / name).mkdir(parents=True, exist_ok=True)
p = argparse.ArgumentParser()
p.add_argument('--mode', choices=['benchmark', 'production'], default='benchmark')
p.add_argument('--samples', type=int, default=96)
p.add_argument('--frames', default='132,260,780')
p.add_argument('--start', type=int, default=0)
p.add_argument('--end', type=int, default=989)
a = p.parse_args(sys.argv[sys.argv.index('--') + 1:])
s = bpy.context.scene
source = Path(bpy.data.filepath)
source_sha = hashlib.file_digest(source.open('rb'), 'sha256').hexdigest()
assert s.camera.name == 'CAM_MASTER'
assert (s.frame_start, s.frame_end, s.render.fps, s.render.fps_base) == (0, 989, 30, 1)
pref = bpy.context.preferences.addons['cycles'].preferences
pref.compute_device_type = 'OPTIX'
pref.get_devices()
gpu = [d for d in pref.devices if d.type == 'OPTIX']
assert gpu, 'OptiX GPU required'
for d in pref.devices:
    d.use = d.type == 'OPTIX'
s.render.engine = 'CYCLES'
s.cycles.device = 'GPU'
s.cycles.samples = a.samples
s.cycles.use_adaptive_sampling = True
s.cycles.adaptive_threshold = .018
s.cycles.adaptive_min_samples = 16
s.cycles.use_denoising = True
s.cycles.denoiser = 'OPENIMAGEDENOISE'
s.cycles.denoising_input_passes = 'RGB_ALBEDO_NORMAL'
s.cycles.seed = 29
s.cycles.use_animated_seed = False
s.render.resolution_x = 1920
s.render.resolution_y = 1080
s.render.resolution_percentage = 100
s.render.use_border = False
s.render.use_persistent_data = True
s.render.image_settings.file_format = 'PNG'
s.render.image_settings.color_mode = 'RGB'
s.render.image_settings.color_depth = '16'
s.render.image_settings.compression = 20
s.render.dither_intensity = 1
info = dict(source=str(source), sha256=source_sha, blender=bpy.app.version_string,
            devices=[dict(name=d.name, type=d.type, enabled=d.use) for d in pref.devices],
            engine=s.render.engine, samples=a.samples, adaptive_threshold=s.cycles.adaptive_threshold,
            min_samples=16, denoiser=s.cycles.denoiser, animated_seed=False,
            resolution=[1920,1080], depth=16, view=s.view_settings.view_transform,
            look=s.view_settings.look, exposure=s.view_settings.exposure,
            frame_start=0, frame_end=989, fps=30, camera='CAM_MASTER', pid=os.getpid())
(ROOT / 'audit' / 'render-settings.json').write_text(json.dumps(info, indent=2))
print('PRODUCTION_SETTINGS', json.dumps(info), flush=True)
if a.mode == 'benchmark':
    results=[]
    for f in map(int, a.frames.split(',')):
        s.frame_set(f)
        s.render.filepath = str(ROOT/'review'/f'cycles-{a.samples}-f{f:04}.png')
        t=time.perf_counter()
        bpy.ops.render.render(write_still=True)
        results.append(dict(frame=f, samples=a.samples, seconds=time.perf_counter()-t, path=s.render.filepath))
        (ROOT/'review'/f'benchmark-{a.samples}.json').write_text(json.dumps(results, indent=2))
        print('BENCHMARK', json.dumps(results[-1]), flush=True)
else:
    s.render.filepath = str(ROOT/'frames'/'f')
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'hero-section-B-web.blend'), copy=True)
    for f in range(a.start, a.end+1):
        dest=ROOT/'frames'/f'f{f:04}.png'
        if dest.exists() and dest.stat().st_size > 10000:
            continue
        s.frame_set(f)
        s.render.filepath=str(dest)
        t=time.perf_counter()
        bpy.ops.render.render(write_still=True)
        with (ROOT/'review'/'frame-times.jsonl').open('a') as log:
            log.write(json.dumps(dict(frame=f, seconds=time.perf_counter()-t))+'\n')
        print('FRAME_COMPLETE', f, flush=True)
assert hashlib.file_digest(source.open('rb'), 'sha256').hexdigest() == source_sha
print('SOURCE_UNCHANGED', source_sha, flush=True)
