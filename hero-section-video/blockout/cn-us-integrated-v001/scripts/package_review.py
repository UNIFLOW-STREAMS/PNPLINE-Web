"""Package source-bound native-camera images; sampled previews retain real timing."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / 'review'
parser = argparse.ArgumentParser()
parser.add_argument('label', nargs='?')
parser.add_argument('--combine', nargs='+', metavar='LABEL')
parser.add_argument('--step', type=int, default=1)
parser.add_argument('--review-end', type=int, help='Inclusive source-frame end for an explicitly partial preview')
args = parser.parse_args()


def metadata(label):
    folder = REVIEW / f'{label}-frames'
    data = json.loads((folder / 'metadata.json').read_text(encoding='utf-8'))
    assert hashlib.sha256(Path(data['source']).read_bytes()).hexdigest() == data['sha256'], label + ' stale source'
    assert data['actual_scene_camera'] and not data['source_saved']
    return folder, data


def contact(label):
    folder, data = metadata(label)
    font = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 21)
    width, height, caption, columns = 480, 270, 34, 4
    frames = data['frames']
    canvas = Image.new('RGB', (width * columns, ((len(frames) + columns - 1) // columns) * (height + caption)), '#142129')
    draw = ImageDraw.Draw(canvas)
    for index, frame in enumerate(frames):
        image = Image.open(folder / f'f{frame:04d}.png').convert('RGB').resize((width, height), Image.Resampling.LANCZOS)
        x, y = (index % columns) * width, (index // columns) * (height + caption)
        draw.text((x + 10, y + 3), f'f{frame:04d} · {frame / data["native_fps"]:.2f}s', fill='#edf4f7', font=font)
        canvas.paste(image, (x, y + caption))
    output = REVIEW / f'{label}-contact-sheet.png'
    canvas.save(output)
    print('CONTACT', output)


if args.label:
    contact(args.label)
if args.combine:
    assert args.step > 0
    records, metas = [], []
    for label in args.combine:
        folder, data = metadata(label)
        metas.append(data)
        records.extend((frame, folder / f'f{frame:04d}.png') for frame in data['frames'])
    assert len({m['sha256'] for m in metas}) == 1
    assert len({(m['native_fps'], m['width'], m['height'], m['scene_frame_start'], m['scene_frame_end']) for m in metas}) == 1
    first = metas[0]
    records.sort()
    review_end = first['scene_frame_end'] if args.review_end is None else args.review_end
    assert first['scene_frame_start'] <= review_end <= first['scene_frame_end']
    partial = review_end < first['scene_frame_end']
    assert [frame for frame, path in records] == list(range(first['scene_frame_start'], review_end + 1, args.step))
    assert all(path.is_file() and path.stat().st_size > 0 for frame, path in records)
    rate = first['native_fps'] / args.step
    output = REVIEW / ('pnpline-cn-us-opening-review.mp4' if partial else 'pnpline-cn-us-integrated-review.mp4')
    command = ['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-f', 'image2pipe',
        '-framerate', str(rate), '-vcodec', 'png', '-i', '-', '-fps_mode', 'passthrough',
        '-frames:v', str(len(records)), '-c:v', 'libx264', '-crf', '18', '-preset', 'fast',
        '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(output)]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    try:
        for frame, path in records:
            process.stdin.write(path.read_bytes())
    finally:
        process.stdin.close()
    assert process.wait() == 0
    probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries',
        'stream=width,height,r_frame_rate,nb_frames:format=duration', '-of', 'json', str(output)], text=True))
    stream = probe['streams'][0]
    assert int(stream['nb_frames']) == len(records)
    numerator, denominator = map(int, stream['r_frame_rate'].split('/'))
    assert abs(numerator / denominator - rate) < 1e-6
    assert abs(float(probe['format']['duration']) - len(records) / rate) < .002
    result = {'source': first['source'], 'sha256': first['sha256'], 'actual_scene_camera': True,
        'native_fps': first['native_fps'], 'preview_fps': rate, 'source_frame_step': args.step,
        'rendered_frames': len(records), 'source_frame_range': [records[0][0], records[-1][0]],
        'preview_scope': 'Changed opening and transition only' if partial else 'Complete timeline',
        'complete_master_frame_range': [first['scene_frame_start'], first['scene_frame_end']],
        'complete_master_duration_seconds': (first['scene_frame_end'] - first['scene_frame_start'] + 1) / first['native_fps'],
        'interpolated_frames': 0, 'video': output.name, 'video_probe': probe,
        'video_sha256': hashlib.sha256(output.read_bytes()).hexdigest(), 'preview_lighting': first['preview_lighting']}
    (REVIEW / 'motion-metadata.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    after_folder, after = metadata('after')
    assert after['sha256'] == first['sha256']
    reference_folder, reference = metadata('us-reference-live')
    common = sorted(set(reference['frames']) & set(after['frames']))
    options = ''.join(f'<option value="{f:04d}">f{f:04d} · {f / first["native_fps"]:.2f}초</option>' for f in common)
    initial = common[0]
    sampling = '전체 프레임을 렌더링했습니다.' if args.step == 1 else f'{args.step}프레임 간격으로 실제 장면을 렌더링했으며 원래 재생 시간을 유지했습니다.'
    preview_description = '아래 영상은 변경된 중국 도입부와 항해 전환 9초만 담은 부분 검토 영상입니다. 전체 미국 구간은 주요 장면 이미지와 Blender 작업본에서 확인할 수 있습니다.' if partial else '아래 영상은 전체 경로를 담은 검토 영상입니다.'
    nav = '<button data-time="0">중국 선적</button><button data-time="3.5">중국 항만</button><button data-time="7">항해 전환</button>'
    if not partial:
        nav += '<button data-time="9.5">미국 접근</button><button data-time="12.5">미국 하역</button><button data-time="17.5">트럭 이동</button><button data-time="24">창고</button><button data-time="29">배송</button>'
    html = f'''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>PNPLINE · 중국–미국 통합 영상</title><style>:root{{color-scheme:dark}}*{{box-sizing:border-box}}body{{margin:0;background:#111c24;color:#edf4f7;font:16px/1.6 system-ui,sans-serif}}main{{max-width:1500px;margin:auto;padding:32px 24px 64px}}h1{{font-size:30px;line-height:1.3}}h2{{font-size:23px;margin:32px 0 12px}}p{{color:#b9cad4}}a{{color:#88dced}}img,video{{width:100%;height:auto;display:block;background:#172832;border-radius:8px}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}figure{{margin:0;min-width:0}}figcaption{{margin-bottom:8px;font-weight:600}}select,button{{font:inherit;background:#203743;color:#edf4f7;border:1px solid #486775;border-radius:6px;padding:6px 12px}}nav{{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0}}.note{{padding:12px 16px;background:#1c303d;border-left:3px solid #64c8df}}@media(max-width:850px){{.grid{{grid-template-columns:1fr}}main{{padding:24px 14px}}}}</style>
<main><h1>PNPLINE · 중국–미국 통합 작업본</h1><p>중국 항만의 선적·도시 공개부터 미국 입항·하역·트럭 이동·창고·배송까지 연결한 33초·30fps Blender 작업본입니다.</p><p>{preview_description}</p>
<p><a href="../{Path(first['source']).name}">Blender 작업본</a> · <a href="motion-metadata.json">영상 기준 파일과 메타데이터</a></p>
<video id="movie" controls playsinline preload="metadata" poster="after-frames/f0132.png" src="{output.name}"></video>
<nav>{nav}</nav>
<p>마스터 {first['native_fps']:g}fps · 검토 영상 {rate:g}fps · 실제 렌더 {len(records)}프레임 · {float(probe['format']['duration']):.2f}초. {sampling} 프레임 보간은 사용하지 않았습니다.</p>
<p class="note">Workbench 검토 영상은 스튜디오 조명과 표면 음영을 사용하며 투사 그림자는 비활성화했습니다. Blender 원본의 제작용 조명과 Cycles 설정은 변경하지 않았습니다. 미국 기준 이미지도 같은 검토 조명으로 원본 파일에서 다시 렌더링했습니다.</p>
<h2>전체 경로의 주요 장면</h2><a href="after-contact-sheet.png" target="_blank"><img src="after-contact-sheet.png" alt="중국부터 미국 배송까지 주요 장면"></a>
<h2>미국 구간의 기존 작업과 비교</h2><select id="frame">{options}</select><div class="grid"><figure><figcaption>기존 미국 작업본</figcaption><img id="reference" src="us-reference-live-frames/f{initial:04d}.png" alt="기존 미국 모델과 카메라"></figure><figure><figcaption>중국–미국 통합본</figcaption><img id="after" src="after-frames/f{initial:04d}.png" alt="통합본 미국 구간"></figure></div></main>
<script>document.querySelectorAll('[data-time]').forEach(b=>b.onclick=()=>{{const v=document.getElementById('movie');v.currentTime=+b.dataset.time;v.play()}});document.getElementById('frame').onchange=e=>{{document.getElementById('reference').src='us-reference-live-frames/f'+e.target.value+'.png';document.getElementById('after').src='after-frames/f'+e.target.value+'.png'}};</script></html>'''
    (REVIEW / 'review.html').write_text(html, encoding='utf-8')
    print('VIDEO_READY', output, len(records), rate)
assert args.label or args.combine
