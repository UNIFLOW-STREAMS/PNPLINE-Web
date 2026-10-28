from pathlib import Path
import json,shutil,hashlib
R=Path(__file__).resolve().parents[1]
qa=json.loads((R/'review/crane-verified-v019.json').read_text());assert all(qa['static_checks'].values())
shutil.copyfile('C:/Users/KIMTAE~1/AppData/Local/Temp/codex-clipboard-e7ebdf27-aa4f-4015-84e0-ce4a77f96acf.png',R/'inputs/crane-reference.png')
report='''# 크레인 외형 제안 v019 — 동작 통합 전

파일: `review/crane-style-proposal-v019.blend`. 기준: `review/layout-proposal-v017.blend`.

## 수정 외형
27m로 길게 뻗던 기존 붐을 약 6.4m의 짧은 수평 붐으로 바꾸었다. 지역 좌표에서 붐 높이는 11.9m→6.5m, 상단 삼각 지지점은 15.2m→8.1m다.
기존 파이프 모양 부재를 청색 직사각형 보·트러스와 흰 수직 기둥 4개로 바꾸었다. 기둥은 기존 부두의 z=1.25 지면에 놓인 받침에 닿는다. 사선 보강재는 기둥 안쪽에 배치했다.
기둥의 작업 공간과 겹치던 NA 가옥 4동과 나무 2그루는 가까운 빈 육지로 이동했다. 개수와 형상은 보존했다. 각 이동은 crane-style-proposal-v019.json에 기록했다.

## 확인한 증거
저장본 재개방, f156 전체 및 확대 Cycles 렌더. 기둥 접지·수직성·가옥과의 중첩·변경 범위·기존 48개 액션 보존 검사 5개 통과.
원본의 구조·액션은 보존하고 해당 크레인의 가시 외형만 대체했다. C 앞 도시·CHINA·구름·수로·선박 및 카메라를 수정하지 않았다.

## 동작 통합은 미완료
이 파일은 외형 검토용 정지 제안본이다. 새 작은 훅은 검토 위치에 정지해 있고 원본 인양 리그에 연결되어 있지 않다. 원본 인양 장치의 시각 요소는 제안본에서만 숨겼다. 원본 v017은 보존했다.
기존 인양 장치 상단은 f0에서 새 붐 하단보다 약 1.39m 높고, f156의 대기 높이는 약 2.74m 높다. 기존 하중 위치도 새 단축 붐의 현재 수평 도달 영역과 다르다. 외형만 축소해도 기존 동작이 정상이라고 주장할 수 없다.
새 구조에 맞추려면 S1 인양 높이·트롤리/상부 구조의 도달 경로·케이블 및 필요시 근접카메라 연결을 조정해야 한다. 컨테이너 안착 시점/최종 적재 위치와 이후 항해는 보호 목표다.
작업지시서 v0.2 §10의 보호된 카메라·동작 변경 전 확인 조건에 따라 별도 승인 전까지 전체 마스터에 채택하지 않는다.

## 범위와 가정
단일 이미지에서 보이지 않는 후면 보강재·기계실·캐빈·받침은 간략한 입체 구조로 구성했다. 최종 구조공학 검증이나 전체 타임라인의 충돌 검증은 수행하지 않았다.
원본 애니메이션에 새 크레인이 연결되었다고 해석하면 안 된다. 승인 이후 실제 연결과 S1–S2 재생 검증이 필요하다.
'''
(R/'review/crane-proposal-v019.md').write_text(report,encoding='utf-8')
p=R/'review.html';html=p.read_text(encoding='utf-8');start=html.index('<section ')
section='''<section id="crane-v019" style="background:white;padding:24px;border:3px solid #278195;margin-bottom:30px"><h1>크레인 외형 수정 제안 — v019</h1><p><b>외형 검토용입니다. S1 인양 동작 통합은 아직 완료되지 않았습니다.</b></p>
<p>긴 돌출 붐을 짧은 수평 보로 바꾸고, 부두에 접지된 흰 기둥 4개와 청색 삼각 지지 구조를 만들었습니다. 기둥 주변 가옥 4동과 나무 2그루를 옮겨 작업 공간을 확보했습니다.</p>
<div class="grid"><figure><img src="review/na-detail-v017.png" style="aspect-ratio:auto"><figcaption>수정 전 v017 · 동일 f156 카메라</figcaption></figure><figure><img src="review/crane-detail-v019.png" style="aspect-ratio:auto"><figcaption>외형 제안 v019 · 실제 저장본 렌더</figcaption></figure></div>
<details open><summary>사용자 스타일프레임</summary><img src="inputs/crane-reference.png" style="max-width:100%;height:auto"></details>
<p><a href="review/crane-style-proposal-v019.blend">Blender 외형 제안본</a> · <a href="review/design-crane-v019.png">전체 렌더</a> · <a href="review/crane-proposal-v019.md">동작 충돌·승인 필요 범위</a> · <a href="review/crane-verified-v019.json">정적 검사 5/5</a></p>
<p>기존 인양 장치는 새 붐보다 f0에서 약 1.39m, f156에서 약 2.74m 높습니다. 원본 동작은 보존했으며, 새 검토용 훅은 아직 원본 인양 리그에 연결하지 않았습니다. S1 인양 경로·높이·케이블과 필요한 근접카메라 조정은 별도 범위 확인 후 진행합니다.</p></section>'''
assert 'id="crane-v019"'not in html;p.write_text(html[:start]+section+html[start:],encoding='utf-8')
paths=['review/crane-style-proposal-v019.blend','review/crane-detail-v019.png','review/design-crane-v019.png','review/layout-proposal-v017.blend','inputs/crane-reference.png']
(R/'review/crane-delivery-v019.json').write_text(json.dumps({'status':'static proposal, animation integration pending','hashes':{f:hashlib.sha256((R/f).read_bytes()).hexdigest()for f in paths},'verification':qa},indent=2))
with (R/'decision-log.md').open('a',encoding='utf-8')as f:f.write('\n\n## 크레인 v019 외형 제안\n스타일프레임과 같은 낮은 포털·짧은 붐 제안. S1 원본 인양 높이와 수평 도달 범위 충돌을 확인했다. 원본 동작은 보존했으며 동작 통합 전 승인 대기. review/crane-proposal-v019.md 참조.\n')
print('Packaged static proposal',qa['static_checks'])
