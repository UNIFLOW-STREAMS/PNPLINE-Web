"""Validate encoded preview cadence and exact rendered US preservation samples."""
import hashlib
import json
import subprocess
from pathlib import Path
from PIL import Image, ImageChops, ImageStat

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / 'review'
after = json.loads((R / 'after-frames/metadata.json').read_text(encoding='utf-8'))
reference = json.loads((R / 'us-reference-live-frames/metadata.json').read_text(encoding='utf-8'))
for meta in [after, reference]:
    assert hashlib.sha256(Path(meta['source']).read_bytes()).hexdigest() == meta['sha256']
poses_a = {p['frame']: p for p in after['camera_poses']}
poses_b = {p['frame']: p for p in reference['camera_poses']}
rows = []
for frame in sorted(set(poses_a) & set(poses_b)):
    a = Image.open(R / 'after-frames' / f'f{frame:04d}.png').convert('RGB')
    b = Image.open(R / 'us-reference-live-frames' / f'f{frame:04d}.png').convert('RGB')
    rows.append({'frame': frame, 'camera_exact': poses_a[frame] == poses_b[frame],
                 'pixels_exact': ImageChops.difference(a, b).getbbox() is None})
pixel_result = {'candidate_sha256': after['sha256'], 'reference_sha256': reference['sha256'],
                'checks': rows, 'pass': all(r['camera_exact'] and r['pixels_exact'] for r in rows)}
(R / 'us-live-pixel-comparison.json').write_text(json.dumps(pixel_result, indent=2), encoding='utf-8')
assert pixel_result['pass']
movie = json.loads((R / 'motion-metadata.json').read_text(encoding='utf-8'))
assert movie['sha256'] == after['sha256']
video = R / movie['video']
assert hashlib.sha256(video.read_bytes()).hexdigest() == movie['video_sha256']
records = []
for label in ['motion-a', 'motion-b']:
    folder = R / f'{label}-frames'
    meta = json.loads((folder / 'metadata.json').read_text(encoding='utf-8'))
    assert meta['sha256'] == movie['sha256']
    records.extend((f, folder / f'f{f:04d}.png') for f in meta['frames'])
records.sort()
indices = sorted({0, 28, 67, 68, len(records) - 1})
expression = '+'.join(f'eq(n,{i})' for i in indices)
raw = subprocess.check_output(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', str(video),
    '-vf', f"select='{expression}'", '-fps_mode', 'passthrough', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'])
width, height = movie['video_probe']['streams'][0]['width'], movie['video_probe']['streams'][0]['height']
size = width * height * 3
assert len(raw) == len(indices) * size
decoded = []
for index, encoded_index in enumerate(indices):
    image = Image.frombytes('RGB', (width, height), raw[index * size:(index + 1) * size])
    source_frame, path = records[encoded_index]
    stat = ImageStat.Stat(ImageChops.difference(image, Image.open(path).convert('RGB')))
    mse = sum(r * r for r in stat.rms) / 3
    assert mse < 30, (encoded_index, mse)
    decoded.append({'encoded_frame': encoded_index, 'source_frame': source_frame, 'mean_squared_pixel_error': mse})
probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_frames',
    '-show_entries', 'frame=best_effort_timestamp_time', '-of', 'json', str(video)], text=True))
times = [float(f['best_effort_timestamp_time']) for f in probe['frames']]
assert len(times) == len(records)
error = max(abs(t - i / movie['preview_fps']) for i, t in enumerate(times))
assert error < .000002
result = {'candidate_sha256': movie['sha256'], 'video_frames': len(times),
          'preview_fps': movie['preview_fps'], 'native_master_fps': movie['native_fps'],
          'maximum_timestamp_error_seconds': error, 'decoded_source_frame_checks': decoded,
          'US_exact_pixel_samples': len(rows), 'pass': True}
(R / 'video-validation.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result))
