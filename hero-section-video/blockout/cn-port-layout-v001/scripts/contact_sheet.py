"""Create a labeled contact sheet from actual, hash-matched review renders."""
from pathlib import Path
import hashlib
import json
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
review = ROOT / 'review'
folder = review / 'after-hoist-frames'
meta = json.loads((folder / 'metadata.json').read_text(encoding='utf-8'))
assert hashlib.sha256(Path(meta['source']).read_bytes()).hexdigest() == meta['sha256']
frames = [(0, '하강 시작'), (36, '컨테이너 하강'), (72, '갑판 안착'),
          (96, '스프레더 상승'), (120, '크레인 선회'), (156, '초기 출항')]
font = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 24)
canvas = Image.new('RGB', (1920, 804), '#142129')
draw = ImageDraw.Draw(canvas)
for index, (frame, label) in enumerate(frames):
    image = Image.open(folder / f'f{frame:04d}.png').convert('RGB')
    image = image.resize((640, 360), Image.Resampling.LANCZOS)
    x, y = (index % 3) * 640, (index // 3) * 402
    draw.text((x + 14, y + 6), f'f{frame:03d}  ·  {label}', fill='#eaf2f5', font=font)
    canvas.paste(image, (x, y + 42))
output = review / 'after-hoist-contact-sheet.png'
canvas.save(output)
print(output)
