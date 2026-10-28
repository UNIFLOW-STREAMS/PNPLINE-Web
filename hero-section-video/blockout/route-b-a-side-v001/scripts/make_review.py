import json,math,html
from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];data=json.loads((R/'review/metrics-summary.json').read_text())
# Orthographic projection into the ORIGINAL China tangent plane; this is not a camera illusion.
def local(p):
 x,y,z=p;dx=x+126.883090185;dz=z-59.16655664
 return (.4226182617*dx+.906307787*dz,y)
def canvas_point(p):return 520+2.5*p[0],280-2.5*p[1]
g=json.loads((R/'review/geometry-probe.json').read_text());pts=g['SF_FRONT_LAND']['vertices'];items=[]
for title,rot,label in [('B / city fixed',1,'candidate-b'),('City 180 / original voyage',-1,'city-final')]:
 im=Image.new('RGB',(1000,440),'#e9f1f3');d=ImageDraw.Draw(im);d.text((20,15),title,fill='black')
 d.polygon([canvas_point((rot*p[0],rot*p[1]))for p in pts],fill='#b7b4a1')
 rows=json.loads((R/'review'/f'{label}-metrics-raw.json').read_text())['rows'];path=[r for r in rows if 144<=r['frame']<=510 and int(r['frame'])==r['frame']]
 points=[canvas_point(local(r['ship']))for r in path];d.line(points,fill='#ca592d',width=4)
 for f in [144,216,300,400,510]:
  p=canvas_point(local(next(r['ship']for r in path if r['frame']==f)));d.ellipse((p[0]-4,p[1]-4,p[0]+4,p[1]+4),fill='#202b39');d.text((p[0]+6,p[1]+4),str(f),fill='#202b39')
 for text,x,y in [('C',21.85,-25.62),('A',-11.88,-20.6)]:d.text(canvas_point((rot*x,rot*y)),text,fill='red')
 d.text((20,402),'Original CN tangent-plane projection (m); globe depth is omitted. Orange: actual ship root.',fill='black');im.save(R/'review'/f'route-{label}.png');items.append(im)
frames=[156,178,216,260,300,340,456,510,648]
for label in ['current','candidate-b','city-final']:
 out=Image.new('RGB',(960,606),'#18232b');d=ImageDraw.Draw(out)
 for i,f in enumerate(frames):
  p=R/'review'/label/f'f{f:04d}.png'
  if not p.exists():continue
  pic=Image.open(p).resize((320,180));x=i%3*320;y=i//3*202;out.paste(pic,(x,y));d.text((x+8,y+182),f'{label} / f{f}',fill='white')
 out.save(R/'review'/f'{label}-final-contact.jpg')
rows=''
for label,name in [('current','현행'),('candidate-b','B: 항로·미국 이동'),('city-final','도시 180° 회전')]:
 w=data[label]['windows'];rows+=f'<tr><th>{name}</th><td>{w["problem_transition"]["camera_rotation_total_deg"]:.1f}°</td><td>{w["problem_transition"]["peak_deg_s"]:.1f}°/s</td><td>{w["all"]["camera_rotation_total_deg"]:.1f}°</td><td>{data[label]["peak_ship_rotation_deg_s"]:.1f}°/s</td></tr>'
