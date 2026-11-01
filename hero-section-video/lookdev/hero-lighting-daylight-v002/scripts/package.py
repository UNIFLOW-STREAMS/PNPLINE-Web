from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,shutil
R=Path(__file__).resolve().parents[1]
B=Path('F:/pnpline-landing/hero-section-video/lookdev/hero-material-v001/review/lighting-advice-current-20261102')
frames={110:'China / port',332:'USA / port',720:'Warehouse / picking',820:'Warehouse / packing aisle'}
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',26)
small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
for label in ('before','after','comparison'):(R/'review'/label).mkdir(parents=True,exist_ok=True)
for f,title in frames.items():
    name=f'f{f:04d}.png'
    shutil.copy2(B/name,R/'review'/'before'/name)
    shutil.copy2(R/'review'/'draft-after'/name,R/'review'/'after'/name)
    board=Image.new('RGB',(1920,616),'#f1f4f7');d=ImageDraw.Draw(board)
    d.text((18,8),f'{f:04d} | {title}',font=font,fill='#182c3c')
    for x,label,caption in [(0,'before','ORIGINAL'),(960,'after','V002 / DIRECTIONAL DAYLIGHT')]:
        d.text((x+18,45),caption,font=small,fill='#126a9c' if x else '#52616e')
        with Image.open(R/'review'/label/name) as im:
            assert im.size==(960,540)
            board.paste(im,(x,76))
    board.save(R/'review'/'comparison'/f'f{f:04d}.jpg',quality=95,subsampling=0)
overview=Image.new('RGB',(1600,2106),'#f1f4f7');d=ImageDraw.Draw(overview)
d.text((18,10),'PNPLINE | Original vs directional daylight v002',font=font,fill='#182c3c')
for i,f in enumerate(frames):
    with Image.open(R/'review'/'comparison'/f'f{f:04d}.jpg') as im:
        overview.paste(im.resize((1600,513),Image.Resampling.LANCZOS),(0,54+i*513))
overview.save(R/'review'/'comparison-overview.jpg',quality=95,subsampling=0)
verify=json.loads((R/'verification.json').read_text());assert verify['passed']
source=json.loads((R/'source.json').read_text());metrics=json.loads((B/'render-metrics.json').read_text())
assert all(m['source_sha256']==source['sha256'] and m['width']==960 and m['samples']==32 for m in metrics)
(R/'review'/'before'/'metrics.json').write_text(json.dumps(metrics,indent=2))
(R/'README.md').write_text('''# PNPLINE directional daylight v002

Feedback: v001 produced too little visible change. This variant changes light direction and key/fill balance more strongly.

- Source: latest hero-material-v001.blend, SHA256 recorded in source.json.
- World strength .45 -> .12; camera background retained.
- CN key: 420000W, size45m, position(-200,-110,135), target(-120,0,65); fill18000W.
- US key: 520000W, size50m, position(-10,-80,205), target(80,28,125); rim55000W, size80m.
- Warehouse: general ceiling220W, aisle260W; local task lights450/550/320W at7.5m in warehouse authoring chart.
- AgX Medium High Contrast and exposure+.3 retained.
- Four previews: 110,332,720,820 at960x540, Cycles OptiX,32 samples,min32,adaptive.02,seed29,OIDN. Original previews reused from the same source hash and same rendering parameters; metadata retained.
- review/comparison: left ORIGINAL, right V002. No grading or exposure adjustment applied to the comparison images.
- Saved blend retains original production render settings. Only lighting/world and3 additional light objects differ. Geometry, material, action, camera and non-light object fingerprints match on reopen. See verification.json.
- This is a stronger lighting study reviewed on four still frames; full animation playback is not included.

Reproduction: Blender5.1 source file --python scripts/lighting.py -- build. Source -- before; candidate -- after; candidate -- verify. Then Python scripts/package.py. Output paths follow the script directory.
''',encoding='utf-8')
print('PACKAGED',len(frames),'comparisons, verification passed')
