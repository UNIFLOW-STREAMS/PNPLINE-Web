from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import json, html

R=Path(__file__).resolve().parents[1]
frames={45:'China / loading',110:'China / port and skyline',200:'Ocean / transition',332:'USA / port and vessel',530:'Warehouse / approach',720:'Warehouse / picking',820:'Warehouse / packing aisle',930:'Dispatch / closing'}
font_path='C:/Windows/Fonts/arial.ttf'
font=ImageFont.truetype(font_path,27)
small=ImageFont.truetype(font_path,22)
out=R/'review'/'comparison';out.mkdir(parents=True,exist_ok=True)
for f,title in frames.items():
    board=Image.new('RGB',(1920,616),'#f3f5f7');d=ImageDraw.Draw(board)
    d.text((18,12),f'{f:04d}  |  {title}',font=font,fill='#162838')
    d.text((18,49),'BEFORE / current material v001',font=small,fill='#52616e')
    d.text((978,49),'AFTER / daylight lighting v001',font=small,fill='#126a9c')
    for x,label in [(0,'before'),(960,'after')]:
        with Image.open(R/'review'/label/f'f{f:04d}.png') as im:
            assert im.size==(1440,810),(label,f,im.size)
            board.paste(im.resize((960,540),Image.Resampling.LANCZOS),(x,76))
    board.save(out/f'f{f:04d}.jpg',quality=94,subsampling=0)
overview=Image.new('RGB',(1600,2106),'#f3f5f7')
d=ImageDraw.Draw(overview);d.text((18,12),'PNPLINE  |  Lighting comparison',font=font,fill='#162838')
for row,f in enumerate((110,332,720,820)):
    with Image.open(out/f'f{f:04d}.jpg') as im:overview.paste(im.resize((1600,513),Image.Resampling.LANCZOS),(0,54+row*513))