sections=''
for label,name,file in [('current','현행 원본','current'),('candidate-b','B: 넓은 해상 선회 + 미국 이동','candidate-b'),('city-final','도시 180° 회전 + S1 항만 연결','city-rotation')]:
 sections+=f'<section><h2>{name}</h2><video id="{label}" controls preload="metadata" src="preview/{file}.mp4"></video><p>f96–672 · 577프레임 · 12fps · 48.083초 · 640×360 · Workbench</p><a href="review/{label}-final-contact.jpg"><img src="review/{label}-final-contact.jpg" alt="{name} 대표 프레임"></a></section>'
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>A쪽 출항 비교 — 미채택 후보</title><style>body{font:16px/1.7 system-ui,sans-serif;margin:32px auto;max-width:1500px;padding:0 24px;background:#edf1f3;color:#18232b}h1{line-height:1.25} .notice{background:#fff0da;border-left:5px solid #b76512;padding:20px}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}section{background:white;padding:18px}video,img{width:100%}button,a{color:#145574}button{padding:10px 20px;cursor:pointer}th,td{padding:12px;text-align:left;border-bottom:1px solid #bac7cd}table{border-collapse:collapse;width:100%}.routes{display:grid;grid-template-columns:1fr 1fr;gap:16px}@media(max-width:1000px){.grid,.routes{grid-template-columns:1fr}} </style>
<h1>도시 방향을 반대로 돌리면 출항이 단순해지는가?</h1><p>현재 통합본과 두 개의 별도 제안 비교. 원본 마스터는 보존했습니다.</p>
<div class="notice"><strong>판정: 재작업 필요 · 마스터 미채택</strong><br>도시 회전안은 기존 항로·미국을 유지하면서 A쪽으로 출항하며 전환 회전량이 줄었습니다. 다만 중국 경사 해안과 미국 지형의 선체 겹침이 남습니다. 두 후보 모두 충돌 없는 완성본이 아닙니다. B안은 넓은 180° 우회와 선회 속도 증가 때문에 우선 권고하지 않습니다.</div>
<p><button id="play">세 영상 처음부터 1배속 재생</button> <button id="pause">모두 일시정지</button> <span id="state">같은 프레임 범위 · 원래 속도</span></p><div class="grid">'''+sections+'''</div><h2>정량 비교</h2><table><tr><th>후보</th><th>전환 f171–340 누적 회전</th><th>전환 최고 각속도</th><th>전체 f96–672 누적 회전</th><th>선박 최고 회전 속도</th></tr>'''+rows+'''</table><p>정규화 Quaternion의 최단 회전각 합계. 카메라 월드 회전과 선박 상대 방위는 서로 다릅니다. 상세한 P95·반전·가림·충돌 범위는 <a href="review/metrics-summary.json">지표 JSON</a>과 <a href="report.md">보고서</a>에 있습니다.</p>
<h2>실제 공간 항로</h2><div class="routes"><img src="review/route-candidate-b.png"><img src="review/route-city-final.png"></div>
<h2>도시 회전안 S1 연결</h2><p>f0–72 카메라·컨테이너는 원본 보존. 크레인 위치·선회/케이블 연결을 조정하고 f73–339 카메라를 연결했습니다.</p><video controls preload="metadata" src="preview/city-s1.mp4" style="max-width:960px"></video>
<h2>Blender 파일</h2><ul><li><a href="city-rotation-proposal/candidate-city-rotation-v002.blend">도시 회전 제안 v002</a></li><li><a href="candidate-b-a-side-v002.blend">B 항로 제안 v002</a></li><li><a href="hashes.json">파일 해시</a> · <a href="report.md">검증 및 남은 문제</a></li></ul>
<script>const vs=[...document.querySelectorAll('.grid video')];document.querySelector('#play').onclick=async()=>{for(const v of vs){v.currentTime=0;v.playbackRate=1;v.muted=true;}await Promise.all(vs.map(v=>v.play()));document.querySelector('#state').textContent='1배속 동시 재생 중';};document.querySelector('#pause').onclick=()=>vs.forEach(v=>v.pause());</script></html>'''
if (R/'adoption.json').exists():
 adoption=json.loads((R/'adoption.json').read_text(encoding='utf-8'))
 notice='<div class="notice"><strong>'+html.escape(adoption['adopted_on'])+' · 도시 회전안 채택 완료</strong><br>최신 프리비즈: <code>'+html.escape(adoption['master'])+'</code><br>아래 비교는 채택 전 검토 이력입니다. 해안·선체 겹침은 후속 수정 사항으로 남습니다.</div>'
 page=page.replace('<h1>',notice+'<h1>',1)
(R/'review.html').write_text(page,encoding='utf-8')
