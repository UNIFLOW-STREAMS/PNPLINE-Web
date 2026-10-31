"""Local IMAGE placeholders requested by the user. No model or paid service."""
from pathlib import Path
import random
import json

root = Path(__file__).resolve().parent
rng = random.Random(20261101)
records = []
for name in ('warehouse', 'freight', 'evidence', 'system'):
    rgb = [rng.randrange(160, 229) for _ in range(3)]
    color = '#' + ''.join(f'{c:02x}' for c in rgb)
    path = root / 'assets' / f'placeholder-{name}.svg'
    path.write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1100" viewBox="0 0 1600 1100" role="img" aria-label="IMAGE placeholder">
<rect width="1600" height="1100" fill="{color}"/>
<text x="800" y="550" text-anchor="middle" dominant-baseline="central" font-family="Arial,sans-serif" font-size="104" font-weight="500" letter-spacing="12" fill="#102a33">IMAGE</text>
</svg>''', encoding='utf-8')
    records.append({'file': str(path.relative_to(root)), 'background': color, 'type': 'local-placeholder', 'depictsRealOperations': False})
(root / 'assets' / 'placeholder-manifest.json').write_text(json.dumps({'method': 'Seeded random color SVG; no image-generation service', 'paidGenerationCalls': 0, 'costUsd': 0, 'assets': records}, indent=2), encoding='utf-8')
print(json.dumps(records))
