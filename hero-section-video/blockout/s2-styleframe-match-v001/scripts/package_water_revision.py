from pathlib import Path
import shutil
R=Path(__file__).resolve().parents[1]
shutil.copyfile('C:/Users/KIMTAE~1/AppData/Local/Temp/codex-clipboard-df44a4f1-819a-42d2-95f7-bfb514304d6d.png',R/'inputs/waterway-reference.png')
p=R/'review.html';html=p.read_text(encoding='utf-8');start=html.index('<section ')
section='''<section style="background:white;padding:20px;border:3px solid #278195;margin-bottom:30px"><h1>N·A 방향 수로 확장 — v011</h1>
<p>수로 오른쪽 끝을 N·A 앞으로 늘리고, 보이는 굽이 구간의 폭을 약 0.87m → 2.10m 이상으로 넓혔습니다. 바깥 수변 벽과 육지·해안 면을 함께 연결했습니다. 도시 쪽 수변, 문자, 구름, 카메라와 애니메이션은 그대로입니다.</p>
<div class="grid"><figure><img src="review/water-detail-v007.png"><figcaption>수정 전 v007 · 오른쪽 수로가 짧고 좁음</figcaption></figure><figure><img src="review/water-detail-v011.png"><figcaption>수정 후 v011 · N·A 앞까지 이어지는 굽이</figcaption></figure></div>
<details><summary>컨셉 수로 비교</summary><img src="inputs/waterway-reference.png" style="max-width:900px;height:auto"></details>
<p><a href="review/layout-proposal-v011.blend">Blender 수정본 v011</a> · <a href="review/design-proposal-v011.png">전체 렌더</a> · <a href="review/waterway-verified-v011.json">수로 검증</a> · <a href="review/title-scope-v011.json">변경 범위 검증</a></p>
<p class="small">수로·육지·해안 메시 4개만 수정한 제안본입니다. 전체 마스터 확정본이 아니며, 기존 카메라 연속성과 크레인/전체 구도 검토는 별도 미결 사항입니다.</p></section>'''
html=html[:start]+section+'<details><summary>이전 문자·구름 수정 기록</summary>'+html[start:]
p.write_text(html.replace('</html>','</details></html>'),encoding='utf-8')
(R/'review/waterway-revision-v011.md').write_text('''# 수로 오른쪽 굽이 확장 v011

사용자 요청: 스타일프레임처럼 수로를 N·A 가까이까지 연결하고 끝 부분 폭을 확보.

기준 v007. SF_BASIN_WATER_SURFACE 외곽, SF_BASIN_OUTER_WALL, SF_FRONT_LAND, SF_COAST_FOLDED_FACE의 메시 좌표만 수정했다. 도시 안쪽 수변과 건물·나무·문자·구름·카메라·선박·크레인·액션은 수정하지 않았다. 수로 X 최대치 8.457→11.814. 오른쪽 전면 굽이(inner x>6, 18<y<20)의 최소 폭 0.871→2.104. 물과 벽·육지 경계의 평면 오차 0. 물 전체가 바깥 해안 안에 포함됨.

v008은 글자 받침 아래 수면 영역을 늘려 기각했다. v009/v010에서 확장 구간을 조절했고, v010 렌더의 육지 면 중첩을 발견했다. v011에서 바깥 해안 경계를 기존 해안과 확장한 수로에 맞춰 방사형으로 재배열하여 면 중첩을 제거했다. 실제 f156 전체/상세 렌더를 다시 생성하고 확인했다.

테스트 정의 보완: 초기 폭 검사는 도시 뒤쪽 좁은 통로까지 포함했다. 사용자가 지적한 화면상 오른쪽 전면 굽이를 구분해 측정 범위를 명시했다. 수정된 동일 검사로 v007 RED, v011 GREEN. 뒤쪽 전체 통로가 2m 이상이라고 주장하지 않는다.

발밑 검사에는 기존 상태와 비교하는 평면 영역 검사를 사용한다. N 하단 8개 샘플, SF_CRANE_LEG.002 하단 4개 샘플이 기존에도 수면 영역 위에 있다. 이번 수정으로 추가된 것은 없으며 기존 지지 문제를 해결했다고 주장하지 않는다. 전체 프로젝트의 기존 카메라 f104 연속성 실패도 이번 수로 수정 범위 밖이다.

재현: v007에서 scripts/widen_waterway.py -- <새 출력 경로>. 검증: tests/waterway_extent.py, scripts/verify_title_scope.py -- --waterway-only. 여섯 수로 조건 통과. 다른 2,619개 오브젝트 검사 항목 및 48개 액션 동일 여부는 title-scope-v011.json 참조.
''',encoding='utf-8')
with (R/'decision-log.md').open('a',encoding='utf-8')as f:f.write('\n\n## N·A 수로 확장 v011\n사용자 요청으로 우측 수로·수변·해안 4개 메시를 수정. review/waterway-revision-v011.md 참조. 기존 글자·구름 배치 유지.\n')
