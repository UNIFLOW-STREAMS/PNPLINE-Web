from pathlib import Path
import json,hashlib,shutil
R=Path(__file__).resolve().parents[1];v='v017'
qa=json.loads((R/f'review/na-district-verified-{v}.json').read_text());assert all(qa['checks'].values())
build=json.loads((R/f'review/na-district-build-{v}.json').read_text())
shutil.copyfile('C:/Users/KIMTAE~1/AppData/Local/Temp/codex-clipboard-b1472102-b44e-40ef-ac4c-30da211ffa00.png',R/'inputs/na-front-district-reference.png')
files=['review/layout-proposal-v014.blend','review/layout-proposal-v017.blend','inputs/na-front-district-reference.png','review/na-detail-v014.png','review/na-detail-v017.png','review/design-proposal-v017.png','review/na-context-v017-f96.png','review/na-context-v017-f216.png']
manifest={f:hashlib.sha256((R/f).read_bytes()).hexdigest()for f in files}
(R/'review/na-district-delivery-v017.json').write_text(json.dumps({'hashes':manifest,'checks':qa,'build':build},indent=2),encoding='utf-8')
report='''# NA 앞 저층 도시 수정 v017

작업 파일: `review/layout-proposal-v017.blend`.
기준은 C 앞 도시 수정이 포함된 `review/layout-proposal-v014.blend`이며 기존 파일은 덮어쓰지 않았다.

## 반영한 구성
- 저층 주택 29동: 경사진 기와지붕 26동, 평지붕과 옥상 난간이 있는 건물 3동. 수로 전면부터 NA 아래의 오른쪽 굽이까지 군집을 연장했다.
- 항구 건물 2동: 더 큰 두 층 규모, 짙은 팔작형 지붕과 올라간 처마, 목재 띠·창틀·석재 모서리·출입 계단.
- 층별 창과 측면 창, 기와선과 용마루, 문·기단을 실제 편집 가능한 형상으로 제작했다.
- 나무 19그루와 소형 트럭 1대, 부두 볼라드·가로등. 기존 크레인 기둥 주변과 전면 서비스 통로를 비웠다.
- 원본 해당 구역 프록시는 숨겼으며 새 모델은 `NA_WATERFRONT_DISTRICT` 컬렉션에 있다.

## 검증
Blender 5.1.0, Cycles CPU. 저장본을 별도 프로세스에서 재개방하여 f156 전체/상세 렌더 및 f96/f216 문맥 렌더를 생성했다.
구성·NA 방향 확장·육지 지지·건물 지붕 외곽끼리 비중첩·차량 접지·기존 프록시 비표시·보호 객체·애니메이션 등 9개 검사 통과.
원본 4,426개 객체의 허용된 가시성 변경 이외 변환/메시/재질 연결/카메라 차이 없음. 48개 애니메이션 액션 동일.
v015의 가옥 23동과 성긴 군집을 발견하여 밀도 검사를 통과하지 못한 기록을 보존했다. v016에서 29동으로 증가시키고 v017에서 작은 집의 지붕을 박공지붕과 일부 평지붕으로 구분했다.
현재 참조와 저장본 해시는 `na-district-delivery-v017.json`에 기록했다.

## 시각 판정과 범위
이번 NA 구역의 빈 공간, 저층 지붕 군집, 오른쪽 항구 건물의 디자인을 수정했다. 정확한 픽셀 복제 또는 최종 전체 스타일프레임 일치로 판정하지 않는다.
참조보다 현재 크레인이 크게 전경을 가리는 문제, 기존 카메라 연속성, 바다/조명/선박의 기존 차이는 그대로 남아 있다. C 앞 구역, CHINA 문자, 구름과 수로는 변경하지 않았다.
골목의 숨은 부분과 후면 창호·문·식재는 참조의 건축 어휘에 맞춘 추론이다.
지원 검사는 지붕 외곽/지면 표본과 정차 차량 접지 검사다. 전 타임라인의 연속 충돌 검증이나 전체 마스터 승인에 해당하지 않는다.
저장 로그의 사용자 썸네일 캐시 쓰기 경고는 .blend 저장과 분리되어 있으며, 별도 재개방과 새 렌더는 정상 종료했다.

## 재현
v014를 `--factory-startup -b`로 열고 `scripts/refine_na_district.py -- <존재하지 않는 출력 .blend>`를 실행한다.
`scripts/verify_na_district.py`는 출력 버전에 대응하는 빌드 기록과 v014를 비교한다.
`render_na_detail.py`, `render_design.py`, `render_na_context.py`는 저장본을 수정하지 않고 검토 이미지를 출력한다.
'''
(R/'review/na-district-revision-v017.md').write_text(report,encoding='utf-8')
p=R/'review.html';html=p.read_text(encoding='utf-8');start=html.index('<section ')
section='''<section id="na-v017" style="background:white;padding:24px;border:3px solid #278195;margin-bottom:30px"><h1>NA 앞 도시 구성·디자인 수정 — v017</h1>
<p>작은 기와·평지붕 건물 29동을 수변과 NA 아래까지 연결하고, 오른쪽 항구 건물 2동에 층별 창호와 올라간 처마를 만들었습니다. 나무·부두 소품·소형 트럭도 정리했습니다.</p>
<div class="grid"><figure><a href="review/na-detail-v014.png"><img src="review/na-detail-v014.png" style="aspect-ratio:auto"></a><figcaption>수정 전 v014 · f156</figcaption></figure><figure><a href="review/na-detail-v017.png"><img src="review/na-detail-v017.png" style="aspect-ratio:auto"></a><figcaption>수정 후 v017 · 동일 카메라·렌더 영역</figcaption></figure></div>
<details open><summary>사용자 스타일프레임</summary><img src="inputs/na-front-district-reference.png" style="max-width:100%;height:auto"></details>
<p><a href="review/layout-proposal-v017.blend"><b>작업 Blender 파일: layout-proposal-v017.blend</b></a> · <a href="review/design-proposal-v017.png">전체 렌더</a> · <a href="review/na-district-verified-v017.json">검증 9/9</a> · <a href="review/na-district-revision-v017.md">수정 기록</a></p>
<p>C 앞 도시·문자·구름·수로 수정이 포함된 v014에서 이어 작업했습니다. 카메라 및 기존 48개 애니메이션 액션은 동일합니다. 크레인의 기존 규모·가림과 전체 장면의 미결 사항은 이번 구역 수정과 별도입니다.</p></section>'''
assert 'id="na-v017"' not in html
p.write_text(html[:start]+section+html[start:],encoding='utf-8')
with (R/'decision-log.md').open('a',encoding='utf-8')as f:f.write('\n\n## NA 앞 도시 v017\n사용자 요청에 따라 v014에서 저층 군집과 항구 건물·정차 차량·식재를 수정했다. review/layout-proposal-v017.blend 및 review/na-district-revision-v017.md 참조. 전체 마스터 확정과 구분한다.\n')
print('PACKAGED',qa['candidate'],qa['checks'])
