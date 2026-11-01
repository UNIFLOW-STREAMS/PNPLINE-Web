"""Encode the new camera frames and verified unchanged frames at exactly 30fps."""
import hashlib, json, subprocess
from pathlib import Path

R = Path(__file__).resolve().parents[1]
cfg = json.loads((R / 'config.json').read_text())
base = (R / cfg['source']).resolve().parent
proof = json.loads((R / 'review/preservation.json').read_text())
current_hash = hashlib.sha256((R / cfg['output']).read_bytes()).hexdigest()
assert proof['passed'] and proof['output_sha256'] == current_hash
assert hashlib.sha256((R / cfg['source']).resolve().read_bytes()).hexdigest() == cfg['source_sha256']
base_meta = [json.loads((base / 'review' / name).read_text()) for name in ('render-0-494.json', 'render-495-989.json')]
new_meta = [json.loads((R / 'review' / name).read_text()) for name in ('render-441-529.json', 'render-530-619.json')]
assert all(m['blend_sha256'] == cfg['source_sha256'] for m in base_meta)
assert all(m['sha256'] == current_hash for m in new_meta)
assert all(m['fps'] == 30 and m['resolution'] == [1280, 720] for m in base_meta + new_meta)
assert sorted(f for m in new_meta for f in m['frames']) == list(range(441, 620))

def frame(f, before=False):
    folder = base if before or not 440 < f < 620 else R
    return folder / 'preview/frames' / f'f{f:04}.png'

def encode(name, frames):
    paths = list(frames)
    assert all(p.is_file() for p in paths)
    listing = R / 'review' / (name + '.ffconcat')
    # Per-file framerate avoids the concat demuxer's default 25fps timestamp grid.
    listing.write_text('ffconcat version 1.0\n' + ''.join(
        f"file '{p.as_posix()}'\noption framerate 30\nduration 0.03333333333333333\n" for p in paths), encoding='utf-8')
    out = R / 'preview' / (name + '.mp4')
    assert not out.exists()
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', str(listing),
                    '-r', '30', '-frames:v', str(len(paths)), '-an', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
                    '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(out)], check=True)
    probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-count_frames', '-show_streams', '-show_format', '-of', 'json', str(out)]))
    video = probe['streams'][0]
    assert video['r_frame_rate'] == video['avg_frame_rate'] == '30/1'
    assert int(video['nb_frames']) == int(video['nb_read_frames']) == len(paths)
    assert abs(float(probe['format']['duration']) - len(paths)/30) < .001
    subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-i', str(out), '-f', 'null', '-'], check=True)
    return {'file': str(out.relative_to(R)).replace('\\', '/'), 'sha256': hashlib.sha256(out.read_bytes()).hexdigest(),
            'frame_count': len(paths), 'fps': 30, 'duration': float(probe['format']['duration']), 'full_decode_passed': True}

reports = [encode('pnpline-33s-truck-camera-v001', (frame(f) for f in range(990))),
           encode('before-f440-f620', (frame(f, True) for f in range(440, 621))),
           encode('after-f440-f620', (frame(f) for f in range(440, 621)))]
(R / 'review/video.json').write_text(json.dumps({'blend_sha256': current_hash, 'videos': reports,
    'rerendered_frames': [441, 619], 'verified_reused_frames': [[0, 440], [620, 989]]}, indent=2))
print(json.dumps(reports, indent=2), flush=True)
