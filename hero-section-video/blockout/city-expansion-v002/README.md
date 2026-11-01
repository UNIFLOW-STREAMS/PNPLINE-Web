# PNPLINE 미국 후면 스카이라인 v002

USA와 기존 도시 뒤의 빈 영역에 랜드마크 3개와 주변 건물 28개를 추가했습니다. 이 중 6개는 후속 요청에서 표시한 화면 왼쪽의 빈 공간을 채웁니다. 같은 main 작업공간에서 작업했고 이전 v001 Blender 결과물을 보존했습니다.

## 결과물

- pnpline-city-expansion-v002.blend: 편집 가능한 최종 장면
- review.html: 동일 카메라의 수정 전후 비교, 전체 영상, 후면 배치와 상세
- preview/pnpline-city-expansion-v002.mp4: 33초 / 30fps / 990프레임 / 1280×720
- scripts/build.py, architecture.py, plan_skyline.py, dense_layout.json: 재현 가능한 제작 코드와 배치
- delivery.json: 검증 요약과 결과물 해시

## 디자인과 배치

새 랜드마크는 원 월드 트레이드 센터의 삼각 패싯과 첨탑, 스페이스 니들의 원반형 전망대와 가는 지지대, 30 록펠러 플라자의 단계형 석재 몸체를 참고했습니다. 미니어처의 식별성을 우선한 해석 모델입니다. 전체 높이는 각각 50·36·36단위이며 첨탑과 상부 난간을 포함합니다.

기존 카메라 f300·315의 실제 투영과 가림 검사를 기준으로 위치와 높이를 정했습니다. 스페이스 니들은 U 왼쪽, 새 첨탑과 계단형 타워는 A 오른쪽에 나타납니다. 후면 보조 타워들은 U/S, S/A 사이에서 다른 높이로 드러납니다. 일반 주변 건물은 낮게 유지하고 글자에 가려지는 일부 후면 타워만 높였습니다. 석재·벽돌·유리 외장과 층수를 달리해 반복을 줄였습니다.

왼쪽 해안의 새 건물 6개는 3×3 기단과 12·15·18단위 높이를 사용합니다. 기존 도로를 유지하며 빈 필지에 배치했습니다. 기단끼리 또는 기단과 보도 사이의 최소 간격은 0.5단위입니다. 후속 카메라 이동에서는 가장 왼쪽 건물이 자연스럽게 화면 밖으로 빠집니다.

v001의 151개 건물을 유지한 최종 건물 수는 182개입니다. 랜드마크 6개와 주변 건물 176개이며, 연결도로 6개와 현수교를 유지했습니다. 새 건물과 겹치는 가로수 4개를 생략해 가로수는 66개입니다.

## 곡률과 표현

기존 지구 중심과 R=140의 구면 매핑을 사용합니다. 지형 상단은 R=140.68이며 건물은 각 기단 위치의 표면 법선에 맞춘 강체입니다. 평평한 상부와 구면 하부를 가진 기초로 지면에 접합니다. 새 평면판을 덧씌우지 않고 기존 곡면 지형의 빈 필지를 사용했습니다.

워크벤치 렌더와 원본 조명·카메라를 유지했습니다. 원 WTC 본체와 유리 면의 깊이 간섭은 유리 패널의 법선 간격을 확보해 제거했습니다. AA8의 동일 카메라에서 재검증했습니다. 열린 창문 면은 그림자를 만들지 않고 닫힌 몸체가 그림자를 만듭니다.

## 검증 기준

- f300·315에서 새 실루엣이 USA 양옆과 글자 사이에 보일 것
- f330·349 및 트럭·창고·배송 구간에서 물류 장면을 가리지 않을 것
- 새 건물의 법선 정렬, 구면 접지, 도로와 기존 기초 사이 간격 검사
- 원본 객체 10,032개와 모든 액션, 990프레임 카메라·렌즈·변환의 정확 일치
- v001의 151개 건물 ROOT·형상·기초·재질·변환의 정확 일치
- 990개 렌더 프레임과 최종 Blender 해시 일치, 영상 30fps·33초와 전체 디코딩 검사

상세 결과는 review/geometry.json, preservation.json, previous-city-preservation.json, skyline-layout.json, view-bookmarks.json 및 렌더 기록에 저장합니다. 고정 시점은 프레임 번호와 카메라 행렬로 재현합니다. GPU 실행 시간은 측정하지 않았으며 렌더 로그의 경과 시간만 기록합니다.

## 재현

Blender 5.1에서 scripts/build.py를 실행하면 검증된 30fps 카메라 원본을 읽고 최종 blend를 생성합니다. 입력 SHA256은 코드에 고정돼 있습니다. plan_skyline.py는 v001 배치와 확정 해안 후보에서 v002 배치를 생성합니다.

    python scripts/plan_skyline.py
    blender --background --factory-startup -t 6 --python-exit-code 1 --python scripts/build.py

렌더나 검증 중인 작업본을 다시 생성하지 마세요. render.py -- --start 0 --end 989로 PNG를 생성하고 package.py로 영상과 전달 기록을 만듭니다. serve.py --port 18793으로 로컬 검토 페이지를 엽니다.

## 적용 스킬과 설계 참고

threejs-procedural-architecture, threejs-procedural-planets, threejs-visual-validation의 모듈식 형상, 재질별 메시 배치, 공유 구면 좌표계, 고정 시점 검증 원칙을 Blender 제작에 적용했습니다.

- [설계사 SOM — One World Trade Center](https://www.som.com/projects/one-world-trade-center/)
- [Space Needle 공식 역사](https://www.spaceneedle.com/history)
- [Rockefeller Center — 30 Rockefeller Plaza](https://www.rockefellercenter.com/leasing/30-rockefeller-plaza/)

Git 원본은 blend, 제작·검증 스크립트, 확정 배치 JSON, 이 문서, 검토 HTML 및 전달 기록입니다. 렌더 PNG, 로그, blend1, 중간 시험 이미지는 제외합니다.
