from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];ver='v031';qa=json.loads((R/f'review/bridge-verified-{ver}.json').read_text());assert all(qa['tests'].values())
blend=R/f'review/layout-proposal-{ver}.blend';assert hashlib.sha256(blend.read_bytes()).hexdigest()==qa['sha256']
report=f'''# 석조 아치교 및 다리 아래 수로 수정 v031

작업 파일: `review/layout-proposal-v031.blend`. 기준 파일 v028을 보존하고 새 파일로 저장했다.

## 변경
- 기존 다리는 물 위를 건너지 않고 육지 위에 놓여 있었다. 왼쪽 수로의 외곽 강둑을 확장해 다리 아래와 정자 뒤쪽까지 이어지는 물길을 만들었다.
- 얇고 측면이 열린 기존 다리 대신 닫힌 석조 아치 메시, 아치 둘레 돌쌓기, 사각 난간 기둥과 손스침, 교대, 바닥 줄눈을 구성했다. 폭은 1.05m이며 아치 중앙 아래 수면 여유는 1.12m다.
- 오른쪽 끝을 강둑에 맞춰 연결했다. 정자·돔 건물·다른 도시 건물과 CHINA, 구름, 안쪽 섬은 유지했다.

## 검증
저장본 재개방 후 {len(qa['tests'])}개 검사 통과. 기존 67개 액션과 전체 정수 프레임의 카메라·선박·컨테이너·인양 장치·회전 붐 변환이 v028과 같다.
중앙 경간 아래 21개 표본 전부에서 수로가 확인됐고 두 교대의 중심은 육지 위에 있다. 인접 정자와 석조 건물의 하단 표본에서 새 수면 침범이 없으며, 아치 본체는 닫힌 메시다. 수로 경계 자기 교차와 지형/수면 경계 틈도 검사했다.
수정 범위는 기존 교량 가시성, 새 교량 형상, 수면·외곽 강둑·전면 육지의 해당 수로 경계다. 전체 스타일프레임의 재질·식생·건축 디테일을 동일하게 재현한 결과를 뜻하지 않는다.

## 재현
v028에서 `scripts/rebuild_arch_bridge.py -- <새 .blend 경로>`를 실행하고 `verify_arch_bridge.py`로 검사한다. `render_bridge_detail.py`는 같은 f156 카메라와 확대 범위로 전후 이미지를 렌더한다.
'''
(R/f'review/bridge-revision-{ver}.md').write_text(report,encoding='utf-8')
section='''<section id="bridge-v031" style="padding:24px;background:white;border:3px solid #257c8c;margin-bottom:32px"><h1>석조 아치교 · 다리 아래 수로 수정 v031</h1>
<p>육지 위에 있던 다리 아래를 열어 정자 뒤쪽까지 수로를 연결하고, 석조 아치와 난간을 다시 만들었습니다.</p>
<figure><img src="inputs/bridge-style-reference.png" style="width:100%;max-width:750px;aspect-ratio:auto"><figcaption>사용자 제공 스타일프레임</figcaption></figure>
<div class="grid"><figure><img src="review/bridge-detail-v028.png" style="width:100%;aspect-ratio:auto"><figcaption>수정 전 v028 · 다리 아래가 육지로 막힘</figcaption></figure><figure><img src="review/bridge-detail-v031.png" style="width:100%;aspect-ratio:auto"><figcaption>수정 후 v031 · 수로와 석조 아치교</figcaption></figure></div>
<p><a href="review/bridge-detail-v031.png">수정 후 확대 원본</a> · <a href="review/layout-proposal-v031.blend"><b>Blender 파일: layout-proposal-v031.blend</b></a> · <a href="review/bridge-verified-v031.json">검증 11/11</a> · <a href="review/bridge-revision-v031.md">변경 기록</a></p>
<details><summary>전체 구도 f156</summary><img src="review/bridge-full-v031.png" style="width:100%;aspect-ratio:auto"></details>
<p>CHINA와 기존 수로 곡률 수정이 포함돼 있습니다. 정자·돔 건물 위치와 기존 카메라·애니메이션은 유지했습니다.</p></section>'''
p=R/'review.html';html=p.read_text(encoding='utf-8')
if 'id="bridge-v031"'in html:
 a=html.index('<section id="bridge-v031"');b=html.index('</section>',a)+len('</section>');html=html[:a]+html[b:]
start=html.index('<section ');p.write_text(html[:start]+section+html[start:],encoding='utf-8')
with (R/'decision-log.md').open('a',encoding='utf-8')as f:f.write('\n\n## 아치교·수로 v031\n다리 아래 막힌 육지를 열고 정자 뒤로 이어지는 수로 및 석조 아치·난간을 만들었다. 두 교대 접지, 주변 건물 보호, 기존 동작 보존 등 11개 검증 통과. 작업 파일 review/layout-proposal-v031.blend.\n')
paths=[blend,R/f'review/bridge-detail-{ver}.png',R/f'review/bridge-full-{ver}.png'];assert all(p.exists()for p in paths)
(R/f'review/bridge-delivery-{ver}.json').write_text(json.dumps({'tests':qa['tests'],'hashes':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths}},indent=2))
print(json.dumps({'file':str(blend),'tests':qa['tests']},indent=2))
