from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];ver='v028';qa=json.loads((R/f'review/title-water-verified-{ver}.json').read_text());assert all(qa['checks'].values())
file=R/f'review/layout-proposal-{ver}.blend';assert hashlib.sha256(file.read_bytes()).hexdigest()==qa['sha256']
report='''# CHINA 곡률 및 S자 수로 수정 v028

작업 파일: `review/layout-proposal-v028.blend`. 기준은 크레인과 S1 동작을 통합한 v021이며, 이전 파일은 보존했다.

## 수정 내용
- CHINA의 다섯 글자 전체를 하나의 원호로 변형했다. I를 중심으로 감싸며 C와 A 중심의 접선 방향 차이는 100도, 두 접선 사이 안쪽 각도는 약 80도다. 글자 폭과 간격을 원호 방향으로 16% 늘려 새 곡률에서도 기존 강둑 위에 놓이게 했다. 양끝 구름은 글자 이동에 맞춰 옮겼다.
- 수로는 참조의 중앙 굽이, 오른쪽 반대 곡률, 끝부분의 회전을 따라 양쪽 강둑을 다시 만들었다. v024의 단순 변위 방식과 v027의 구간별 곡선 연결을 수정하고, 최종본은 각 강둑을 하나의 주기적 3차 B-spline으로 구성했다. 위치·접선·곡률이 연속되며, 강둑당 512개 표본으로 메시를 구성했다.
- 강둑에 맞춰 나무를 이동하고 줄기를 가장자리에서 24cm 안쪽에 배치했다. 오른쪽 고층 건물 6동은 형태·상대 배치를 유지한 채 함께 이동해 지면 위에 놓았다. 글자 아래 기존 육지의 뒤쪽 경계도 확장했다. 수로를 가리던 시험용 글자 받침은 최종본에 없다.

## 검증
저장본을 재개방해 13개 검사 통과. 애니메이션 67개는 v021과 동일하며, 전체 정수 프레임에서 카메라·타깃·컨테이너·선박·인양 장치·회전 붐 행렬이 동일하다. 변경은 글자·구름·수로·강둑·인접 나무와 고층 건물에 한정했다.
강둑 자기 교차 없음, 수면과 지형 경계 오차 0, 글자 밑면의 수면 침범 없음, 강변 나무와 고층 건물의 접지 검사를 통과했다. 전면 수로의 폭과 S자 곡률 전환은 `title-water-verified-v028.json`에 기록했다.

## 시각 검토
f156의 같은 카메라로 v021, v024, v027, v028 수로 확대 화면을 비교했다. 참조 이미지를 그대로 투영한 것이 아니라 실제 편집 가능한 3D 지형이다. 카메라·도시의 전체 비례와 기존 프록시 건물 디자인이 스타일프레임과 완전히 같은 것은 아니다. 이번 수정은 CHINA의 감싸는 배치와 수로 곡선에 해당한다.

## 재현
정적 곡률 조정은 shape_title_water.py, 수로 윤곽은 trace_s_basin.py --smooth, 글자 강둑 배치는 fit_title_shore.py, 최종 접지는 repair_bank_support.py를 사용했다. 최종 검증은 verify_title_water.py, 확대 렌더는 render_basin_comparison.py다. 각 중간 파일과 변화 기록을 함께 보존했다.
'''
(R/f'review/title-water-revision-{ver}.md').write_text(report,encoding='utf-8')
section='''<section id="title-water-v028" style="padding:24px;background:white;border:3px solid #257c8c;margin-bottom:32px"><h1>CHINA 곡률 · 수로 곡선 수정 v028</h1>
<p>중앙의 완만한 굽이와 오른쪽 S자 전환부를 연속 곡선으로 다시 만들었습니다. f156, 같은 카메라·조명으로 비교합니다.</p>
<figure><img src="inputs/basin-curve-reference.png" style="width:100%;aspect-ratio:auto"><figcaption>사용자 제공 스타일프레임의 수로 곡선</figcaption></figure>
<div class="grid"><figure><img src="review/basin-detail-v027.png" style="width:100%;aspect-ratio:auto"><figcaption>수정 전 v027 · 지적하신 두 연결부</figcaption></figure><figure><img src="review/basin-detail-v028.png" style="width:100%;aspect-ratio:auto"><figcaption>수정 후 v028 · 중앙과 오른쪽을 연속 곡선으로 연결</figcaption></figure></div>
<p><a href="review/basin-detail-v028.png">수정 후 확대 원본</a> · <a href="review/layout-proposal-v028.blend"><b>Blender 파일: layout-proposal-v028.blend</b></a> · <a href="review/title-water-verified-v028.json">검증 결과 13/13</a> · <a href="review/title-water-revision-v028.md">변경 기록</a></p>
<figure><img src="review/title-water-v028.png" style="width:100%;aspect-ratio:auto"><figcaption>CHINA와 도시·수로 전체 배치 · f156</figcaption></figure>
<details><summary>이전 시도와 최초 기준</summary><div class="grid"><figure><img src="review/basin-detail-v024.png" style="aspect-ratio:auto"><figcaption>v024 · 오른쪽 직선 느낌이 남았던 시도</figcaption></figure><figure><img src="review/basin-detail-v021.png" style="aspect-ratio:auto"><figcaption>v021 · 수정 전 기준</figcaption></figure></div></details>
<p>v021의 애니메이션 67개와 전체 프레임 카메라·선박·크레인 동작은 유지했습니다. 기존 파일은 보존했습니다.</p></section>'''
p=R/'review.html';html=p.read_text(encoding='utf-8')
if 'id="title-water-v028"'in html:
 a=html.index('<section id="title-water-v028"');b=html.index('</section>',a)+len('</section>');html=html[:a]+html[b:]
start=html.index('<section ');p.write_text(html[:start]+section+html[start:],encoding='utf-8')
with (R/'decision-log.md').open('a',encoding='utf-8')as f:f.write('\n\n## CHINA 및 수로 v028\n사용자가 지적한 중앙과 오른쪽의 곡선 연결부까지 재수정했다. 최종 작업 파일은 review/layout-proposal-v028.blend이며 13개 검사 통과. 단순 변위 및 개별 Bezier 연결 시도를 거쳐, 강둑을 C2 연속 B-spline으로 교체했다.\n')
paths=[file,R/'review/basin-detail-v028.png',R/'review/title-water-v028.png'];assert all(p.exists()for p in paths)
(R/f'review/title-water-delivery-{ver}.json').write_text(json.dumps({'file':str(file),'checks':qa['checks'],'hashes':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths}},indent=2))
print(json.dumps({'file':str(file),'checks':qa['checks'],'review_url':'http://127.0.0.1:18774/review.html?revision=title-water-v028#title-water-v028'},indent=2))
