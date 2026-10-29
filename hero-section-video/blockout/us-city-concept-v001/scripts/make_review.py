from pathlib import Path
import json,html,hashlib
R=Path(__file__).resolve().parents[1]
def xy(x,y):return (60+(x+55)*5,540-(y+30)*5)
svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 980 590"><rect width="980" height="590" fill="#edf2f2"/><style>text{font-family:Arial,sans-serif;font-size:12px;fill:#152d38}.zone{stroke-width:1.5}</style>']
def rect(x,y,w,h,color,label):
 px,py=xy(x,y+h);svg.append(f'<rect class="zone" x="{px}" y="{py}" width="{w*5}" height="{h*5}" fill="{color}" fill-opacity=".28" stroke="{color}"/><text x="{px+4}" y="{py+16}">{label}</text>')
rect(-31,3.3,150,60.7,'#627d75','Existing US terrace (unchanged)')
rect(-17,4,34,8,'#c47a24','Quay / work crane')
rect(-3,-7,8,22,'#c0473d','P02 work envelope')
rect(35,23,48,17,'#c0473d','Warehouse, docks and outbound yard')
rect(-27,24,49,29,'#2b7ba2','Dense skyline / blocks')
rect(22,34,14,14,'#628544','Civic group')
rect(-24,51,46,4,'#243e6a','USA + stars')
rect(-43,-14,8,8,'#15977c','Liberty island')
rect(20,-1,16,2,'#ab342b','Bridge')
rows=json.loads((R/'review/camera-layout.json').read_text())
pts=' '.join(f'{xy(*r["camera"][:2])[0]},{xy(*r["camera"][:2])[1]}' for r in rows if r['frame']>=421)
svg.append(f'<polyline points="{pts}" fill="none" stroke="#7e38a0" stroke-width="2" stroke-dasharray="5 4"/>')
for row in rows:
 if row['frame']<421:continue
 x,y=xy(*row['camera'][:2]);svg.append(f'<circle cx="{x}" cy="{y}" r="3" fill="#7e38a0"/><text x="{x+5}" y="{y-5}">f{row["frame"]}</text>')
