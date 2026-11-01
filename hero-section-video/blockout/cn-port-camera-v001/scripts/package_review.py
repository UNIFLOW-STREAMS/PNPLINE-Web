"""Package actual-camera review frames into contact sheets and optional video."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]


def combine_motion():
    review = ROOT / 'review'
    records = []
    manifests = []
    for label in ['motion-a', 'motion-b']:
        folder = review / f'{label}-frames'
        meta = json.loads((folder / 'metadata.json').read_text(encoding='utf-8'))
        assert hashlib.sha256(Path(meta['source']).read_bytes()).hexdigest() == meta['sha256'], label + ' stale source'
        assert meta['actual_scene_camera'] and not meta['source_saved']
        assert meta['width'] == 960 and meta['height'] == 540
        manifests.append(meta)
        records.extend((frame, folder / f'f{frame:04d}.png') for frame in meta['frames'])
    assert len({m['sha256'] for m in manifests}) == 1
    assert all(m['native_fps'] == 12 for m in manifests)
    records.sort()
    assert [frame for frame, path in records] == list(range(401))
    assert all(path.is_file() and path.stat().st_size > 0 for frame, path in records)
    concat = review / 'motion-concat.txt'
    concat.write_text(''.join("file '" + path.as_posix().replace("'", "'\\''") + "'\nduration 0.0833333333333333\n" for frame, path in records)
                      + "file '" + records[-1][1].as_posix() + "'\n", encoding='utf-8')
    output = review / 'cn-port-camera-review.mp4'
    # Set each image sequence's native rate explicitly. This avoids the PNG
    # demuxer's default 25fps timestamp quantization and keeps one output frame
    # for every rendered frame, with no frame interpolation or rate resampling.
    subprocess.run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
                    '-framerate', '12', '-start_number', '0', '-i', str(review / 'motion-a-frames/f%04d.png'),
                    '-framerate', '12', '-start_number', '201', '-i', str(review / 'motion-b-frames/f%04d.png'),
                    '-filter_complex', '[0:v][1:v]concat=n=2:v=1:a=0[v]', '-map', '[v]',
                    '-fps_mode', 'passthrough', '-frames:v', '401', '-c:v', 'libx264',
                    '-crf', '18', '-preset', 'fast', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(output)], check=True)
    probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries',
        'stream=width,height,r_frame_rate,nb_frames:format=duration', '-of', 'json', str(output)], text=True))
    stream = probe['streams'][0]
    assert stream['nb_frames'] == '401' and stream['r_frame_rate'] == '12/1'
    assert (stream['width'], stream['height']) == (960, 540)
    assert abs(float(probe['format']['duration']) - 401 / 12) < .002
    metadata = {'source': manifests[0]['source'], 'sha256': manifests[0]['sha256'],
                'actual_scene_camera': True, 'frames': 401, 'frame_range': [0, 400],
                'native_fps': 12, 'interpolated_frames': 0, 'video': output.name,
                'video_sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
                'video_probe': probe, 'preview_lighting': manifests[0]['preview_lighting']}
    (review / 'motion-metadata.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    reference = json.loads((review / 'reference-frames/metadata.json').read_text(encoding='utf-8'))
    after = json.loads((review / 'after-frames/metadata.json').read_text(encoding='utf-8'))
    assert after['sha256'] == metadata['sha256']
    common = sorted(set(reference['frames']) & set(after['frames']))
    options = ''.join(f'<option value="{frame:04d}">f{frame:04d} · {frame / 12:.2f}초</option>' for frame in common)
    html = '''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>중국 항만 카메라 · 하역부터 출항까지</title><style>
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#111c24;color:#eff5f7;font:16px/1.6 system-ui,sans-serif}main{max-width:1500px;margin:auto;padding:32px 24px 64px}h1{font-size:30px;line-height:1.3;margin:0 0 12px}h2{font-size:23px;margin:32px 0 12px}p{color:#b9cad4}a{color:#88dced}video,img{width:100%;height:auto;display:block;background:#162731;border-radius:8px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}figure{margin:0;min-width:0}figcaption{margin:0 0 8px;font-weight:600}.note{padding:12px 16px;background:#1c303d;border-left:3px solid #64c8df}select{font:inherit;background:#203743;color:#f0f5f7;border:1px solid #486775;border-radius:6px;padding:6px 12px;margin-bottom:14px}.small{font-size:14px}@media(max-width:850px){.grid{grid-template-columns:1fr}main{padding:24px 14px}h1{font-size:25px}}</style>
<main><h1>중국 항만 카메라 · 하역부터 출항까지</h1><p>컨테이너 하강, 항만 전체 공개, 출항과 선박 추적을 연결한 실제 카메라 검토 영상입니다.</p>
<p><a href="../master-cn-port-camera-v001.blend">Blender 작업본</a> · <a href="motion-metadata.json">영상·원본 정보</a></p>
<video controls playsinline preload="metadata" poster="after-frames/f0144.png" src="cn-port-camera-review.mp4"></video>
<p class="small">f0–400 · 12fps · 401개 실제 렌더 프레임 · 960×540 · 33.42초. 프레임 보간을 사용하지 않았습니다.</p>
<p class="note">Workbench 검토 영상은 스튜디오 조명과 표면 음영을 사용합니다. 미리보기의 잘못된 투사 그림자를 끄고 촬영했으며, Blender 파일의 제작용 조명과 Cycles 설정은 변경하지 않았습니다.</p>
<h2>기준 카메라와 같은 시점 비교</h2><select id="frame">OPTIONS</select>
<div class="grid"><figure><figcaption>기준 · 항만 확장 전</figcaption><img id="reference" src="reference-frames/f0000.png" alt="기존 카메라의 기준 프레임"></figure><figure><figcaption>수정 · 확장 항만 카메라</figcaption><img id="after" src="after-frames/f0000.png" alt="수정된 항만 카메라 프레임"></figure></div>
<h2>수정본의 주요 장면</h2><a href="after-contact-sheet.png" target="_blank"><img src="after-contact-sheet.png" alt="하역, 항만 공개, 출항의 주요 프레임"></a>
<p class="small"><a href="reference-contact-sheet.png" target="_blank">기준 카메라의 주요 장면</a> · <a href="after-frames/metadata.json">수정본 카메라 포즈와 렌즈 기록</a></p></main>
<script>document.getElementById('frame').onchange=e=>{['reference','after'].forEach(k=>document.getElementById(k).src=k+'-frames/f'+e.target.value+'.png')};</script></html>'''
    (review / 'review.html').write_text(html.replace('OPTIONS', options), encoding='utf-8')
    print('COMBINED_NATIVE_MOTION', output, metadata['sha256'])


parser = argparse.ArgumentParser()
parser.add_argument('label', nargs='?')
parser.add_argument('--combine', action='store_true')
parser.add_argument('--video', action='store_true')
parser.add_argument('--sheet-frames', help='Optional comma-separated subset')
args = parser.parse_args()
if args.combine:
    combine_motion()
    raise SystemExit(0)
assert args.label, 'A label is required unless --combine is used'
folder = ROOT / 'review' / f'{args.label}-frames'
metadata = json.loads((folder / 'metadata.json').read_text(encoding='utf-8'))
assert hashlib.sha256(Path(metadata['source']).read_bytes()).hexdigest() == metadata['sha256']
all_frames = metadata['frames']
frames = [int(x) for x in args.sheet_frames.split(',')] if args.sheet_frames else all_frames
assert all(frame in all_frames for frame in frames)
columns = 4
width, height, caption = 480, 270, 32
rows = (len(frames) + columns - 1) // columns
sheet = Image.new('RGB', (columns * width, rows * (height + caption)), '#142129')
draw = ImageDraw.Draw(sheet)
font = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 21)
for index, frame in enumerate(frames):
    image = Image.open(folder / f'f{frame:04d}.png').convert('RGB')
    image = image.resize((width, height), Image.Resampling.LANCZOS)
    x, y = (index % columns) * width, (index // columns) * (height + caption)
    draw.text((x + 10, y + 2), f'f{frame:04d}  ·  {frame / metadata["native_fps"]:.2f}s',
              fill='#edf4f7', font=font)
    sheet.paste(image, (x, y + caption))
sheet_path = ROOT / 'review' / f'{args.label}-contact-sheet.png'
sheet.save(sheet_path)
print('CONTACT_SHEET', sheet_path)
if args.video:
    assert len(all_frames) > 1
    step = all_frames[1] - all_frames[0]
    assert all(b - a == step for a, b in zip(all_frames, all_frames[1:]))
    duration = step / metadata['native_fps']
    concat = ROOT / 'review' / f'{args.label}-concat.txt'
    paths = [folder / f'f{frame:04d}.png' for frame in all_frames]
    assert all(path.is_file() for path in paths)
    concat.write_text(''.join("file '" + path.as_posix().replace("'", "'\\''") + "'\nduration " + str(duration) + '\n' for path in paths)
                      + "file '" + paths[-1].as_posix() + "'\n", encoding='utf-8')
    output = ROOT / 'review' / f'{args.label}.mp4'
    subprocess.run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-f', 'concat', '-safe', '0',
                    '-i', str(concat), '-vf', f'fps={metadata["native_fps"]}',
                    '-t', str(len(paths) * duration), '-c:v', 'libx264', '-crf', '18',
                    '-preset', 'fast', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(output)], check=True)
    print('VIDEO', output)
