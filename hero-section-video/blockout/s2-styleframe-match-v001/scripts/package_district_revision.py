from pathlib import Path
import json,shutil,hashlib
R=Path(__file__).resolve().parents[1]
tests=json.loads((R/'review/c-district-verified-v014.json').read_text());scope=json.loads((R/'review/c-district-scope-v014.json').read_text());build=json.loads((R/'review/c-district-build-v014.json').read_text())
assert not tests['failures'] and not tests['errors'] and not scope['changed_objects'] and scope['all_actions_equal'] and not scope['unsupported_vehicle_wheels_or_paths']
for f in ['district-detail-v014.png','design-proposal-v014.png','district-detail-v011.png']:assert (R/'review'/f).exists()
shutil.copyfile('C:/Users/KIMTAE~1/AppData/Local/Temp/codex-clipboard-87bc4c31-54d2-4d82-8ab8-bf835999540b.png',R/'inputs/c-front-district-reference.png')
p=R/'review.html';html=p.read_text(encoding='utf-8');start=html.index('<section ')
section='''<section style="background:white;padding:20px;border:3px solid #278195;margin-bottom:30px"><h1>C 앞 수변 도시 구성·디자인 수정 — v014</h1>
<p>평평했던 돔을 창이 있는 받침부와 둥근 돔으로 바꾸고, 석조 건물 5동의 창·기둥·처마띠·지붕 난간을 세부 모델링했습니다. 정자는 붉은 기둥 8개와 휘어진 팔각 지붕으로 구성했습니다. 전통 건물의 이중 처마, 정원·보행로·가로등·소형 트럭 2대를 함께 정리했습니다.</p>
<div class="grid"><figure><img src="review/district-detail-v011.png" style="aspect-ratio:auto"><figcaption>수정 전 v011</figcaption></figure><figure><img src="review/district-detail-v014.png" style="aspect-ratio:auto"><figcaption>수정 후 v014 · 저장본 f156 직접 렌더</figcaption></figure></div>
<details><summary>사용자 스타일프레임 부분 이미지</summary><img src="inputs/c-front-district-reference.png" style="max-width:1100px;height:auto"></details>
<p><a href="review/layout-proposal-v014.blend"><b>작업 Blender 파일: layout-proposal-v014.blend</b></a> · <a href="review/design-proposal-v014.png">전체 렌더</a> · <a href="review/c-district-verified-v014.json">구성 검사 6/6</a> · <a href="review/c-district-scope-v014.json">변경 범위·접지 검사</a></p>
<p class="small">v011의 문자·구름·수로 수정이 포함된 장면입니다. C 앞 구역의 가시 모델을 교체했고, 기존 애니메이션 48개 액션은 동일합니다. 전체 스타일프레임 작업의 최종 확정 마스터는 아니며 기존 카메라 연속성·크레인 구도 검토는 별도입니다.</p></section>'''
p.write_text((html[:start]+section+'<details><summary>이전 수로·문자·구름 수정 기록</summary>'+html[start:]).replace('</html>','</details></html>'),encoding='utf-8')
blend=R/'review/layout-proposal-v014.blend'
record={'file':str(blend),'sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),'source':build['source'],'new_objects':len(build['new_objects']),'trees':build['tree_count'],'shrubs':build['shrub_count'],'tests':tests,'scope':scope}
(R/'review/c-district-delivery-v014.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
(R/'review/c-district-revision-v014.md').write_text('''# C 앞 수변 도시 수정 v014

## 파일
`review/layout-proposal-v014.blend`가 이번 수정본이다. v011을 기준으로 작업하여 CHINA 곡률, 오른쪽 구름 위치, N·A 방향 수로 수정이 포함되어 있다. 원본 v011 및 중간 v012/v013은 보존했다.

## 구현
- 석조 건물 5동: 아치형 창, 창틀과 창턱, 기둥·주두, 층별 처마띠, 출입구·계단, 옥상 난간과 돌출부.
- 주요 돔 2개: 창이 있는 다각형 받침부, 높이가 있는 곡면 돔, 세로 리브, 상부 장식. 왼쪽 돔은 앞쪽 모서리로 옮겨 구름과의 중첩을 줄였다.
- 붉은 기둥 8개의 정자: 팔각 기단·계단, 이중 곡면 지붕과 올라간 처마·기와선.
- 전통 건물: 두 층의 짙은 기와 처마와 붉은 띠, 사각 출입문·격자. 후면 소규모 전통 지붕도 추가.
- 정원: 새 나무 16그루, 관목 71개, 잔디 화단·석재 경계·정원석·가로등·보행로.
- 정차 차량 2대: 운전석·적재함·창·바퀴·전조등을 분리 모델링하고 실제 육지 안의 주차 공간을 확보.

원본 모델은 해당 구역 가시성만 끄고 새 컬렉션 C_FRONT_HISTORIC_DISTRICT에 편집 가능한 모델을 추가했다. 이미지를 투영하거나 평면으로 대체하지 않았다. 뒷면과 식물 종 등 참조에서 보이지 않는 세부는 일관된 간략 형상으로 구성했다. 이미지와 픽셀 단위로 동일한 복원이라고 주장하지 않는다.

## 검증
v011에서 구성 검사 6개 실패를 확인한 뒤 구현했다. v012의 기둥 개수 검사에는 받침까지 집계하는 오류가 있어 이름을 구분해 수정했다. v014 저장본 재열기 후 6/6 통과. 기존 오브젝트 2,623개를 비교하여 허용된 가시성 교체 외 형상·변환 차이 없음, 48개 액션 동일. 새 트럭 바퀴와 보행로의 육지 지지 검사 통과. f156 전체 및 상세 Cycles 렌더를 새로 출력했다.

초기 v012에서 정자 앞 식재 과밀, 해안 밖으로 나간 보행로, 차량 주변 식재 간섭을 보고 수정했다. 최종 식재는 주차 공간과 정자 입구를 비웠으며 보행로는 육지 내부로 잘랐다.

전체 프로젝트 미결(이 구역 작업과 별도): f104 카메라 회전 연속성, 크레인과 전체 스타일프레임 정합, 기존 지지 문제 및 S1–S4 전체 영상 검증. 이번 구역 완료를 전체 마스터 확정으로 해석하지 않는다.

## 재현
v011에서 scripts/refine_c_district.py -- <새 출력 경로> 실행. 생성 도구는 기존 build_layout_proposal.py의 명시한 기하 함수 정의만 재사용한다. 기준 장면을 생성하는 본문은 실행하지 않는다. 난수 시드는 고정이며 사용한 참조 크롭은 inputs/c-front-district-reference.png에 원본 바이트 그대로 보존했다.
''',encoding='utf-8')
with (R/'decision-log.md').open('a',encoding='utf-8')as f:f.write('\n\n## C 앞 도시 v014\n사용자 요청으로 석조 건물·정자·전통 지붕·정원·차량 구성 수정. review/c-district-revision-v014.md 및 layout-proposal-v014.blend 참조.\n')