x,y=xy(-55,0);x2,y2=xy(7,0);svg.append(f'<line x1="{x}" y1="{y}" x2="{x2}" y2="{y2}" stroke="#28667c" stroke-width="12" opacity=".45"/><text x="{x}" y="{y+22}">Arrival route: actual swept mesh audited separately</text>')
svg.append('<text x="30" y="30" style="font-size:20px">US_FRAME local XY: functional areas and static dressing</text><text x="30" y="570">Schematic footprint map. Purple: existing camera path. Red: protected work space. Not a collision certificate.</text></svg>')
(R/'review/functional-map.svg').write_text(''.join(svg),encoding='utf-8')
candidate=R/'candidate-us-city-concept-v004.blend';sha=hashlib.sha256(candidate.read_bytes()).hexdigest()
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PNPLINE 미국 도시 후보 검토</title><style>body{margin:0;background:#f4f4ef;color:#162c36;font:16px/1.65 system-ui,sans-serif}main{max-width:1280px;margin:auto;padding:36px}h1{font-size:32px;margin:0}h2{font-size:21px;margin-top:42px}.status{color:#a12e21;font-weight:700}.row{display:grid;grid-template-columns:1fr 1fr;gap:18px}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}img,video{width:100%;background:#ddd}figure{margin:0}figcaption{font-size:14px;padding:8px 0}button,a{color:#155a76}button{padding:9px 16px;border:1px solid #46717c;background:white;cursor:pointer}code{word-break:break-all;font-size:12px}small{color:#52646a} @media(max-width:700px){.row,.grid{grid-template-columns:1fr}}</style><main>
<p>PNPLINE · EDITABLE BLENDER CANDIDATE</p><h1>미국 미니어처 도시</h1><p class="status">판정: 재작업 필요 · 운영 채택본이 아닙니다.</p>
<p>기존 카메라·항로·하역 동작은 보존했습니다. 현재 카메라에서는 자유의 여신상과 도시 상부가 잘리므로 AC-3·AC-4를 충족하지 못합니다. 조감도는 모델 확인용 보조 자료입니다.</p>
<p><a href="candidate-us-city-concept-v004.blend">최종 검토 후보 v004</a> · <a href="report.md">상세 보고서</a> · <a href="decision-log.md">결정 기록</a> · <a href="hashes.json">해시 목록</a></p><code>SHA256: '''+sha+'''</code>
<h2>참조와 편집 가능한 모델</h2><div class="row"><figure><img src="inputs/usa-miniature.png"><figcaption>사용자 첨부 원본</figcaption></figure><figure><img src="review/final-presentation/overview.png"><figcaption>v004 진단 조감도 · 본편 카메라가 아닙니다.</figcaption></figure></div>
<h2>본편 카메라 · 정상 속도 비교</h2><p>f300–720, 모든 정수 프레임, 12fps, 35.083초. 두 영상의 프레임 범위와 속도가 같습니다.</p><button id="play">두 영상 재생</button> <button id="pause">일시 정지</button> <button id="restart">처음부터</button><div class="row"><figure><video id="base" controls preload="metadata" src="preview/baseline-normal.mp4"></video><figcaption>현재 채택 원본</figcaption></figure><figure><video id="candidate" controls preload="metadata" src="preview/candidate-final-normal.mp4"></video><figcaption>최종 후보 v004 · 가독성 실패도 그대로 표시합니다.</figcaption></figure></div>
<h2>실제 카메라의 한계와 미적용 진단 대안</h2><p>아래 화각 대안은 별도의 임시 카메라로만 렌더했으며 .blend에 저장하지 않았습니다. 렌즈를 넓히는 것만으로 모든 장면이 해결됐다는 뜻은 아닙니다.</p><div class="row"><figure><img src="review/camera-options-final/f0421-lens-1.00.png"><figcaption>f421 · 기존 카메라</figcaption></figure><figure><img src="review/camera-options-final/f0421-lens-0.45.png"><figcaption>f421 · 초점거리 45% 진단안, 미적용</figcaption></figure><figure><img src="review/camera-options-final/f0495-lens-1.00.png"><figcaption>f495 · 기존 카메라</figcaption></figure><figure><img src="review/camera-options-final/f0495-lens-0.45.png"><figcaption>f495 · 초점거리 45% 진단안, 미적용</figcaption></figure></div>
<h2>동상 본체 확대 비교</h2><p>참조에서 추정한 본체 높이 7.74 → 10.836, 1.4배입니다. 기단과 카메라는 동일합니다. 배율은 구현 가정이며 미술 승인값이 아닙니다.</p><div class="row"><figure><img src="review/statue-scale-comparison-final/reference-diagnostic.png"><figcaption>참조 비율 기준안</figcaption></figure><figure><img src="review/statue-scale-comparison-final/enlarged-diagnostic.png"><figcaption>선택한 확대안</figcaption></figure></div>
<h2>기본 재질 비교</h2><p>동일한 원본 조명·World·색 관리, Cycles 16샘플입니다. 위 Workbench 형상 검토와 구분합니다.</p><div class="row"><figure><img src="review/baseline-material/f0495.png"><figcaption>f495 원본</figcaption></figure><figure><img src="review/final-material/f0495.png"><figcaption>f495 후보 · 최종 라이팅 작업 전</figcaption></figure></div>
<h2>후속 스타일프레임 입력 후보</h2><p>현재 카메라의 최초·진입·공개 관찰 프레임 3장입니다. 스타일프레임 생성이나 가독성 합격을 의미하지 않습니다.</p><div class="grid"><figure><img src="review/final-reopened/f0000.png"><figcaption>최초 f0</figcaption></figure><figure><img src="review/final-reopened/f0421.png"><figcaption>진입 f421 · 동상 잘림</figcaption></figure><figure><img src="review/final-reopened/f0495.png"><figcaption>공개 관찰 f495 · 문자 상부 잘림</figcaption></figure></div>
<h2>공간과 검증 근거</h2><img src="review/functional-map.svg"><p><a href="review/candidate-us-city-concept-v004-preservation.json">원본 보존 검사</a> · <a href="review/candidate-us-city-concept-v004-collisions.json">메시 교차 검사</a> · <a href="review/visibility-audit.json">가시성 검사</a> · <a href="review/reproduction-comparison.json">재현 비교</a> · <a href="review/independent-review.md">독립 검토</a></p>
<p><small>기존 마스터와 latest-previz.json은 수정하지 않았습니다. 커밋·푸시·PR·외부 업로드·유료 생성 호출은 수행하지 않았습니다.</small></p></main><script>const v=[document.querySelector('#base'),document.querySelector('#candidate')];document.querySelector('#play').onclick=()=>{const t=v[0].currentTime;v.forEach(x=>{x.currentTime=t;x.playbackRate=1;x.play()})};document.querySelector('#pause').onclick=()=>v.forEach(x=>x.pause());document.querySelector('#restart').onclick=()=>v.forEach(x=>{x.currentTime=0;x.playbackRate=1;x.play()});</script></html>'''
(R/'review.html').write_text(page,encoding='utf-8')
print('REVIEW_HTML',sha)
