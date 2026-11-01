# 상하이 건축 밀도 보강 v001

작업 파일: `pnpline-cn-shanghai-density-v001.blend`

- 추가 건물 127동: 고층 33동, 와이탄풍 19동, 석고문 주거 74동, 문화시설 1동.
- 중앙 랜드마크 3동 높이 1.6배. SWFC 폭 1.30배, 진마오 폭 1.25배, 상하이 타워 폭 1.35배. 두 보조 고층은 겹침을 피하도록 재배치.
- 건물 사이와 정원에 나무 316그루 추가. 오른쪽 빈터의 과밀 식재와 보행로에 걸친 나무는 제외.
- 기존 수로, 양안, 섬, 다리, 통합 구면 지형 보존. 새 건물과 나무는 해당 위치의 지구 법선에 정렬.
- 항만, 선박, 하역 애니메이션, 미국 구역과 기존 카메라를 보존. 0–989프레임, 30 fps, 총 33초.

`review.html`에서 같은 시점의 전후 비교와 실제 카메라 5개 프레임을 확인할 수 있습니다. 진단 이미지는 Workbench 검토용입니다.

확대된 상하이 타워 상단은 기존 카메라 f96, f132에서 화면 밖으로 나갑니다. 이번 모델링 수정에서는 카메라 구도를 변경하지 않았습니다.

검증 24/24 통과. 원본 오브젝트·메시·재질·액션 보존, 990프레임 카메라/이동 오차 0, 추가 건축의 수로 침범 및 구조물 교차 없음.

원본: `F:\pnpline-landing\hero-section-video\blockout\cn-unified-curvature-v001\pnpline-cn-unified-curvature-v001.blend`

결과 SHA-256: `c0f7d784dbb67562614cfd46cc3a493418de6f6712db2aef2d8933fbee5672ce`

재생성: Blender 5.1에서 `scripts/build.py` 실행. 검증은 `scripts/verify_density.py`, `scripts/audit_preservation.py`로 수행합니다. `scripts/finalize.py`는 현재 파일 해시와 검증·렌더 해시가 모두 일치할 때만 최신 작업 포인터를 갱신합니다.
