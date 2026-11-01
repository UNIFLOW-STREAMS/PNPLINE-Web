"""Copy only source-hash-verified actual US camera frames into this review."""
import hashlib
import json
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
source_root = ROOT.parent / 'port-densification-v001'
source = source_root / 'pnpline-port-densification-v001.blend'
sha = hashlib.sha256(source.read_bytes()).hexdigest()
delivery = json.loads((source_root / 'delivery.json').read_text(encoding='utf-8'))
assert sha == delivery['master_sha256']
rendered = set()
for filename in ['render-0-494.json', 'render-495-989.json']:
    meta = json.loads((source_root / 'review' / filename).read_text(encoding='utf-8'))
    assert meta['sha256'] == sha
    rendered.update(meta['frames'])
frames = [(315, '미국 도시·항만'), (349, '선박 측면 접근'), (390, '컨테이너 인양'),
          (420, '안벽으로 이송'), (450, '트레일러 안착'), (480, '트럭 출발'),
          (505, '항만 출구'), (530, '창고 접근'), (570, '트럭 정렬'),
          (630, '도크 진입'), (660, '창고 입고'), (720, '보관 구역'),
          (780, '포장 작업'), (840, '출고 상차'), (870, '배송 출발'),
          (930, '배송 분기'), (989, '마지막 프레임')]
folder = ROOT / 'review' / 'us-reference'
folder.mkdir(parents=True, exist_ok=True)
outputs = []
for frame, label in frames:
    assert frame in rendered
    origin = source_root / 'preview' / 'final-frames' / f'f{frame:04d}.png'
    target = folder / origin.name
    shutil.copy2(origin, target)
    outputs.append({'frame': frame, 'label': label, 'file': target.name,
                    'source_render': str(origin), 'sha256': hashlib.sha256(target.read_bytes()).hexdigest()})
font = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 20)
width, height, caption, cols = 480, 270, 34, 4
sheet = Image.new('RGB', (width * cols, ((len(frames) + cols - 1) // cols) * (height + caption)), '#142129')
draw = ImageDraw.Draw(sheet)
for index, (frame, label) in enumerate(frames):
    image = Image.open(folder / f'f{frame:04d}.png').convert('RGB').resize((width, height), Image.Resampling.LANCZOS)
    x, y = (index % cols) * width, (index // cols) * (height + caption)
    draw.text((x + 10, y + 3), f'f{frame:03d} · {frame / 30:.2f}s · {label}', fill='#edf4f7', font=font)
    sheet.paste(image, (x, y + caption))
sheet.save(ROOT / 'review' / 'us-reference-contact-sheet.png')
(folder / 'metadata.json').write_text(json.dumps({'source': str(source), 'source_sha256': sha,
    'native_fps': 30, 'source_saved': False, 'actual_scene_camera': True,
    'provenance': 'Copied unmodified from existing hash-bound final actual-camera renders',
    'source_preview_lighting': 'Original Workbench render settings, including cast shadows',
    'frames': [frame for frame, label in frames], 'outputs': outputs}, indent=2, ensure_ascii=False), encoding='utf-8')
print('US_REFERENCE_READY', sha)
