"""Check native frame cadence and visual correspondence across the encode join."""
import json
import subprocess
from pathlib import Path
from PIL import Image, ImageChops, ImageStat

ROOT = Path(__file__).resolve().parents[1]
review = ROOT / 'review'
video = review / 'cn-port-camera-review.mp4'
frames = [0, 72, 144, 200, 201, 400]
expression = '+'.join(f'eq(n,{frame})' for frame in frames)
raw = subprocess.check_output(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', str(video),
    '-vf', f"select='{expression}'", '-fps_mode', 'passthrough', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'])
size = 960 * 540 * 3
assert len(raw) == len(frames) * size
errors = []
for index, frame in enumerate(frames):
    decoded = Image.frombytes('RGB', (960, 540), raw[index * size:(index + 1) * size])
    label = 'motion-a' if frame <= 200 else 'motion-b'
    original = Image.open(review / f'{label}-frames' / f'f{frame:04d}.png').convert('RGB')
    difference = ImageStat.Stat(ImageChops.difference(decoded, original))
    mse = sum(r * r for r in difference.rms) / 3
    assert mse < 25, (frame, mse)
    errors.append({'frame': frame, 'mean_squared_pixel_error': mse})
probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_frames',
    '-show_entries', 'frame=best_effort_timestamp_time', '-of', 'json', str(video)], text=True))
times = [float(frame['best_effort_timestamp_time']) for frame in probe['frames']]
assert len(times) == 401
maximum_time_error = max(abs(time - index / 12) for index, time in enumerate(times))
assert maximum_time_error < .000002
result = {'frames': len(times), 'native_fps': 12,
          'maximum_timestamp_error_seconds': maximum_time_error,
          'decoded_source_frame_checks': errors, 'pass': True}
(review / 'video-validation.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result))