overview.save(R/'review'/'comparison-overview.jpg',quality=94,subsampling=0)
options=''.join(f'<option value="{f:04d}" {"selected" if f==110 else ""}>{f:04d} · {html.escape(t)}</option>' for f,t in frames.items())
gallery=''.join(f'<article><h2>{f:04d} · {html.escape(t)}</h2><a href="review/comparison/f{f:04d}.jpg"><img loading="lazy" src="review/comparison/f{f:04d}.jpg" alt="Before and after frame {f}"></a></article>' for f,t in frames.items())
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PNPLINE 라이팅 비교</title><style>
*{box-sizing:border-box}body{margin:0;background:#eef2f5;color:#172c3b;font:16px/1.65 system-ui,sans-serif}main{max-width:1500px;margin:auto;padding:30px 22px}h1{font-size:32px;line-height:1.3}p{max-width:1000px;color:#415565}a{color:#126a9c}article,.panel{margin:28px 0;background:white;padding:18px;border:1px solid #d5dfe5;border-radius:10px}img{display:block;width:100%}select,input{font:inherit;padding:8px}select{max-width:100%}.stage{position:relative;aspect-ratio:16/9;overflow:hidden;background:#d8dde2}.stage img{position:absolute;inset:0;height:100%;object-fit:contain}.stage .new{clip-path:inset(0 50% 0 0)}.line{position:absolute;top:0;bottom:0;left:50%;border-left:2px solid white;pointer-events:none}.labels{display:flex;justify-content:space-between;font-weight:600;margin:8px 0}input[type=range]{width:100%;padding:0}table{border-collapse:collapse;width:100%;max-width:900px}td,th{text-align:left;border-bottom:1px solid #dce3e8;padding:9px}h2{font-size:20px}@media(max-width:700px){h1{font-size:25px}main{padding:18px 10px}.panel,article{padding:10px}}</style><main>
<p>PNPLINE · HERO VIDEO · LIGHTING STUDY v001</p><h1>기존 조명과 데이라이트 조명 비교</h1>
<p>최신 material v001에서 분기한 별도 Blender 파일입니다. 같은 카메라와 프레임을 Cycles OptiX · 1440×810 · 최대 64 samples · 고정 seed 29 · AgX / Medium High Contrast · 노출 +0.3으로 렌더했습니다. 아래 이미지는 실제 Blender 렌더이며, 비교 이미지는 크기만 줄였습니다.</p>
<p><a href="pnpline-hero-lighting-daylight-v001.blend">별도 Blender 파일</a> · <a href="verification.json">보존 검증</a> · <a href="README.md">작업 기록</a> · <a href="review/comparison-overview.jpg">대표 프레임 모음</a></p>
<section class="panel"><h2>동일 프레임 슬라이더</h2><label for="frame">대표 프레임 </label><select id="frame">OPTIONS</select><div class="labels"><span>왼쪽: 적용 후</span><span>오른쪽: 기존</span></div><div class="stage"><img id="old" src="review/before/f0110.png" alt="기존 조명"><img id="new" class="new" src="review/after/f0110.png" alt="적용 후 조명"><div class="line"></div></div><label for="split">비교 경계</label><input id="split" type="range" min="0" max="100" value="50"></section>
<section class="panel"><h2>적용한 조명값</h2><table><tr><th>항목</th><th>기존</th><th>적용 후</th></tr><tr><td>World strength</td><td>0.45</td><td>0.28</td></tr><tr><td>중국 Key</td><td>170,000W / 95m</td><td>170,000W / 70m</td></tr><tr><td>중국 Fill</td><td>70,000W</td><td>40,000W</td></tr><tr><td>미국 Key</td><td>200,000W / 105m</td><td>200,000W / 75m</td></tr><tr><td>미국 Rim</td><td>110,000W</td><td>65,000W</td></tr><tr><td>창고</td><td>기존 천장광</td><td>긴 직사각형 조명 + 작업 구역 보조광 3개</td></tr></table><p>배경·재질·형상·카메라·애니메이션·노출은 유지했습니다. 청색 보조광을 중성에 가깝게 조정했습니다. 정지 프레임 비교이며 전체 영상의 연속 재생 검토는 포함하지 않습니다.</p></section>GALLERY
</main><script>const f=document.querySelector('#frame'),s=document.querySelector('#split'),n=document.querySelector('#new'),o=document.querySelector('#old'),l=document.querySelector('.line');f.onchange=()=>{n.src='review/after/f'+f.value+'.png';o.src='review/before/f'+f.value+'.png'};s.oninput=()=>{n.style.clipPath='inset(0 '+(100-s.value)+'% 0 0)';l.style.left=s.value+'%'}</script></html>'''
(R/'review.html').write_text(page.replace('OPTIONS',options).replace('GALLERY',gallery),encoding='utf-8')
v=json.loads((R/'verification.json').read_text());assert v['passed']
readme=f'''# PNPLINE daylight lighting v001

Source: {json.loads((R/'source.json').read_text())['source']}

Separate working file: pnpline-hero-lighting-daylight-v001.blend

Source remains unchanged. The lighting variant reduces environment and fill, shapes the exterior key, neutralizes light colors and adds 3 warehouse task lights. Existing camera, geometry, materials and animation fingerprints match after reopening the saved file. Details: verification.json and changes.json.

Comparison frames: {', '.join(str(f) for f in frames)}. Before and after: Cycles OptiX, 1440x810, maximum64 samples, minimum32, adaptive threshold .02, OIDN, seed29, animated seed off. AgX Medium High Contrast, exposure+.3. These are still comparisons; full animation and temporal/compression review were not performed.

The saved Blender file retains its original production render settings. Preview settings are applied only in memory after saving.

Open review.html for a before/after slider and all 8 paired views. review/before and review/after contain full 1440x810 PNGs. review/comparison contains labeled pairs. review/comparison-overview.jpg shows four principal frames.

Candidate SHA256: {v['candidate_sha256']}

Reproduce: open the source blend with Blender 5.1 background factory-startup and run scripts/lighting.py -- build; render source with -- before; open candidate and run -- after, then -- verify; run Python scripts/package.py. Paths are recorded in scripts/lighting.py; adjust ROOT/SOURCE when moving.
'''
(R/'README.md').write_text(readme,encoding='utf-8')
plan=R/'PLAN.md';plan.write_text(plan.read_text(encoding='utf-8-sig').replace('- [ ]','- [x]'),encoding='utf-8')
print(json.dumps({'comparisons':len(frames),'overview':str(R/'review'/'comparison-overview.jpg'),'verification_passed':v['passed']}))
